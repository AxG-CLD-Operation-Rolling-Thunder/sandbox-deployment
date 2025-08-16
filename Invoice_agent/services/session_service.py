"""
Session management service
"""
from typing import List, Optional
from google.adk.tools import ToolContext

class SessionService:
    def __init__(self):
        # Use instance variables, not class variables
        self._invoices: List[dict] = []
        self._tool_context: Optional[ToolContext] = None
        
    @property
    def invoices(self) -> List[dict]:
        return self._invoices
        
    @property
    def tool_context(self) -> Optional[ToolContext]:
        return self._tool_context
        
    def add_invoice(self, invoice_data: dict):
        """Add invoice to current session"""
        self._invoices.append(invoice_data)
        
    def set_tool_context(self, context: ToolContext):
        """Set tool context for current session"""
        self._tool_context = context
        
    def clear(self, data: dict = None) -> dict:
        """Clear session data"""
        count = len(self._invoices)
        self._invoices.clear()  # Use clear() instead of reassigning
        self._tool_context = None
        return {
            "status": "success",
            "message": f"Session cleared. {count} invoice(s) removed."
        }
        
    def get_invoice_count(self) -> int:
        """Get current invoice count"""
        return len(self._invoices)
