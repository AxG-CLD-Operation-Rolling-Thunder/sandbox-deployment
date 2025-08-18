"""
Session management service using ADK ToolContext for proper session isolation
"""
import logging
from typing import List, Optional, Dict, Any
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self):
        self._tool_context: Optional[ToolContext] = None
        
    @property
    def invoices(self) -> List[dict]:
        """Get invoices from tool context state"""
        if self._tool_context and hasattr(self._tool_context, 'state'):
            return self._tool_context.state.get('invoices', [])
        return []
        
    @property
    def tool_context(self) -> Optional[ToolContext]:
        """Get current tool context"""
        return self._tool_context
        
    def set_tool_context(self, context: Optional[ToolContext]):
        """Set tool context for current session"""
        logger.debug(f"Setting tool context: {context is not None}")
        self._tool_context = context
        
        if context and hasattr(context, 'state'):
            if 'invoices' not in context.state:
                context.state['invoices'] = []
                logger.info("Initialized empty invoice list in tool context")
                
    def add_invoice(self, invoice_data: dict):
        """Add invoice to current session state"""
        if self._tool_context and hasattr(self._tool_context, 'state'):
            invoices = self._tool_context.state.get('invoices', [])
            invoices.append(invoice_data)
            self._tool_context.state['invoices'] = invoices
            logger.info(f"Added invoice. Total invoices in session: {len(invoices)}")
        else:
            logger.warning("No tool context available to store invoice")
            
    def clear(self, data: dict = None) -> dict:
        """Clear session data"""
        count = 0
        if self._tool_context and hasattr(self._tool_context, 'state'):
            invoices = self._tool_context.state.get('invoices', [])
            count = len(invoices)
            self._tool_context.state['invoices'] = []
            logger.info(f"Cleared {count} invoices from session")
        
        return {
            "status": "success",
            "message": f"Session cleared. {count} invoice(s) removed."
        }
        
    def get_invoice_count(self) -> int:
        """Get current invoice count"""
        return len(self.invoices)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about current session"""
        has_context = self._tool_context is not None
        invoice_count = self.get_invoice_count()
        
        session_id = None
        if self._tool_context:
            session_id = (
                getattr(self._tool_context, 'session_id', None) or
                getattr(self._tool_context, 'conversation_id', None) or
                (self._tool_context.state.get('session_id') if hasattr(self._tool_context, 'state') else None)
            )
        
        return {
            "has_context": has_context,
            "session_id": session_id,
            "invoice_count": invoice_count,
            "invoices": self.invoices
        }
