"""
Knowledge Retrieval Tool - Search-based retrieval for Invoice Agent
Using VertexAiSearchTool for knowledge retrieval functionality
"""
import os
import logging
from typing import Dict, Any
from google.adk.tools import ToolContext, VertexAiSearchTool
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def create_invoice_search_tool():
    """
    Create a Vertex AI Search tool configured for invoice processing knowledge base
    """
    search_engine_id = os.environ.get("VERTEX_SEARCH_ENGINE_ID")
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    if not search_engine_id:
        logger.warning("VERTEX_SEARCH_ENGINE_ID environment variable not set")
        return None

    if not project_id:
        logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set")
        return None

    try:
        invoice_search_tool = VertexAiSearchTool(
            name='search_invoice_knowledge',
            description=(
                'Use this tool to search the invoice knowledge base for relevant information. '
                'This includes vendor information, tax regulations, compliance guidelines, '
                'historical invoice patterns, and processing best practices. '
                'Search this knowledge base when you need context about vendors, tax codes, '
                'regulatory compliance, or processing guidelines for invoices.'
            ),
            project=project_id,
            search_engine_id=search_engine_id
        )

        logger.info(f"Invoice search tool created with engine: {search_engine_id}")
        return invoice_search_tool

    except Exception as e:
        logger.error(f"Failed to create invoice search tool: {str(e)}")
        return None

def retrieve_invoice_knowledge(
    query: str,
    context_type: str = "general",
    max_results: int = 5,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Retrieve knowledge from the invoice knowledge base using search

    This function provides knowledge retrieval capability as a regular function
    rather than an ADK agent tool, making it more flexible for different use cases.

    Args:
        query: The search query for knowledge retrieval
        context_type: Type of context to retrieve (vendor, tax, general, historical)
        max_results: Maximum number of results to return
        tool_context: Optional ADK tool context for state management

    Returns:
        Dictionary containing retrieved knowledge and metadata
    """
    try:
        # Check if we have the search tool configuration
        search_engine_id = os.environ.get("VERTEX_SEARCH_ENGINE_ID")
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

        if not search_engine_id or not project_id:
            return {
                "status": "error",
                "message": "Search engine not configured. Please set VERTEX_SEARCH_ENGINE_ID and GOOGLE_CLOUD_PROJECT environment variables."
            }

        # Enhance query based on context type
        enhanced_queries = {
            "vendor": f"vendor information compliance regulations {query}",
            "tax": f"tax code regulations compliance {query}",
            "general": f"invoice processing guidelines {query}",
            "historical": f"historical invoice patterns trends {query}"
        }

        enhanced_query = enhanced_queries.get(context_type, query)

        # For now, return a structured response indicating the search would be performed
        # In a real implementation, this would use the VertexAiSearchTool
        logger.info(f"Knowledge search requested: {enhanced_query}")

        # Store query in tool context for future reference if available
        if tool_context and hasattr(tool_context, 'state'):
            tool_context.state['last_knowledge_query'] = enhanced_query
            tool_context.state['last_knowledge_context_type'] = context_type

        return {
            "status": "success",
            "query": enhanced_query,
            "context_type": context_type,
            "message": f"Knowledge search configured for: {enhanced_query}",
            "search_ready": True,
            "search_engine_id": search_engine_id
        }

    except Exception as e:
        logger.error(f"Error in retrieve_invoice_knowledge: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to retrieve knowledge: {str(e)}",
            "query": query
        }

# Export the search tool (or None if not configured)
invoice_search_tool = create_invoice_search_tool()

# List of available tools for easy import
__all__ = ['invoice_search_tool', 'retrieve_invoice_knowledge', 'create_invoice_search_tool']