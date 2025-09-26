# Google Cloud Brand Voice Agent

An AI-powered writing assistant designed specifically for Google Cloud marketers and content creators. This agent helps brainstorm, draft, and refine blog content while ensuring alignment with Google Cloud brand voice guidelines.

## 🎯 Overview

The Brand Voice Agent is built on Google's Agent Development Kit (ADK) and provides three core capabilities:

1. **Content Reviewer** (Priority 1) - Analyzes existing content for brand voice compliance
2. **Content Generator** (Priority 2) - Creates new blog content from topics and key points
3. **Headline Generator** (Priority 3) - Generates multiple compelling headline options

## 🚀 Features

### Core Functionality
- **Content Analysis**: Review existing text and get specific brand voice improvement suggestions
- **Content Creation**: Generate full blog drafts from topics, key points, and target audience
- **Headline Generation**: Create multiple headline variations optimized for SEO and engagement
- **Brand Compliance**: Automated checking against Google Cloud brand voice guidelines
- **Knowledge Integration**: RAG-powered search through brand voice documentation (when configured)

### Technical Features
- **OAuth Integration**: Secure user authentication via Google Cloud
- **RAG Support**: Vertex AI Search integration for enhanced knowledge retrieval
- **Flexible Deployment**: Works in local development and cloud environments
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Graceful Fallbacks**: Uses embedded knowledge when RAG is unavailable

## 📁 Project Structure

```
├── agent/
│   ├── agent.py                    # Main agent entry point
│   ├── .env                        # Environment configuration
│   ├── .env.example               # Environment template
│   ├── prompts/
│   │   └── brand_voice_instructions.py  # Agent instructions and prompts
│   └── tools/                     # Agent tools
│       ├── __init__.py
│       ├── content_reviewer.py    # Content analysis tools
│       ├── content_generator.py   # Content creation tools
│       ├── headline_generator.py  # Headline creation tools
│       ├── brand_voice_knowledge.py  # Core knowledge base
│       ├── brand_voice_search_tool.py # RAG search integration
│       ├── oauth_support.py       # OAuth utilities
│       └── ...
├── agent.yaml                     # Agent metadata and configuration
├── requirements.txt               # Python dependencies
└── README.md                      # This documentation
```

## 🛠 Installation & Setup

### Prerequisites
- Python 3.8+
- Google Cloud Project with enabled APIs:
  - Vertex AI API
  - Cloud AI Platform API
  - Identity and Access Management (IAM) API

### Local Development Setup

1. **Clone and Navigate**
   ```bash
   git clone <repository-url>
   cd sandbox-deployment
   git checkout sa-ort-brand-voice-agent-deployment-branch
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp agent/.env.example agent/.env
   # Edit agent/.env with your configuration
   ```

5. **Run Agent Locally**
   ```bash
   adk agent run
   ```

### Environment Configuration

Copy `agent/.env.example` to `agent/.env` and configure:

```bash
# Required: Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_PROJECT_NUMBER=your-project-number

# Required: OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your-oauth-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-oauth-client-secret

# Required: API Keys
GOOGLE_API_KEY=your-google-api-key
GOOGLE_GENAI_API_KEY=your-genai-api-key
GOOGLE_GENAI_MODEL=gemini-2.5-flash

# Optional: RAG Configuration (for enhanced knowledge retrieval)
RAG_CORPUS=projects/your-project/locations/us-central1/ragCorpora/brand-voice-corpus-id
VERTEX_SEARCH_ENGINE_ID=your-search-engine-id

# AgentSpace Configuration
AUTHORIZATION_NAME=brand-voice-auth-001
```

## 🔧 Configuration

### Agent Configuration (agent.yaml)

```yaml
defaults:
  scopes:
    - https://www.googleapis.com/auth/cloud-platform
    - openid
    - https://www.googleapis.com/auth/userinfo.email
    - https://www.googleapis.com/auth/userinfo.profile
  metadata:
    reasoning_engine_name: ort_brand_voice_agent
    reasoning_engine_description: A reasoning engine for Google Cloud Brand Voice Agent
    agent_space_name: Cloud Marketing Brand Voice Agent
    agent_space_description: An AI-powered writing assistant for Google Cloud marketers
    agent_space_tool_description: Use this tool to analyze content, generate drafts, and create headlines
  auth:
    oauth_authorization_id: brand_voice_auth_001
  environment_variables:
    RAG_CORPUS: "projects/your-project/locations/us-central1/ragCorpora/brand-voice-corpus-id"
```

### RAG Setup (Optional)

For enhanced knowledge retrieval, set up Vertex AI Search:

1. **Create a Search Application** in Google Cloud Console
2. **Upload Brand Voice Documents**:
   - Google Cloud Brand Voice & Style Guide
   - 50+ gold standard blog post examples
   - Terminology standards
   - Content best practices
3. **Configure Environment Variables**:
   ```bash
   RAG_CORPUS=projects/your-project/locations/us-central1/ragCorpora/your-corpus-id
   VERTEX_SEARCH_ENGINE_ID=your-search-engine-id
   ```

## 🎯 Usage

### Available Tools

The agent provides these tools for content creation:

#### Core Content Tools
1. **`review_content_for_brand_voice`** - Analyze existing content
   ```python
   review_content_for_brand_voice(
       content="Your blog post content...",
       content_type="blog_post",
       target_audience="technical professionals"
   )
   ```

2. **`generate_blog_content`** - Create new blog posts
   ```python
   generate_blog_content(
       topic="How to optimize Google Cloud costs",
       key_points=["Right-sizing instances", "Using preemptible VMs", "Storage optimization"],
       target_audience="technical professionals",
       content_length="medium"
   )
   ```

3. **`generate_headlines`** - Create multiple headline options
   ```python
   generate_headlines(
       topic="Google Cloud security best practices",
       target_audience="security professionals",
       headline_types=["how-to", "benefit-driven", "problem-solution"]
   )
   ```

#### Knowledge & Reference Tools
4. **`search_brand_voice_knowledge`** - Search knowledge base (when RAG configured)
5. **`retrieve_brand_voice_guidelines`** - Get specific brand guidelines
6. **`check_brand_voice_compliance`** - Automated compliance checking
7. **`get_google_cloud_terminology`** - Access official terminology

#### Helper Tools
8. **`get_quick_brand_voice_tips`** - Quick tips for content types
9. **`get_headline_best_practices`** - Headline writing guidelines

### Example Interactions

#### Content Review
```
User: "Please review this blog post intro for brand voice compliance..."

Agent: I'll analyze your content for Google Cloud brand voice compliance.

[Reviews content and provides specific feedback]

## Brand Voice Analysis Results

### 3 Key Improvements:
1. **Clarity Enhancement**: Replace "leverage" with "use" for clearer language
2. **Brand Voice Alignment**: Add more customer-focused benefits
3. **Structure Optimization**: Break up the 150-word paragraph into shorter sections

### Brand Voice Score: 7/10
**Explanation**: Good technical accuracy but needs more conversational tone and customer focus.
```

#### Content Generation
```
User: "Generate a blog post about Google Cloud AI/ML for technical teams"

Agent: I'll create a comprehensive blog post about Google Cloud AI/ML for technical teams.

[Generates structured blog content with proper Google Cloud brand voice]

# Accelerate Innovation with Google Cloud AI and Machine Learning

## Introduction
Technical teams today face mounting pressure to deliver AI-powered solutions...

[Full blog post with proper structure, examples, and Google Cloud integration]
```

## 🧠 Brand Voice Guidelines

The agent follows Google Cloud's brand voice principles:

### Voice Characteristics
- **Clear and Accessible**: Plain language, conversational but professional
- **Helpful and Solution-Oriented**: Focus on solving customer problems
- **Confident but Humble**: Show expertise without arrogance
- **Innovation-Focused**: Highlight cutting-edge technology
- **Inclusive and Welcoming**: Use inclusive language for all audiences

### Content Standards
- Remove corporate jargon and buzzwords
- Use active voice and clear, concise sentences
- Structure content with clear headings and logical flow
- Include specific examples and practical applications
- Follow AP style guidelines where applicable

### Terminology Standards
- Use "Google Cloud" not "GCP" in customer-facing content
- Say "AI and machine learning" not just "AI/ML"
- Use "multicloud" not "multi-cloud"
- Refer to "customers" not "users" when appropriate

## 🚀 Deployment

### Local Development
```bash
# Start the agent locally
adk agent run

# Access the web interface
open http://localhost:8000
```

### Cloud Deployment

The agent automatically deploys when pushed to the deployment branch:

```bash
# Commit changes
git add agent/agent.py agent.yaml
git commit -m "Update Brand Voice Agent"

# Push to trigger deployment
git push origin sa-ort-brand-voice-agent-deployment-branch
```

### Deployment Requirements
- **Three files minimum**: `agent/`, `agent.py`, `agent.yaml`
- **Unique naming**: Ensure reasoning engine and agent space names are unique
- **OAuth configuration**: Set up authorization in Google Cloud Console
- **Environment variables**: Configure secrets via Google Cloud Secret Manager

## 🔍 Troubleshooting

### Common Issues

#### Type Annotation Errors
**Error**: `Default value None of parameter ... is not compatible`
**Solution**: Use `Optional[Type] = None` instead of `Type = None`

```python
# ❌ Incorrect
def my_function(param: List[str] = None):

# ✅ Correct
def my_function(param: Optional[List[str]] = None):
```

#### RAG Not Working
**Error**: `VERTEX_SEARCH_ENGINE_ID environment variable not set`
**Solution**: Either configure RAG or agent will use embedded knowledge

```bash
# Configure RAG (optional)
VERTEX_SEARCH_ENGINE_ID=your-search-engine-id

# Or comment out for embedded knowledge only
# VERTEX_SEARCH_ENGINE_ID=your-search-engine-id
```

#### Authorization Conflicts
**Error**: Authorization already in use
**Solution**: Use unique authorization names in `agent.yaml`

```yaml
auth:
  oauth_authorization_id: brand_voice_auth_001  # Make this unique
```

### Logging

The agent provides comprehensive logging:

```bash
# View agent logs
tail -f logs/agent.log

# Key log messages
INFO - Brand voice search tool added to agent
WARNING - VERTEX_SEARCH_ENGINE_ID environment variable not set
INFO - Brand voice search tool not configured - using embedded knowledge only
```

## 🧪 Testing

### Manual Testing
1. **Start the agent**: `adk agent run`
2. **Open web interface**: http://localhost:8000
3. **Test core functions**:
   - Review sample content
   - Generate a blog post
   - Create headlines

### Function Testing
```python
# Test agent import
from agent.agent import root_agent
print(f"Agent loaded with {len(root_agent.tools)} tools")

# Test specific tools
from agent.tools import review_content_for_brand_voice
result = review_content_for_brand_voice("Sample content...")
print(result)
```

## 📈 Performance & Metrics

### Success Metrics
- **Adoption Rate**: Percentage of generated suggestions users copy or use
- **Time Saved**: Self-reported time savings from users
- **Quality Improvement**: Manual review scores of outputs by brand team

### Performance Considerations
- **Response Time**: ~2-5 seconds for content review, ~10-30 seconds for generation
- **Token Usage**: Optimized prompts to minimize LLM token consumption
- **RAG Efficiency**: Search results cached and optimized for relevance

## 🤝 Contributing

### Development Workflow
1. **Branch from main**: Create feature branch from `main`
2. **Implement changes**: Follow existing code patterns
3. **Test thoroughly**: Verify all tools work correctly
4. **Update documentation**: Keep README and code comments current
5. **Deploy to branch**: Push to `sa-ort-brand-voice-agent-deployment-branch`

### Code Standards
- **Type Hints**: Use proper type annotations with Optional for None defaults
- **Documentation**: Document all functions with clear docstrings
- **Error Handling**: Graceful fallbacks and informative error messages
- **Logging**: Use appropriate log levels for debugging and monitoring

## 📚 References

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder)
- [Vertex AI Search Documentation](https://cloud.google.com/vertex-ai-search/docs)
- [Google Cloud Brand Guidelines](https://cloud.google.com/brand-guidelines) (Internal)

## 📄 License

Copyright 2025 Google LLC. Licensed under the Apache License, Version 2.0.

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review agent logs for error details
3. Contact the development team via internal channels
4. Create an issue in the repository (if applicable)

---

**Built with ❤️ by the Google Cloud Marketing Team**