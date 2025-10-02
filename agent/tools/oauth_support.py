import os, pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.adk.tools import ToolContext
from ..config.config import (LOG_IDENTIFIER, LOCAL_AUTH_CREDS_LOADED, API_SCOPES, AUTHORIZATION_ID)
import pickle
import logging


# def get_temp_credentials() -> Credentials:
#     """Local dev helper for OAuth2 flow."""
#     if os.path.exists("token.pickle"):
#         with open("token.pickle", "rb") as token:
#             return pickle.load(token)
        
#     flow = InstalledAppFlow.from_client_config(LOCAL_AUTH_CREDS_LOADED, API_SCOPES)
#     creds = flow.run_local_server(port=8081)
    
#     if creds:
#         with open("token.pickle", "wb") as token:
#             pickle.dump(creds, token)

#     return creds


# def retrieve_user_auth(tool_context: ToolContext) -> Credentials:
#     """This function will retrieve the user's OAuth2 access token. Wired to support local flow"""

#     if os.getenv("LOCAL_DEV", "0") == "1":
#         credentials = get_temp_credentials()
#     else:
#         credentials = tool_context.state.get(f"temp:{AUTHORIZATION_ID}")
#         credentials = Credentials(token=credentials)

#     if not credentials:
#         raise RuntimeError(f"[{LOG_IDENTIFIER} FAILURE]: Unable to acquire access token.")

#     return credentials



logger = logging.getLogger(__name__)

def get_temp_credentials() -> Credentials:
    """
    Local dev helper for OAuth2 flow.
    Source note: Exact pattern from EBC agent/tools/oauth_support.py
    """
    token_file = "gtm_token.pickle"
    
    if os.path.exists(token_file):
        logger.info(f"[{LOG_IDENTIFIER}] Loading cached credentials from {token_file}")
        with open(token_file, "rb") as token:
            return pickle.load(token)
    
    logger.info(f"[{LOG_IDENTIFIER}] Starting OAuth flow for local development")
    flow = InstalledAppFlow.from_client_config(LOCAL_AUTH_CREDS_LOADED, API_SCOPES)
    creds = flow.run_local_server(port=8082)  # Different port to avoid conflicts with EBC
    
    if creds:
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)
        logger.info(f"[{LOG_IDENTIFIER}] Credentials cached to {token_file}")
    
    return creds


def retrieve_user_auth(tool_context: ToolContext) -> Credentials:
    """
    Retrieve the user's OAuth2 access token. Wired to support local flow.
    Source note: Exact pattern from EBC agent/tools/oauth_support.py
    """
    try:
        if os.getenv("LOCAL_DEV", "0") == "1":
            logger.debug(f"[{LOG_IDENTIFIER}] Using local dev credentials")
            credentials = get_temp_credentials()
        else:
            # In production, retrieve from tool context state
            logger.debug(f"[{LOG_IDENTIFIER}] Retrieving credentials from tool context")
            token = tool_context.state.get(f"temp:{AUTHORIZATION_ID}")
            if not token:
                raise RuntimeError(f"No OAuth token found for {AUTHORIZATION_ID}")
            credentials = Credentials(token=token)
        
        if not credentials:
            error_msg = f"[{LOG_IDENTIFIER} FAILURE]: Unable to acquire access token."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Log success metric if telemetry enabled
        if TELEMETRY_ENABLED:
            logger.info(f"[{LOG_IDENTIFIER}] OAuth retrieval successful")
        
        return credentials
        
    except Exception as e:
        logger.exception(f"[{LOG_IDENTIFIER}] Failed to retrieve user auth: {str(e)}")
        raise


def validate_oauth_scopes(credentials: Credentials) -> bool:
    """
    Validate that the credentials have the required scopes.
    Additional safety check not in EBC but recommended for production.
    """
    if not hasattr(credentials, 'scopes'):
        logger.warning(f"[{LOG_IDENTIFIER}] Cannot validate scopes - not available in credentials")
        return True  # Assume valid if we can't check
    
    missing_scopes = set(API_SCOPES) - set(credentials.scopes or [])
    if missing_scopes:
        logger.error(f"[{LOG_IDENTIFIER}] Missing required OAuth scopes: {missing_scopes}")
        return False
    
    return True