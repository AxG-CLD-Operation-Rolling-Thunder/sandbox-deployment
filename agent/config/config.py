# Simplified configuration - no feature flags needed!
# Source note: Simplified from EBC pattern, removing unnecessary complexity

import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env")

# Logging configuration
LOG_IDENTIFIER = "GRAD_AGENT"

# OAuth configuration
# Source note: From EBC agent/config/config.py - same OAuth pattern
AUTHORIZATION_ID = os.getenv("GTM_AUTHORIZATION_ID", "gtm_priority_play_auth")
LOCAL_AUTH_CREDS = os.getenv("GTM_CLIENT_JSON_PAYLOAD", "{}")
LOCAL_AUTH_CREDS_LOADED = json.loads(LOCAL_AUTH_CREDS)

# API Scopes - matching EBC's pattern from agent.yaml
API_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]

# Upload constraints (sensible defaults, no config needed)
MAX_UPLOAD_SIZE_MB = 10
SUPPORTED_MIME_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'text/csv',
    'application/json',
]

# Telemetry configuration
TELEMETRY_ENABLED = os.getenv("TELEMETRY_ENABLED", "false").lower() == "true"

def get_oauth_config() -> Dict[str, Any]:
    """Get OAuth configuration for the agent."""
    return {
        "authorization_id": AUTHORIZATION_ID,
        "scopes": API_SCOPES,
        "local_creds": LOCAL_AUTH_CREDS_LOADED if os.getenv("LOCAL_DEV", "0") == "1" else None,
    }