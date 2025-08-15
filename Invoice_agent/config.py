import json, os
from dotenv import load_dotenv
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound

load_dotenv()

IS_LOCAL = os.getenv("IS_LOCAL", "False").lower() in ["true", "1", "yes"]
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", None)

if not GOOGLE_PROJECT_ID:
    raise RuntimeError("GOOGLE_CLOUD_PROJECT environment variable is not set.")
    
def get_secret_or_env(secret_id, env_var=None, fallback=None):
    env_var = env_var or secret_id 
    print("env_var", env_var)

    if IS_LOCAL:
        return os.getenv(env_var, fallback)
    
    # return get_secret(secret_id)

raw_oauth = get_secret_or_env("SLIDES_OAUTH_CREDENTIALS")
print("raw_oauth", raw_oauth)
if not raw_oauth:
    raise RuntimeError("OAUTH_CREDENTIALS not set.")
OAUTH_CREDENTIALS = json.loads(raw_oauth)
GOOGLE_API_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.compose"
]