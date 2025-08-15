"""
Session management service
"""
from typing import List, Optional
from google.adk.tools import ToolContext

class SessionService:
    def __init__(self):
        self._invoices: List[dict] = []
        self._tool_context: Optional[ToolContext] = None
        
    @property
    def invoices(self) -> List[dict]:
        return self._invoices
        
    @property
    def tool_context(self) -> Optional[ToolContext]:
        return self._tool_context
        
    def add_invoice(self, invoice_data: dict):
        self._invoices.append(invoice_data)
        
    def set_tool_context(self, context: ToolContext):
        self._tool_context = context
        
    def clear(self, data: dict = None) -> dict:
        """Clear session data"""
        count = len(self._invoices)
        self._invoices = []
        self._tool_context = None
        return {
            "status": "success",
            "message": f"Session cleared. {count} invoice(s) removed."
        }