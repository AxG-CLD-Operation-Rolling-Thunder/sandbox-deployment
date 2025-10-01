from google.adk.agents import LlmAgent
from .tools.oauth_support import retrieve_user_auth
from .prompts.pulse_generation_agent import PULSE_GENERATION_AGENT
from .tools.file_upload_support import list_artifacts
from google.adk.tools import agent_tool, ToolContext
import requests 

def get_users_name(tool_context: ToolContext) -> dict:
    auth = retrieve_user_auth(tool_context).token

    resp = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {auth}"},
    ).json()

    print(resp)
    email = resp.get("email")
    name  = resp.get("name")

    return {"email": email, "name": name}

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="cloud_marketing_pulse_assistant",
    description="I am an AI assistant that helps create weekly updates and on-brand snippets for the Cloud Marketing Pulse newsletter.",
    instruction=PULSE_GENERATION_AGENT,
    sub_agents=[],
    tools=[get_users_name,list_artifacts]
)