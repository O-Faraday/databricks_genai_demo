# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # Agent Bricks by code: Knowledge Assistant + Supervisor Agent
# MAGIC
# MAGIC **Everything by code, on serverless compute.** This notebook:
# MAGIC 1. Creates a **Unity Catalog function** as an action tool (`issue_refund`)
# MAGIC 3. Creates a **Supervisor Agent** coordinating 2 sub-agents/tools: the `customer genie` Genie Space, and the UC function
# MAGIC 4. Tests it with **human-in-the-loop** approval before any refund action
# MAGIC 5. **Autologs every call as MLflow traces**
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Serverless compute attached to this notebook
# MAGIC - Previews enabled: *Mosaic AI Agent Bricks* (+ *AI Gateway* if you use the Supervisor API cells)
# MAGIC - An existing Genie Space (`customer genie`) over `demo.demo` tables

# COMMAND ----------

# MAGIC %pip install databricks-sdk==0.120.0 databricks-langchain==0.20.0 langchain==1.3.13 langchain-openai==1.3.5 mlflow==3.14.0
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ../_config/config_unity_catalog

# COMMAND ----------

# MAGIC %run ../_config/config_multiagent

# COMMAND ----------

# DBTITLE 1,Configuration
CATALOG = catalog
SCHEMA = schema

# ID of your existing Genie Space (Genie UI > your space > URL: /genie/rooms/<this-id>)
GENIE_SPACE_ID = "01f129b87e20108fad4b9f084cfb50ac"

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
print("Workspace:", w.config.host)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Action tool: a Unity Catalog function
# MAGIC `issue_refund` is the *sensitive action* of this demo: the supervisor may only
# MAGIC call it **after explicit human approval**. Here it returns a confirmation ID;
# MAGIC in production it would write to a Delta table or call a payment API.

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.issue_refund(
    order_id INT COMMENT 'The order to refund',
    amount DOUBLE COMMENT 'Refund amount in USD',
    reason STRING COMMENT 'Business justification for the refund'
)
RETURNS STRING
LANGUAGE PYTHON
COMMENT 'Issues a customer refund and returns the confirmation ID. SENSITIVE ACTION: only call after explicit human approval.'
AS $$
    import hashlib
    h = hashlib.sha1(f"{{order_id}}-{{amount}}-{{reason}}".encode()).hexdigest()[:8].upper()
    return f"REFUND-{{h}} registered: order {{order_id}}, amount ${{amount:.2f}} ({{reason}})"
$$
""")
print(f"UC function {CATALOG}.{SCHEMA}.issue_refund created")

# Sanity check
display(spark.sql(f"SELECT {CATALOG}.{SCHEMA}.issue_refund(1001, 399.99, 'defective monitor')"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Create the Supervisor Agent (SDK)
# MAGIC One supervisor, three tools. Descriptions drive delegation; instructions
# MAGIC enforce the human-in-the-loop policy.

# COMMAND ----------

# DBTITLE 1,Create the supervisor
from databricks.sdk.service.supervisoragents import (
    SupervisorAgent,
    Tool,
    GenieSpace,
    UcFunction
)

sup = w.supervisor_agents.create_supervisor_agent(
    supervisor_agent=SupervisorAgent(
        display_name="customer supervisor",
        description=(
            "Answers customer questions by combining order data (Genie), "
            "TechStore policies (Knowledge Assistant), and can issue refunds "
            "after human approval."
        ),
        instructions=(
            "You coordinate customer operations. "
            "Use the genie space for any question about customers, orders, "
            "order items, products or shipping zones. "
            "HUMAN-IN-THE-LOOP POLICY: issue_refund is a sensitive action. "
            "Never call it directly. First present the exact order id, amount "
            "and reason, then ask for explicit approval. Only call issue_refund "
            "after the user replies with an explicit approval such as "
            "'I approve'. Never disclose customer registration dates."
        ),
    )
)
print("Supervisor created:", sup.name)
print("Endpoint:", sup.endpoint_name)
print("MLflow experiment:", sup.experiment_id)

# COMMAND ----------

# DBTITLE 1,Attach the three sub-agents / tools
tools = [
    (
        "customer_genie",
        Tool(
            tool_type="genie_space",
            genie_space=GenieSpace(id=GENIE_SPACE_ID),
            description=(
                "Answers analytical questions about customers, orders, order "
                "items, products and shipping zones by generating SQL on the "
                "demo.demo tables."
            ),
        ),
    ),
    (
        "issue_refund",
        Tool(
            tool_type="uc_function",
            uc_function=UcFunction(name=f"{CATALOG}.{SCHEMA}.issue_refund"),
            description=(
                "Issues a customer refund and returns a confirmation ID. "
                "SENSITIVE: only invoke after the user gave explicit approval "
                "of the exact amount."
            ),
        ),
    ),
]


for tool_id, tool in tools:
    created = w.supervisor_agents.create_tool(parent=sup.name, tool=tool, tool_id=tool_id)
    print("Tool attached:", created.name)

# COMMAND ----------

# DBTITLE 1,Wait for the supervisor endpoint to be ready
import time

while True:
    ep = w.serving_endpoints.get(sup.endpoint_name)
    state = ep.state.ready.value if ep.state and ep.state.ready else "UNKNOWN"
    print("Endpoint state:", state)
    if state == "READY":
        break
    time.sleep(30)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — MLflow autolog (LangChain)
# MAGIC `mlflow.langchain.autolog()` traces every LangChain invocation: inputs,
# MAGIC outputs, latency, and the full delegation visible in the **Traces** tab of
# MAGIC the notebook experiment. The supervisor also logs its own traces in its
# MAGIC Agent Bricks experiment (`sup.experiment_id`).

# COMMAND ----------

import mlflow

mlflow.langchain.autolog()

# Optional: send traces to a dedicated experiment instead of the notebook's
# mlflow.set_experiment("/Shared/agent-bricks-code-demo")

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# Agent Bricks endpoints implement the Responses API ('input' field, not
# 'messages'), so we use ChatOpenAI with use_responses_api=True, pointed at
# the workspace serving endpoints.
ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
DATABRICKS_HOST = ctx.apiUrl().get()
DATABRICKS_TOKEN = ctx.apiToken().get()

llm = ChatOpenAI(
    model=sup.endpoint_name,
    base_url=f"{DATABRICKS_HOST}/serving-endpoints",
    api_key=DATABRICKS_TOKEN,
    use_responses_api=True,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Test 1: cross-source question (Genie + Knowledge Assistant)

# COMMAND ----------

def ask(messages):
    """Query the supervisor endpoint through LangChain and return the reply text."""
    resp = llm.invoke(messages)
    # In Responses API mode, content may be a list of content blocks
    if isinstance(resp.content, str):
        return resp.content
    return "".join(
        b.get("text", "") for b in resp.content if isinstance(b, dict)
    )

history = [
    HumanMessage(
        "John Smith wants a refund for his last order. Can you help me ?"
    )
]

answer = ask(history)
history.append(AIMessage(answer))
print(answer)

# COMMAND ----------

# MAGIC %md
# MAGIC The supervisor delegates: **Genie** confirms the order and delivery from
# MAGIC `demo.demo`, the **techstore document** cites the 30-day return window and the
# MAGIC original-packaging conditions from `return_policy.pdf`. Open the **Traces**
# MAGIC tab to see the full delegation tree.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Test 2: human-in-the-loop refund
# MAGIC **Turn 1** - we ask for a refund. Per its instructions the supervisor must
# MAGIC *propose*, not *execute*.

# COMMAND ----------

history.append(
    HumanMessage("The monitor is defective (dead pixels). Please refund this order.")
)

proposal = ask(history)
history.append(AIMessage(proposal))
print(proposal)

# COMMAND ----------

# MAGIC %md
# MAGIC ☝️ **The human checkpoint is now.** Read the proposal above: order ID,
# MAGIC amount, reason. Nothing has been executed - `issue_refund` was not called
# MAGIC (check the trace). Run the next cell **only if you approve**.

# COMMAND ----------

# DBTITLE 1,Turn 2 - explicit human approval
history.append(HumanMessage("I approve, issue the refund."))

confirmation = ask(history)
history.append(AIMessage(confirmation))
print(confirmation)

# COMMAND ----------

# MAGIC %md
# MAGIC The trace of this call now shows the `issue_refund` UC function execution
# MAGIC and the confirmation ID. Two layers of control: the instructions force a
# MAGIC proposal first, and the action only runs in a turn where a human explicitly
# MAGIC approved.
# MAGIC
# MAGIC > **Note - platform-native HITL:** with the Supervisor API in background
# MAGIC > mode, MCP tool calls *require* an `mcp_approval_request` /
# MAGIC > `mcp_approval_response` exchange enforced by Databricks itself.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8 — Review the traces in MLflow

# COMMAND ----------

print("Notebook traces:   MLflow UI > this notebook's experiment > Traces tab")
print(f"Supervisor traces: experiment_id = {sup.experiment_id}")
print(f"Agents UI:         {w.config.host}/agents")

# Programmatic access to the traces:
traces = mlflow.search_traces(max_results=5)
display(traces)

# COMMAND ----------

# MAGIC %md
# MAGIC ## (Optional) Cleanup

# COMMAND ----------

CLEANUP = True  # set to True to delete everything created by this notebook

if CLEANUP:
    # 1. Supervisor Agent (tools are deleted with it, endpoint is removed)
    w.supervisor_agents.delete_supervisor_agent(name=sup.name)
    print("Deleted supervisor:", sup.name)

    # 2. UC function
    spark.sql(f"DROP FUNCTION IF EXISTS {CATALOG}.{SCHEMA}.issue_refund")
    print(f"Dropped function {CATALOG}.{SCHEMA}.issue_refund")

    print("Cleanup complete.")
else:
    print("CLEANUP is False - nothing deleted.")
