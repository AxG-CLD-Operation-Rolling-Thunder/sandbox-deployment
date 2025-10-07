from google.adk.agents import LlmAgent
from .tools.oauth_support import retrieve_user_auth
from google.adk.tools import ToolContext
import requests

test = 'AIzaSyBItU3CpLXLamNOUIUvw5QZceOTxjvK35A'

def get_users_name(tool_context: ToolContext) -> dict:
    auth = retrieve_user_auth(tool_context).token

    resp = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {auth}"},
    ).json()

    print(resp)
    email = resp.get("email")
    name = resp.get("name")

    return {"email": email, "name": name}


def self_report():
    return "You are version 0.0.1"

root_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="example_agent",
    description="An example agent to serve as a basis for your agent.",
    instruction="Call self_report and get_users_name tool when requested to do so by user. also say hello world after each message",
    tools=[self_report, get_users_name],
)
