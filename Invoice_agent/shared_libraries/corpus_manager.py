"""
Corpus Manager - Manages RAG corpus for Invoice Agent
Based on GTM-Priority-Play prepare_corpus.py implementation
Optional component for organizations that want to manage their own knowledge base
"""
import os
import logging
from google.auth import default
try:
    # Try the newer import path first (google-cloud-aiplatform >= 1.95.0)
    from google.cloud.aiplatform.preview import rag
except ImportError:
    # Fallback to older vertexai import
    try:
        import vertexai
        from vertexai.preview import rag
    except ImportError:
        rag = None
from dotenv import load_dotenv, set_key
from typing import Optional, List

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
CORPUS_DISPLAY_NAME = "invoice_agent_knowledge_base"
CORPUS_DESCRIPTION = "Knowledge base containing invoice processing guidelines, vendor information, tax regulations, and compliance rules"
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

class InvoiceCorpusManager:
    """
    Manages the RAG corpus for Invoice Agent knowledge base
    """

    def __init__(self):
        self.project_id = PROJECT_ID
        self.location = LOCATION
        self.corpus_display_name = CORPUS_DISPLAY_NAME
        self.corpus_description = CORPUS_DESCRIPTION
        self._initialize_vertex_ai()

    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with proper credentials"""
        if not rag:
            raise ValueError("RAG module not available - check your google-cloud-aiplatform installation")

        if not self.project_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
            )
        if not self.location:
            raise ValueError(
                "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
            )

        try:
            credentials, _ = default()
            # For google-cloud-aiplatform >= 1.95.0, initialization is handled automatically
            # But we can still initialize vertexai if using the fallback path
            if 'vertexai' in globals():
                vertexai.init(
                    project=self.project_id,
                    location=self.location,
                    credentials=credentials
                )
            logger.info("Vertex AI/RAG initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            raise

    def create_or_get_corpus(self) -> rag.Corpus:
        """Creates a new corpus or retrieves an existing one."""
        embedding_model_config = rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-004"
        )

        # Check for existing corpus
        existing_corpora = rag.list_corpora()
        corpus = None

        for existing_corpus in existing_corpora:
            if existing_corpus.display_name == self.corpus_display_name:
                corpus = existing_corpus
                logger.info(f"Found existing corpus: {self.corpus_display_name}")
                break

        if corpus is None:
            corpus = rag.create_corpus(
                display_name=self.corpus_display_name,
                description=self.corpus_description,
                embedding_model_config=embedding_model_config,
            )
            logger.info(f"Created new corpus: {self.corpus_display_name}")

        return corpus

    def upload_document_to_corpus(
        self,
        corpus_name: str,
        document_path: str,
        display_name: str,
        description: str
    ) -> Optional[rag.File]:
        """Uploads a document to the specified corpus."""
        logger.info(f"Uploading {display_name} to corpus...")

        try:
            rag_file = rag.upload_file(
                corpus_name=corpus_name,
                path=document_path,
                display_name=display_name,
                description=description,
            )
            logger.info(f"Successfully uploaded {display_name}")
            return rag_file

        except Exception as e:
            logger.error(f"Error uploading {display_name}: {str(e)}")
            return None

    def upload_text_to_corpus(
        self,
        corpus_name: str,
        text_content: str,
        display_name: str,
        description: str
    ) -> Optional[rag.File]:
        """Uploads text content directly to the corpus."""
        logger.info(f"Uploading text content: {display_name}")

        try:
            # Create temporary file for text content
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
                tmp_file.write(text_content)
                tmp_file_path = tmp_file.name

            # Upload the temporary file
            rag_file = self.upload_document_to_corpus(
                corpus_name=corpus_name,
                document_path=tmp_file_path,
                display_name=display_name,
                description=description
            )

            # Clean up temporary file
            os.unlink(tmp_file_path)
            return rag_file

        except Exception as e:
            logger.error(f"Error uploading text content {display_name}: {str(e)}")
            return None

    def list_corpus_files(self, corpus_name: str) -> List[rag.File]:
        """Lists files in the specified corpus."""
        try:
            files = list(rag.list_files(corpus_name=corpus_name))
            logger.info(f"Total files in corpus: {len(files)}")

            for file in files:
                logger.info(f"File: {file.display_name} - {file.name}")

            return files

        except Exception as e:
            logger.error(f"Error listing corpus files: {str(e)}")
            return []

    def update_env_file(self, corpus_name: str, env_file_path: str = None) -> bool:
        """Updates the .env file with the corpus name."""
        if env_file_path is None:
            env_file_path = ENV_FILE_PATH

        try:
            set_key(env_file_path, "RAG_CORPUS", corpus_name)
            logger.info(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
            return True

        except Exception as e:
            logger.error(f"Error updating .env file: {str(e)}")
            return False

    def delete_file_from_corpus(self, file_name: str) -> bool:
        """Deletes a file from the corpus."""
        try:
            rag.delete_file(name=file_name)
            logger.info(f"Deleted file: {file_name}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file {file_name}: {str(e)}")
            return False

    def setup_default_knowledge_base(self) -> str:
        """
        Sets up a default knowledge base with sample invoice processing guidelines.
        Returns the corpus name.
        """
        logger.info("Setting up default knowledge base...")

        # Create or get corpus
        corpus = self.create_or_get_corpus()

        # Sample knowledge content for invoice processing
        default_knowledge = {
            "invoice_processing_guidelines": {
                "content": """
                Invoice Processing Guidelines:
                1. Always verify vendor information against approved vendor lists
                2. Check tax calculations for accuracy based on applicable rates
                3. Ensure all required fields are present: date, amount, tax, vendor info
                4. Flag invoices over $10,000 for additional review
                5. Verify PO numbers when present
                6. Check for duplicate invoices based on vendor and amount
                7. Ensure proper GL coding for different expense categories
                """,
                "description": "General guidelines for invoice processing and validation"
            },
            "tax_compliance_rules": {
                "content": """
                Tax Compliance Rules:
                1. US invoices: Check for valid state tax rates
                2. International invoices: Verify VAT rates and formats
                3. Tax-exempt transactions: Require proper exemption certificates
                4. Service vs. goods: Different tax treatment may apply
                5. Multi-jurisdiction: Calculate composite tax rates correctly
                6. Documentation: Maintain proper tax records for audits
                """,
                "description": "Tax compliance and validation rules for invoice processing"
            },
            "vendor_validation_criteria": {
                "content": """
                Vendor Validation Criteria:
                1. Verify vendor is in approved vendor master list
                2. Check vendor tax ID and registration status
                3. Validate business address and contact information
                4. Confirm banking details for payment processing
                5. Review vendor risk profile and compliance status
                6. Check for any vendor restrictions or special terms
                """,
                "description": "Criteria for validating vendor information on invoices"
            }
        }

        # Upload default knowledge
        for knowledge_type, data in default_knowledge.items():
            self.upload_text_to_corpus(
                corpus_name=corpus.name,
                text_content=data["content"],
                display_name=knowledge_type,
                description=data["description"]
            )

        # Update environment variable
        self.update_env_file(corpus.name)

        logger.info(f"Default knowledge base setup complete. Corpus: {corpus.name}")
        return corpus.name


def main():
    """
    Main function to set up the corpus manager
    """
    try:
        manager = InvoiceCorpusManager()
        corpus_name = manager.setup_default_knowledge_base()

        print(f"✅ Invoice Agent knowledge base setup complete!")
        print(f"📄 Corpus name: {corpus_name}")
        print(f"🔧 Environment variable RAG_CORPUS updated")
        print(f"📚 Default knowledge base content uploaded")

        # List files in corpus
        files = manager.list_corpus_files(corpus_name)
        print(f"📊 Total files in knowledge base: {len(files)}")

    except Exception as e:
        logger.error(f"Failed to set up knowledge base: {str(e)}")
        print(f"❌ Error setting up knowledge base: {str(e)}")
        print("Please check your Google Cloud credentials and project configuration.")


if __name__ == "__main__":
    main()