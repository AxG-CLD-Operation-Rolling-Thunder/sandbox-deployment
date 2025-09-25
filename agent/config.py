import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env once for the application
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)

# Helper to read booleans consistently
def _bool_env(name: str, default: str = "0") -> bool:
    val = os.getenv(name, default)
    return str(val).lower() in ("1", "true", "yes", "on")

# Basic settings (add more as repo needs them)
GOOGLE_GENAI_MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.5-flash")
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_PROJECT_NUMBER = os.getenv("GOOGLE_PROJECT_NUMBER", "")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
AS_APP = os.getenv("AS_APP", "")
AUTHORIZATION_NAME = os.getenv("AUTHORIZATION_NAME", "invoice-expense-auth-2")

# Flags
LOCAL_DEV = _bool_env("LOCAL_DEV", "0")
ADK_DEV_MODE = _bool_env("ADK_DEV_MODE", "0")
ADK_LOCAL_RUN = _bool_env("ADK_LOCAL_RUN", "0")
AGENTSPACE_DEPLOYMENT = _bool_env("AGENTSPACE_DEPLOYMENT", "0")

# Deployment / staging
STAGING_BUCKET = os.getenv("STAGING_BUCKET", "gs://csplanner_aiexchange")

# OAuth specific defaults and helpers (moved from oauth/config.py)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://mail.google.com/",
]

OAUTH_CONFIG = {
    "client_id": GOOGLE_OAUTH_CLIENT_ID,
    "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
    "project_id": GOOGLE_CLOUD_PROJECT,
    "project_number": GOOGLE_PROJECT_NUMBER,
    "location": GOOGLE_CLOUD_LOCATION,
    "engine_name": AS_APP,
}

AUTHORIZATION_ID = AUTHORIZATION_NAME

def validate_oauth_config():
    """Validate that all required OAuth configuration is present"""
    if not OAUTH_CONFIG["client_id"] or not OAUTH_CONFIG["client_secret"]:
        raise ValueError("GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET must be set")
    if not OAUTH_CONFIG["project_id"]:
        raise ValueError("GOOGLE_CLOUD_PROJECT must be set")
    return True

def is_local_environment():
    """Centralized environment detection"""
    if LOCAL_DEV:
        return True
    if ADK_DEV_MODE:
        return True
    if ADK_LOCAL_RUN:
        return True
    # Rely on AS_APP / project presence for cloud detection
    cloud_indicators = [GOOGLE_CLOUD_PROJECT, AS_APP]
    return not any(cloud_indicators)

# Expose a single centralized 'settings' dict (optional convenience)
settings = {
    "GOOGLE_GENAI_MODEL": GOOGLE_GENAI_MODEL,
    "GOOGLE_OAUTH_CLIENT_ID": GOOGLE_OAUTH_CLIENT_ID,
    "GOOGLE_OAUTH_CLIENT_SECRET": GOOGLE_OAUTH_CLIENT_SECRET,
    "GOOGLE_CLOUD_PROJECT": GOOGLE_CLOUD_PROJECT,
    "GOOGLE_PROJECT_NUMBER": GOOGLE_PROJECT_NUMBER,
    "GOOGLE_CLOUD_LOCATION": GOOGLE_CLOUD_LOCATION,
    "AS_APP": AS_APP,
    "AUTHORIZATION_NAME": AUTHORIZATION_NAME,
    "LOCAL_DEV": LOCAL_DEV,
    "ADK_DEV_MODE": ADK_DEV_MODE,
    "ADK_LOCAL_RUN": ADK_LOCAL_RUN,
    "AGENTSPACE_DEPLOYMENT": AGENTSPACE_DEPLOYMENT,
    "STAGING_BUCKET": STAGING_BUCKET,
}
