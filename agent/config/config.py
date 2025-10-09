import json, os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.agent")

LOG_IDENTIFIER = os.getenv("LOG_IDENTIFIER", "WORK_WITH_ME_AGENT")
AUTHORIZATION_ID = os.getenv("AUTHORIZATION_ID", "work_with_me_auth_1")

_local_auth_str = os.getenv("CLIENT_JSON_PAYLOAD", "{}")
try:
    LOCAL_AUTH_CREDS_LOADED = json.loads(_local_auth_str) if _local_auth_str.strip() else {}
except json.JSONDecodeError:
    LOCAL_AUTH_CREDS_LOADED = {}

TEMPLATE_BUCKET = os.getenv("TEMPLATE_BUCKET_PATH", "")
AGENT_SPACE_DISCOVERY_ENGINE_URL = os.getenv("AGENT_SPACE_DISCOVERY_ENGINE_URL", "")

# new additions for agent
ENTERPRISE_MODE = os.getenv("ENTERPRISE_MODE", "false").lower() == "true"
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_LOCATION   = os.getenv("GCP_LOCATION", "us-central1")
AGENTSPACE_API_KEY = os.getenv("AGENTSPACE_API_KEY", "")
DATA_SOURCE = os.getenv("DATA_SOURCE", "mock")  # 'mock' or 'gmail'
MOCK_EMAILS_PATH = os.getenv("MOCK_EMAILS_PATH", "data/mock_sent_emails.json")


API_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/cloud-platform",
    # additions
    "https://www.googleapis.com/auth/gmail.readonly",
    # potential future
    # "https://www.googleapis.com/auth/documents.readonly",
    # "https://www.googleapis.com/auth/chat.messages.readonly",
]
