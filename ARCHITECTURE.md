# Plan on a Page Agent Architecture

## System Overview

The Plan on a Page Agent is built using Google's Agent Development Kit (ADK) and follows a modular architecture designed for facilitating marketing campaign planning across global, regional, and local teams.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                           │
│                 (ADK Web Interface)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Agent Core                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              LlmAgent                                  │ │
│  │  - Model: gemini-2.0-flash-001                         │ │
│  │  - Instructions: Plan on a Page Agent Instructions    │ │
│  │  - Tools: 18 specialized planning tools                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Tool Layer                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌────────────────┐ │
│  │  Core Planning  │ │ G/R/L Expert    │ │  Support Tools │ │
│  │  - Analyzer     │ │ - Assignment    │ │  - Validator   │ │
│  │  - Generator    │ │ - A/A/I Guide   │ │  - Formatter   │ │
│  │  - Validator    │ │ - Best Practices│ │  - Duplicates  │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Knowledge & Integration Layer                │
│  ┌─────────────────┐       ┌─────────────────────────────┐  │
│  │ Template        │       │ External Integrations       │  │
│  │ Knowledge Base  │       │ - Google Drive (Duplicates) │  │
│  │ - Plan template │       │ - OAuth (Authentication)    │  │
│  │ - G/R/L guide   │       │ - File Upload (DOCX/PDF)    │  │
│  │ - Best practices│       │ - RAG Corpus (Optional)     │  │
│  └─────────────────┘       └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Agent Core (`agent/agent.py`)

**Primary Responsibilities:**
- Initialize and configure the LlmAgent with planning-focused model
- Load and register all 18 planning tools
- Handle OAuth authentication for Drive access
- Manage conversation flow and context

**Key Components:**

```python
root_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="plan_on_page_agent",
    description="Plan on a Page Agent - Collaborative planning assistant",
    instruction=PLAN_ON_PAGE_AGENT_INSTRUCTION,
    tools=agent_tools
)
```

**Tool Organization:**
- Core planning tools (analyze, generate, validate)
- G/R/L specialized tools (critical for cross-geography alignment)
- Supporting tools (formatting, templates, section guidance)
- External integration tools (duplicate detection, file upload)

### 2. Tool Layer

#### Core Planning Tools

**Plan Analyzer** (`plan_analyzer.py`)
- Analyzes existing Plan on a Page documents
- Identifies gaps and missing sections
- Provides specific, actionable improvement suggestions
- Special focus on G/R/L section quality
- Returns completeness score and recommendations

**Plan Generator** (`plan_generator.py`)
- Guides users through creating plans from scratch
- Interactive, step-by-step conversation flow
- Collects information for all required sections
- Builds partial plan progressively
- Provides context for why each section matters

**Plan Validator** (`plan_validator.py`)
- Comprehensive validation of plan completeness
- Checks for TBD/placeholder text
- Validates named individuals (not teams)
- Ensures quantified metrics
- Overall quality score calculation

#### G/R/L Specialized Tools

**G/R/L Helper** (`grl_helper.py`)
- Expert guidance for Global/Regional/Local assignments
- Applies Adopt/Adapt/Invent framework
- Helps identify which team leads each component
- Prompts for named leads and rationale
- Decision tree for A/A/I recommendations

**Key Functions:**
```python
guide_grl_assignment()      # Interactive G/R/L assignment help
suggest_adopt_adapt_invent() # Recommend A/A/I for components
get_grl_best_practices()    # Access patterns and examples
format_grl_table_entry()    # Format G/R/L table markdown
```

#### Supporting Tools

**Plan Formatter** (`plan_formatter.py`)
- Formats plans according to standard template
- Validates format compliance
- Extracts structured data from text
- Cleans formatting issues

**Duplicate Detector** (`duplicate_detector.py`)
- Searches Google Drive for similar plans
- Calculates similarity scores
- Flags potential duplicate initiatives
- Prevents redundant work

**Template Knowledge** (`plan_template_knowledge.py`)
- Embedded template and best practices
- Section-specific guidance
- G/R/L framework details
- Quality checklists
- Common mistakes to avoid

### 3. Knowledge Layer

#### Embedded Knowledge

Located in `plan_template_knowledge.py`, provides:

```python
PLAN_KNOWLEDGE = {
    "template_sections": {
        "grl_section": { ... },           # G/R/L guidance
        "objectives_description": { ... }, # Objectives help
        "activation_components": { ... },  # Component examples
        "kpis_measurement": { ... }        # KPI guidance
    },
    "grl_framework_detailed": { ... },     # A/A/I framework
    "quality_checklist": { ... }           # Validation criteria
}
```

#### External Integrations

**Google Drive Integration:**
- Search for similar existing plans
- OAuth-based authentication
- Support for Google Docs, PDFs, DOCX
- Duplicate detection across all Drive sources

**File Upload Support:**
- Process uploaded DOCX/PDF/TXT documents
- Extract plan content for analysis
- Support for draft review workflow

**RAG Corpus (Optional):**
- Can integrate with Vertex AI Search
- Enhanced knowledge retrieval for planning best practices
- Fallback to embedded knowledge when unavailable

## Data Flow

### New Plan Creation Flow

```
User: "Create a new plan"
    ↓
generate_new_plan()
    ↓
Interactive Q&A (Foundation)
    ↓
Collect: Name, Sponsor, Objectives
    ↓
Interactive Q&A (Activation)
    ↓
Identify Activation Components
    ↓
guide_grl_assignment() for each component
    ↓
Collect: Leads, A/A/I decisions, Notes
    ↓
Interactive Q&A (Details)
    ↓
Collect: Investment, Milestones, KPIs
    ↓
format_plan_output()
    ↓
validate_plan_completeness()
    ↓
Polished, Complete Plan
```

### Existing Plan Review Flow

```
User uploads/pastes plan
    ↓
analyze_plan(plan_content)
    ↓
Section Completeness Check
    ↓
G/R/L Quality Assessment
    ↓
TBD/Placeholder Detection
    ↓
Specificity Validation
    ↓
Quantification Check
    ↓
Generate Recommendations
    ↓
Structured Feedback + Improvement Suggestions
```

### Duplicate Detection Flow

```
User provides project name/description
    ↓
search_similar_plans()
    ↓
Extract search keywords
    ↓
Query Google Drive (My Drive + Shared)
    ↓
Filter for Plan documents
    ↓
Calculate similarity scores
    ↓
Rank by relevance
    ↓
Present top matches with recommendations:
  - Same initiative? → Coordinate
  - Feature extension? → Build on existing
  - Distinct? → Proceed with new plan
```

### G/R/L Assignment Flow

```
User working on G/R/L section
    ↓
guide_grl_assignment(component="Social Media")
    ↓
Interactive Questions:
  - Which team creates the work?
  - Will Regional Adopt/Adapt/Invent?
  - Will Local Adopt/Adapt/Invent?
  - Who are the named leads?
  - Any dependencies or notes?
    ↓
suggest_adopt_adapt_invent() for each geography
    ↓
Decision tree recommendations
    ↓
format_grl_table_entry()
    ↓
Complete G/R/L assignment with rationale
```

### RAG-Enhanced Planning Flow (Optional)

When RAG corpus is configured with VERTEX_SEARCH_ENGINE_ID and RAG_CORPUS:

```
User creating or analyzing plan
    ↓
Agent detects campaign type (product_launch, brand_campaign, event)
    ↓
┌─────────────────────────────────────────────────────────┐
│         RAG Search Functions (Conditionally Available)  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  plan_example_search()                                  │
│    ↓                                                    │
│  Query: "similar successful plans"                      │
│  Filter: campaign_type, geography                       │
│    ↓                                                    │
│  Vertex AI Search retrieves top_k examples              │
│    ↓                                                    │
│  Returns: Patterns, best practices, real examples       │
│                                                          │
│  plan_grl_pattern_search()                              │
│    ↓                                                    │
│  Query: "G/R/L assignments for [activation_component]"  │
│    ↓                                                    │
│  Returns: Real Adopt/Adapt/Invent decisions             │
│                                                          │
│  plan_similar_by_type()                                 │
│    ↓                                                    │
│  Retrieve complete example plans by type                │
│    ↓                                                    │
│  Returns: Full plan examples with structure analysis    │
│                                                          │
└─────────────────────────────────────────────────────────┘
    ↓
Agent enriches guidance with real-world examples
    ↓
User sees:
  - "Based on 5 similar product launch plans..."
  - "Common G/R/L pattern: Global creates, Regional adapts..."
  - "Typical KPIs for this campaign type: ..."
    ↓
Improved plan quality through example-based learning
```

**RAG Integration Points:**
- **plan_analyzer.py** - Compare against example plans during analysis
- **plan_generator.py** - Show examples during guided creation (activation stage)
- **grl_helper.py** - Display real G/R/L patterns from similar campaigns
- **get_grl_best_practices()** - Enrich with corpus insights by campaign type

**Graceful Degradation:**
If RAG not configured:
- All functions return `rag_available: False`
- Agent falls back to embedded knowledge
- No functionality loss, just missing example enrichment

## Configuration Management

### Environment Variables

```
┌─────────────────────────────────────────┐
│           Configuration Sources          │
├─────────────────────────────────────────┤
│  1. agent/.env (Local Development)      │
│  2. agent.yaml (Agent Metadata)         │
│  3. Google Cloud Secrets (Production)   │
│  4. Environment Variables (Runtime)     │
└─────────────────────────────────────────┘
```

### Configuration Hierarchy

1. **Runtime Environment Variables** (highest priority)
2. **agent/.env file** (local development)
3. **agent.yaml** (agent metadata and scopes)
4. **Default values** (fallback)

### Required Scopes

```yaml
scopes:
  - https://www.googleapis.com/auth/cloud-platform
  - openid
  - https://www.googleapis.com/auth/userinfo.email
  - https://www.googleapis.com/auth/userinfo.profile
  - https://www.googleapis.com/auth/drive.readonly    # NEW: For duplicate detection
  - https://www.googleapis.com/auth/drive.file        # NEW: For file access
```

## Security Architecture

### Authentication Flow

```
User Request
    ↓
OAuth Token Validation
    ↓
Google Cloud IAM Check
    ↓
Drive Access Authorization (if needed)
    ↓
Tool Access Authorization
    ↓
Response
```

### Security Measures

- **OAuth 2.0** for user authentication
- **Google Cloud IAM** for service authorization
- **Scoped Permissions** for Drive access (readonly + file)
- **Token Validation** on each request
- **Environment Variable Protection** for secrets
- **No credential storage** in agent code

## Scalability Considerations

### Horizontal Scaling

- **Stateless Design**: No session state stored in agent
- **Tool Isolation**: Each tool is independent and modular
- **Concurrent Requests**: Supports multiple simultaneous users
- **Progressive Plan Building**: Handles long conversations efficiently

### Performance Optimization

- **Prompt Optimization**: Focused instructions for each tool
- **Lazy Loading**: Knowledge loaded only when needed
- **Error Handling**: Graceful degradation on failures
- **Caching**: Template and knowledge cached in memory

## Monitoring & Observability

### Logging Strategy

```python
logger = logging.getLogger(__name__)

# Key log events
logger.info("Plan on a Page Agent initialized with {N} tools")
logger.info("Analyzing plan with {N} sections")
logger.warning("G/R/L section incomplete")
logger.error("Plan validation failed: {error}")
```

### Metrics to Track

- **Tool Usage**: Which tools are used most frequently
- **Plan Completeness**: Average completeness scores
- **G/R/L Quality**: G/R/L section quality metrics
- **Duplicate Detection**: Number of duplicates prevented
- **Validation Pass Rate**: Plans passing validation first time
- **User Satisfaction**: Feedback on plan quality

## Extension Points

### Adding New Validation Checks

1. Add check function to `plan_validator.py`
2. Integrate into `validate_plan_completeness()`
3. Update quality checklist in `plan_template_knowledge.py`
4. Add to agent instructions

### Adding New Plan Sections

1. Update template in `plan_template_knowledge.py`
2. Add section guidance
3. Update `plan_analyzer.py` to check for new section
4. Update `plan_formatter.py` to format new section
5. Update validation logic

### Enhanced Duplicate Detection

1. Integrate semantic search algorithms
2. Connect to enterprise search systems
3. Add machine learning similarity scoring
4. Cross-reference with project management systems

### New G/R/L Patterns

1. Add new patterns to `grl_framework_detailed`
2. Update decision tree logic
3. Add examples to knowledge base
4. Update agent instructions with new scenarios

## Testing Architecture

### Unit Testing

- **Tool Functions**: Test each tool in isolation
- **Validation Logic**: Test completeness checks
- **G/R/L Framework**: Test A/A/I recommendations
- **Formatting**: Test template compliance

### Integration Testing

- **Agent Loading**: Full agent initialization
- **Tool Integration**: End-to-end tool workflows
- **Drive Integration**: Search and duplicate detection
- **File Upload**: Document processing pipeline

### User Acceptance Testing

- **New Plan Creation**: Complete workflow from start to finish
- **Plan Review**: Upload and analyze existing plans
- **G/R/L Guidance**: Interactive assignment help
- **Duplicate Detection**: Find similar plans

## Deployment Architecture

### Local Development

```
Developer Machine
├── Python Virtual Environment
├── ADK CLI
├── Agent Code (all tools)
├── Local Configuration (.env)
└── Sample Templates
```

### Cloud Deployment

```
Google Cloud Platform
├── Vertex AI Agent Builder
├── Reasoning Engine (plan_on_a_page_agent)
├── Agent Space (Plan on a Page Agent)
├── Google Drive API (duplicate detection)
├── Secret Manager (OAuth credentials)
└── Cloud Logging (monitoring)
```

### CI/CD Pipeline

```
Code Push → Branch Detection → Build → Deploy → Validation
     ↓              ↓             ↓        ↓         ↓
  Git Commit   Deploy Branch   Package  Vertex AI  Health Check
```

## Key Differentiators from Brand Voice Agent

| Aspect | Brand Voice Agent | Plan on a Page Agent |
|--------|------------------|---------------------|
| **Purpose** | Content creation | Strategic planning |
| **Focus** | Writing quality | Cross-team alignment |
| **Key Section** | Headlines | G/R/L assignments |
| **Framework** | Brand voice principles | Adopt/Adapt/Invent |
| **Validation** | Tone & style | Completeness & clarity |
| **Integration** | RAG for examples | Drive for duplicates |
| **Users** | Content creators | Marketing planners |

## Future Enhancements

### Planned Features

1. **Integration with Project Management**: Sync with Asana, Jira, Monday.com
2. **Automated G/R/L Suggestions**: ML-based recommendations for A/A/I
3. **Plan Version Control**: Track iterations and changes over time
4. **Collaboration Features**: Multi-user real-time editing
5. **Analytics Dashboard**: Plan quality metrics and insights
6. **Template Customization**: Support for different plan types
7. **Smart Dependencies**: Automatic dependency detection between plans

### Technology Upgrades

1. **Model Updates**: Newer Gemini models as available
2. **Enhanced Search**: Semantic search for better duplicate detection
3. **Tool Optimization**: Performance improvements for large plans
4. **UI Enhancements**: Better visualization of G/R/L assignments

---

This architecture provides a robust foundation for the Plan on a Page Agent while maintaining flexibility for future enhancements and scale.
