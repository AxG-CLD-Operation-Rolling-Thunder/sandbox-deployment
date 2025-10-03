"""
Plan Generator Tool - Guides users through creating new Plan on a Page documents from scratch
"""
from typing import Dict, Any, Optional, List
from google.adk.tools import ToolContext
from ..prompts.plan_on_page_instructions import PLAN_GENERATOR_PROMPT
from .plan_template_knowledge import get_template, get_section_guidance

# Import RAG search functions (will be None if RAG not configured)
try:
    from .plan_rag_search_tool import plan_example_search, plan_similar_by_type
except ImportError:
    plan_example_search = None
    plan_similar_by_type = None


def generate_new_plan(
    project_name: Optional[str] = None,
    project_description: Optional[str] = None,
    objectives: Optional[str] = None,
    activation_components: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Guide users through creating a new Plan on a Page from scratch.

    This tool provides interactive, step-by-step guidance for creating a complete
    plan, with special focus on G/R/L assignments and the Adopt/Adapt/Invent framework.

    Args:
        project_name: Name of the project/campaign (optional, will prompt if not provided)
        project_description: Brief description (optional, will prompt if not provided)
        objectives: Marketing objectives (optional, will prompt if not provided)
        activation_components: List of activation channels/tactics (optional, will prompt if not provided)
        tool_context: Google ADK tool context

    Returns:
        Dict containing guidance prompts, next steps, and partial plan content
    """
    # Determine what stage of plan creation we're in
    stage = "initial"
    if project_name and project_description and objectives:
        stage = "activation_planning"
    elif project_name:
        stage = "basic_info"

    guidance_prompt = f"""
{PLAN_GENERATOR_PROMPT}

## Current Stage: {stage}

## Information Collected So Far:
{f"**Project Name:** {project_name}" if project_name else "**Project Name:** Not yet provided"}
{f"**Project Description:** {project_description}" if project_description else ""}
{f"**Objectives:** {objectives}" if objectives else ""}
{f"**Activation Components:** {', '.join(activation_components)}" if activation_components else ""}

## Next Steps:
Please guide the user through the next section of their Plan on a Page based on the current stage.
Be conversational, provide context for why each section matters, and ask 1-3 questions at a time.
"""

    try:
        # Use the tool context to get LLM response if available
        if tool_context and hasattr(tool_context, 'llm_client'):
            response = tool_context.llm_client.generate_content(guidance_prompt)
            guidance_text = response.text if hasattr(response, 'text') else str(response)
        else:
            # Fallback - provide structured guidance based on stage
            if stage == "initial":
                guidance_text = """
## Let's Create Your Plan on a Page!

I'll guide you through this step by step. Let's start with the foundation:

### 1. Project Basics

First, tell me about your initiative:

**Question 1:** What's the name of this project or campaign?

**Question 2:** In 1-3 sentences, what is this project? (What are you creating/launching?)

**Question 3:** What marketing objectives does this support? Which OKRs does this ladder to?

Once I have these basics, we'll move on to identifying your activation components and working through the G/R/L assignments together.
"""
            elif stage == "basic_info":
                guidance_text = f"""
## Great Start! Project: {project_name}

Now let's gather a bit more information before we dive into activation planning:

**Question 1:** Who is the Executive Sponsor for this initiative? (Full name)

**Question 2:** Who is the Project Lead? (Full name)

**Question 3:** Who is the target audience? Be specific - not just "developers" but perhaps "senior developers at enterprise companies" or "marketing decision-makers at mid-size businesses"

**Question 4:** Why does this matter to them? What problem does it solve or opportunity does it provide?

After this, we'll identify your activation components and work through the critical G/R/L (Global/Regional/Local) assignments.
"""
            elif stage == "activation_planning":
                guidance_text = f"""
## Excellent! Now Let's Plan Your Activation Components

Activation components are the channels and tactics you'll use to reach your audience.

**Common examples:**
- Social media (LinkedIn, Twitter, etc.)
- Content marketing (blogs, whitepapers, videos)
- Events (conferences, webinars, workshops)
- Paid advertising (Google Ads, display, social)
- PR and thought leadership
- Email campaigns
- Partner co-marketing
- Out-of-home (OOH) advertising

**Question:** What are the 3-7 key activation components for your campaign?

{f"You mentioned: {', '.join(activation_components)}. Let's work with these." if activation_components else ""}

Once we have your components, we'll go through each one and determine the G/R/L (Global/Regional/Local) assignments using the Adopt/Adapt/Invent framework. This is THE most important part for ensuring cross-team alignment!
"""

                # Add RAG-based examples from similar campaigns if available
                if plan_example_search is not None and project_description:
                    # Try to detect campaign type from description
                    campaign_type = None
                    desc_lower = project_description.lower()
                    if 'product launch' in desc_lower or 'launching' in desc_lower:
                        campaign_type = 'product_launch'
                    elif 'brand' in desc_lower or 'awareness' in desc_lower:
                        campaign_type = 'brand_campaign'
                    elif 'event' in desc_lower or 'conference' in desc_lower:
                        campaign_type = 'event'

                    if campaign_type:
                        try:
                            rag_results = plan_example_search(
                                query=f"activation components for {campaign_type}",
                                campaign_type=campaign_type,
                                top_k=3
                            )

                            if rag_results.get('rag_available') and rag_results.get('examples_found', 0) > 0:
                                guidance_text += f"""

### Examples from Similar Campaigns

Based on {rag_results.get('examples_found', 0)} similar {campaign_type.replace('_', ' ')} plans in our knowledge base, here are common activation patterns that worked well:

{rag_results.get('message', 'Reviewing similar campaign approaches...')}
"""
                        except Exception as e:
                            # RAG search failed, continue without it
                            pass
            else:
                guidance_text = "Let's continue building your plan. What information would you like to add next?"

        # Build partial plan based on what we have
        partial_plan = _build_partial_plan(
            project_name=project_name,
            project_description=project_description,
            objectives=objectives,
            activation_components=activation_components
        )

        return {
            "guidance": guidance_text,
            "stage": stage,
            "partial_plan": partial_plan,
            "fields_collected": {
                "project_name": bool(project_name),
                "project_description": bool(project_description),
                "objectives": bool(objectives),
                "activation_components": bool(activation_components)
            },
            "next_steps": _get_next_steps(stage),
            "status": "in_progress"
        }

    except Exception as e:
        return {
            "error": f"Plan generation guidance failed: {str(e)}",
            "guidance": "Please provide the project name to get started.",
            "status": "error"
        }


def _build_partial_plan(
    project_name: Optional[str] = None,
    project_description: Optional[str] = None,
    objectives: Optional[str] = None,
    activation_components: Optional[List[str]] = None,
    executive_sponsor: Optional[str] = None,
    project_lead: Optional[str] = None
) -> str:
    """Build a partial plan document based on collected information."""

    plan = f"Plan On a Page: **{project_name or '[Project Name - To Be Provided]'}**\n\n"
    plan += f"**Executive Sponsor:** {executive_sponsor or '[To Be Provided]'}\n\n"
    plan += f"**Project Lead:** {project_lead or '[To Be Provided]'}\n\n"
    plan += "**Project Manager:** [To Be Provided]\n\n"
    plan += "**Vendor / Agency Details:** [If applicable]\n\n"
    plan += "**Internal Creative Team(s):** [If applicable]\n\n"
    plan += "**D/I/N:** [To Be Completed]\n\n"

    plan += "**G/R/L Table:**\n\n"
    plan += "| Geography | Lead Name | Notes (Adopt/Adapt/Invent) |\n"
    plan += "|-----------|-----------|---------------------------|\n"
    plan += "| Global:   | [TBD]     | [TBD]                     |\n"
    plan += "| Regional: | [TBD]     | [TBD]                     |\n"
    plan += "| Local:    | [TBD]     | [TBD]                     |\n\n"

    plan += f"**Marketing objectives:** {objectives or '[To Be Provided - 1-2 sentences on OKRs this ladders to]'}\n\n"
    plan += f"**Project description:** {project_description or '[To Be Provided - 1-3 sentence description]'}\n\n"
    plan += "**Audience:** [To Be Provided]\n\n"
    plan += "**Key messages:** [To Be Provided - 2-4 key messages]\n\n"
    plan += "**Investment:** [$ and FTEs]\n\n"
    plan += "**Milestones | Key activities:**\n[Deliverable/Activity] | [Date]\n\n"
    plan += "**Risks / Blockers:**\n[To Be Identified]\n\n"

    if activation_components:
        plan += "**Activation Components:**\n"
        for component in activation_components:
            plan += f"- {component}\n"
    else:
        plan += "**Activation Components:**\n[To Be Identified]\n"

    plan += "\n**KPIs, Anticipated Impact & Measurement:**\n[To Be Provided - Quantified metrics]\n"

    return plan


def _get_next_steps(stage: str) -> List[str]:
    """Get recommended next steps based on current stage."""
    steps_by_stage = {
        "initial": [
            "Provide project name and basic description",
            "State marketing objectives and OKR alignment",
            "Identify target audience"
        ],
        "basic_info": [
            "Name Executive Sponsor and Project Lead",
            "Define target audience specifically",
            "Identify activation components"
        ],
        "activation_planning": [
            "List 3-7 activation components",
            "Work through G/R/L assignments for each component",
            "Apply Adopt/Adapt/Invent framework"
        ],
        "grl_assignment": [
            "Name leads for Global, Regional, and Local",
            "Specify Adopt/Adapt/Invent for each activation component",
            "Add notes explaining rationale for assignments"
        ],
        "details": [
            "Complete D/I/N roles",
            "Add key messages (2-4)",
            "Specify investment ($$ and FTEs)",
            "Define milestones with dates"
        ],
        "measurement": [
            "Define KPIs with quantified targets",
            "List risks and blockers",
            "Add vendor/agency details if applicable"
        ]
    }

    return steps_by_stage.get(stage, ["Continue providing information for remaining sections"])


def get_section_prompts(section_name: str, campaign_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get specific prompts and guidance for a particular section of the plan.

    Args:
        section_name: Name of the section (e.g., 'grl', 'objectives', 'kpis')
        campaign_type: Optional campaign type for RAG-based example retrieval

    Returns:
        Dict containing prompts and guidance for that section
    """
    section_prompts = {
        "grl": {
            "title": "G/R/L (Global/Regional/Local) Assignment",
            "purpose": "Define which teams lead and how work is distributed across geographies",
            "questions": [
                "Who is the Global lead for this initiative? (Full name)",
                "Who is the Regional lead? (Full name)",
                "Who is the Local lead? (Full name)",
                "For each activation component, which team creates the work?",
                "Will other teams Adopt (use as-is), Adapt (modify), or Invent (create new)?"
            ],
            "guidance": get_section_guidance("grl_section"),
            "tips": [
                "Name specific individuals, not teams",
                "Default to Adopt when possible for efficiency",
                "Use Adapt for localization (translation, cultural tuning)",
                "Use Invent only when truly necessary",
                "Add notes explaining the rationale"
            ]
        },
        "objectives": {
            "title": "Marketing Objectives",
            "purpose": "Explain how this initiative supports broader marketing goals",
            "questions": [
                "Which specific OKRs does this ladder to?",
                "How does this initiative contribute to those OKRs?"
            ],
            "guidance": get_section_guidance("objectives_description"),
            "example": "Support Q2 brand awareness OKR by driving 500K impressions and 50K engagements among target technical audience"
        },
        "kpis": {
            "title": "KPIs, Anticipated Impact & Measurement",
            "purpose": "Define quantified success metrics",
            "questions": [
                "What are 3-5 key metrics you'll track?",
                "What are the specific numeric targets?",
                "How will you measure these?"
            ],
            "guidance": get_section_guidance("kpis_measurement"),
            "tips": [
                "Make them quantified (numbers, not vague goals)",
                "Tie to business outcomes",
                "Specify measurement methodology"
            ]
        },
        "activation": {
            "title": "Activation Components",
            "purpose": "Define the channels and tactics to reach your audience",
            "questions": [
                "What channels will you use to reach your audience?",
                "What tactics within each channel?"
            ],
            "examples": [
                "Social media: LinkedIn thought leadership posts (3x/week)",
                "Events: Webinar series (monthly for Q2-Q3)",
                "Content: Technical blog posts and whitepapers"
            ],
            "guidance": get_section_guidance("activation_components")
        }
    }

    result = section_prompts.get(section_name, {
        "error": f"Section '{section_name}' not found",
        "available_sections": list(section_prompts.keys())
    })

    # Enrich with RAG examples if available
    if plan_similar_by_type is not None and campaign_type and section_name in section_prompts:
        try:
            rag_results = plan_similar_by_type(
                campaign_type=campaign_type,
                top_k=3
            )

            if rag_results.get('rag_available') and rag_results.get('examples_found', 0) > 0:
                result['rag_examples'] = {
                    'available': True,
                    'count': rag_results.get('examples_found', 0),
                    'message': f"Found {rag_results.get('examples_found', 0)} example {campaign_type} plans showing how this section is typically structured",
                    'source': 'rag_corpus'
                }
            elif rag_results.get('rag_available'):
                result['rag_examples'] = {
                    'available': True,
                    'count': 0,
                    'message': 'RAG corpus available but no examples found for this campaign type',
                    'source': 'rag_corpus'
                }
        except Exception as e:
            # RAG search failed, continue without it
            pass

    return result


def get_plan_template_blank() -> str:
    """
    Return the blank Plan on a Page template.

    Returns:
        String containing the blank template
    """
    return get_template()
