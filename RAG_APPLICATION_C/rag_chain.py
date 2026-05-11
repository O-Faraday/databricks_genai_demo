# ============================================================================
# RAG CHAIN - Retrieval Augmented Generation Implementation
# ============================================================================

"""Databricks RAG Chain with Vector Search Integration

This module implements a production-ready RAG (Retrieval Augmented Generation) 
chain using LangChain and Databricks services. The chain retrieves relevant 
documents from a vector store and uses them as context for LLM generation.
"""

import os
import mlflow
from operator import itemgetter
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from databricks_langchain import DatabricksVectorSearch, ChatDatabricks
from datetime import datetime

# Enable automatic tracing for LangChain operations
mlflow.langchain.autolog()


# ============================================================================
# 1 - Configuration Loading
# ============================================================================

# Load configuration from YAML file
model_config = mlflow.models.ModelConfig(development_config='rag_chain_config.yaml')

# Extract configuration sections
databricks_resources = model_config.get("databricks_resources")
llm_config = model_config.get("llm_config")
retriever_config = model_config.get("retriever_config")
vector_search_schema = retriever_config.get("schema")


# ============================================================================
# 2 - Message Processing Utilities
# ============================================================================

def extract_user_query_string(chat_messages_array):
    """Extract the most recent user message from the conversation history.
    
    Args:
        chat_messages_array: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        str: Content of the last user message
    """
    return chat_messages_array[-1]["content"]


def extract_previous_messages(chat_messages_array):
    """Format all previous messages (excluding the last one) into a string.
    
    This creates a conversation history string that can be used as context
    for the retriever or LLM.
    
    Args:
        chat_messages_array: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        str: Formatted string of previous messages in "role: content" format
    """
    messages = "\n"
    for msg in chat_messages_array[:-1]:
        messages += (msg["role"] + ": " + msg["content"] + "\n")
    return messages


def combine_all_messages_for_vector_search(chat_messages_array):
    """Combine conversation history with current query for vector search.
    
    This creates a comprehensive query string that includes both the conversation
    context and the current user question, improving retrieval relevance.
    
    Args:
        chat_messages_array: List of message dictionaries
        
    Returns:
        str: Combined message history and current query
    """
    return extract_previous_messages(chat_messages_array) + extract_user_query_string(chat_messages_array)


# ============================================================================
# 3 - Vector Search Retriever Configuration
# ============================================================================

# Initialize the Databricks Vector Search as a LangChain retriever
vector_search_as_retriever = DatabricksVectorSearch(
    endpoint=databricks_resources.get("vector_search_endpoint_name"),
    index_name=retriever_config.get("vector_search_index"),
    columns=[
        vector_search_schema.get("primary_key"),
        vector_search_schema.get("raw_text"),
        vector_search_schema.get("document_source"),
    ],
).as_retriever(search_kwargs=retriever_config.get("parameters"))


@mlflow.trace(
    name="vector_search_retrieval", 
    span_type="RETRIEVER", 
    attributes={
        "index_name": retriever_config.get("vector_search_index"),
        "endpoint": databricks_resources.get("vector_search_endpoint_name")
    }
)
def retrieve_documents(query: str):
    """Retrieve relevant documents from the vector store with MLflow tracing.
    
    This wrapper function adds MLflow tracing around the retriever to track:
    - Query execution
    - Number of results returned
    - Retrieval latency
    
    Args:
        query: Search query string
        
    Returns:
        list: Retrieved document chunks matching the query
    """
    results = vector_search_as_retriever.invoke(query)
    
    # Access current span to add custom attributes
    current_span = mlflow.get_current_active_span()
    
    # Add number of results as a trace attribute for observability
    if current_span:
        current_span.set_attribute("num_results", len(results))
    
    return results


# Configure retriever schema for MLflow
# Required to:
# 1. Enable the RAG Studio Review App to properly display retrieved chunks
# 2. Enable evaluation suite to measure the retriever's performance
mlflow.models.set_retriever_schema(
    primary_key=vector_search_schema.get("primary_key"),
    text_column=vector_search_schema.get("chunk_text"),
    doc_uri=vector_search_schema.get("document_uri")
)


# ============================================================================
# 4 - Context Formatting
# ============================================================================

def format_context(docs):
    """Format retrieved documents into a single context string for the prompt.
    
    Transforms a list of retrieved document objects into a concatenated string
    that will be inserted into the LLM prompt as context.
    
    Args:
        docs: List of LangChain Document objects from the retriever
        
    Returns:
        str: Formatted context string with all document contents
    """
    chunk_contents = [
        f"Document : {d.page_content}"
        for d in docs
    ]
    return "".join(chunk_contents)


# ============================================================================
# 5 - LLM Configuration
# ============================================================================

# Create the prompt template for generation
prompt = PromptTemplate(
    template=llm_config.get("llm_prompt_template"),
    input_variables=llm_config.get("llm_prompt_template_variables"),
)

# Initialize the Databricks Foundation Model for generation
model = ChatDatabricks(
    endpoint=databricks_resources.get("llm_endpoint_name"),
    extra_params=llm_config.get("llm_parameters"),
)


# ============================================================================
# 6 - RAG Chain Assembly
# ============================================================================

# Construct the complete RAG chain using LangChain Expression Language (LCEL)
chain = (
    {  # Prepare all prompt variables
        "question":  # Extract current user question
            itemgetter("messages") |  # Get the list of messages from input
            RunnableLambda(extract_user_query_string),  # Extract the last user message
        
        "context":  # Retrieve and format relevant context
            itemgetter("messages") | 
            RunnableLambda(combine_all_messages_for_vector_search) |  # Prepare comprehensive query
            retrieve_documents |  # Retrieve relevant documents from vector store
            RunnableLambda(format_context),  # Format documents into prompt-ready text
        
        "chat_history":  # Extract conversation history
            itemgetter("messages") | 
            RunnableLambda(extract_previous_messages)  # Format previous messages
    }
    | prompt  # Insert variables into the prompt template
    | model  # Generate response using the LLM
    | StrOutputParser()  # Parse the output to a string
)

# Register the chain with MLflow for deployment and tracking
mlflow.models.set_model(model=chain)

# COMMAND ----------

# Example usage (uncommented for testing):
# print(chain.invoke(model_config.get("input_example")))
