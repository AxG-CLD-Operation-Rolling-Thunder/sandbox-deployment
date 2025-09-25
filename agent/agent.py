# from google.adk.agents import LlmAgent
from google.adk.agents import LlmAgent
from .tools.oauth_support import retrieve_user_auth
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from difflib import get_close_matches
import requests
# from google.genai import client as genai_client # to run locally


# def get_users_name(tool_context: ToolContext) -> dict:
#     auth = retrieve_user_auth(tool_context).token

#     resp = requests.get(
#         "https://openidconnect.googleapis.com/v1/userinfo",
#         headers={"Authorization": f"Bearer {auth}"},
#     ).json()

#     print(resp)
#     email = resp.get("email")
#     name = resp.get("name")

#     return {"email": email, "name": name}


# def self_report():
#     return "You are version 0.0.1"

# root_agent = LlmAgent(
#     model="gemini-2.0-flash-001",
#     name="example_agent",
#     description="An example agent to serve as a basis for your agent.",
#     instruction="Call self_report and get_users_name tool when requested to do so by user.",
#     tools=[self_report, get_users_name],
# )


# def summarize_plan(input_text):
#     return "Summary: " + input_text

# root_agent = LlmAgent(
#     model="gemini-2.0-flash-001",
#     name="PlanOnAPage", 
#     description="Summarizes complex plans into a single page",
#     instruction="tbd",
#     run=summarize_plan
# )





EXISTING_AGENT_NAMES = [
    "marketing_segmentation_agent",
    "sales_forecast_agent",
    "customer_insight_agent",
    "product_recommendation_agent",
    "lead_generation_agent",
    "social_media_analysis_agent",
    "email_campaign_agent",
    "customer_retention_agent",
    "market_research_agent",
    "brand_monitoring_agent",
    "competitive_analysis_agent",
    "pricing_strategy_agent",
    "advertising_optimization_agent",
    "customer_feedback_agent",
    "sales_performance_agent",
    "content_marketing_agent",
    "influencer_marketing_agent",
    "digital_analytics_agent",
    "conversion_rate_agent",
    "customer_support_agent"
]

def similar_agent_names(agent_name: str) -> dict:
    """Find agent names similar to the input string."""
    matches = get_close_matches(agent_name, EXISTING_AGENT_NAMES, n=5, cutoff=0.5)
    is_similar = len(matches) > 0
    return {
        "provided_agent_name": agent_name,
        "similar_agents_found": matches,
        "is_similar": is_similar,
    }

def self_report() -> str:
    return "You are version 0.1 MVP - similarity match only."

# Get the Gemini model by name
model = "gemini-2.0-flash-001"


root_agent = LlmAgent(
    # model="gemini-2.0-flash-001",
    model = model,
    name="call_of_agents",
    description="MVP agent that finds agent names similar to input using fuzzy matching.",
    instruction="Call self_report for version info. Use similar_agent_names to find similar agents.",
    tools=[self_report, similar_agent_names],
)
