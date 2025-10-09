import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.adk.tools import ToolContext
from ..config.config import (LOG_IDENTIFIER, LOCAL_AUTH_CREDS_LOADED, API_SCOPES, AUTHORIZATION_ID)

# Import the ADK tool decorator
from .oauth_support import retrieve_user_auth



# @tool
def append_to_google_doc(document_id: str, text: str,tool_context: ToolContext) -> str:
    """
    Appends text to the top of a specified Google Document.

    Args:
        document_id: The ID of the Google Document to edit.
        text: The text content to append to the top of the document.

    Returns:
        A string indicating success or failure.
    """
    # creds = None
    # # The file token.json stores the user's access and refresh tokens.
    # if os.path.exists("token.json"):
    #     creds = Credentials.from_authorized_user_file("token.json", API_SCOPES)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             "credentials.json", API_SCOPES
    #         )
    #         creds = flow.run_local_server(port=0)
    #     # Save the credentials for the next run
    #     with open("token.json", "w") as token:
    #         token.write(creds.to_json())

    try:
        service = build("docs", "v1", credentials=retrieve_user_auth(tool_context))
        print("Here 1")
        # The request to insert text at the beginning of the document body.
        # Index 1 is the beginning of the body.
        requests = [
            {
                "insertText": {
                    "location": {
                        "index": 1,
                    },
                    "text": text,
                }
            }
        ]
        print("here 2")
        # Execute the request. The edit is saved automatically.
        service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()

        return f"Successfully appended text to document ID: {document_id}"

    except HttpError as err:
        return f"An error occurred: {err}"