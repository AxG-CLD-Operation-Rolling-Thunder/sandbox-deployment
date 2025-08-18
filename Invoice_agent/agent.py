"""
Invoice AI Agent - Entry point for the ADK agent
"""
import os
import logging
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from .controllers.request_handler import RequestHandler
from .prompts import invoice_agent_instruction
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def process_request(
    request_type: str, 
    data: Optional[Dict[str, Any]] = None, 
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Route requests to the appropriate handler.
    Creates a new RequestHandler for each request to ensure proper session isolation.
    """
    request_handler = RequestHandler()
    
    logger.info(f"Processing request: {request_type}")
    logger.debug(f"Tool context provided: {tool_context is not None}")
    
    return request_handler.handle(request_type, data, tool_context)


root_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.5-flash"),
    name='invoice_expense_agent',
    instruction=invoice_agent_instruction.INVOICE_AGENT_INSTRUCTION,
    tools=[process_request]
)
