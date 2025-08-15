"""
Request handler - Routes requests to appropriate services
"""
import logging
from typing import Dict, Any, Optional
from google.adk.tools import ToolContext
from ..services.invoice_service import InvoiceService
from ..services.summary_service import SummaryService
from ..services.email_service import EmailService
from ..services.oauth_service import OAuthService
from ..services.session_service import SessionService
from ..oauth.config import is_local_environment

logger = logging.getLogger(__name__)

class RequestHandler:
    def __init__(self):
        self.session = SessionService()
        self.invoice_service = InvoiceService(self.session)
        self.summary_service = SummaryService(self.session)
        self.email_service = EmailService(self.session)
        self.oauth_service = OAuthService(self.session)
        
    def handle(self, request_type: str, data: Dict[str, Any] = None, 
               tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
        """
        Route requests to appropriate service based on request type
        """
        if data is None:
            data = {}
            
        # Store tool context in session for OAuth
        if tool_context:
            self.session.set_tool_context(tool_context)
            
        try:
            # Log environment info
            environment = "local" if is_local_environment() else "cloud"
            logger.info(f"Processing request type: {request_type} in {environment} environment")
            logger.debug(f"Data keys: {list(data.keys())}")
            
            # Route to appropriate service
            handlers = {
                "process_invoice": self.invoice_service.process,
                "generate_summary": self.summary_service.generate,
                "create_email": self.email_service.create_draft,
                "check_oauth_status": self.oauth_service.check_status,
                "clear_session": self.session.clear
            }
            
            handler = handlers.get(request_type)
            if not handler:
                return {
                    "status": "error",
                    "message": f"Unknown request type: {request_type}. Valid types are: {', '.join(handlers.keys())}"
                }
                
            return handler(data)
            
        except Exception as e:
            logger.error(f"Error in request handler: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }