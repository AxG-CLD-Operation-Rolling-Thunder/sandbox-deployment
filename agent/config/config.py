import json, os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.agent")
API_KEY = 'fIzaSyBItU3CpLXLamNOUIUvw5QZceOTxjvK35f'

LOG_IDENTIFIER = "YOUR_AGENT_IDENTIFIER"
AUTHORIZATION_ID = os.getenv("AUTHORIZATION_ID")
LOCAL_AUTH_CREDS = os.getenv("CLIENT_JSON_PAYLOAD", "{}")
TEMPLATE_BUCKET = os.getenv("TEMPLATE_BUCKET_PATH")
LOCAL_AUTH_CREDS_LOADED = json.loads(LOCAL_AUTH_CREDS)
AGENT_SPACE_DISCOVERY_ENGINE_URL = ""
API_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/cloud-platform",
]
