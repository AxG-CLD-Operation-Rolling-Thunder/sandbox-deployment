"""
Invoice AI Agent - Simplified entry point
"""
import logging
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from ..controllers.request_handler import RequestHandler
from ..prompts import invoice_agent_instruction
from ..config import GOOGLE_GENAI_MODEL

logger = logging.getLogger(__name__)

async def get_artifact(filename: str, tool_context: ToolContext = None) -> dict:
    """Get a specific artifact by filename"""
    if not filename:
        return {"error": "No filename provided"}
        
    try:
        part = await tool_context.load_artifact(filename=filename)
        
        if not (part and part.get('inlineData')):
            return {"error": f"File '{filename}' not found or invalid"}
        
        return {
            "file_data": part['inlineData']['data'], 
            "mimetype": part['inlineData']['mimeType']
        }
    except Exception as e:
        logger.error(f"Error loading artifact {filename}: {str(e)}")
        return {"error": f"Error loading file: {str(e)}"}

async def process_request(
    request_type: str, 
    filename: Optional[str] = None, 
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Route requests to the appropriate handler.
    """
    request_handler = RequestHandler()
    
    logger.info(f"Processing request: {request_type}, filename: {filename}")
    
    # For invoice processing, get the file data
    if request_type == "process_invoice" and filename:
        file_data = await get_artifact(filename, tool_context)
        if "error" in file_data:
            return {
                "status": "error",
                "message": file_data["error"]
            }
        return request_handler.handle(request_type, file_data, tool_context)
    else:
        return request_handler.handle(request_type, {}, tool_context)

# Optional: Keep list_artifacts only if users explicitly need to see all files
async def list_artifacts(tool_context: ToolContext = None) -> dict:
    """List all uploaded files - only used when explicitly requested"""
    if not tool_context:
        return {"files": [], "message": "No files available"}
        
    names = await tool_context.list_artifacts()
    return {
        "files": names,
        "count": len(names),
        "message": f"Found {len(names)} file(s)"
    }

root_agent = Agent(
    model=GOOGLE_GENAI_MODEL,
    name='invoice_expense_agent',
    instruction=invoice_agent_instruction.INVOICE_AGENT_INSTRUCTION,
    tools=[process_request, get_artifact, list_artifacts],
)
