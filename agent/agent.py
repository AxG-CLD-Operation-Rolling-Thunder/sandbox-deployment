import os
import logging
from google.adk.agents import LlmAgent  # Changed from Agent to LlmAgent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from google.adk.tools import agent_tool, ToolContext
from vertexai.preview import rag
from dotenv import load_dotenv
from .prompts import prompts
from .tools.file_upload_support import list_artifacts
from .tools.document_upload_tool import upload_to_google_docs_tool

load_dotenv()
logger = logging.getLogger(__name__)

# Original RAG retrieval tool
vertexai_retrieval = VertexAiRagRetrieval(
    name='retrieve_rag_documents',
    description=(
        'Use this tool to assist with your Google performance and development process.'
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus=os.environ.get("RAG_CORPUS")
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

# ALWAYS include document tools - they're smart enough to handle no-upload cases
# Source note: Converting from Agent to LlmAgent following EBC pattern
root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='grad_agent',
    description='GTM Priority Play Navigator with automatic document grounding',
    instruction=prompts.GRAD_AGENT_SYSTEM_PROMPT,
    tools=[
        vertexai_retrieval,
        list_artifacts,  # Always available - returns empty if no uploads
        upload_to_google_docs_tool,  # Always available for generating shareable docs
    ],
)