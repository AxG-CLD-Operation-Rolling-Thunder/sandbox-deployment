import os
import logging
import sys
import json
import subprocess
import vertexai
from absl import app, flags
from dotenv import load_dotenv, set_key
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from invoice_agent.agent import root_agent
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP Cloud Storage bucket for staging.")
flags.DEFINE_string("resource_id", None, "Agent Engine resource ID for update/delete.")
flags.DEFINE_string("engine_name", None, "Agent Space engine name.")
flags.DEFINE_bool("create", False, "Creates a new agent.")
flags.DEFINE_bool("update", False, "Updates an existing agent.")
flags.DEFINE_bool("delete", False, "Deletes an existing agent.")
flags.DEFINE_bool("list", False, "Lists all deployed agents.")
flags.DEFINE_bool("with_agentspace", False, "Deploy to Agent Space after creation.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "update", "delete", "list"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_authorization(project_number: str, auth_name: str, oauth_client_id: str, oauth_client_secret: str) -> tuple:
    """Ensure OAuth authorization exists in Discovery Engine"""
    logger.info(f"Ensuring authorization '{auth_name}' exists")
    
    # Check if authorization already exists
    headers_cmd = [
        "curl", "-X", "GET",
        "-H", f"Authorization: Bearer $(gcloud auth print-access-token)",
        "-H", "Content-Type: application/json",
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/authorizations/{auth_name}"
    ]
    
    result = subprocess.run(" ".join(headers_cmd), shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        logger.info(f"Authorization '{auth_name}' already exists")
        return (True, "exists")
    
    logger.info(f"Creating authorization '{auth_name}'")
    
    # Create authorization with Gmail scopes
    payload = {
        "name": f"projects/{project_number}/locations/global/authorizations/{auth_name}",
        "serverSideOauth2": {
            "clientId": oauth_client_id,
            "clientSecret": oauth_client_secret,
            "authorizationUri": (
                "https://accounts.google.com/o/oauth2/auth"
                "?response_type=code"
                f"&client_id={oauth_client_id}"
                "&scope=openid"
                "%20https://www.googleapis.com/auth/userinfo.email"
                "%20https://www.googleapis.com/auth/gmail.compose"  # For creating drafts
                "%20https://www.googleapis.com/auth/gmail.send"     # For sending emails
                "&access_type=offline&prompt=consent"
            ),
            "tokenUri": "https://oauth2.googleapis.com/token"
        }
    }
    
    with open("/tmp/auth_payload.json", "w") as f:
        json.dump(payload, f)
    
    create_cmd = [
        "curl", "-X", "POST",
        "-H", f"Authorization: Bearer $(gcloud auth print-access-token)",
        "-H", "Content-Type: application/json",
        "-H", f"X-Goog-User-Project: {project_number}",
        "-d", f"@/tmp/auth_payload.json",
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/authorizations?authorizationId={auth_name}"
    ]
    
    result = subprocess.run(" ".join(create_cmd), shell=True, capture_output=True, text=True)
    
    if result.returncode == 0 or "already exists" in result.stderr:
        logger.info(f"Authorization '{auth_name}' ready")
        return (True, "created")
    else:
        logger.error(f"Failed to create authorization: {result.stderr}")
        return (False, result.stderr)

def deploy_to_agentspace(resource_name: str, project_number: str, engine_name: str, auth_name: str) -> tuple:
    """Deploy the agent to Agent Space with OAuth authorization"""
    logger.info(f"Deploying to Agent Space with authorization '{auth_name}'")
    
    payload = {
        "displayName": "Invoice Expense Report Agent",
        "description": "AI-powered assistant for processing invoices and creating expense reports",
        "adk_agent_definition": {
            "tool_settings": {
                "tool_description": "Process invoices and create Gmail expense report drafts"
            },
            "provisioned_reasoning_engine": {
                "reasoning_engine": resource_name
            },
            "authorizations": [
                f"projects/{project_number}/locations/global/authorizations/{auth_name}"
            ]
        }
    }
    
    with open("/tmp/deploy_payload.json", "w") as f:
        json.dump(payload, f)
    
    deploy_cmd = [
        "curl", "-X", "POST",
        "-H", f"Authorization: Bearer $(gcloud auth print-access-token)",
        "-H", "Content-Type: application/json",
        "-H", f"X-Goog-User-Project: {project_number}",
        "-d", f"@/tmp/deploy_payload.json",
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/engines/{engine_name}/assistants/default_assistant/agents"
    ]
    
    result = subprocess.run(" ".join(deploy_cmd), shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        agent_id = response.get("name", "").split("/")[-1]
        logger.info(f"Deployed to Agent Space with ID: {agent_id}")
        
        # Save the agent ID to .env
        env_path = Path(__file__).resolve().parent.parent.parent / '.env'
        set_key(env_path, "INVOICE_AGENTSPACE_AGENT_ID", agent_id)
        
        return (True, agent_id)
    else:
        logger.error(f"Failed to deploy to Agent Space: {result.stderr}")
        return (False, result.stderr)

def get_adk_app_with_requirements():
    """Get ADK app with all required dependencies"""
    adk_app = AdkApp(agent=root_agent, enable_tracing=True)
    requirements = [
        "google-adk>=1.0.0", 
        "google-cloud-aiplatform[adk,agent-engines]>=1.93.0",
        "google-genai>=1.5.0",
        "google-auth>=2.23.0",
        "google-auth-oauthlib>=1.2.0",
        "google-api-python-client>=2.100.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0"
    ]
    return adk_app, requirements

def create_agent() -> None:
    """Create and optionally deploy agent to Agent Space"""
    logger.info("Starting agent creation with OAuth integration")
    
    adk_app, requirements = get_adk_app_with_requirements()

    remote_agent = agent_engines.create(
        adk_app,
        display_name=root_agent.name,
        description="AI-powered assistant for processing invoices and creating expense reports",
        requirements=requirements,
        extra_packages=["./invoice_agent"],
    )

    logger.info(f"Agent created: {remote_agent.resource_name}")
    
    # Save to .env
    env_path = Path(__file__).resolve().parent.parent / '.env'
    set_key(env_path, "INVOICE_AGENT_ENGINE_ID", remote_agent.resource_name)
    
    if FLAGS.with_agentspace:
        project_number = os.getenv("GOOGLE_PROJECT_NUMBER")
        engine_name = os.getenv("AS_APP")
        auth_name = os.getenv("INVOICE_AUTHORIZATION_NAME", "invoice-agent-auth")
        oauth_client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
        oauth_client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
        
        if not all([project_number, engine_name, oauth_client_id, oauth_client_secret]):
            logger.error("Missing required environment variables for Agent Space deployment")
            logger.error("Required: GOOGLE_PROJECT_NUMBER, AS_APP, GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET")
            return
        
        # Ensure OAuth authorization exists with correct scopes
        auth_success, auth_msg = ensure_authorization(
            project_number, auth_name, oauth_client_id, oauth_client_secret
        )
        
        if auth_success:
            # Deploy to Agentspace with authorization
            deploy_success, deploy_msg = deploy_to_agentspace(
                remote_agent.resource_name, project_number, engine_name, auth_name
            )
            
            if deploy_success:
                print("\n" + "="*60)
                print("✅ Invoice Agent Successfully Deployed to Agent Space!")
                print(f"   Resource Name: {remote_agent.resource_name}")
                print(f"   Agent Space ID: {deploy_msg}")
                print(f"   Authorization: {auth_name}")
                print("="*60)
                print("\n🎉 Your agent is ready in Agent Space!")
                print("   Users will be prompted for OAuth consent on first use.")
                print("\n⚠️  IMPORTANT: Make sure INVOICE_AUTHORIZATION_NAME in .env matches exactly!")
            else:
                logger.error(f"Agent Space deployment failed: {deploy_msg}")
        else:
            logger.error(f"Authorization creation failed: {auth_msg}")
    else:
        print("\n" + "="*60)
        print("✅ Agent Created Successfully!")
        print(f"   Resource Name: {remote_agent.resource_name}")
        print("="*60)
        print("\n💡 To deploy to Agent Space, run with --with_agentspace flag")

def update_agent(resource_id: str) -> None:
    """Update existing agent"""
    logger.info(f"Starting agent update process for: {resource_id}")
    adk_app, requirements = get_adk_app_with_requirements()

    try:
        existing_agent = agent_engines.get(resource_id)
        display_name = existing_agent.display_name
        description = getattr(existing_agent, 'description', 'AI-powered assistant for processing invoices and creating expense reports')
        
        logger.info("Deleting existing agent for update...")
        existing_agent.delete(force=True)
        
        logger.info("Creating updated agent...")
        updated_agent = agent_engines.create(
            adk_app,
            display_name=display_name,
            description=description,
            requirements=requirements,
            extra_packages=["./invoice_agent"],
        )
        
        print("\n" + "="*60)
        print(f"✅ Agent updated successfully!")
        print(f"   New Resource ID: {updated_agent.resource_name}")
        print("="*60)
        
        # Update .env
        env_path = Path(__file__).resolve().parent.parent / '.env'
        set_key(env_path, "INVOICE_AGENT_ENGINE_ID", updated_agent.resource_name)
        
    except Exception as e:
        logger.error(f"Update failed: {str(e)}")

def delete_agent(resource_id: str) -> None:
    """Delete agent"""
    logger.info(f"Deleting agent: {resource_id}")
    agent_engines.get(resource_id).delete(force=True)
    print(f"✅ Agent deleted successfully: {resource_id}")

def list_agents() -> None:
    """List all deployed agents"""
    agents = agent_engines.list()
    if not agents:
        print("No agents found in this project and location.")
        return

    print("\nDeployed agents:")
    print("="*80)
    for agent in agents:
        print(f"Resource ID: {agent.resource_name}")
        print(f"Display Name: {agent.display_name}")
        if hasattr(agent, 'create_time'):
            print(f"Created: {agent.create_time}")
        print("-"*80)

def main(argv: list[str]) -> None:
    del argv
    load_dotenv()

    project_id = FLAGS.project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    location = FLAGS.location or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket = FLAGS.bucket or os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    if not all([project_id, location, bucket]):
        logger.error("Missing required environment variables")
        logger.error("Required: GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, GOOGLE_CLOUD_STORAGE_BUCKET")
        return

    if bucket.startswith("gs://"):
        bucket = bucket[5:]

    vertexai.init(
        project=project_id, location=location, staging_bucket=f"gs://{bucket}"
    )

    logger.info(f"Using Project: {project_id}, Location: {location}, Bucket: gs://{bucket}")

    if FLAGS.create:
        create_agent()
    elif FLAGS.update:
        if not FLAGS.resource_id:
            print("❌ --resource_id is required for update. Use --list to find it.")
            return
        update_agent(FLAGS.resource_id)
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("❌ --resource_id is required for delete.")
            return
        delete_agent(FLAGS.resource_id)
    elif FLAGS.list:
        list_agents()
    else:
        print("No action specified. Use --create, --update, --delete, or --list.")
        print("\nExample: python invoice_agent/deployment/deploy.py --create --with_agentspace")

if __name__ == "__main__":
    app.run(main)