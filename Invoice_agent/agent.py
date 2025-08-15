"""
Invoice AI Agent - Entry point for the ADK agent
"""
import os
from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.tools import ToolContext
from .controllers.request_handler import RequestHandler
from .prompts import prompts
from dotenv import load_dotenv

load_dotenv()

# Initialize the request handler
request_handler = RequestHandler()

def process_request(
    request_type: str, 
    data: Optional[Dict[str, Any]] = None, 
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Route requests to the appropriate handler.
    This is the only tool exposed to the agent.
    """
    return request_handler.handle(request_type, data, tool_context)

# Create the agent
root_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.5-flash"),
    name='invoice_expense_agent',
    instruction=prompts.INVOICE_AGENT_INSTRUCTION,
    tools=[process_request]
)