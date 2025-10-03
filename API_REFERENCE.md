# Plan on a Page Agent - API Reference

Complete reference documentation for all tools and functions available in the Plan on a Page Agent.

## Table of Contents

- [Core Planning Tools](#core-planning-tools)
- [G/R/L Specialized Tools](#grl-specialized-tools)
- [Supporting Tools](#supporting-tools)
- [Template & Knowledge Tools](#template--knowledge-tools)
- [Utility Tools](#utility-tools)
- [RAG-Enhanced Tools (Optional)](#rag-enhanced-tools-optional)

---

## Core Planning Tools

### analyze_plan

Analyze an existing Plan on a Page document and provide comprehensive feedback.

**Module:** `plan_analyzer.py`

**Function Signature:**
```python
def analyze_plan(
    plan_content: str,
    focus_area: str = "all",
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `plan_content` (str, required): The full text content of the Plan on a Page document
- `focus_area` (str, optional): Specific area to focus on. Options: `"all"`, `"grl"`, `"completeness"`, `"clarity"`. Default: `"all"`
- `tool_context` (ToolContext, optional): Google ADK tool context

**Returns:**
```python
{
    "analysis": str,                    # Detailed analysis text
    "completeness_score": str,          # "X/15" format
    "present_sections": List[str],      # Sections found
    "missing_sections": List[str],      # Sections missing
    "focus_area": str,                  # Focus area used
    "status": str,                      # "completed" or "error"
    "recommendations": Dict[str, str]   # Priority recommendations
}
```

**Example Usage:**
```python
result = analyze_plan(
    plan_content=uploaded_plan_text,
    focus_area="grl"
)
print(f"Completeness: {result['completeness_score']}")
print(f"Recommendations: {result['recommendations']}")
```

---

### generate_new_plan

Guide users through creating a new Plan on a Page from scratch.

**Module:** `plan_generator.py`

**Function Signature:**
```python
def generate_new_plan(
    project_name: Optional[str] = None,
    project_description: Optional[str] = None,
    objectives: Optional[str] = None,
    activation_components: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `project_name` (str, optional): Name of the project/campaign
- `project_description` (str, optional): Brief description
- `objectives` (str, optional): Marketing objectives
- `activation_components` (List[str], optional): List of activation channels/tactics
- `tool_context` (ToolContext, optional): Google ADK tool context

**Returns:**
```python
{
    "guidance": str,                 # Next step guidance text
    "stage": str,                    # Current stage of plan creation
    "partial_plan": str,             # Plan built so far
    "fields_collected": Dict[str, bool],  # What's been collected
    "next_steps": List[str],         # Recommended next steps
    "status": str                    # "in_progress" or "error"
}
```

**Example Usage:**
```python
result = generate_new_plan(
    project_name="Q3 Product Launch Campaign"
)
print(result['guidance'])
```

---

### validate_plan_completeness

Validate that a Plan on a Page document is complete and ready for submission.

**Module:** `plan_validator.py`

**Function Signature:**
```python
def validate_plan_completeness(
    plan_content: str
) -> Dict[str, Any]
```

**Parameters:**
- `plan_content` (str, required): Full text of the Plan on a Page document

**Returns:**
```python
{
    "valid": bool,                      # Overall validation result
    "overall_score": float,             # Score 0-100
    "validation_results": Dict,         # Detailed validation by category
    "issues_found": List[str],          # All issues identified
    "issue_count": int,                 # Number of issues
    "recommendations": List[str],       # Top recommendations
    "quality_checklist": Dict,          # Quality criteria
    "status": str,                      # "completed"
    "ready_for_submission": bool        # Ready to submit?
}
```

**Validation Categories:**
- `sections`: Presence of required sections
- `grl_quality`: G/R/L section quality
- `completeness`: No TBD/placeholders
- `specificity`: Named individuals and specific details
- `quantification`: Quantified KPIs

---

## G/R/L Specialized Tools

### guide_grl_assignment

Interactive guidance for assigning G/R/L roles for an activation component.

**Module:** `grl_helper.py`

**Function Signature:**
```python
def guide_grl_assignment(
    activation_component: str,
    component_description: Optional[str] = None,
    creating_team: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `activation_component` (str, required): The activation component to assign (e.g., "Social Media")
- `component_description` (str, optional): Description of the component
- `creating_team` (str, optional): Which team is creating this work ("Global", "Regional", or "Local")
- `tool_context` (ToolContext, optional): Google ADK tool context

**Returns:**
```python
{
    "guidance": str,                    # Interactive guidance text
    "activation_component": str,        # Component being assigned
    "framework_info": Dict,             # G/R/L framework details
    "next_steps": List[str],            # Recommended actions
    "status": str                       # "guidance_provided"
}
```

---

### suggest_adopt_adapt_invent

Suggest whether a geography should Adopt, Adapt, or Invent for a specific component.

**Module:** `grl_helper.py`

**Function Signature:**
```python
def suggest_adopt_adapt_invent(
    activation_component: str,
    creating_geography: str,
    target_geography: str,
    context: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `activation_component` (str, required): The component being assigned
- `creating_geography` (str, required): Geography creating the work ("Global"/"Regional"/"Local")
- `target_geography` (str, required): Geography receiving the assignment
- `context` (str, optional): Additional context about market needs

**Returns:**
```python
{
    "activation_component": str,
    "creating_geography": str,
    "target_geography": str,
    "recommendation": str,              # "ADOPT", "ADAPT", "INVENT", or "CREATE"
    "rationale": str,                   # Reason for recommendation
    "considerations": List[str],        # Additional factors to consider
    "framework": Dict,                  # A/A/I definitions
    "questions_to_ask": List[str]       # Questions to clarify decision
}
```

**Recommendation Logic:**
- Same geography → `"CREATE"`
- Global → Regional → `"ADAPT"` (adapt for region)
- Global → Local → `"ADOPT"` (use as-is)
- Regional → Local → `"ADOPT"` (use regional version)

---

### get_grl_best_practices

Get best practices and common patterns for G/R/L assignments.

**Module:** `grl_helper.py`

**Function Signature:**
```python
def get_grl_best_practices() -> Dict[str, Any]
```

**Returns:**
```python
{
    "core_principles": List[str],           # Core G/R/L principles
    "common_patterns": Dict[str, Dict],     # Patterns by scenario
    "decision_framework": Dict,             # Decision tree
    "common_mistakes": List[str],           # Mistakes to avoid
    "quality_checklist": List[str]          # Quality criteria
}
```

**Common Patterns:**
- `global_campaign`: Global creates, Regional adapts, Local adopts
- `regional_initiative`: Regional creates, Local adopts/adapts
- `local_innovation`: Local invents, evaluate for scaling
- `hybrid_approach`: Mix of A/A/I across components

---

### format_grl_table_entry

Format a complete G/R/L table entry with all information.

**Module:** `grl_helper.py`

**Function Signature:**
```python
def format_grl_table_entry(
    global_lead: str,
    regional_lead: str,
    local_lead: str,
    global_notes: str,
    regional_notes: str,
    local_notes: str
) -> str
```

**Parameters:**
All parameters are required strings containing the information for each geography.

**Returns:**
Formatted markdown string for the G/R/L table.

---

## Supporting Tools

### format_plan_output

Format a complete Plan on a Page document according to the standard template.

**Module:** `plan_formatter.py`

**Function Signature:**
```python
def format_plan_output(
    plan_data: Dict[str, Any],
    output_format: str = "markdown"
) -> Dict[str, Any]
```

**Parameters:**
- `plan_data` (Dict, required): Dictionary containing all plan sections
- `output_format` (str, optional): Output format. Currently supports `"markdown"`. Default: `"markdown"`

**Plan Data Structure:**
```python
{
    "project_name": str,
    "executive_sponsor": str,
    "project_lead": str,
    "project_manager": str,
    "vendor_agency": str,
    "creative_teams": str,
    "din": {
        "decide": str,
        "input": str,
        "notify": str
    },
    "grl": {
        "global_lead": str,
        "global_notes": str,
        "regional_lead": str,
        "regional_notes": str,
        "local_lead": str,
        "local_notes": str
    },
    "objectives": str,
    "description": str,
    "audience": str,
    "key_messages": Union[str, List[str]],
    "investment": str,
    "milestones": List[Dict] or List[str],
    "risks": Union[str, List[str]],
    "activation_components": List[str],
    "kpis": List[str]
}
```

**Returns:**
```python
{
    "formatted_plan": str,              # Formatted markdown plan
    "output_format": str,               # Format used
    "sections_included": List[str],     # Sections in output
    "word_count": int,                  # Total word count
    "status": str                       # "completed" or "error"
}
```

---

### search_similar_plans

Search Google Drive for similar Plan on a Page documents.

**Module:** `duplicate_detector.py`

**Function Signature:**
```python
def search_similar_plans(
    project_name: str,
    project_description: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `project_name` (str, required): Name of the project to search for
- `project_description` (str, optional): Description for more context
- `tool_context` (ToolContext, required): Tool context for Drive access

**Returns:**
```python
{
    "search_query": str,
    "similar_plans_found": int,
    "plans": List[Dict],                # Top similar plans
    "recommendations": List[str],       # Action recommendations
    "action_needed": bool,              # Are there duplicates?
    "status": str
}
```

**Plan Structure in Results:**
```python
{
    "file_id": str,
    "name": str,
    "mime_type": str,
    "owners": List[Dict],
    "similarity_score": float          # 0.0 to 1.0
}
```

---

### quick_completeness_check

Perform a quick check for basic completeness of required sections.

**Module:** `plan_analyzer.py`

**Function Signature:**
```python
def quick_completeness_check(
    plan_content: str
) -> Dict[str, Any]
```

**Parameters:**
- `plan_content` (str, required): The plan text to check

**Returns:**
```python
{
    "complete": bool,                       # All sections present?
    "completeness_percentage": float,       # Percentage complete
    "sections_found": List[str],            # Sections present
    "sections_missing": List[str],          # Sections absent
    "details": Dict[str, bool]              # Per-section results
}
```

---

### get_grl_specific_feedback

Provide focused feedback specifically on the G/R/L section.

**Module:** `plan_analyzer.py`

**Function Signature:**
```python
def get_grl_specific_feedback(
    plan_content: str
) -> Dict[str, Any]
```

**Parameters:**
- `plan_content` (str, required): Plan content containing G/R/L section

**Returns:**
```python
{
    "has_grl_section": bool,
    "quality_score": float,             # 0-10 scale
    "checks_passed": Dict[str, bool],   # Individual checks
    "issues_identified": List[str],     # Issues found
    "recommendation": str,              # Improvement recommendation
    "status": str                       # "good" or "needs_improvement"
}
```

**Checks Performed:**
- Has Global lead named
- Has Regional lead named
- Has Local lead named
- Adopt/Adapt/Invent framework applied
- Detailed notes present

---

## Template & Knowledge Tools

### get_template

Return the blank Plan on a Page template.

**Module:** `plan_template_knowledge.py`

**Function Signature:**
```python
def get_template() -> str
```

**Returns:**
Full Plan on a Page template as markdown string with all sections and placeholder text.

---

### get_section_guidance

Get detailed guidance for a specific section of the template.

**Module:** `plan_template_knowledge.py`

**Function Signature:**
```python
def get_section_guidance(
    section_name: str
) -> Dict[str, Any]
```

**Parameters:**
- `section_name` (str, required): Name of the section

**Available Sections:**
- `"grl_section"` - G/R/L table and framework
- `"objectives_description"` - Marketing objectives and description
- `"key_messages"` - Key messages guidance
- `"activation_components"` - Activation component examples
- `"kpis_measurement"` - KPI and measurement guidance
- `"decision_framework"` - D/I/N framework
- `"investment_milestones"` - Investment and milestone guidance
- `"risks_blockers"` - Risk identification help

**Returns:**
```python
{
    "fields": List[str],                # Fields in this section
    "description": str,                 # What this section is for
    "best_practice": Union[str, List],  # Best practices
    "example": str,                     # Example (if applicable)
    "common_mistakes": List[str]        # Mistakes to avoid (if applicable)
}
```

---

### get_grl_framework_guide

Get comprehensive guidance on the G/R/L framework.

**Module:** `plan_template_knowledge.py`

**Function Signature:**
```python
def get_grl_framework_guide() -> Dict[str, Any]
```

**Returns:**
```python
{
    "purpose": str,                     # Why use G/R/L
    "when_to_use": str,                 # When to apply
    "benefits": List[str],              # Benefits of using
    "common_scenarios": Dict[str, Dict], # Scenario examples
    "decision_tree": Dict               # Decision framework
}
```

**Common Scenarios Include:**
- Global campaign with local execution
- Regional customization
- Local innovation

---

### get_section_prompts

Get specific prompts and guidance for a particular section of the plan.

**Module:** `plan_generator.py`

**Function Signature:**
```python
def get_section_prompts(
    section_name: str
) -> Dict[str, Any]
```

**Parameters:**
- `section_name` (str, required): Section name (`"grl"`, `"objectives"`, `"kpis"`, `"activation"`)

**Returns:**
```python
{
    "title": str,                       # Section title
    "purpose": str,                     # Purpose of section
    "questions": List[str],             # Questions to ask user
    "guidance": Dict,                   # Detailed guidance
    "tips": List[str],                  # Tips for completion
    "examples": List[str]               # Examples (if applicable)
}
```

---

### get_plan_template_blank

Return the blank Plan on a Page template.

**Module:** `plan_generator.py`

**Function Signature:**
```python
def get_plan_template_blank() -> str
```

**Returns:**
Blank template as markdown string.

---

## Utility Tools

### list_artifacts

List all uploaded artifacts/documents.

**Module:** `file_upload_supprt.py`

**Function Signature:**
```python
async def list_artifacts(
    tool_context: ToolContext = None
) -> dict
```

**Parameters:**
- `tool_context` (ToolContext, required): Tool context for artifact access

**Returns:**
```python
{
    "grounding_material": List[Dict]    # List of artifact data
}
```

---

### get_artifact

Retrieve a specific uploaded artifact by filename.

**Module:** `file_upload_supprt.py`

**Function Signature:**
```python
async def get_artifact(
    filename: str,
    tool_context: ToolContext = None
) -> dict
```

**Parameters:**
- `filename` (str, required): Name of the file to retrieve
- `tool_context` (ToolContext, required): Tool context

**Returns:**
```python
{
    "filename": str,
    "mime_type": str,
    "size_bytes": int,
    "data": str                         # Extracted text content
}
```

**Supported MIME Types:**
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (DOCX)
- `text/plain` (TXT)

---

### get_users_name

Get the authenticated user's name and email.

**Module:** `agent.py`

**Function Signature:**
```python
def get_users_name(
    tool_context: ToolContext
) -> dict
```

**Returns:**
```python
{
    "email": str,
    "name": str
}
```

---

### self_report

Report the agent version and capabilities.

**Module:** `agent.py`

**Function Signature:**
```python
def self_report() -> dict
```

**Returns:**
```python
{
    "name": str,                        # "Plan on a Page Agent"
    "version": str,                     # Version number
    "capabilities": List[str],          # List of capabilities
    "description": str                  # Agent description
}
```

---

## RAG-Enhanced Tools (Optional)

These tools are available only when RAG corpus is configured with `VERTEX_SEARCH_ENGINE_ID` and `RAG_CORPUS` environment variables. They search a corpus of example Plan on a Page documents to provide real-world patterns and guidance.

### plan_example_search

Search the corpus of example Plan on a Page documents for similar plans.

**Module:** `agent/tools/plan_rag_search_tool.py`

**Function Signature:**
```python
def search_example_plans(
    query: str,
    campaign_type: Optional[str] = None,
    geography: Optional[str] = None,
    top_k: int = 5
) -> Dict[str, Any]
```

**Parameters:**
- `query` (str, required): Natural language search query (e.g., "product launch plans with social media")
- `campaign_type` (str, optional): Filter by campaign type ("product_launch", "brand_campaign", "event")
- `geography` (str, optional): Filter by geography ("global", "emea", "apac", "americas")
- `top_k` (int, optional): Number of examples to return (default: 5)

**Returns:**
```python
{
    "rag_available": bool,              # Whether RAG is configured
    "query": str,                       # The search query used
    "filters": dict,                    # Applied filters
    "examples_found": int,              # Number of examples found
    "examples": List[dict],             # Retrieved example plans
    "patterns_extracted": List[str],    # Common patterns identified
    "source": str,                      # "rag_corpus"
    "message": str                      # Status or explanation
}
```

**Example:**
```python
results = plan_example_search(
    query="social media campaigns for product launches",
    campaign_type="product_launch",
    top_k=3
)
```

**Use Cases:**
- Compare user's plan against similar successful examples
- Show activation component patterns from similar campaigns
- Surface best practices during plan creation

---

### plan_grl_pattern_search

Find G/R/L (Global/Regional/Local) patterns from example plans for a specific activation component.

**Module:** `agent/tools/plan_rag_search_tool.py`

**Function Signature:**
```python
def find_grl_patterns(
    activation_component: str,
    campaign_type: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `activation_component` (str, required): The component to find patterns for (e.g., "Social Media", "Events")
- `campaign_type` (str, optional): Optional campaign type filter

**Returns:**
```python
{
    "rag_available": bool,              # Whether RAG is configured
    "activation_component": str,        # Component searched
    "campaign_type": Optional[str],     # Applied filter
    "patterns_found": int,              # Number of patterns found
    "common_patterns": List[dict],      # Frequent G/R/L approaches
    "example_assignments": List[dict],  # Real examples from corpus
    "adopt_adapt_invent_stats": dict,   # Statistics on A/A/I usage
    "source": str,                      # "rag_corpus"
    "message": str                      # Status message
}
```

**Example:**
```python
patterns = plan_grl_pattern_search(
    activation_component="Social Media",
    campaign_type="brand_campaign"
)
```

**Use Cases:**
- Show how similar campaigns handled G/R/L for specific components
- Display real Adopt/Adapt/Invent decisions from successful plans
- Guide users with proven patterns

---

### plan_similar_by_type

Retrieve complete example plans of a specific campaign type.

**Module:** `agent/tools/plan_rag_search_tool.py`

**Function Signature:**
```python
def get_similar_plans_by_type(
    campaign_type: str,
    additional_filters: Optional[Dict[str, str]] = None,
    top_k: int = 3
) -> Dict[str, Any]
```

**Parameters:**
- `campaign_type` (str, required): Type of campaign ("product_launch", "brand_campaign", "event", etc.)
- `additional_filters` (dict, optional): Additional filters (geography, industry, etc.)
- `top_k` (int, optional): Number of examples to return (default: 3)

**Returns:**
```python
{
    "rag_available": bool,              # Whether RAG is configured
    "campaign_type": str,               # Campaign type searched
    "filters": Optional[dict],          # Additional filters applied
    "examples_found": int,              # Number of examples found
    "examples": List[dict],             # Complete example plans
    "common_sections": dict,            # Analysis of section structures
    "source": str,                      # "rag_corpus"
    "message": str                      # Status message
}
```

**Example:**
```python
examples = plan_similar_by_type(
    campaign_type="product_launch",
    additional_filters={"geography": "global"},
    top_k=3
)
```

**Use Cases:**
- Inspire users with complete example plans
- Show section structure from successful campaigns
- Provide templates during guided creation

---

### plan_corpus_insights

Get statistical insights and aggregate data from the corpus of example plans.

**Module:** `agent/tools/plan_rag_search_tool.py`

**Function Signature:**
```python
def get_corpus_insights(
    section_name: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `section_name` (str, optional): Optional section to get insights for (e.g., "grl", "activation_components", "kpis")

**Returns:**
```python
{
    "rag_available": bool,              # Whether RAG is configured
    "section": Optional[str],           # Section analyzed
    "corpus_size": int,                 # Number of example plans in corpus
    "insights": dict,                   # Statistical insights
    "common_patterns": List[str],       # Most frequent patterns
    "source": str,                      # "rag_corpus"
    "message": str                      # Status message
}
```

**Example:**
```python
insights = plan_corpus_insights(section_name="grl")
```

**Use Cases:**
- Show aggregate patterns from all example plans
- Display common KPIs, activation components, etc.
- Provide data-driven best practices

---

**Note on RAG Availability:**
All RAG functions gracefully degrade when RAG is not configured:
- They return `rag_available: False` in the response
- They provide a fallback message
- Agent continues operating with embedded knowledge only
- No functionality is lost, just missing example enrichment

---

## Error Handling

All tools follow consistent error handling:

**Error Response Format:**
```python
{
    "error": str,                       # Error message
    "status": "error"
}
```

**Common Error Scenarios:**
- Missing required parameters → `"Please provide [parameter_name]"`
- Invalid input → `"Invalid [parameter]: [reason]"`
- Tool context required → `"Tool context required for [operation]"`
- External API failure → `"[Operation] failed: [error details]"`

---

## Best Practices

### Using Planning Tools Together

**Typical Workflow:**
```python
# 1. Start new plan or upload existing
result = generate_new_plan(project_name="Q3 Launch")

# 2. For each activation component, get G/R/L guidance
grl_help = guide_grl_assignment(
    activation_component="Social Media",
    creating_team="Global"
)

# 3. Get A/A/I recommendations
recommendation = suggest_adopt_adapt_invent(
    activation_component="Social Media",
    creating_geography="Global",
    target_geography="Regional"
)

# 4. Validate completeness
validation = validate_plan_completeness(plan_content)

# 5. Check for duplicates before finalizing
duplicates = search_similar_plans(
    project_name="Q3 Launch",
    tool_context=context
)

# 6. Format final output
formatted = format_plan_output(plan_data)
```

### Tool Selection Guide

| Use Case | Primary Tool | Supporting Tools |
|----------|-------------|------------------|
| Creating from scratch | `generate_new_plan` | `get_section_prompts`, `guide_grl_assignment` |
| Reviewing existing plan | `analyze_plan` | `get_grl_specific_feedback`, `quick_completeness_check` |
| G/R/L assignment help | `guide_grl_assignment` | `suggest_adopt_adapt_invent`, `get_grl_best_practices` |
| Final validation | `validate_plan_completeness` | `quick_completeness_check` |
| Avoiding duplicates | `search_similar_plans` | - |
| Getting template | `get_plan_template_blank` | `get_template`, `get_section_guidance` |

---

## Version History

**v1.0.0** - Initial release
- 18 specialized planning tools
- G/R/L framework support
- Duplicate detection
- Template-based validation

---

For additional support or questions, refer to the main README.md or contact the development team.
