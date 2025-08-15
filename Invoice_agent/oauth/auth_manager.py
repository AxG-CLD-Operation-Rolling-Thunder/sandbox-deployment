import os
import logging
import pickle
from typing import Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleAuthRequest
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.adk.tools import ToolContext
from .config import AUTHORIZATION_ID, SCOPES, OAUTH_CONFIG

logger = logging.getLogger(__name__)

PICKLE_FILE = "token.pickle"

def get_local_credentials():
    """Get credentials from local token.pickle file or initiate OAuth flow"""
    logger.debug("Attempting to load local credentials")
    
    # Check if token.pickle exists
    if os.path.exists(PICKLE_FILE):
        try:
            with open(PICKLE_FILE, "rb") as token:
                creds = pickle.load(token)
                logger.info("Loaded credentials from token.pickle")
                
                # Check if credentials are valid
                if creds and creds.valid:
                    return creds
                
                # Try to refresh if expired
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired credentials")
                    creds.refresh(GoogleAuthRequest())
                    # Save refreshed credentials
                    with open(PICKLE_FILE, "wb") as token:
                        pickle.dump(creds, token)
                    return creds
        except Exception as e:
            logger.error(f"Error loading token.pickle: {e}")
    
    # No valid credentials, initiate OAuth flow
    logger.info("No valid credentials found, initiating OAuth flow")
    
    client_config = {
        "installed": {
            "client_id": OAUTH_CONFIG["client_id"],
            "client_secret": OAUTH_CONFIG["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8081"]
        }
    }
    
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=8081)
    
    # Save credentials for future use
    if creds:
        with open(PICKLE_FILE, "wb") as token:
            pickle.dump(creds, token)
            logger.info("Saved credentials to token.pickle")
    
    return creds

def get_credentials_from_context(tool_context: Optional[ToolContext] = None) -> Optional[Credentials]:
    """
    Get credentials from tool context (for cloud) or local storage
    
    Args:
        tool_context: ADK tool context containing OAuth token in cloud environments
        
    Returns:
        Google OAuth2 Credentials object or None
    """
    logger.debug("Getting credentials from context")
    
    creds = None
    
    # First, try to get credentials from tool context (cloud environment)
    if tool_context and hasattr(tool_context, 'state') and tool_context.state:
        access_token = tool_context.state.get(f"temp:{AUTHORIZATION_ID}")
        if access_token:
            logger.info(f"Using access token from tool context for {AUTHORIZATION_ID}")
            creds = Credentials(token=access_token)
            return creds
        else:
            logger.warning(f"No access token found for {AUTHORIZATION_ID} in tool context")
    
    # If no tool context or no token in context, check if we're in local environment
    if not creds:
        if os.getenv("LOCAL_DEV", "0") == "1" or (not tool_context and os.path.exists(PICKLE_FILE)):
            logger.info("Local environment detected, using local credentials")
            creds = get_local_credentials()
            return creds
    
    # No credentials available
    if not creds:
        logger.warning("No credentials available from context or local storage")
        return None
    
    return creds

def get_authenticated_service(api_name: str, api_version: str, tool_context: Optional[ToolContext] = None):
    """
    Create an authenticated Google API service
    
    Args:
        api_name: Name of the API (e.g., 'gmail')
        api_version: API version (e.g., 'v1')
        tool_context: ADK tool context for OAuth in cloud environments
        
    Returns:
        Authenticated Google API service object
    """
    logger.debug(f"Creating authenticated service for {api_name} v{api_version}")
    
    # Get credentials using the unified method
    creds = get_credentials_from_context(tool_context)
    
    if not creds:
        raise RuntimeError(f"No valid credentials available for {api_name}")
    
    # Check if credentials are valid
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials")
            creds.refresh(GoogleAuthRequest())
            # Save refreshed credentials if in local environment
            if os.path.exists(PICKLE_FILE):
                with open(PICKLE_FILE, "wb") as token:
                    pickle.dump(creds, token)
        else:
            raise RuntimeError("Credentials are invalid and cannot be refreshed")
    
    # Build and return the service
    service = build(api_name, api_version, credentials=creds)
    logger.info(f"Successfully created {api_name} service")
    
    return service

def clear_local_credentials():
    """Clear local token.pickle file"""
    if os.path.exists(PICKLE_FILE):
        os.remove(PICKLE_FILE)
        logger.info("Cleared local credentials (token.pickle)")
        return True
    return False

def check_credentials_validity(tool_context: Optional[ToolContext] = None) -> dict:
    """
    Check if credentials are valid and return status information
    
    Args:
        tool_context: ADK tool context for OAuth in cloud environments
        
    Returns:
        Dictionary with authorization status and details
    """
    try:
        creds = get_credentials_from_context(tool_context)
        
        if creds and creds.valid:
            # Try to get Gmail profile to verify credentials work
            service = build('gmail', 'v1', credentials=creds)
            profile = service.users().getProfile(userId='me').execute()
            
            return {
                "valid": True,
                "email": profile.get('emailAddress', 'Unknown'),
                "source": "cloud" if tool_context else "local",
                "message": f"Authorized as {profile.get('emailAddress', 'Unknown')}"
            }
        else:
            return {
                "valid": False,
                "email": None,
                "source": "cloud" if tool_context else "local",
                "message": "No valid credentials available"
            }
    except Exception as e:
        logger.error(f"Error checking credentials: {str(e)}")
        return {
            "valid": False,
            "email": None,
            "source": "cloud" if tool_context else "local",
            "message": f"Error checking credentials: {str(e)}"
        }