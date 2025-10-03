# Plan on a Page Agent Deployment Guide

## Overview

This guide covers the complete deployment process for the Plan on a Page Agent, from local development to production deployment using Google Cloud's Agent Development Kit (ADK).

## Prerequisites

### Required Software
- **Python 3.8+** with pip
- **Google Cloud SDK** (gcloud CLI)
- **Git** for version control
- **Google ADK CLI** (`pip install google-adk`)

### Required Google Cloud APIs
Enable these APIs in your Google Cloud project:
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable discoveryengine.googleapis.com
gcloud services enable iamcredentials.googleapis.com
gcloud services enable oauth2.googleapis.com
```

### Required Permissions
Your Google Cloud account needs:
- **Vertex AI Administrator** role
- **Agent Builder Admin** role
- **IAM Admin** role (for OAuth setup)
- **Project Editor** role

## Local Development Setup

### 1. Repository Setup

```bash
# Clone the repository
git clone <repository-url>
cd sandbox-deployment

# Switch to the deployment branch
git checkout sa-ort-brand-voice-agent-deployment-branch

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

#### Create Local Environment File
```bash
cp agent/.env.example agent/.env
```

#### Configure Required Variables
Edit `agent/.env` with your project details:

```bash
# Google Cloud Configuration (Required)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_PROJECT_NUMBER=123456789012

# OAuth Configuration (Required)
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# API Keys (Required)
GOOGLE_API_KEY=your-api-key
GOOGLE_GENAI_API_KEY=your-genai-api-key
GOOGLE_GENAI_MODEL=gemini-2.5-flash

# AgentSpace Configuration (Required)
AS_APP=your-agentspace-app-id
AUTHORIZATION_NAME=plan_on_page_auth_001

# RAG Configuration (Optional - for enhanced planning knowledge)
RAG_CORPUS=projects/your-project/locations/us-central1/ragCorpora/plan-knowledge-corpus-id
# VERTEX_SEARCH_ENGINE_ID=your-search-engine-id  # Uncomment when RAG is set up

# Development Flags
LOCAL_DEV=1
ADK_DEV_MODE=false
ADK_LOCAL_RUN=false
AGENTSPACE_DEPLOYMENT=false
```

### 3. OAuth Setup

#### Create OAuth Credentials
1. Go to [Google Cloud Console > APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials > OAuth 2.0 Client IDs**
3. Select **Web application**
4. Add authorized redirect URIs:
   - `http://localhost:8000/oauth/callback`
   - `https://your-agent-domain.com/oauth/callback`
5. Copy Client ID and Client Secret to your `.env` file

#### Test OAuth Configuration
```bash
# Test OAuth flow
adk agent run --test-oauth
```

### 4. Local Testing

#### Start the Agent
```bash
# Start local development server
adk agent run

# Agent will be available at http://localhost:8000
```

#### Verify Agent Functionality
```bash
# Test agent import
python -c "from agent.agent import root_agent; print(f'Agent loaded with {len(root_agent.tools)} tools')"

# Expected output:
# Plan on a Page Agent initialized with 18 tools
```

#### Test Core Functions
1. Open http://localhost:8000 in your browser
2. Test creating a new Plan on a Page
3. Upload and analyze an existing plan draft
4. Test G/R/L assignment guidance

## RAG Setup (Optional)

### 1. Create Vertex AI Search Application

#### Using Google Cloud Console
1. Go to [Vertex AI Search](https://console.cloud.google.com/vertex-ai/search)
2. Click **Create App**
3. Select **Search** app type
4. Choose **Generic** as the content type
5. Name: `plan-on-page-knowledge-base`

#### Using gcloud CLI
```bash
gcloud alpha discovery-engine data-stores create \
    --display-name="Plan on a Page Knowledge Base" \
    --industry-vertical=GENERIC \
    --content-config=CONTENT_REQUIRED \
    --solution-type=SOLUTION_TYPE_SEARCH \
    --location=us-central1
```

### 2. Upload Planning Documents

#### Document Types to Include
- **Plan on a Page Template** (official template)
- **Example Plans** (successful completed plans)
- **G/R/L Framework Guide** (Global/Regional/Local best practices)
- **Adopt/Adapt/Invent Guidelines** (framework documentation)
- **Planning Best Practices** (tips and common patterns)

#### Upload via Console
1. In your search app, go to **Data > Data Stores**
2. Click **Import** and select **Cloud Storage** or **Direct Upload**
3. Upload your brand voice documents
4. Wait for indexing to complete (may take 1-2 hours)

### 3. Configure Search Engine

#### Get Search Engine ID
```bash
# List search engines
gcloud alpha discovery-engine search-engines list --location=us-central1

# Copy the search engine ID for your brand voice app
```

#### Update Environment Configuration
```bash
# Uncomment and configure in agent/.env
VERTEX_SEARCH_ENGINE_ID=your-search-engine-id
```

#### Test RAG Integration
```bash
# Restart agent to pick up RAG configuration
adk agent run

# Look for log message:
# INFO - Plan on a Page Agent initialized with 18 tools
```

## Production Deployment

### 1. Pre-deployment Checklist

#### Code Quality
- [ ] All tools have proper type annotations (`Optional[Type] = None`)
- [ ] All functions include docstrings
- [ ] Error handling is implemented
- [ ] Logging is configured appropriately

#### Configuration
- [ ] `agent.yaml` has unique names for reasoning engine and agent space
- [ ] OAuth authorization ID is unique
- [ ] Environment variables are properly set
- [ ] RAG corpus is configured (if using RAG)

#### Testing
- [ ] Agent loads without errors
- [ ] All tools function correctly
- [ ] OAuth flow works end-to-end
- [ ] Content generation produces quality output

### 2. Agent Configuration (agent.yaml)

Ensure your `agent.yaml` is properly configured:

```yaml
defaults:
  scopes:
    - https://www.googleapis.com/auth/cloud-platform
    - openid
    - https://www.googleapis.com/auth/userinfo.email
    - https://www.googleapis.com/auth/userinfo.profile
  metadata:
    reasoning_engine_name: ort_brand_voice_agent
    reasoning_engine_description: A reasoning engine for Google Cloud Brand Voice Agent that helps with content creation and brand voice analysis
    agent_space_name: Cloud Marketing Brand Voice Agent
    agent_space_description: An AI-powered writing assistant for Google Cloud marketers and content creators that helps brainstorm, draft, and refine blog content while ensuring alignment with Google Cloud brand voice guidelines.
    agent_space_tool_description: Use this tool to analyze existing content for brand voice compliance, generate new blog content drafts, and create compelling headlines for Google Cloud marketing content.
  auth:
    oauth_authorization_id: brand_voice_auth_001
  environment_variables:
    RAG_CORPUS: "projects/your-project/locations/us-central1/ragCorpora/brand-voice-corpus-id"
```

### 3. Secret Management

#### Using Google Cloud Secret Manager
```bash
# Create secrets for sensitive configuration
gcloud secrets create oauth-client-secret --data-file=- <<< "your-oauth-client-secret"
gcloud secrets create genai-api-key --data-file=- <<< "your-genai-api-key"

# Grant access to the agent service account
gcloud secrets add-iam-policy-binding oauth-client-secret \
    --member="serviceAccount:your-agent-service-account@project.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

#### Update Agent Code for Secrets
```python
from google.cloud import secretmanager

def get_secret(secret_name: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

### 4. Deployment Process

#### Push to Deployment Branch
```bash
# Ensure you're on the correct branch
git checkout sa-ort-brand-voice-agent-deployment-branch

# Add and commit your changes
git add agent/agent.py agent.yaml
git commit -m "Deploy Brand Voice Agent v1.0"

# Push to trigger deployment
git push origin sa-ort-brand-voice-agent-deployment-branch
```

#### Monitor Deployment
The deployment is handled automatically by the pipeline. Monitor progress:

```bash
# Check Cloud Build logs
gcloud builds list --filter="source.repoSource.branchName=sa-ort-brand-voice-agent-deployment-branch"

# Get detailed build information
gcloud builds describe BUILD_ID
```

### 5. Post-deployment Verification

#### Check Agent Status
```bash
# List reasoning engines
gcloud ai reasoning-engines list --location=us-central1

# Check agent space deployment
gcloud alpha agent-builder agent-spaces list --location=us-central1
```

#### Test Production Agent
1. Access the deployed agent through Agent Builder UI
2. Test all core functionalities:
   - Content review
   - Blog content generation
   - Headline creation
   - RAG search (if configured)
3. Verify OAuth authentication works
4. Check performance and response times

## Monitoring & Maintenance

### 1. Logging and Monitoring

#### View Agent Logs
```bash
# View reasoning engine logs
gcloud logging read "resource.type=vertex_ai_reasoning_engine AND resource.labels.reasoning_engine_id=your-engine-id"

# View agent space logs
gcloud logging read "resource.type=agent_builder_agent_space"
```

#### Set Up Monitoring
```yaml
# monitoring.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: brand-voice-agent-monitor
spec:
  selector:
    matchLabels:
      app: brand-voice-agent
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### 2. Performance Monitoring

#### Key Metrics to Track
- **Response Time**: Average time for tool execution
- **Error Rate**: Percentage of failed requests
- **Token Usage**: LLM token consumption
- **User Adoption**: Number of active users
- **Quality Scores**: User feedback on output quality

#### Alerting Setup
```bash
# Create alerting policy for high error rates
gcloud alpha monitoring policies create \
    --policy-from-file=alerting-policy.yaml
```

### 3. Regular Maintenance Tasks

#### Weekly Tasks
- [ ] Review error logs for issues
- [ ] Check performance metrics
- [ ] Update RAG knowledge base if needed
- [ ] Monitor token usage and costs

#### Monthly Tasks
- [ ] Review and update brand voice guidelines
- [ ] Analyze user feedback and usage patterns
- [ ] Update model to latest version if available
- [ ] Backup configuration and knowledge base

#### Quarterly Tasks
- [ ] Comprehensive security review
- [ ] Performance optimization analysis
- [ ] User satisfaction survey
- [ ] Technology stack updates

## Troubleshooting

### Common Deployment Issues

#### Authentication Errors
**Symptom**: OAuth flow fails
**Solution**:
1. Verify OAuth client ID and secret
2. Check redirect URIs are correctly configured
3. Ensure scopes match agent.yaml requirements

#### Agent Won't Load
**Symptom**: "Default value None of parameter ... is not compatible"
**Solution**:
1. Check all function parameters use `Optional[Type] = None`
2. Verify imports include `Optional` from typing
3. Review function signatures for type consistency

#### RAG Not Working
**Symptom**: "VERTEX_SEARCH_ENGINE_ID environment variable not set"
**Solution**:
1. Verify search engine is created and indexed
2. Check environment variable is set correctly
3. Ensure service account has Discovery Engine permissions

#### Naming Conflicts
**Symptom**: "reasoning_engine_name already exists"
**Solution**:
1. Use unique names in agent.yaml
2. Delete old deployments if needed
3. Consider versioning in names (e.g., brand-voice-v2)

### Performance Issues

#### Slow Response Times
**Causes & Solutions**:
- **Large prompts**: Optimize prompt length and structure
- **RAG performance**: Review search query optimization
- **Model selection**: Consider faster model variants

#### High Token Usage
**Optimization Strategies**:
- Shorten system prompts
- Use more specific instructions
- Implement response caching
- Optimize RAG result processing

### Recovery Procedures

#### Rollback Deployment
```bash
# Revert to previous commit
git revert HEAD
git push origin sa-ort-brand-voice-agent-deployment-branch
```

#### Emergency Disable
```bash
# Disable reasoning engine
gcloud ai reasoning-engines update REASONING_ENGINE_ID \
    --location=us-central1 \
    --disable
```

#### Restore from Backup
```bash
# Restore configuration
git checkout previous-working-commit -- agent/
git commit -m "Restore working configuration"
git push origin sa-ort-brand-voice-agent-deployment-branch
```

## Security Considerations

### Data Protection
- **No sensitive data** should be logged or stored
- **User inputs** are processed but not persisted
- **OAuth tokens** are handled securely by ADK
- **API keys** should be stored in Secret Manager

### Access Control
- Use **least privilege** principle for service accounts
- **Regular audit** of IAM permissions
- **Rotate secrets** periodically
- **Monitor access** logs for unusual activity

### Compliance
- Ensure **data residency** requirements are met
- Follow **Google Cloud security** best practices
- Implement **audit logging** for compliance
- **Document security** measures and procedures

---

## Support and Resources

### Documentation
- [Google ADK Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder)
- [Vertex AI Search Documentation](https://cloud.google.com/vertex-ai-search/docs)
- [Agent Builder Best Practices](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder/best-practices)

### Getting Help
1. Check this deployment guide and troubleshooting section
2. Review agent logs for specific error details
3. Consult ADK documentation for tool-specific issues
4. Contact the development team for custom issues

### Emergency Contacts
- **Development Team**: [Internal contact information]
- **Google Cloud Support**: Use your support case system
- **On-call Engineer**: [Emergency contact information]

---

**This deployment guide provides comprehensive instructions for successfully deploying and maintaining the Google Cloud Brand Voice Agent in production environments.**