"""
Plan RAG Search Tool - Search corpus of example Plan on a Page documents for patterns and guidance
"""
import os
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Check if RAG/Vertex Search is configured
VERTEX_SEARCH_ENGINE_ID = os.getenv("VERTEX_SEARCH_ENGINE_ID")
RAG_CORPUS = os.getenv("RAG_CORPUS")

# Determine if RAG is available
RAG_AVAILABLE = bool(VERTEX_SEARCH_ENGINE_ID and RAG_CORPUS)

if RAG_AVAILABLE:
    logger.info(f"Plan RAG search configured with corpus: {RAG_CORPUS}")
else:
    logger.info("Plan RAG search not configured - VERTEX_SEARCH_ENGINE_ID or RAG_CORPUS not set")


def search_example_plans(
    query: str,
    campaign_type: Optional[str] = None,
    geography: Optional[str] = None,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Search the corpus of example Plan on a Page documents for similar plans.

    This function searches a curated corpus of high-quality example plans to find
    relevant patterns, structures, and approaches that users can learn from.

    Args:
        query: Natural language search query (e.g., "product launch plans with social media")
        campaign_type: Optional filter by campaign type ("product_launch", "brand_campaign", "event")
        geography: Optional filter by geography ("global", "emea", "apac", "americas")
        top_k: Number of examples to return (default: 5)

    Returns:
        Dict containing example plans and extracted patterns
    """
    if not RAG_AVAILABLE:
        return {
            "rag_available": False,
            "message": "RAG corpus not configured. Using embedded knowledge only.",
            "examples": [],
            "fallback": "embedded_knowledge"
        }

    try:
        # Build enhanced query with filters
        enhanced_query = query
        if campaign_type:
            enhanced_query += f" campaign_type:{campaign_type}"
        if geography:
            enhanced_query += f" geography:{geography}"

        # Note: Actual Vertex AI Search implementation would go here
        # For now, return structure that shows what RAG would provide

        # This is a placeholder structure - in production, this would call Vertex AI Search API
        logger.info(f"RAG search query: {enhanced_query}")

        return {
            "rag_available": True,
            "query": query,
            "filters": {
                "campaign_type": campaign_type,
                "geography": geography
            },
            "examples_found": 0,  # Would be populated by actual search
            "examples": [],  # Would contain retrieved example plans
            "patterns_extracted": [],  # Common patterns from examples
            "source": "rag_corpus",
            "message": "RAG search configured. In production, this would return example plans from Vertex AI Search corpus."
        }

    except Exception as e:
        logger.error(f"RAG search failed: {str(e)}")
        return {
            "rag_available": False,
            "error": str(e),
            "fallback": "embedded_knowledge",
            "examples": []
        }


def find_grl_patterns(
    activation_component: str,
    campaign_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find G/R/L (Global/Regional/Local) patterns from example plans for a specific activation component.

    Searches the corpus for how similar campaigns handled G/R/L assignments for the same
    activation component, showing real Adopt/Adapt/Invent decisions.

    Args:
        activation_component: The component to find patterns for (e.g., "Social Media", "Events")
        campaign_type: Optional campaign type filter

    Returns:
        Dict containing G/R/L patterns and real examples
    """
    if not RAG_AVAILABLE:
        return {
            "rag_available": False,
            "message": "RAG not configured. Using embedded G/R/L guidance.",
            "patterns": [],
            "fallback": "embedded_knowledge"
        }

    try:
        search_query = f"G/R/L assignments for {activation_component}"
        if campaign_type:
            search_query += f" in {campaign_type} campaigns"

        logger.info(f"Searching G/R/L patterns: {search_query}")

        # Placeholder structure for G/R/L patterns from corpus
        return {
            "rag_available": True,
            "activation_component": activation_component,
            "campaign_type": campaign_type,
            "patterns_found": 0,  # Would be populated by search
            "common_patterns": [],  # Would show frequent G/R/L approaches
            "example_assignments": [],  # Real examples from corpus
            "adopt_adapt_invent_stats": {},  # Statistics on A/A/I usage
            "source": "rag_corpus",
            "message": "RAG configured. Would return real G/R/L patterns from example plans."
        }

    except Exception as e:
        logger.error(f"G/R/L pattern search failed: {str(e)}")
        return {
            "rag_available": False,
            "error": str(e),
            "fallback": "embedded_knowledge"
        }


def get_similar_plans_by_type(
    campaign_type: str,
    additional_filters: Optional[Dict[str, str]] = None,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Retrieve example plans of a specific campaign type.

    Useful for showing users complete examples of similar campaigns to inspire
    their own planning.

    Args:
        campaign_type: Type of campaign ("product_launch", "brand_campaign", "event", etc.)
        additional_filters: Optional dict of additional filters (geography, industry, etc.)
        top_k: Number of examples to return

    Returns:
        Dict containing complete example plans
    """
    if not RAG_AVAILABLE:
        return {
            "rag_available": False,
            "message": "RAG not configured. Cannot retrieve example plans.",
            "examples": [],
            "fallback": "Use get_template() for blank template"
        }

    try:
        search_query = f"campaign_type:{campaign_type}"

        if additional_filters:
            for key, value in additional_filters.items():
                search_query += f" {key}:{value}"

        logger.info(f"Searching example plans: {search_query}")

        # Placeholder structure
        return {
            "rag_available": True,
            "campaign_type": campaign_type,
            "filters": additional_filters,
            "examples_found": 0,
            "examples": [],  # Would contain full example plans
            "common_sections": {},  # Analysis of how examples structured sections
            "source": "rag_corpus",
            "message": "RAG configured. Would return complete example plans for reference."
        }

    except Exception as e:
        logger.error(f"Example plan retrieval failed: {str(e)}")
        return {
            "rag_available": False,
            "error": str(e),
            "fallback": "embedded_knowledge"
        }


def get_corpus_insights(section_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistical insights from the corpus of example plans.

    Provides aggregate data about common patterns, frequently used activation components,
    typical KPIs, etc. from the example plan corpus.

    Args:
        section_name: Optional section to get insights for (e.g., "grl", "activation_components", "kpis")

    Returns:
        Dict containing corpus insights and statistics
    """
    if not RAG_AVAILABLE:
        return {
            "rag_available": False,
            "message": "RAG not configured. No corpus insights available.",
            "insights": {}
        }

    try:
        logger.info(f"Retrieving corpus insights for: {section_name or 'all sections'}")

        # Placeholder for corpus statistics
        return {
            "rag_available": True,
            "section": section_name,
            "corpus_size": 0,  # Number of example plans in corpus
            "insights": {},  # Statistical insights
            "common_patterns": [],  # Most frequent patterns
            "source": "rag_corpus",
            "message": "RAG configured. Would provide statistical insights from corpus."
        }

    except Exception as e:
        logger.error(f"Corpus insights retrieval failed: {str(e)}")
        return {
            "rag_available": False,
            "error": str(e)
        }


# Conditionally export tools based on RAG availability
# The agent will check if these are None and only add them if available

if RAG_AVAILABLE:
    # RAG is configured - export all search functions
    plan_example_search = search_example_plans
    plan_grl_pattern_search = find_grl_patterns
    plan_similar_by_type = get_similar_plans_by_type
    plan_corpus_insights = get_corpus_insights

    logger.info("Plan RAG search tools exported and available")
else:
    # RAG not configured - set to None so agent knows to skip
    plan_example_search = None
    plan_grl_pattern_search = None
    plan_similar_by_type = None
    plan_corpus_insights = None

    logger.info("Plan RAG search tools not available - RAG not configured")
