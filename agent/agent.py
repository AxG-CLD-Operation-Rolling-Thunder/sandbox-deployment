"""
Google Cloud Brand Voice Agent - AI-powered writing assistant for Google Cloud content creators
"""
import requests
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from .tools.oauth_support import retrieve_user_auth
from .tools import (
    review_content_for_brand_voice,
    generate_blog_content,
    generate_content_outline,
    generate_headlines,
    optimize_existing_headline,
    get_quick_brand_voice_tips,
    get_headline_best_practices,
    retrieve_brand_voice_guidelines,
    check_brand_voice_compliance,
    get_google_cloud_terminology
)
from .prompts.brand_voice_instructions import BRAND_VOICE_AGENT_INSTRUCTION


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
    return {
        "name": "Google Cloud Brand Voice Agent",
        "version": "1.0.0",
        "capabilities": [
            "Content review and brand voice analysis",
            "Blog content generation from topics and key points",
            "Headline generation and optimization",
            "Brand voice compliance checking",
            "Google Cloud terminology guidance"
        ],
        "description": "AI-powered writing assistant for Google Cloud marketers and content creators"
    }


root_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="brand_voice_agent",
    description="Google Cloud Brand Voice Agent - An AI-powered writing assistant for Google Cloud marketers and content creators that helps brainstorm, draft, and refine blog content while ensuring alignment with Google Cloud brand voice guidelines.",
    instruction=BRAND_VOICE_AGENT_INSTRUCTION,
    tools=[
        # Core functionality tools
        review_content_for_brand_voice,
        generate_blog_content,
        generate_content_outline,
        generate_headlines,
        optimize_existing_headline,

        # Helper and reference tools
        get_quick_brand_voice_tips,
        get_headline_best_practices,
        retrieve_brand_voice_guidelines,
        check_brand_voice_compliance,
        get_google_cloud_terminology,

        # User management tools
        get_users_name,
        self_report
    ],
)
