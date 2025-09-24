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
from .tools.knowledge_retrieval_tool import invoice_search_tool, retrieve_invoice_knowledge
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def process_request(
    request_type: str,
    data: Optional[Dict[str, Any]] = None,
    tool_context: Optional[ToolContext] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Route requests to the appropriate handler.
    Creates a new RequestHandler for each request to ensure proper session isolation.
    """
    request_handler = RequestHandler()

    logger.info(f"Processing request: {request_type}")
    logger.debug(f"Tool context provided: {tool_context is not None}")
    logger.debug(f"Additional kwargs: {kwargs}")

    # Merge kwargs into data if data is provided, otherwise use kwargs as data
    if data is None:
        data = kwargs
    else:
        data.update(kwargs)

    return request_handler.handle(request_type, data, tool_context)


# Prepare tools list with RAG capabilities
agent_tools = [process_request]

# Add search tool if available
if invoice_search_tool is not None:
    agent_tools.append(invoice_search_tool)
    logger.info("Search tool added to agent")
else:
    # Fallback to manual knowledge retrieval tool
    agent_tools.append(retrieve_invoice_knowledge)
    logger.info("Manual knowledge retrieval tool added to agent")

root_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.5-flash"),
    name='invoice_expense_agent',
    instruction=invoice_agent_instruction.INVOICE_AGENT_INSTRUCTION,
    tools=agent_tools
)
