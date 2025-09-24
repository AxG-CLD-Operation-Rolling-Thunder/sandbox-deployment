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
            # Initialize RAG context if not present
            if 'rag_queries' not in context.state:
                context.state['rag_queries'] = []
            if 'rag_results' not in context.state:
                context.state['rag_results'] = []
                
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
        rag_count = 0
        if self._tool_context and hasattr(self._tool_context, 'state'):
            invoices = self._tool_context.state.get('invoices', [])
            count = len(invoices)
            self._tool_context.state['invoices'] = []

            # Clear RAG context as well
            rag_queries = self._tool_context.state.get('rag_queries', [])
            rag_count = len(rag_queries)
            self._tool_context.state['rag_queries'] = []
            self._tool_context.state['rag_results'] = []

            logger.info(f"Cleared {count} invoices and {rag_count} RAG queries from session")

        return {
            "status": "success",
            "message": f"Session cleared. {count} invoice(s) and {rag_count} RAG queries removed."
        }
        
    def get_invoice_count(self) -> int:
        """Get current invoice count"""
        return len(self.invoices)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about current session"""
        has_context = self._tool_context is not None
        invoice_count = self.get_invoice_count()
        rag_query_count = len(self.get_rag_queries())

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
            "invoices": self.invoices,
            "rag_query_count": rag_query_count,
            "rag_queries": self.get_rag_queries()
        }

    # RAG-specific methods
    def add_rag_query(self, query: str):
        """Add RAG query to session context"""
        if self._tool_context and hasattr(self._tool_context, 'state'):
            queries = self._tool_context.state.get('rag_queries', [])
            queries.append({
                "query": query,
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            self._tool_context.state['rag_queries'] = queries
            logger.info(f"Added RAG query. Total queries: {len(queries)}")
        else:
            logger.warning("No tool context available to store RAG query")

    def add_rag_results(self, results: List[Dict[str, Any]]):
        """Add RAG results to session context"""
        if self._tool_context and hasattr(self._tool_context, 'state'):
            all_results = self._tool_context.state.get('rag_results', [])
            all_results.extend(results)
            # Keep only last 50 results to prevent memory issues
            if len(all_results) > 50:
                all_results = all_results[-50:]
            self._tool_context.state['rag_results'] = all_results
            logger.info(f"Added {len(results)} RAG results. Total results: {len(all_results)}")
        else:
            logger.warning("No tool context available to store RAG results")

    def get_rag_queries(self) -> List[Dict[str, Any]]:
        """Get RAG queries from session context"""
        if self._tool_context and hasattr(self._tool_context, 'state'):
            return self._tool_context.state.get('rag_queries', [])
        return []

    def get_rag_results(self) -> List[Dict[str, Any]]:
        """Get RAG results from session context"""
        if self._tool_context and hasattr(self._tool_context, 'state'):
            return self._tool_context.state.get('rag_results', [])
        return []

    def clear_rag_context(self):
        """Clear only RAG context, keeping invoices"""
        if self._tool_context and hasattr(self._tool_context, 'state'):
            rag_count = len(self._tool_context.state.get('rag_queries', []))
            self._tool_context.state['rag_queries'] = []
            self._tool_context.state['rag_results'] = []
            logger.info(f"Cleared {rag_count} RAG queries and results from session")
