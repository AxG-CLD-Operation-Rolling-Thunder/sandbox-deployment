"""
Plan on a Page Agent - Collaborative assistant for marketers creating campaign planning documents
"""
import requests
import logging
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from .tools.oauth_support import retrieve_user_auth
from .tools import (
    # Plan Analysis
    analyze_plan,
    quick_completeness_check,
    get_grl_specific_feedback,

    # Plan Generation
    generate_new_plan,
    get_section_prompts,
    get_plan_template_blank,

    # G/R/L Helper
    guide_grl_assignment,
    suggest_adopt_adapt_invent,
    get_grl_best_practices,

    # Formatting & Validation
    format_plan_output,
    validate_plan_completeness,

    # Duplicate Detection
    search_similar_plans,

    # Template & Knowledge
    get_template,
    get_section_guidance,
    get_grl_framework_guide,

    # File Upload
    list_artifacts,
    get_artifact
)

# Conditionally import RAG search tools (will be None if not configured)
try:
    from .tools import (
        plan_example_search,
        plan_grl_pattern_search,
        plan_similar_by_type,
        plan_corpus_insights
    )
    RAG_AVAILABLE = plan_example_search is not None
except ImportError:
    plan_example_search = None
    plan_grl_pattern_search = None
    plan_similar_by_type = None
    plan_corpus_insights = None
    RAG_AVAILABLE = False

from .prompts.plan_on_page_instructions import PLAN_ON_PAGE_AGENT_INSTRUCTION

logger = logging.getLogger(__name__)


def get_users_name(tool_context: ToolContext) -> dict:
    """Get the authenticated user's name and email."""
    auth = retrieve_user_auth(tool_context).token

    resp = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {auth}"},
    ).json()

    email = resp.get("email")
    name = resp.get("name")

    return {"email": email, "name": name}


def self_report():
    """Report the agent version and capabilities."""
    capabilities = [
        "Analyze existing Plan on a Page documents and identify gaps",
        "Guide users through creating new plans from scratch",
        "Provide specialized G/R/L (Global/Regional/Local) assignment help",
        "Apply Adopt/Adapt/Invent framework for cross-geography alignment",
        "Detect duplicate initiatives to prevent redundant work",
        "Validate plan completeness before submission",
        "Format plans according to standard template"
    ]

    if RAG_AVAILABLE:
        capabilities.extend([
            "Search corpus of example Plan on a Page documents for patterns and best practices",
            "Show real G/R/L assignments from similar campaigns",
            "Compare plans against successful examples from knowledge base"
        ])

    return {
        "name": "Plan on a Page Agent",
        "version": "1.0.0",
        "capabilities": capabilities,
        "rag_enabled": RAG_AVAILABLE,
        "description": "A collaborative assistant for marketers who need to develop or refine their Plan on a Page submissions for campaigns, launches, or major initiatives"
    }


# Prepare tools list
agent_tools = [
    # Core plan analysis and generation tools
    analyze_plan,
    generate_new_plan,
    validate_plan_completeness,

    # G/R/L specialized tools (critical for cross-geography alignment)
    guide_grl_assignment,
    suggest_adopt_adapt_invent,
    get_grl_best_practices,

    # Supporting tools
    get_section_prompts,
    get_plan_template_blank,
    format_plan_output,
    quick_completeness_check,
    get_grl_specific_feedback,

    # Duplicate detection
    search_similar_plans,

    # Template and knowledge access
    get_template,
    get_section_guidance,
    get_grl_framework_guide,

    # File upload support
    list_artifacts,
    get_artifact,

    # User management tools
    get_users_name,
    self_report
]

# Conditionally add RAG search tools if available
if RAG_AVAILABLE:
    agent_tools.extend([
        plan_example_search,
        plan_grl_pattern_search,
        plan_similar_by_type,
        plan_corpus_insights
    ])
    logger.info("RAG search tools available and loaded")
else:
    logger.info("RAG search tools not available (VERTEX_SEARCH_ENGINE_ID or RAG_CORPUS not configured)")

logger.info(f"Plan on a Page Agent initialized with {len(agent_tools)} tools")

root_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="plan_on_page_agent",
    description="Plan on a Page Agent - A collaborative assistant designed for marketers who need to develop or refine their Plan on a Page submissions for campaigns, launches, or major initiatives. This agent acts as both a strategic guide and a process facilitator, ensuring that every plan is complete and aligned across global, regional, and local teams.",
    instruction=PLAN_ON_PAGE_AGENT_INSTRUCTION,
    tools=agent_tools,
)
