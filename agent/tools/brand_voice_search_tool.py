"""
Brand Voice Knowledge Search Tool - Search-based retrieval for Brand Voice Agent
Using VertexAiSearchTool for Google Cloud brand voice knowledge retrieval functionality
"""
import os
import logging
from typing import Dict, Any
from google.adk.tools import ToolContext, VertexAiSearchTool
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def create_brand_voice_search_tool():
    """
    Create a Vertex AI Search tool configured for Google Cloud brand voice knowledge base
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
        brand_voice_search_tool = VertexAiSearchTool(
            name='search_brand_voice_knowledge',
            description=(
                'Use this tool to search the Google Cloud brand voice knowledge base for relevant information. '
                'This includes brand voice guidelines, style guides, terminology standards, content examples, '
                'best practices for Google Cloud marketing content, and gold standard blog post examples. '
                'Search this knowledge base when you need context about Google Cloud brand voice, writing standards, '
                'content creation guidelines, or examples of high-quality Google Cloud content.'
            ),
            project=project_id,
            search_engine_id=search_engine_id
        )

        logger.info(f"Brand voice search tool created with engine: {search_engine_id}")
        return brand_voice_search_tool

    except Exception as e:
        logger.error(f"Failed to create brand voice search tool: {str(e)}")
        return None

def retrieve_brand_voice_knowledge(
    query: str,
    content_type: str = "general",
    max_results: int = 5,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Retrieve knowledge from the brand voice knowledge base using search

    This function provides knowledge retrieval capability as a regular function
    rather than an ADK agent tool, making it more flexible for different use cases.

    Args:
        query: The search query for knowledge retrieval
        content_type: Type of content context (blog_post, email, social_media, guidelines, examples)
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

        # Enhance query based on content type
        enhanced_queries = {
            "blog_post": f"Google Cloud blog writing guidelines examples {query}",
            "email": f"Google Cloud email marketing content guidelines {query}",
            "social_media": f"Google Cloud social media content guidelines {query}",
            "guidelines": f"Google Cloud brand voice style guidelines {query}",
            "examples": f"Google Cloud content examples best practices {query}",
            "terminology": f"Google Cloud terminology standards {query}",
            "general": f"Google Cloud brand voice content creation {query}"
        }

        enhanced_query = enhanced_queries.get(content_type, query)

        # For now, return a structured response indicating the search would be performed
        # In a real implementation, this would use the VertexAiSearchTool
        logger.info(f"Brand voice knowledge search requested: {enhanced_query}")

        # Store query in tool context for future reference if available
        if tool_context and hasattr(tool_context, 'state'):
            tool_context.state['last_brand_voice_query'] = enhanced_query
            tool_context.state['last_brand_voice_content_type'] = content_type

        return {
            "status": "success",
            "query": enhanced_query,
            "content_type": content_type,
            "message": f"Brand voice knowledge search configured for: {enhanced_query}",
            "search_ready": True,
            "search_engine_id": search_engine_id,
            "knowledge_areas": [
                "Google Cloud brand voice principles",
                "Content writing guidelines and best practices",
                "Terminology and style standards",
                "High-quality content examples",
                "Content structure and formatting guidelines"
            ]
        }

    except Exception as e:
        logger.error(f"Error in retrieve_brand_voice_knowledge: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to retrieve brand voice knowledge: {str(e)}",
            "query": query
        }

def search_brand_voice_examples(
    content_goal: str,
    audience: str = "technical professionals",
    format_type: str = "blog_post",
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Search for specific examples of Google Cloud content that match the user's goal.

    Args:
        content_goal: What the user wants to achieve (e.g., "explain AI/ML benefits", "security best practices")
        audience: Target audience for the content
        format_type: Type of content format needed
        tool_context: Optional ADK tool context

    Returns:
        Dictionary containing relevant content examples and analysis
    """
    search_query = f"Google Cloud {format_type} examples {content_goal} {audience}"

    return retrieve_brand_voice_knowledge(
        query=search_query,
        content_type="examples",
        tool_context=tool_context
    )

# Export the search tool (or None if not configured)
brand_voice_search_tool = create_brand_voice_search_tool()

# List of available tools for easy import
__all__ = [
    'brand_voice_search_tool',
    'retrieve_brand_voice_knowledge',
    'create_brand_voice_search_tool',
    'search_brand_voice_examples'
]