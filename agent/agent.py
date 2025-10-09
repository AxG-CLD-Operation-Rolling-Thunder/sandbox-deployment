"""
Work with Me AI Agent - Ingestion
"""
import os
import logging
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from .prompts import work_with_me_instructions
#from .tools. import invoice_search_tool, retrieve_invoice_knowledge
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)







root_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.5-flash"),
    name='invoice_expense_agent',
    instruction=work_with_me_instructions.PROMPT_1,
    tools=agent_tools
)

