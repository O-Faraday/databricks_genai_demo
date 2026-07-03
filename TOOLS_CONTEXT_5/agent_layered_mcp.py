"""
agent_layered_mcp.py
Layered MCP agent: Discovery -> Planning -> Execution
Uses the GitHub MCP server connected through Databricks AI Gateway.

All MCP calls use DatabricksMCPClient (synchronous, from databricks-mcp),
consistent with the notebook cells 2 and 6.

Usage (from a script):
    python agent_layered_mcp.py

Usage (from a notebook cell after nest_asyncio.apply()):
    from agent_layered_mcp import LAYERED_AGENT
    result = await LAYERED_AGENT.ainvoke({...})
"""

import json
import os
import tiktoken
from typing import Annotated, Sequence, TypedDict

import mlflow
import nest_asyncio
from dotenv import load_dotenv
from pydantic import create_model
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient
from databricks_langchain import ChatDatabricks
from langchain_core.messages import (
    AnyMessage, AIMessage, HumanMessage, SystemMessage, ToolMessage,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

# Allow await in notebooks and scripts that already have a running event loop
nest_asyncio.apply()

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

GITHUB_CONNECTION = os.getenv("GITHUB_CONNECTION", "github_mcp")

w              = WorkspaceClient()
llm            = ChatDatabricks(endpoint="databricks-meta-llama-3-3-70b-instruct")
enc            = tiktoken.get_encoding("cl100k_base")
GITHUB_MCP_URL = f"{w.config.host}/api/2.0/mcp/external/{GITHUB_CONNECTION}"

# Single shared client — DatabricksMCPClient is stateless between calls
github_client = DatabricksMCPClient(
    server_url=GITHUB_MCP_URL,
    workspace_client=w,
)

# ── Discovery manifest ────────────────────────────────────────────────────────
# Built once at import time from the real tool list.
# Avoids a network call on every agent invocation.

_raw_tools = github_client.list_tools()

DISCOVERY_MANIFEST = [
    {"name": t.name, "summary": (t.description or "")[:120]}
    for t in _raw_tools
]
MANIFEST_VALID_NAMES = {t["name"] for t in DISCOVERY_MANIFEST}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mcp_to_lc_tool(mcp_t) -> StructuredTool:
    """
    Wrap a DatabricksMCPClient Tool as a LangChain StructuredTool.
    The func is a placeholder — execution uses github_client.call_tool() directly.
    """
    props    = mcp_t.inputSchema.get("properties", {})
    required = set(mcp_t.inputSchema.get("required", []))
    fields   = {
        name: (str, ... if name in required else None)
        for name in props
    }
    InputModel = (
        create_model(f"{mcp_t.name}_input", **fields)
        if fields
        else create_model(f"{mcp_t.name}_input")
    )
    return StructuredTool(
        name=mcp_t.name,
        description=mcp_t.description or "",
        args_schema=InputModel,
        func=lambda **kw: None,  # real call in execute_node
    )


# ── Agent state ───────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages:          Annotated[Sequence[AnyMessage], add_messages]
    shortlisted_tools: list[str]
    token_log:         dict[str, int]


# ── Graph nodes ───────────────────────────────────────────────────────────────

def discover_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Stage 1 — Discovery.
    Only names + one-line summaries enter the context window.
    The model returns a shortlist of 1-3 tool names.
    """
    tool_index   = "\n".join(
        f"  {i+1:2}. {t['name']:<45} {t['summary']}"
        for i, t in enumerate(DISCOVERY_MANIFEST)
    )
    manifest_str = json.dumps(DISCOVERY_MANIFEST)
    token_count  = len(enc.encode(manifest_str))

    system = SystemMessage(content=(
        "You are a tool router for the GitHub MCP server.\n"
        "Respond with ONLY a raw JSON array of tool names (no markdown, no explanation).\n"
        "Select 1 to 3 tools. Use EXACT names from the numbered list below.\n"
        "\n"
        "Routing hints:\n"
        "  - listing issues              -> list_issues\n"
        "  - counting or listing commits -> list_commits\n"
        "  - adding a PR review          -> pull_request_review_write\n"
        "  - searching repositories      -> search_repositories\n"
        "  - reading a specific PR       -> pull_request_read\n"
        "  - reading a specific issue    -> issue_read\n"
        "\n"
        f"Available tools:\n{tool_index}\n"
        "\n"
        'Example output: ["list_issues"] or ["search_repositories", "list_commits"]'
    ))

    response = llm.invoke([system, state["messages"][-1]])
    raw = response.content.strip().strip("```json").strip("```").strip()
    try:
        shortlisted = [n for n in json.loads(raw) if n in MANIFEST_VALID_NAMES]
    except Exception:
        shortlisted = []

    return {
        "messages":          [response],
        "shortlisted_tools": shortlisted,
        "token_log":         {"discovery": token_count},
    }


def plan_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Stage 2 — Planning.
    Full schemas loaded ONLY for the shortlisted tools.
    The model generates a structured tool call.
    """
    shortlisted = state.get("shortlisted_tools", [])
    if not shortlisted:
        return {"token_log": {**state.get("token_log", {}), "planning": 0}}

    raw_tools  = github_client.list_tools()
    selected   = [t for t in raw_tools if t.name in shortlisted]
    schema_str = json.dumps([
        {"name": t.name, "description": t.description, "inputSchema": t.inputSchema}
        for t in selected
    ])
    tokens   = len(enc.encode(schema_str))
    lc_tools = [_mcp_to_lc_tool(t) for t in selected]

    system = SystemMessage(content=(
        "You are a planning agent. Using the detailed tool schemas below, "
        "call the appropriate GitHub MCP tool to answer the user request.\n\n"
        f"Tool schemas:\n{schema_str}"
    ))
    user_msg = [m for m in state["messages"] if isinstance(m, HumanMessage)][-1]
    response = llm.bind_tools(lc_tools).invoke([system, user_msg])

    return {
        "messages":  [response],
        "token_log": {**state.get("token_log", {}), "planning": tokens},
    }


def execute_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Stage 3 — Execution.
    Calls github_client.call_tool() directly.
    Planning schemas are NOT forwarded — only the raw result enters context.
    """
    last = state["messages"][-1]
    if not (isinstance(last, AIMessage) and last.tool_calls):
        return {}

    results = []
    for tc in last.tool_calls:
        mcp_result = github_client.call_tool(tool_name=tc["name"], arguments=tc["args"])
        content    = (
            mcp_result.content[0].text
            if mcp_result.content
            else f"No result from {tc['name']}"
        )
        results.append(ToolMessage(content=content, tool_call_id=tc["id"]))

    return {"messages": results}


def should_execute(state: AgentState) -> str:
    last = state["messages"][-1]
    return "execute" if (isinstance(last, AIMessage) and last.tool_calls) else "end"


# ── Build the graph ───────────────────────────────────────────────────────────

def build_layered_agent():
    workflow = StateGraph(AgentState)
    workflow.add_node("discover", discover_node)
    workflow.add_node("plan",     plan_node)
    workflow.add_node("execute",  execute_node)
    workflow.set_entry_point("discover")
    workflow.add_edge("discover", "plan")
    workflow.add_conditional_edges(
        "plan", should_execute, {"execute": "execute", "end": END}
    )
    workflow.add_edge("execute", END)
    return workflow.compile()


mlflow.langchain.autolog()
LAYERED_AGENT = build_layered_agent()


# ── Standalone entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio

    tasks = [
        "List the 5 most recent open issues in the databricks/databricks-sdk-py repo",
        "Search for repos about context engineering with more than 500 stars",
    ]

    async def run():
        for task in tasks:
            print(f"\nTask: {task}")
            result = await LAYERED_AGENT.ainvoke({
                "messages":          [{"role": "user", "content": task}],
                "shortlisted_tools": [],
                "token_log":         {},
            })
            token_log   = result.get("token_log", {})
            shortlisted = result.get("shortlisted_tools", [])
            total       = sum(token_log.values())
            print(f"  Shortlisted : {shortlisted}")
            print(f"  Token log   : {token_log}  |  total ~{total:,} tokens")
            final = result["messages"][-1]
            if hasattr(final, "content") and final.content:
                print(f"  Answer      : {str(final.content)[:300]}")

    asyncio.run(run())
