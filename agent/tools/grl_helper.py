"""
G/R/L Helper Tool - Specialized assistance for Global/Regional/Local section and Adopt/Adapt/Invent framework
"""
from typing import Dict, Any, Optional, List
from google.adk.tools import ToolContext
from ..prompts.plan_on_page_instructions import GRL_HELPER_PROMPT
from .plan_template_knowledge import get_grl_framework_guide

# Import RAG search functions (will be None if RAG not configured)
try:
    from .plan_rag_search_tool import plan_grl_pattern_search
except ImportError:
    plan_grl_pattern_search = None


def guide_grl_assignment(
    activation_component: str,
    component_description: Optional[str] = None,
    creating_team: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Interactive guidance for assigning G/R/L (Global/Regional/Local) roles for an activation component.

    This tool helps users think through which geography leads, which teams Adopt/Adapt/Invent,
    and ensures proper documentation of the decisions.

    Args:
        activation_component: The activation component to assign (e.g., "Social Media", "Events")
        component_description: Optional description of what this component entails
        creating_team: Which team is creating/leading this work (Global, Regional, or Local)
        tool_context: Google ADK tool context

    Returns:
        Dict containing guidance questions and framework application
    """
    if not activation_component:
        return {
            "error": "Please specify the activation component you're assigning",
            "examples": ["Social Media", "Content Marketing", "Events", "Paid Advertising"]
        }

    framework_guide = get_grl_framework_guide()

    guidance_prompt = f"""
{GRL_HELPER_PROMPT}

## Current Activation Component: {activation_component}

{f"Description: {component_description}" if component_description else ""}
{f"Creating Team: {creating_team}" if creating_team else ""}

Please provide interactive guidance to help the user complete the G/R/L assignment for this component,
asking questions about:
1. Which geography is leading/creating this work
2. For other geographies, will they Adopt, Adapt, or Invent
3. Who are the named leads for each geography
4. What notes should be captured about this assignment

Keep the conversation flowing and help them think through the best approach.
"""

    try:
        if tool_context and hasattr(tool_context, 'llm_client'):
            response = tool_context.llm_client.generate_content(guidance_prompt)
            guidance_text = response.text if hasattr(response, 'text') else str(response)
        else:
            # Fallback - structured guidance
            guidance_text = f"""
## G/R/L Assignment for: {activation_component}

Let's work through this systematically using the Adopt/Adapt/Invent framework.

### Step 1: Which team is creating this work?

{f"You indicated: **{creating_team}** is creating this work." if creating_team else "**Question:** Is Global, Regional, or Local creating the {activation_component} work?"}

### Step 2: What will the other teams do?

For the teams NOT creating this work, they can:
- **Adopt**: Use the work exactly as created (most efficient)
- **Adapt**: Modify for local needs (translation, cultural adaptation, local examples)
- **Invent**: Create entirely new work (only when market needs are unique)

**Questions:**
{f"- Will Regional teams Adopt, Adapt, or Invent for {activation_component}?" if creating_team != "Regional" else ""}
{f"- Will Local markets Adopt, Adapt, or Invent for {activation_component}?" if creating_team != "Local" else ""}
{f"- Will Global Adopt, Adapt, or Invent for {activation_component}?" if creating_team not in ["Global", None] else ""}

### Step 3: Name the leads

**Questions:**
- Who is the Global lead? (Full name)
- Who is the Regional lead? (Full name)
- Who is the Local lead? (Full name)

### Step 4: Add context notes

**Question:** Any important notes to capture?
- Dependencies between teams?
- Timeline considerations?
- Special requirements?
- Cultural or market-specific needs?

### Framework Guidance:

{framework_guide.get('purpose', '')}

**Common Patterns:**
- **Global creates, Regional/Local Adopt**: Consistent global messaging
- **Global creates, Regional Adapts, Local Adopts**: Regional customization with local consistency
- **Regional creates, Local Adapts**: Regional campaigns with local flavors
- **Local Invents**: Truly unique market opportunities

**Best Practice:** Default to Adopt when possible, use Adapt for localization, Invent only when necessary.
"""

        # Add RAG-based G/R/L patterns from example plans if available
        rag_patterns = None
        if plan_grl_pattern_search is not None:
            try:
                rag_results = plan_grl_pattern_search(
                    activation_component=activation_component,
                    campaign_type=None  # Could be enhanced by passing campaign type
                )

                if rag_results.get('rag_available'):
                    rag_patterns = {
                        'available': True,
                        'patterns_found': rag_results.get('patterns_found', 0),
                        'message': rag_results.get('message', 'RAG patterns available')
                    }

                    if rag_results.get('patterns_found', 0) > 0:
                        guidance_text += f"""

### Real-World Patterns from Example Plans

Found {rag_results.get('patterns_found', 0)} examples of G/R/L assignments for **{activation_component}** in our knowledge base.

{rag_results.get('message', 'Reviewing how similar campaigns handled this component...')}
"""
            except Exception as e:
                # RAG search failed, continue without it
                pass

        return {
            "guidance": guidance_text,
            "activation_component": activation_component,
            "framework_info": framework_guide,
            "rag_patterns": rag_patterns,
            "next_steps": [
                "Identify which team (G/R/L) creates the work",
                "Determine Adopt/Adapt/Invent for other teams",
                "Name specific leads for each geography",
                "Document rationale and dependencies"
            ],
            "status": "guidance_provided"
        }

    except Exception as e:
        return {
            "error": f"G/R/L guidance failed: {str(e)}",
            "status": "error"
        }


def suggest_adopt_adapt_invent(
    activation_component: str,
    creating_geography: str,
    target_geography: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Suggest whether a geography should Adopt, Adapt, or Invent for a specific component.

    Args:
        activation_component: The component being assigned (e.g., "Social Media")
        creating_geography: Geography creating the work (Global/Regional/Local)
        target_geography: Geography receiving the assignment (Global/Regional/Local)
        context: Additional context about market needs, existing work, etc.

    Returns:
        Dict containing recommendation and rationale
    """
    if creating_geography == target_geography:
        return {
            "recommendation": "CREATE",
            "rationale": f"{target_geography} is the creating team for this component",
            "status": "n/a"
        }

    # Simple heuristic-based recommendations
    recommendations = {
        ("Global", "Regional"): {
            "default": "ADAPT",
            "rationale": "Regional teams typically adapt global work for regional markets (language, cultural relevance)"
        },
        ("Global", "Local"): {
            "default": "ADOPT",
            "rationale": "Local teams often adopt global or regional work to maintain consistency and efficiency"
        },
        ("Regional", "Local"): {
            "default": "ADOPT",
            "rationale": "Local teams typically adopt regional work when it's already customized for the region"
        },
        ("Regional", "Global"): {
            "default": "N/A",
            "rationale": "Regional work typically doesn't flow back to Global, but can inspire global initiatives"
        },
        ("Local", "Global"): {
            "default": "N/A",
            "rationale": "Local work typically doesn't flow to Global, but successful local innovations can be evaluated for scaling"
        },
        ("Local", "Regional"): {
            "default": "N/A",
            "rationale": "Local work is market-specific and typically not adopted by Regional"
        }
    }

    key = (creating_geography, target_geography)
    recommendation_data = recommendations.get(key, {
        "default": "EVALUATE",
        "rationale": "Consider whether this work can be reused or needs to be created fresh"
    })

    # Adjust based on context if provided
    considerations = []
    if context:
        context_lower = context.lower()
        if any(word in context_lower for word in ["translation", "language", "localize"]):
            considerations.append("Translation/localization needs suggest ADAPT")
        if any(word in context_lower for word in ["unique", "different", "special"]):
            considerations.append("Unique market needs may warrant INVENT")
        if any(word in context_lower for word in ["same", "consistent", "standard"]):
            considerations.append("Consistency requirements favor ADOPT")

    return {
        "activation_component": activation_component,
        "creating_geography": creating_geography,
        "target_geography": target_geography,
        "recommendation": recommendation_data["default"],
        "rationale": recommendation_data["rationale"],
        "considerations": considerations if considerations else None,
        "framework": {
            "ADOPT": "Use the work exactly as created (most efficient)",
            "ADAPT": "Modify for local market needs (translation, cultural tuning)",
            "INVENT": "Create new work specific to this market (only when necessary)"
        },
        "questions_to_ask": [
            f"Can {target_geography} use the {creating_geography} work as-is?",
            f"What modifications would {target_geography} need to make?",
            f"Are {target_geography}'s needs so unique that new work is required?"
        ]
    }


def format_grl_table_entry(
    global_lead: str,
    regional_lead: str,
    local_lead: str,
    global_notes: str,
    regional_notes: str,
    local_notes: str
) -> str:
    """
    Format a complete G/R/L table entry with all information.

    Args:
        global_lead: Name of Global lead
        regional_lead: Name of Regional lead
        local_lead: Name of Local lead
        global_notes: Notes for Global (including Adopt/Adapt/Invent)
        regional_notes: Notes for Regional
        local_notes: Notes for Local

    Returns:
        Formatted G/R/L table as markdown string
    """
    table = "**G/R/L**\t\t\t\t        **Notes including Adopt, Adapt, Invent**\n\n"
    table += "| Global: " + global_lead + " | " + global_notes + " |\n"
    table += "| :---- | :---- |\n"
    table += "| Regional: " + regional_lead + " | " + regional_notes + " |\n"
    table += "| Local: " + local_lead + " | " + local_notes + " |\n"

    return table


def get_grl_best_practices(campaign_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get best practices and common patterns for G/R/L assignments.

    Args:
        campaign_type: Optional campaign type for RAG-based pattern enrichment

    Returns:
        Dict containing best practices, patterns, and examples
    """
    result = {
        "core_principles": [
            "Name specific individuals, not teams or roles",
            "Default to Adopt when possible for efficiency",
            "Use Adapt for localization (language, culture, examples)",
            "Use Invent only when market needs are truly unique",
            "Document rationale for each assignment in notes",
            "Map each activation component to G/R/L in the notes"
        ],
        "common_patterns": {
            "global_campaign": {
                "pattern": "Global creates, Regional adapts, Local adopts",
                "example": "Global creates social content in English, Regional translates and adapts for cultural relevance, Local markets adopt regional versions",
                "activation_components": ["Social media", "Digital advertising", "Email campaigns"]
            },
            "regional_initiative": {
                "pattern": "Regional creates, Local adopts or adapts",
                "example": "EMEA creates event strategy, local markets adopt and execute with local vendors",
                "activation_components": ["Events", "Regional PR", "Partner marketing"]
            },
            "local_innovation": {
                "pattern": "Local invents, evaluate for regional/global scaling",
                "example": "Japan creates unique partnership program, monitors success for potential regional expansion",
                "activation_components": ["Local partnerships", "Market-specific channels", "Cultural initiatives"]
            },
            "hybrid_approach": {
                "pattern": "Mix of Adopt/Adapt/Invent across different components",
                "example": "Adopt global messaging, Adapt content format, Invent local activation channels",
                "activation_components": "Varies by component"
            }
        },
        "decision_framework": {
            "step_1": {
                "question": "Does existing work from another geography fully meet your needs?",
                "if_yes": "ADOPT",
                "if_partially": "Go to step 2",
                "if_no": "Go to step 3"
            },
            "step_2": {
                "question": "What modifications are needed? (Translation, cultural adaptation, format changes)",
                "action": "ADAPT - specify what changes are needed in notes"
            },
            "step_3": {
                "question": "Are your market needs truly unique, or could you modify existing work?",
                "if_unique": "INVENT - but document why existing work won't work",
                "if_adaptable": "Go back to step 2 and ADAPT"
            }
        },
        "common_mistakes": [
            "Not naming specific individuals (using 'team' or 'TBD')",
            "Not specifying Adopt/Adapt/Invent for each component",
            "Missing notes explaining rationale",
            "Defaulting to Invent when Adopt or Adapt would work",
            "Not mapping activation components to G/R/L roles"
        ],
        "quality_checklist": [
            "✓ Named lead for Global (full name)",
            "✓ Named lead for Regional (full name)",
            "✓ Named lead for Local (full name)",
            "✓ Each activation component has G/R/L assignment",
            "✓ Adopt/Adapt/Invent specified for each geography and component",
            "✓ Notes explain rationale for assignments",
            "✓ Dependencies between teams are documented",
            "✓ No 'TBD' or vague descriptions remain"
        ]
    }

    # Enrich with RAG corpus insights if available
    if plan_grl_pattern_search is not None and campaign_type:
        try:
            rag_results = plan_grl_pattern_search(
                activation_component="general G/R/L patterns",
                campaign_type=campaign_type
            )

            if rag_results.get('rag_available'):
                result['rag_corpus_insights'] = {
                    'available': True,
                    'campaign_type': campaign_type,
                    'patterns_found': rag_results.get('patterns_found', 0),
                    'message': rag_results.get('message', 'Corpus insights available'),
                    'source': 'rag_corpus'
                }

                if rag_results.get('patterns_found', 0) > 0:
                    result['rag_corpus_insights']['note'] = f"Knowledge base contains {rag_results.get('patterns_found', 0)} example plans for {campaign_type} campaigns with real G/R/L patterns"
        except Exception as e:
            # RAG search failed, continue without it
            pass

    return result
