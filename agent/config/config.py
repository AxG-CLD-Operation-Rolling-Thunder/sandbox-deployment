import json
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

LOG_IDENTIFIER = "PULSE_AGENT"
AUTHORIZATION_ID = os.getenv("AUTHORIZATION_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LOCAL_AUTH_CREDS = os.getenv("CLIENT_JSON_PAYLOAD", "{}")
TEMPLATE_BUCKET = os.getenv("TEMPLATE_BUCKET_PATH")
LOCAL_AUTH_CREDS_LOADED = json.loads(LOCAL_AUTH_CREDS)
DISCOVERY_ENGINE_URL = ""
API_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/cloud-platform"
]
TELEMETRY_ENABLED = os.getenv("TELEMETRY_ENABLED", "false").lower() == "true"
