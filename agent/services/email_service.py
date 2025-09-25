
"""
Email draft creation service
"""
import os
import logging
from typing import Dict, Any
from ..workspace_tools.email_composer import create_expense_email_draft
from ..oauth import get_credentials_from_context
from ..config import LOCAL_DEV, ADK_DEV_MODE, ADK_LOCAL_RUN, AS_APP, GOOGLE_CLOUD_PROJECT

def is_local_environment():
    return (LOCAL_DEV or ADK_DEV_MODE or ADK_LOCAL_RUN) and not (AS_APP or GOOGLE_CLOUD_PROJECT)

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, session_service):
        self.session = session_service
        
    def create_draft(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create email draft with expense report from current session"""
        invoices = self.session.invoices
        logger.info(f"Creating email draft for {len(invoices)} invoices from current session")
        
        if not invoices:
            return {
                "status": "error",
                "message": "No invoices to include in email. Please process invoices first."
            }
            
        try:
            credentials = get_credentials_from_context(self.session.tool_context)
            
            if not credentials:
                return self._handle_missing_credentials()
                
            result = create_expense_email_draft(
                invoice_data=invoices,
                credentials=credentials,
                recipient_email=data.get('recipient'),
                cc_emails=data.get('cc_emails'),
                additional_notes=data.get('notes')
            )
            
            if result["success"]:
                return self._format_success_response(result)
            else:
                return self._format_error_response(result)
                
        except Exception as e:
            logger.error(f"Error creating email draft: {str(e)}")
            return {
                "status": "error",
                "message": f"Error creating email draft: {str(e)}"
            }
    
    def _handle_missing_credentials(self) -> Dict[str, Any]:
        """Handle missing credentials based on environment"""
        if is_local_environment():
            return {
                "status": "oauth_required",
                "message": "Gmail authorization is required to create email drafts.",
                "instructions": (
                    "In local development, credentials will be requested automatically. "
                    "A browser window should open for authorization."
                ),
                "environment": "local"
            }
        else:
            return {
                "status": "oauth_required",
                "message": "Gmail authorization is required to create email drafts.",
                "instructions": (
                    "In cloud environments, OAuth should be configured during deployment. "
                    "Please ensure the app has been authorized in Agentspace."
                ),
                "environment": "cloud"
            }
            
    def _format_success_response(self, result: dict) -> dict:
        """Format successful email creation response"""
        environment = "local" if is_local_environment() else "cloud"
        return {
            "status": "success",
            "message": (
                f"✅ Email draft created successfully in your Gmail!\n\n"
                f"**Draft ID:** {result.get('draft_id', 'N/A')}\n"
                f"**Subject:** {result.get('subject', 'N/A')}\n"
                f"**Recipient:** {result.get('recipient', 'You')}\n\n"
                f"The draft is now in your Gmail drafts folder."
            ),
            "draft_id": result.get("draft_id"),
            "subject": result.get("subject"),
            "recipient": result.get("recipient", "You"),
            "environment": environment,
            "session_info": self.session.get_session_info()
        }
        
    def _format_error_response(self, result: dict) -> dict:
        """Format error response based on error type"""
        error = result.get('error', 'Unknown error')
        environment = "local" if is_local_environment() else "cloud"
        
        if result.get("error_code") in [401, 403]:
            if is_local_environment():
                message = (
                    "Gmail authorization has expired or is invalid. "
                    "Please delete token.pickle and try again."
                )
            else:
                message = (
                    "Gmail authorization has expired or is invalid. "
                    "Please re-authorize the app in Agentspace."
                )
                
            return {
                "status": "oauth_expired",
                "message": message,
                "error": error,
                "environment": environment
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to create Gmail draft: {error}",
                "environment": environment
            }
