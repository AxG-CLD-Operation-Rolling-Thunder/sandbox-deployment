# from oauth2client.service_account import ServiceAccountCredentials  # For service account OAuth credentials
# from googleapiclient.discovery import build  # To build the Google Docs API client

# def create_agent_brief_doc(agent_name, brief_content):
#     docs_service = get_docs_service()

#     # Create new doc
#     doc = docs_service.documents().create(body={
#         'title': f"Agent Brief - {agent_name}"
#     }).execute()
#     doc_id = doc.get('documentId')

#     # Insert text into the new doc
#     requests = [
#         {
#             'insertText': {
#                 'location': {'index': 1},
#                 'text': brief_content
#             }
#         }
#     ]

#     docs_service.documents().batchUpdate(
#         documentId=doc_id,
#         body={'requests': requests}
#     ).execute()

#     # Return the accessible link
#     return f"https://docs.google.com/document/d/{doc_id}/edit"



# import io
# from docx import Document
# from docx.text.paragraph import Paragraph
# from docx.shared import Pt
# from google.cloud import storage
# from pydantic import BaseModel, Field
# from typing import Dict # for brief_creator.py

# # ------------------ AgentBrief Model ------------------
# class AgentBrief(BaseModel):
#     agent_overview: str = Field(..., description="High-level summary of the agent")
#     vision: str = Field(..., description="Long-term goal or aspiration")
#     problem_statement: str = Field(..., description="What problem this agent solves")
#     target_users: str = Field(..., description="Who will use this agent")
#     key_features: str = Field(..., description="Core capabilities")
#     success_metrics: str = Field(..., description="How success will be measured")
#     dependencies_or_constraints: str = Field(..., description="Any blockers or requirements")

# # ------------------ GCS Template Loader ------------------
# def get_template_from_gcs(bucket_name: str) -> io.BytesIO:
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob("Agent Brief.docx")  # https://console.cloud.google.com/storage/browser/_details/ponette-bucket/Agent%20Brief.docx;tab=live_object?hl=en&project=oxjytxr-mss-mkt-genai-accel
#     return io.BytesIO(blob.download_as_bytes())

# # ------------------ Placeholder Map Builder ------------------
# def build_agent_placeholder_map(agent: AgentBrief) -> Dict[str, str]:
#     return {
#         "AGENT_OVERVIEW": agent.agent_overview or "To Be Added",
#         "VISION": agent.vision or "To Be Added",
#         "PROBLEM_STATEMENT": agent.problem_statement or "To Be Added",
#         "TARGET_USERS": agent.target_users or "To Be Added",
#         "KEY_FEATURES": agent.key_features or "To Be Added",
#         "SUCCESS_METRICS": agent.success_metrics or "To Be Added",
#         "DEPENDENCIES_OR_CONSTRAINTS": agent.dependencies_or_constraints or "To Be Added",
#     }

# # ------------------ Paragraph Utilities ------------------
# def _all_paragraphs(doc: Document):
#     for p in doc.paragraphs:
#         yield p
#     for t in doc.tables:
#         for r in t.rows:
#             for c in r.cells:
#                 for p in c.paragraphs:
#                     yield p

# def _clear_runs_and_set(p: Paragraph, text: str):
#     if p.runs:
#         for r in p.runs:
#             r.text = ""
#         p.runs[0].text = text
#     else:
#         p.add_run(text)

# # ------------------ Replace Placeholders ------------------
# def replace_in_document(doc: Document, data: Dict[str, str]) -> None:
#     for p in _all_paragraphs(doc):
#         full = "".join(r.text for r in p.runs)
#         if not full:
#             continue
#         changed = False
#         for token, val in data.items():
#             placeholder = f"{{{token}}}"
#             if placeholder in full:
#                 full = full.replace(placeholder, val)
#                 changed = True
#         if changed:
#             _clear_runs_and_set(p, full)

# # ------------------ Main Export Function ------------------
# def create_agent_brief_doc(agent: AgentBrief) -> io.BytesIO:
#     doc = Document(get_template_from_gcs("ponette-bucket"))  
#     placeholder_map = build_agent_placeholder_map(agent)
#     replace_in_document(doc, placeholder_map)
#     out = io.BytesIO()
#     doc.save(out)
#     out.seek(0)
#     return out
