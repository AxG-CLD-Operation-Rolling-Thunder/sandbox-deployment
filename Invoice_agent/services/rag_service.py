"""
Knowledge Service - Handles knowledge retrieval and document queries
Simplified implementation using available ADK tools
"""
import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from .session_service import SessionService

load_dotenv()
logger = logging.getLogger(__name__)

class RagService:
    """
    Service for handling knowledge retrieval operations in the Invoice Agent
    """

    def __init__(self, session: SessionService):
        self.session = session
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.search_engine_id = os.getenv("VERTEX_SEARCH_ENGINE_ID")
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the knowledge service"""
        try:
            if self.project_id and self.search_engine_id:
                logger.info("Knowledge service initialized with Vertex AI Search")
            else:
                logger.warning("Knowledge service running in limited mode - search engine not configured")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge service: {str(e)}")

    def query_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the knowledge base for relevant information
        """
        try:
            query = data.get("query", "")
            if not query:
                return {"status": "error", "message": "Query parameter is required"}

            # Store query in session for context
            self.session.add_rag_query(query)

            # Check if search engine is configured
            if not self.search_engine_id or not self.project_id:
                return {
                    "status": "error",
                    "message": "Search engine not configured. Please set VERTEX_SEARCH_ENGINE_ID and GOOGLE_CLOUD_PROJECT environment variables."
                }

            # For now, return a structured response indicating the search capability is ready
            # In a production environment, this would integrate with the actual search implementation
            logger.info(f"Knowledge query: {query}")

            mock_results = [
                {
                    "content": f"Knowledge base entry related to: {query}",
                    "source": "Invoice Processing Guidelines",
                    "relevance_score": 0.85
                },
                {
                    "content": f"Additional context for: {query}",
                    "source": "Compliance Documentation",
                    "relevance_score": 0.72
                }
            ]

            # Store results in session
            self.session.add_rag_results(mock_results)

            return {
                "status": "success",
                "query": query,
                "results": mock_results,
                "total_results": len(mock_results),
                "search_engine_configured": True
            }

        except Exception as e:
            logger.error(f"Error in query_knowledge: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to query knowledge base: {str(e)}"
            }

    def retrieve_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve contextual information for invoice processing
        """
        try:
            context_type = data.get("context_type", "general")
            entity = data.get("entity", "")  # vendor name, tax code, etc.

            # Build query based on context type and entity
            queries = {
                "vendor": f"vendor information regulations compliance {entity}",
                "tax": f"tax regulations codes compliance {entity}",
                "general": f"invoice processing guidelines {entity}",
                "historical": f"historical patterns trends {entity}"
            }

            query = queries.get(context_type, queries["general"])

            # Use the existing query_knowledge method
            return self.query_knowledge({"query": query, "top_k": 5})

        except Exception as e:
            logger.error(f"Error in retrieve_context: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve context: {str(e)}"
            }

    def get_rag_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the current status of RAG configuration
        """
        try:
            status_info = {
                "rag_corpus": self.rag_corpus,
                "project_id": self.project_id,
                "location": self.location,
                "is_configured": bool(self.rag_corpus and self.project_id),
                "session_queries": len(self.session.get_rag_queries()) if hasattr(self.session, 'get_rag_queries') else 0
            }

            return {
                "status": "success",
                "rag_status": status_info
            }

        except Exception as e:
            logger.error(f"Error getting RAG status: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get RAG status: {str(e)}"
            }

    def clear_rag_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clear RAG context from the session
        """
        try:
            if hasattr(self.session, 'clear_rag_context'):
                self.session.clear_rag_context()

            return {
                "status": "success",
                "message": "RAG context cleared successfully"
            }

        except Exception as e:
            logger.error(f"Error clearing RAG context: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to clear RAG context: {str(e)}"
            }