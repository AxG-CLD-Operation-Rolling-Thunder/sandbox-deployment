import os, pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.adk.tools import ToolContext
from ..config.config import LOG_IDENTIFIER, LOCAL_AUTH_CREDS_LOADED, API_SCOPES, AUTHORIZATION_ID
import pickle


def get_temp_credentials() -> Credentials:
    """Local dev helper for OAuth2 flow."""

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            return pickle.load(token)
        
    flow = InstalledAppFlow.from_client_config(LOCAL_AUTH_CREDS_LOADED, API_SCOPES)
    creds = flow.run_local_server(port=8081)
    
    if creds:
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def retrieve_user_auth(tool_context: ToolContext) -> Credentials:
    """This function will retrieve the user's OAuth2 access token. Wired to support local flow"""

    if os.getenv("LOCAL_DEV", "0") == "1":
        credentials = get_temp_credentials()
    else:
        credentials = tool_context.state.get(f"temp:{AUTHORIZATION_ID}")
        credentials = Credentials(token=credentials)

    if not credentials:
        raise RuntimeError(f"[{LOG_IDENTIFIER} FAILURE]: Unable to acquire access token.")

    return credentials