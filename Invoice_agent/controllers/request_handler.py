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
from ..config import LOCAL_DEV, ADK_DEV_MODE, ADK_LOCAL_RUN, AS_APP, GOOGLE_CLOUD_PROJECT

def is_local_environment():
    return (LOCAL_DEV or ADK_DEV_MODE or ADK_LOCAL_RUN) and not (AS_APP or GOOGLE_CLOUD_PROJECT)

logger = logging.getLogger(__name__)

class RequestHandler:
    def __init__(self):
        self.session = SessionService()
        
    def handle(self, request_type: str, data: Dict[str, Any] = None, 
               tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
        """
        Route requests to appropriate service based on request type
        """
        if data is None:
            data = {}
            
        if tool_context:
            self.session.set_tool_context(tool_context)
            logger.info(f"Tool context set for request type: {request_type}")
        else:
            logger.warning(f"No tool context provided for request type: {request_type}")
            
        try:
            environment = "local" if is_local_environment() else "cloud"
            logger.info(f"Processing request type: {request_type} in {environment} environment")
            logger.debug(f"Session info: {self.session.get_session_info()}")
            
            invoice_service = InvoiceService(self.session)
            summary_service = SummaryService(self.session)
            email_service = EmailService(self.session)
            oauth_service = OAuthService(self.session)
            
            handlers = {
                "process_invoice": invoice_service.process,
                "generate_summary": summary_service.generate,
                "create_email": email_service.create_draft,
                "check_oauth_status": oauth_service.check_status,
                "clear_session": self.session.clear,
                "get_session_info": lambda d: {"status": "success", **self.session.get_session_info()}
            }
            
            handler = handlers.get(request_type)
            if not handler:
                return {
                    "status": "error",
                    "message": f"Unknown request type: {request_type}. Valid types are: {', '.join(handlers.keys())}"
                }
                
            result = handler(data)
            
            logger.debug(f"After {request_type}, invoice count: {self.session.get_invoice_count()}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in request handler: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }
