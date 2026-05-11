# ============================================================================
# AGENT - langchain agent code sample
# ============================================================================

"""Databricks LangGraph ResponsesAgent Implementation"""

import json
from typing import Annotated, Any, Generator, Optional, Sequence, TypedDict, Union
from uuid import uuid4

import mlflow
from databricks_langchain import (
    ChatDatabricks,
    UCFunctionToolkit,
    VectorSearchRetrieverTool,
    DatabricksFunctionClient,
    set_uc_function_client,
)

from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    convert_to_openai_messages,
)
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.tools import BaseTool

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt.tool_node import ToolNode

from mlflow.entities import SpanType
from mlflow.pyfunc import ResponsesAgent
from mlflow.models import ModelConfig
from mlflow.models.resources import DatabricksFunction, DatabricksServingEndpoint
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)

# Enable automatic tracing for LangChain operations
mlflow.langchain.autolog()

# Initialize the Unity Catalog function client
set_uc_function_client(DatabricksFunctionClient())


# ============================================================================
# 1 - Agent State Definition
# ============================================================================

class AgentState(TypedDict):
    """Defines the state structure for the LangGraph agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    custom_inputs: Optional[dict[str, Any]]
    custom_outputs: Optional[dict[str, Any]]


# ============================================================================
# 2 - LangGraph Agent Factory
# ============================================================================

def create_tool_calling_agent(
    model: LanguageModelLike,
    tools: Union[ToolNode, Sequence[BaseTool]],
    system_prompt: Optional[str] = None,
):
    """Creates a tool-calling agent using LangGraph's StateGraph."""
    # Bind tools to the model
    model = model.bind_tools(tools)

    def should_continue(state: AgentState):
        """Determines if the agent should continue to tool execution or end."""
        last = state["messages"][-1]
        return "continue" if isinstance(last, AIMessage) and last.tool_calls else "end"

    # Prepend system prompt if provided
    pre = (
        RunnableLambda(lambda s: [{"role": "system", "content": system_prompt}] + s["messages"])
        if system_prompt
        else RunnableLambda(lambda s: s["messages"])
    )
    model_runnable = pre | model

    def call_model(state: AgentState, config: RunnableConfig):
        """Invokes the language model with the current conversation state."""
        return {"messages": [model_runnable.invoke(state, config)]}

    # Build the state graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("agent", RunnableLambda(call_model))
    graph.add_node("tools", ToolNode(tools))
    
    # Set entry point and edges
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
    graph.add_edge("tools", "agent")

    return graph.compile()


# ============================================================================
# 3 - ResponsesAgent Implementation
# ============================================================================

class LangGraphResponsesAgent(ResponsesAgent):
    """Production-ready agent implementation using MLflow's ResponsesAgent interface."""
    
    def __init__(
        self,
        uc_tool_names: Sequence[str] = ("main_build.dbdemos_ai_agent.*",),
        llm_endpoint_name: str = "databricks-meta-llama-3-70b-instruct",
        system_prompt: Optional[str] = None,
        retriever_config: Optional[dict] = None,
        max_history_messages: int = 20,
    ):
        """Initialize the LangGraph ResponsesAgent."""
        self.llm_endpoint_name = llm_endpoint_name
        self.system_prompt = system_prompt
        self.max_history_messages = max_history_messages

        # Initialize the language model
        self.llm = ChatDatabricks(endpoint=llm_endpoint_name)
        
        # Load Unity Catalog functions as tools
        self.tools = UCFunctionToolkit(function_names=uc_tool_names).tools
        
        # Add Vector Search retriever if configured
        if retriever_config:
            vs_tool = VectorSearchRetrieverTool(
                index_name=retriever_config.get("index_name"),
                num_results=retriever_config.get("num_results", 5),
            )
            self.tools.append(vs_tool)
        
        # Create the agent
        self.agent = create_tool_calling_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
        )

    def _responses_to_cc(self, message: dict[str, Any]) -> list[dict[str, Any]]:
        """Convert ResponsesAgent format to Chat Completion format."""
        msg_type = message.get("type")
        
        if msg_type == "message":
            return [{"role": message["role"], "content": message["content"]}]
        elif msg_type == "function_call":
            return [{
                "role": "assistant",
                "content": "tool_call",
                "tool_calls": [{
                    "id": message["call_id"],
                    "type": "function",
                    "function": {
                        "arguments": message["arguments"],
                        "name": message["name"],
                    },
                }],
            }]
        elif msg_type == "function_call_output":
            return [{
                "role": "tool",
                "content": message["output"],
                "tool_call_id": message["call_id"],
            }]
        
        # Default
        filtered = {k: v for k, v in message.items() if k in {"role", "content", "name", "tool_calls", "tool_call_id"}}
        return [filtered] if filtered else []

    def _langchain_to_responses(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert LangChain message format to ResponsesAgent format."""
        for message in messages:
            message = message.model_dump()
            
            if message["type"] == "ai":
                if tool_calls := message.get("tool_calls"):
                    return [
                        self.create_function_call_item(
                            id=message.get("id") or str(uuid4()),
                            call_id=tc["id"],
                            name=tc["name"],
                            arguments=json.dumps(tc["args"]),
                        )
                        for tc in tool_calls
                    ]
                mlflow.update_current_trace(response_preview=message["content"])
                return [self.create_text_output_item(
                    text=message["content"],
                    id=message.get("id") or str(uuid4())
                )]
            elif message["type"] == "tool":
                return [self.create_function_call_output_item(
                    call_id=message["tool_call_id"],
                    output=message["content"]
                )]
        return []

    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        """Non-streaming prediction endpoint."""
        outputs = [
            event.item for event in self.predict_stream(request)
            if event.type == "response.output_item.done"
        ]
        return ResponsesAgentResponse(output=outputs, custom_outputs=request.custom_inputs)

    def predict_stream(
        self, request: ResponsesAgentRequest,
    ) -> Generator[ResponsesAgentStreamEvent, None, None]:
        """Streaming prediction endpoint."""
        cc_msgs = []
        
        # Update trace
        mlflow.update_current_trace(request_preview=request.input[0].content)
        
        # Convert all input messages
        for msg in request.input:
            cc_msgs.extend(self._responses_to_cc(msg.model_dump()))

        # Limit conversation history
        if len(cc_msgs) > self.max_history_messages:
            cc_msgs = cc_msgs[-self.max_history_messages:]
        
        # Stream agent execution
        for event in self.agent.stream({"messages": cc_msgs}, stream_mode=["updates", "messages"]):
            if event[0] == "updates":
                for node_data in event[1].values():
                    for item in self._langchain_to_responses(node_data["messages"]):
                        yield ResponsesAgentStreamEvent(type="response.output_item.done", item=item)
            
            elif event[0] == "messages":
                try:
                    chunk = event[1][0]
                    if isinstance(chunk, AIMessageChunk) and (content := chunk.content):
                        yield ResponsesAgentStreamEvent(
                            **self.create_text_delta(delta=content, item_id=chunk.id),
                        )
                except Exception:
                    pass
    
    def get_resources(self):
        """Declare all Databricks resources used by this agent."""
        res = [DatabricksServingEndpoint(endpoint_name=self.llm.endpoint)]
        
        for t in self.tools:
            if isinstance(t, VectorSearchRetrieverTool):
                res.extend(t.resources)
            elif hasattr(t, "uc_function_name"):
                res.append(DatabricksFunction(function_name=t.uc_function_name))
        
        return res


# ============================================================================
# 4 - Agent Initialization
# ============================================================================

# Load configuration
model_config = ModelConfig(development_config="agent_config.yaml")

# Instantiate the agent
AGENT = LangGraphResponsesAgent(
    uc_tool_names=model_config.get("uc_tool_names"),
    llm_endpoint_name=model_config.get("llm_endpoint_name"),
    system_prompt=model_config.get("system_prompt"),
    retriever_config=model_config.get("vector_search_infos"),
    max_history_messages=model_config.get("max_history_messages"),
)

# Register with MLflow
mlflow.models.set_model(AGENT)
