"""
OAuth management service
"""
import logging
from typing import Dict, Any
from ..oauth import get_authenticated_service, get_credentials_from_context
from ..oauth.config import is_local_environment

logger = logging.getLogger(__name__)

class OAuthService:
    def __init__(self, session_service):
        self.session = session_service
        
    def check_status(self, data: dict = None) -> dict:
        """Check current OAuth authorization status"""
        try:
            tool_context = self.session.tool_context
            environment = "local" if is_local_environment() else "cloud"
            logger.info(f"Checking OAuth status in {environment} environment")
            logger.info(f"Tool context available: {tool_context is not None}")
            
            credentials = get_credentials_from_context(tool_context)
            
            if credentials and credentials.valid:
                service = get_authenticated_service('gmail', 'v1', tool_context)
                profile = service.users().getProfile(userId='me').execute()
                
                return {
                    "status": "success",
                    "authorized": True,
                    "message": f"Gmail is authorized for {profile.get('emailAddress', 'Unknown')}",
                    "user_email": profile.get('emailAddress'),
                    "environment": environment,
                    "session_info": self.session.get_session_info()
                }
            else:
                return {
                    "status": "success",
                    "authorized": False,
                    "message": "Gmail is not authorized.",
                    "environment": environment,
                    "session_info": self.session.get_session_info()
                }
                
        except Exception as e:
            logger.error(f"Error checking OAuth status: {str(e)}")
            return {
                "status": "success",
                "authorized": False,
                "message": "Gmail authorization check failed.",
                "environment": "local" if is_local_environment() else "cloud",
                "error": str(e),
                "session_info": self.session.get_session_info()
            }
