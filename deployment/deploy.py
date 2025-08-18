# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import logging
from dotenv import set_key

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from invoice_agent.agent import root_agent


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET", "gs://csplanner_aiexchange")
logging.info("staging_bucket", STAGING_BUCKET)
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

vertexai.init(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    staging_bucket=STAGING_BUCKET,
)

def create_deployment_config() -> dict:
    logger.debug("Creating deployment configuration")
    config = {
        "requirements": [
            "google-cloud-aiplatform",
            "google-adk",
            "python-dotenv",
            "google-auth",
            "google-cloud-discoveryengine>=0.11.0",
            "requests",
            "google-auth-oauthlib",
            "google-api-python-client",
            "absl-py",
            "pydantic"
        ],
        "extra_packages": [
            "../invoice_agent",
        ],
    }
    logger.debug(f"Deployment config created with {len(config['env_vars'])} env vars")
    return config

def update_env_file(agent_engine_id, env_file_path):
    """Updates the .env file with the agent engine ID."""
    try:
        set_key(env_file_path, "AGENT_ENGINE_ID", agent_engine_id)
        logger.info(f"Updated AGENT_ENGINE_ID in {env_file_path} to {agent_engine_id}")
    except Exception as e:
        logger.error(f"Error updating .env file: {e}")

logger.info("deploying app...")
app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

logging.debug("deploying agent to agent engine:")

remote_app = agent_engines.create(
    app,
    requirements=[
        "google-cloud-aiplatform[adk,agent-engines]>=1.88.0",
        "google-adk",
        "google-generativeai",
        "google-ai-generativelanguage",
        "python-dotenv",
        "google-auth",
        "tqdm",
        "requests",
        "llama-index",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
        "absl-py",
        "pydantic"
    ],
    extra_packages=[
        "../invoice_agent",
    ],
)

logging.info(f"Deployed agent to Vertex AI Agent Engine successfully, resource name: {remote_app.resource_name}")

update_env_file(remote_app.resource_name, ENV_FILE_PATH)
