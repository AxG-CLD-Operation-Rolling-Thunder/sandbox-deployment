import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.adk.tools import ToolContext
import pickle
from ..config.config import (LOG_IDENTIFIER, LOCAL_AUTH_CREDS_LOADED, API_SCOPES, AUTHORIZATION_ID)

import logging

logger = logging.getLogger(LOG_IDENTIFIER)


# Import the ADK tool decorator
from .oauth_support import retrieve_user_auth



# @tool
def append_to_google_doc(document_id: str, text: str,tool_context: ToolContext) -> str:
    logger.info("Started Document Upload Attempt")
    try:
        creds = retrieve_user_auth(tool_context)
        logger.info(creds)
        service = build("docs", "v1", credentials=creds)
        logger.info('Got Through Service')
        logger.info(service.documents().get(documentId=document_id).execute())

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
        logger.info("request executed")
        return f"Successfully appended text to document ID: {document_id}"
    except Exception as e:
        logger.exception("Failed to upload file to Google Drive.")
        return {"status": "error", "error": str(e)}
    # except HttpError as err:
    #     return f"An error occurred: {err}"