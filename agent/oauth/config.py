import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)
logger.debug(f"Loading .env from: {env_path}")

AUTHORIZATION_ID = os.getenv("AUTHORIZATION_NAME", "invoice-expense-auth")
logger.info(f"Using authorization ID: {AUTHORIZATION_ID}")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://mail.google.com/",
]

OAUTH_CONFIG = {
    "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
    "project_number": os.getenv("GOOGLE_PROJECT_NUMBER", ""),
    "location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    "engine_name": os.getenv("AS_APP", ""),
}

def validate_oauth_config():
    """Validate that all required OAuth configuration is present"""
    logger.debug("Validating OAuth configuration")
    
    if not OAUTH_CONFIG["client_id"] or not OAUTH_CONFIG["client_secret"]:
        logger.error("Missing OAuth credentials")
        raise ValueError("GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET must be set")
    
    if not OAUTH_CONFIG["project_id"]:
        logger.error("Missing project ID")
        raise ValueError("GOOGLE_CLOUD_PROJECT must be set")
    
    logger.info("OAuth configuration validated successfully")
    logger.debug(f"Client ID: {OAUTH_CONFIG['client_id'][:10]}...")
    logger.debug(f"Project: {OAUTH_CONFIG['project_id']}")
    logger.debug(f"Location: {OAUTH_CONFIG['location']}")
    
    return True

def is_local_environment():
    """Check if running in local environment vs cloud"""
    if os.getenv('LOCAL_DEV', '0') == '1':
        return True
    
    if os.getenv('ADK_DEV_MODE', '').lower() == 'true':
        return True
    
    if os.getenv('ADK_LOCAL_RUN', '').lower() == 'true':
        return True
    
    cloud_indicators = [
        os.getenv('AGENTSPACE_ENV'),
        os.getenv('GAE_APPLICATION'),
        os.getenv('K_SERVICE'),
        os.getenv('CLOUD_RUN_JOB'),
        os.getenv('AGENTSPACE_DEPLOYMENT') == 'true',
        os.getenv('GOOGLE_CLOUD_PROJECT_NUMBER'),  # Often set in cloud
        os.getenv('AS_APP'),  # Agentspace app name
    ]
    
    return not any(cloud_indicators)

def get_api_key():
    """Get the Google API key for Gemini"""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY must be set for invoice processing")
    return api_key
