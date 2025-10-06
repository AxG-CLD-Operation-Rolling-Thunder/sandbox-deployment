# Source note: Adapted from agent/tools/user_gws_support.py in EBC

import os
import uuid
import logging
from typing import Dict, Any, Optional
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError
from google.adk.tools import ToolContext
from .oauth_support import retrieve_user_auth

logger = logging.getLogger(__name__)
LOG_IDENTIFIER = "GRAD_AGENT"

def upload_to_google_docs_tool(
    tool_context: ToolContext,
    document_title: Optional[str] = None,
    document_type: Optional[str] = "Grad Agent Context"
) -> Dict[str, Any]:
    """
    Uploads generated content to Google Docs.
    Always available - no configuration needed.
    Source note: Enhanced version of EBC agent/tools/user_gws_support.py
    
    Args:
        tool_context: ADK tool context containing state and auth
        document_title: Optional custom title for the document
        document_type: Type of document being uploaded
    
    Returns:
        Dict with status, document_id, document_url, and message
    """
    
    logger.info(f"[{LOG_IDENTIFIER}] Starting upload_to_google_docs_tool...")
    
    try:
        # Step 1: Retrieve OAuth credentials
        credentials = retrieve_user_auth(tool_context)
        
        # Step 2: Check for document in context
        # Look for multiple possible keys where document might be stored
        possible_keys = [
            "generated_document",      # Generic
            "document_buffer",         # Alternative
            "executive_summary_document"  # Legacy EBC compatibility
        ]
        
        doc_buffer = None
        used_key = None
        
        for key in possible_keys:
            if key in tool_context.state:
                doc_buffer = tool_context.state[key]
                used_key = key
                logger.info(f"[{LOG_IDENTIFIER}] Found document buffer in context at key: {key}")
                break
        
        if not doc_buffer:
            logger.warning(f"[{LOG_IDENTIFIER}] No document buffer found in tool_context.state")
            logger.debug(f"[{LOG_IDENTIFIER}] Checked keys: {possible_keys}")
            logger.debug(f"[{LOG_IDENTIFIER}] Available keys: {list(tool_context.state.keys())}")
            return {
                "status": "error",
                "error": "No document found in context. Please generate a document first."
            }
        
        # Step 3: Determine document title
        if not document_title:
            # Try to get from context or use default
            document_title = tool_context.state.get("document_title", 
                            tool_context.state.get("initiative_title", 
                            f"{document_type} - {uuid.uuid4().hex[:8]}"))
        
        # Step 4: Create Drive service
        try:
            drive_service = build('drive', 'v3', credentials=credentials)
            logger.info(f"[{LOG_IDENTIFIER}] Google Drive service built successfully")
        except Exception as e:
            logger.exception(f"[{LOG_IDENTIFIER}] Failed to build Drive service")
            return {"status": "error", "error": f"Drive service error: {str(e)}"}
        
        # Step 5: Handle buffer data (could be BytesIO or bytes)
        if isinstance(doc_buffer, BytesIO):
            file_bytes = doc_buffer.getvalue()
        elif isinstance(doc_buffer, bytes):
            file_bytes = doc_buffer
        else:
            # Try to convert to bytes
            try:
                file_bytes = bytes(doc_buffer)
            except:
                logger.error(f"[{LOG_IDENTIFIER}] Unknown document buffer type: {type(doc_buffer)}")
                return {
                    "status": "error",
                    "error": f"Invalid document buffer type: {type(doc_buffer)}"
                }
        
        # Step 6: Prepare file metadata
        file_metadata = {
            'name': f"{document_title}",
            'mimeType': 'application/vnd.google-apps.document'
        }
        logger.info(f"[{LOG_IDENTIFIER}] File metadata: {file_metadata}")
        
        # Step 7: Create media upload object
        try:
            # Use in-memory upload instead of temp file
            media = MediaIoBaseUpload(
                BytesIO(file_bytes),
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                resumable=True
            )
            logger.info(f"[{LOG_IDENTIFIER}] MediaIoBaseUpload object created successfully")
        except Exception as e:
            logger.exception(f"[{LOG_IDENTIFIER}] Failed to create MediaIoBaseUpload object")
            return {"status": "error", "error": f"Media upload error: {str(e)}"}
        
        # Step 8: Upload and convert to Google Docs
        try:
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()
            
            document_id = file.get('id')
            document_url = file.get('webViewLink', f'https://docs.google.com/document/d/{document_id}/edit')
            
            logger.info(f"[{LOG_IDENTIFIER}] Google Doc created with ID: {document_id}")
            
        except HttpError as e:
            logger.exception(f"[{LOG_IDENTIFIER}] HTTP error uploading to Google Drive")
            return {
                "status": "error",
                "error": f"Google Drive API error: {str(e)}"
            }
        except Exception as e:
            logger.exception(f"[{LOG_IDENTIFIER}] Failed to upload file to Google Drive")
            return {"status": "error", "error": str(e)}
        
        # Step 9: Store result in tool_context for potential reuse
        tool_context.state["uploaded_document_id"] = document_id
        tool_context.state["uploaded_document_url"] = document_url
        logger.info(f"[{LOG_IDENTIFIER}] Document metadata stored in context")
        
        # Step 10: Return successful result
        return {
            "status": "success",
            "document_id": document_id,
            "document_url": document_url,
            "message": f"Document uploaded successfully to Google Docs",
            "document_title": document_title
        }
        
    except Exception as e:
        logger.exception(f"[{LOG_IDENTIFIER}] Unexpected error in upload_to_google_docs_tool")
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        }


def share_google_doc(
    document_id: str,
    share_emails: list,
    tool_context: ToolContext,
    role: str = "writer"
) -> Dict[str, Any]:
    """
    Share a Google Doc with specified email addresses.
    Additional functionality not in original EBC but useful for collaboration.
    
    Args:
        document_id: Google Doc ID to share
        share_emails: List of email addresses to share with
        tool_context: ADK tool context for auth
        role: Permission role (reader, writer, commenter)
    
    Returns:
        Dict with status and list of successfully shared emails
    """
    
    logger.info(f"[{LOG_IDENTIFIER}] Sharing document {document_id} with {len(share_emails)} users")
    
    try:
        credentials = retrieve_user_auth(tool_context)
        drive_service = build('drive', 'v3', credentials=credentials)
        
        shared_with = []
        errors = []
        
        for email in share_emails:
            try:
                permission = {
                    'type': 'user',
                    'role': role,
                    'emailAddress': email
                }
                
                drive_service.permissions().create(
                    fileId=document_id,
                    body=permission,
                    sendNotificationEmail=True
                ).execute()
                
                shared_with.append(email)
                logger.info(f"[{LOG_IDENTIFIER}] Shared with {email}")
                
            except HttpError as e:
                error_msg = f"Failed to share with {email}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"[{LOG_IDENTIFIER}] {error_msg}")
            except Exception as e:
                error_msg = f"Error sharing with {email}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"[{LOG_IDENTIFIER}] {error_msg}")
        
        result = {
            "status": "success" if shared_with else "failed",
            "shared_with": shared_with,
            "document_id": document_id
        }
        
        if errors:
            result["errors"] = errors
        
        return result
        
    except Exception as e:
        logger.exception(f"[{LOG_IDENTIFIER}] Failed to share document")
        return {
            "status": "error",
            "error": str(e),
            "document_id": document_id
        }