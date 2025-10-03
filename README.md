# Plan on a Page Agent

A collaborative AI assistant designed specifically for marketers who need to develop or refine their "Plan on a Page" submissions for campaigns, launches, or major initiatives. This agent acts as both a strategic guide and a process facilitator, ensuring that every plan is complete and aligned across global, regional, and local teams.

## 🎯 Overview

The Plan on a Page Agent helps marketers create clear, actionable plans that align work across geographies and teams, with special focus on the G/R/L (Global/Regional/Local) section using the Adopt/Adapt/Invent framework.

## 💼 Business Problem

Marketers struggle to create complete, aligned plans. The G/R/L section is frequently misunderstood or underutilized, leading to:
- **Duplication** of effort across teams
- **Misalignment** between global, regional, and local initiatives
- **Missed opportunities** for scaling successful work
- **Unclear roles** and responsibilities

## 🚀 Core Capabilities

### 1. **Plan Analysis & Improvement** (Priority 1)
For users with existing drafts:
- Analyze uploaded documents for completeness and clarity
- Identify gaps, ambiguities, or missing information
- Suggest targeted improvements, especially for G/R/L section
- Validate that roles and responsibilities are explicit
- Check that Adopt/Adapt/Invent framework is properly applied

### 2. **Guided Plan Creation** (Priority 2)
For users starting from scratch:
- Guide step-by-step through each section of the template
- Prompt for all required fields
- Focus especially on activation components and G/R/L assignments
- Help apply the Adopt/Adapt/Invent framework to each component
- Encourage early alignment conversations with stakeholders

### 3. **Duplicate Detection** (Priority 3)
- Search existing plans in Drive for similar initiatives
- Flag potential duplicates or overlaps
- Prevent redundant work and encourage collaboration

### 4. **Validation & Quality Assurance**
- Validate plan completeness before finalization
- Check that all mandatory fields are filled
- Ensure G/R/L assignments are clear and comprehensive
- Verify that team leads are named for each geography

### 5. **RAG-Enhanced Knowledge (Optional)**
When configured with a Vertex AI Search corpus:
- **Search example plans** - Find similar successful plans from knowledge base
- **Real G/R/L patterns** - Show how similar campaigns handled G/R/L assignments
- **Campaign type insights** - Compare against relevant examples (product launches, brand campaigns, events)
- **Best practices** - Surface patterns and approaches from high-quality example plans

This optional enhancement enriches guidance with concrete examples from real campaigns, helping users learn from proven approaches.

## 📋 Plan on a Page Template

Required sections:
1. **Project Identifiers** - Name, Executive Sponsor, Project Lead, Project Manager
2. **Decision Framework (D/I/N)** - Decide, Input, Notify roles
3. **G/R/L Table** - Global/Regional/Local leads with Adopt/Adapt/Invent notes
4. **Strategic Context** - Marketing objectives, OKR alignment, project description
5. **Audience & Messaging** - Target audience, key messages
6. **Execution** - Investment, milestones, activation components
7. **Risk & Measurement** - Risks/blockers, KPIs, anticipated impact

## 🌍 G/R/L Framework Expertise

The agent is an expert on the Global/Regional/Local framework:

**Geographies:**
- **Global (G):** Work created centrally and deployed across all markets
- **Regional (R):** Work created for specific regions (EMEA, APAC, Americas, etc.)
- **Local (L):** Work created for specific countries or local markets

**Adopt/Adapt/Invent Framework:**
- **Adopt:** Use the work as-is from another team (most efficient)
- **Adapt:** Modify existing work to fit local needs (translation, cultural adaptation)
- **Invent:** Create net-new work specific to this geography (only when necessary)

**Key Principles:**
- Each activation component should have clear G/R/L ownership
- Name the lead person for each geography
- Specify whether each team will Adopt, Adapt, or Invent
- Include notes explaining the rationale for each decision
- Encourage early alignment conversations between teams

## 🛠 Installation & Setup

### Prerequisites
- Python 3.8+
- Google Cloud Project with enabled APIs:
  - Vertex AI API
  - Cloud AI Platform API
  - Google Drive API (for duplicate detection)
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
GOOGLE_GENAI_MODEL=gemini-2.0-flash-001

# AgentSpace Configuration
AUTHORIZATION_NAME=plan_on_page_auth_001
```

## 📁 Project Structure

```
├── agent/
│   ├── agent.py                           # Main agent entry point
│   ├── .env                               # Environment configuration
│   ├── .env.example                       # Environment template
│   ├── prompts/
│   │   └── plan_on_page_instructions.py   # Agent instructions
│   └── tools/                             # Agent tools
│       ├── __init__.py
│       ├── plan_analyzer.py               # Analyze existing plans
│       ├── plan_generator.py              # Guide new plan creation
│       ├── grl_helper.py                  # G/R/L assignment help
│       ├── plan_formatter.py              # Template formatting
│       ├── plan_validator.py              # Completeness validation
│       ├── duplicate_detector.py          # Find similar plans
│       ├── plan_template_knowledge.py     # Template & best practices
│       ├── file_upload_supprt.py          # Document upload support
│       ├── drive_search_supporter.py      # Drive search for duplicates
│       └── oauth_support.py               # OAuth utilities
│   └── sample-templates/
│       └── Plan on a Page.md              # Template reference
├── agent.yaml                             # Agent metadata
├── requirements.txt                       # Python dependencies
└── README.md                              # This documentation
```

## 🎯 Usage

### Example Interactions

#### Starting a New Plan

```
User: "I need to create a Plan on a Page for our Q3 product launch campaign."

Agent: "Absolutely! I'll help you create a Plan on a Page for your Q3 product launch.
Let's start with the basics:

1. What's the specific name for this campaign?
2. Who is the Executive Sponsor?
3. What marketing objectives does this support? Which OKRs does it ladder to?

Once we have the foundation, we'll identify your activation components and work through
the G/R/L assignments to ensure alignment across all teams."
```

#### Reviewing an Existing Plan

```
User: "Can you review my plan draft and help me improve the G/R/L section?"

Agent: "I'd be happy to review your plan! Please upload your draft document or paste
the content, and I'll analyze it for completeness and provide specific recommendations,
with special focus on the G/R/L section to ensure clear assignments and proper use of
the Adopt/Adapt/Invent framework."
```

### Available Tools

The agent provides these specialized tools:

#### Core Planning Tools
1. **`analyze_plan`** - Review existing plans and identify gaps
2. **`generate_new_plan`** - Guide users through creating plans from scratch
3. **`validate_plan_completeness`** - Check if all required sections are complete

#### G/R/L Specialized Tools
4. **`guide_grl_assignment`** - Interactive help for G/R/L section
5. **`suggest_adopt_adapt_invent`** - Recommend A/A/I framework application
6. **`get_grl_best_practices`** - Access G/R/L best practices and patterns

#### Supporting Tools
7. **`format_plan_output`** - Format final plan according to template
8. **`search_similar_plans`** - Find potential duplicate initiatives
9. **`get_template`** - Retrieve the blank template
10. **`list_artifacts`** - See uploaded documents

#### RAG-Enhanced Tools (Optional)
When RAG corpus is configured:
11. **`plan_example_search`** - Search corpus of example plans for patterns
12. **`plan_grl_pattern_search`** - Find real G/R/L assignments from similar campaigns
13. **`plan_similar_by_type`** - Retrieve example plans by campaign type
14. **`plan_corpus_insights`** - Get statistical insights from example plans

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
git add .
git commit -m "Update Plan on a Page Agent"

# Push to trigger deployment
git push origin sa-ort-brand-voice-agent-deployment-branch
```

### Deployment Requirements
- **Three files minimum**: `agent/`, `agent.py`, `agent.yaml`
- **Unique naming**: Ensure reasoning engine and agent space names are unique
- **OAuth configuration**: Set up authorization in Google Cloud Console
- **Environment variables**: Configure secrets via Google Cloud Secret Manager

## 📈 Use Cases

### 1. Guided Idea Intake
**Scenario:** A marketer needs to create a plan from scratch
- Agent prompts for required sections systematically
- Ensures all mandatory fields are captured
- Guides through G/R/L assignments step-by-step

**Outcome:** Complete, standardized plan ready for review

### 2. Duplicate Detection & Clarification
**Scenario:** Multiple teams may be working on similar initiatives
- Agent searches for similar existing plans
- Flags potential duplicates with similarity scores
- Asks: "Is this the same, a feature extension, or distinct?"

**Outcome:** Eliminates duplicate work, encourages collaboration

### 3. G/R/L Alignment Facilitation
**Scenario:** Team needs to coordinate across geographies
- Agent helps identify which team leads each component
- Guides Adopt/Adapt/Invent decisions
- Prompts for named leads and rationale notes

**Outcome:** Clear roles, efficient reuse of work, aligned execution

### 4. Standardized Requirements Compilation
**Scenario:** Plan content is scattered across emails and docs
- Agent extracts key information conversationally
- Formats into standardized template structure
- Validates completeness before submission

**Outcome:** Consistent format, faster review cycles

### 5. Accelerated Committee Review
**Scenario:** Leadership reviews multiple plan submissions
- All plans follow same template and quality standard
- Duplicates are already resolved or flagged
- G/R/L assignments are clear and explicit

**Outcome:** Faster prioritization, less administrative burden

## 🧪 Testing

### Manual Testing
1. **Start the agent**: `adk agent run`
2. **Open web interface**: http://localhost:8000
3. **Test flows**:
   - Create a new plan from scratch
   - Upload and analyze an existing plan
   - Test G/R/L assignment guidance
   - Validate a complete plan

## 🔍 Troubleshooting

### Common Issues

#### OAuth/Drive Access Issues
**Error**: Cannot search for duplicates
**Solution**: Ensure Drive API scopes are included in agent.yaml and OAuth consent screen

#### File Upload Issues
**Error**: Cannot process uploaded documents
**Solution**: Verify file_upload_supprt.py is properly configured for DOCX/PDF/TXT formats

## 📚 Key Concepts

### D/I/N Framework
- **Decide**: 1-2 people with final say
- **Input**: 3-5 people who provide input before decisions
- **Notify**: Anyone else who should be informed

### Activation Components
Channels and tactics to reach your audience:
- Social media
- Content marketing
- Events and webinars
- Paid advertising
- PR and thought leadership
- Email campaigns
- Partner co-marketing

### Quality Checklist
- ✓ All 15 required sections complete
- ✓ No TBD or placeholder text
- ✓ Named individuals (not teams)
- ✓ Actual dates (not "Q2" or "upcoming")
- ✓ Quantified KPIs
- ✓ G/R/L table with named leads
- ✓ Adopt/Adapt/Invent specified for each component
- ✓ Explanatory notes for assignments

## 🤝 Contributing

### Development Workflow
1. **Branch from main**: Create feature branch
2. **Implement changes**: Follow existing code patterns
3. **Test thoroughly**: Verify all tools work correctly
4. **Update documentation**: Keep README current
5. **Deploy to branch**: Push to deployment branch

### Code Standards
- **Type Hints**: Use proper type annotations
- **Documentation**: Document all functions with clear docstrings
- **Error Handling**: Graceful fallbacks and informative errors
- **Logging**: Use appropriate log levels

## 📄 License

Copyright 2025 Google LLC. Licensed under the Apache License, Version 2.0.

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review agent logs for error details
3. Contact the development team
4. Create an issue in the repository

---

**Built for Marketing Excellence by Google Cloud Marketing Team**
