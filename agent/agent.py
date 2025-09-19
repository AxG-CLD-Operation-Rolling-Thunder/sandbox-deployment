from google.adk.agents import LlmAgent
from .tools.oauth_support import retrieve_user_auth
from .prompts.pulse_generation_agent import PULSE_GENERATION_AGENT

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="cloud_marketing_pulse_assistant",
    description="This agent manages calling on the appropriate document generation tools and corresponding uploading functionality.",
    instruction=PULSE_GENERATION_AGENT
    tools=[]
)