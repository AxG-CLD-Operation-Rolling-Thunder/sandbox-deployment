import io
from typing import List, Dict
from google.adk.tools import ToolContext
from googleapiclient.discovery import build
from PyPDF2 import PdfReader
from docx import Document
from .oauth_support import retrieve_user_auth

def get_drive_service(tool_context: ToolContext):
    """Builds an authenticated Drive API client."""
    return build("drive", "v3", credentials=retrieve_user_auth(tool_context))


# === Data Processing ===
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from a PDF byte stream."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = []
    for page in reader.pages:
        try:
            text.append(page.extract_text() or "")
        except Exception as e:
            print(f"Failed to extract text from page: {e}")
    return "\n".join(text)


def extract_text_from_docx(docx_bytes: bytes) -> str:
    """Extracts text from a DOCX byte stream."""
    file_stream = io.BytesIO(docx_bytes)
    doc = Document(file_stream)
    return "\n".join(
        [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    )


# === Core Drive Search ===
def search_all_drive_sources(query: str, drive_service) -> List[Dict]:
    """Search My Drive, Shared Drives, and 'Shared with me' files."""
    files = []

    # My Drive + Shared Drives
    my_files = (
        drive_service.files()
        .list(
            q=f"name contains '{query}' and trashed = false",
            corpora="user",
            spaces="drive",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields="files(id, name, mimeType, owners)",
        )
        .execute()
        .get("files", [])
    )
    files.extend(my_files)

    # Shared With Me
    shared_with_me = (
        drive_service.files()
        .list(
            q=f"sharedWithMe and name contains '{query}' and trashed = false",
            spaces="drive",
            fields="files(id, name, mimeType, owners)",
        )
        .execute()
        .get("files", [])
    )
    files.extend(shared_with_me)

    # Deduplicate by file ID
    seen = set()
    unique_files = []
    for f in files:
        if f["id"] not in seen:
            unique_files.append(f)
            seen.add(f["id"])
    return unique_files


def search_drive_and_extract_relevant_file(
    query: str, tool_context: ToolContext
) -> str:
    """
    Searches Google Drive and extracts the text from the first matching file.
    Supports Google Docs, PDFs, and DOCX.

    4k character response limit
    """

    drive_service = get_drive_service(tool_context)
    items = search_all_drive_sources(query, drive_service)
    if not items:
        return "No relevant files found."

    for file in items:
        file_id = file["id"]
        name = file["name"]
        mime_type = file["mimeType"]
        try:
            if mime_type == "application/vnd.google-apps.document":
                content = (
                    drive_service.files()
                    .export(fileId=file_id, mimeType="text/plain")
                    .execute()
                    .decode("utf-8")
                )
            elif mime_type == "application/pdf":
                raw = drive_service.files().get_media(fileId=file_id).execute()
                content = extract_text_from_pdf(raw)
            elif mime_type.endswith(".docx"):
                raw = drive_service.files().get_media(fileId=file_id).execute()
                content = extract_text_from_docx(raw)
            else:
                continue

            if content:
                return f"File: {name}\n\n{content[:4000]}"  # Truncate for token safety
        except Exception as e:
            print(f"Error processing file {name}: {e}")
            continue

    return "No relevant files found or couldn't extract content."
