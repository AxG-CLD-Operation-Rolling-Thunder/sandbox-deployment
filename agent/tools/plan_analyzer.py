"""
Plan Analyzer Tool - Analyzes existing Plan on a Page documents for completeness and quality
"""
from typing import Dict, Any, Optional, List
from google.adk.tools import ToolContext
from ..prompts.plan_on_page_instructions import PLAN_ANALYZER_PROMPT
from .plan_template_knowledge import get_quality_checklist, get_common_mistakes

# Import RAG search functions (will be None if RAG not configured)
try:
    from .plan_rag_search_tool import plan_example_search
except ImportError:
    plan_example_search = None


def analyze_plan(
    plan_content: str,
    focus_area: str = "all",
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Analyze an existing Plan on a Page document and provide comprehensive feedback.

    This tool reviews uploaded or pasted plan content, identifies gaps and ambiguities,
    and provides specific recommendations for improvement, with special focus on
    the G/R/L section.

    Args:
        plan_content: The full text content of the Plan on a Page document
        focus_area: Specific area to focus on ('all', 'grl', 'completeness', 'clarity')
        tool_context: Google ADK tool context

    Returns:
        Dict containing analysis results, gaps identified, and improvement suggestions
    """
    if not plan_content or not plan_content.strip():
        return {
            "error": "Please provide plan content to analyze",
            "suggestions": [],
            "completeness_score": 0,
            "status": "error"
        }

    # Check for required sections
    required_sections = [
        "Project name", "Executive Sponsor", "Project Lead", "Project Manager",
        "D/I/N", "G/R/L", "Marketing objectives", "Project description",
        "Audience", "Key messages", "Investment", "Milestones",
        "Risks", "Activation Components", "KPIs"
    ]

    missing_sections = []
    present_sections = []

    for section in required_sections:
        # Simple keyword matching - could be enhanced
        if section.lower() in plan_content.lower():
            present_sections.append(section)
        else:
            missing_sections.append(section)

    completeness_score = len(present_sections)
    total_sections = len(required_sections)

    # Construct the analysis prompt
    analysis_prompt = f"""
{PLAN_ANALYZER_PROMPT}

## Plan Content to Analyze:

{plan_content}

## Initial Assessment:
- Sections found: {len(present_sections)}/{total_sections}
- Present: {', '.join(present_sections[:10])}
- Missing or unclear: {', '.join(missing_sections) if missing_sections else 'None identified'}

## Focus Area:
{focus_area if focus_area != 'all' else 'Comprehensive analysis of all sections'}

Please provide your detailed analysis following the specified format. Pay special attention to:
1. The G/R/L section - is it complete with leads named and Adopt/Adapt/Invent specified?
2. Are activation components clearly mapped to G/R/L assignments?
3. Are objectives tied to specific OKRs?
4. Are KPIs quantified?
"""

    try:
        # Use the tool context to get LLM response if available
        if tool_context and hasattr(tool_context, 'llm_client'):
            response = tool_context.llm_client.generate_content(analysis_prompt)
            analysis_text = response.text if hasattr(response, 'text') else str(response)
        else:
            # Fallback - return structured template
            quality_checklist = get_quality_checklist()
            common_mistakes = get_common_mistakes()

            analysis_text = f"""
## Plan Analysis Results

### Completeness Score: {completeness_score}/{total_sections} sections identified

**Present Sections:** {', '.join(present_sections)}
**Missing Sections:** {', '.join(missing_sections) if missing_sections else 'All sections appear to be present'}

### Top Gaps and Improvement Opportunities:

1. **G/R/L Section Quality**
   - Check if specific lead names are provided for Global, Regional, and Local
   - Verify that Adopt/Adapt/Invent framework is applied
   - Ensure activation components are mapped to G/R/L assignments
   - Add detailed notes explaining rationale for each assignment

2. **Specificity and Clarity**
   - Replace any "TBD" or vague placeholders with specific information
   - Ensure dates are actual dates (not "Q2" or "upcoming")
   - Verify that individual names are used (not team names)
   - Make sure KPIs include quantified targets

3. **Strategic Alignment**
   - Confirm marketing objectives explicitly state OKR alignment
   - Verify audience is specific (not generic like "developers")
   - Check that key messages are memorable and actionable
   - Ensure activation components are concrete and channel-specific

### G/R/L Section Assessment:

**Critical Questions to Address:**
- Is there a named lead for Global? For Regional? For Local?
- For each activation component, is it clear which team leads and which teams Adopt/Adapt/Invent?
- Are there explanatory notes in the G/R/L table?
- Are dependencies between teams documented?

### Quality Checklist Items to Verify:

**Completeness:**
{chr(10).join(f'- {item}' for item in quality_checklist.get('completeness', []))}

**G/R/L Quality:**
{chr(10).join(f'- {item}' for item in quality_checklist.get('grl_quality', []))}

**Clarity:**
{chr(10).join(f'- {item}' for item in quality_checklist.get('clarity', []))}

### Recommended Next Steps:

1. **Address missing sections** - Fill in any blank or TBD sections
2. **Clarify G/R/L assignments** - Name leads and specify Adopt/Adapt/Invent for each component
3. **Add quantified metrics** - Ensure KPIs have specific numbers and targets
4. **Document dependencies** - Note any cross-team dependencies or blockers
5. **Validate alignment** - Confirm plan aligns with stated OKRs

### Questions to Clarify with Stakeholders:

1. Who are the specific named leads for Global, Regional, and Local execution?
2. For each activation component, which team will create the work and which will Adopt/Adapt/Invent?
3. What are the specific, quantified KPI targets for this initiative?
"""

            # Optional: Add RAG-based comparison with example plans
            if plan_example_search is not None:
                # Try to identify campaign type from content for better RAG search
                campaign_type = None
                if 'product launch' in plan_content.lower():
                    campaign_type = 'product_launch'
                elif 'brand campaign' in plan_content.lower():
                    campaign_type = 'brand_campaign'
                elif 'event' in plan_content.lower():
                    campaign_type = 'event'

                try:
                    rag_results = plan_example_search(
                        query="similar successful plans",
                        campaign_type=campaign_type,
                        top_k=3
                    )

                    if rag_results.get('rag_available') and rag_results.get('examples'):
                        analysis_text += f"""

### Comparison with Example Plans (from RAG corpus):

Based on {rag_results.get('examples_found', 0)} similar example plans:
- Common patterns and best practices from successful plans
- How similar campaigns structured their G/R/L assignments
- Typical activation components and KPIs for this campaign type

**RAG Insights:** {rag_results.get('message', 'Example plans analyzed')}
"""
                    elif rag_results.get('rag_available'):
                        analysis_text += "\n\n**Note:** RAG corpus search available but no directly comparable examples found."
                except Exception as e:
                    # RAG search failed, continue without it
                    pass

        return {
            "analysis": analysis_text,
            "completeness_score": f"{completeness_score}/{total_sections}",
            "present_sections": present_sections,
            "missing_sections": missing_sections,
            "focus_area": focus_area,
            "status": "completed",
            "recommendations": {
                "priority_1": "Complete G/R/L section with named leads and Adopt/Adapt/Invent assignments",
                "priority_2": "Fill in any missing or TBD sections with specific information",
                "priority_3": "Add quantified KPIs and specific dates to milestones"
            }
        }

    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "suggestions": [],
            "completeness_score": f"{completeness_score}/{total_sections}",
            "status": "error"
        }


def quick_completeness_check(plan_content: str) -> Dict[str, Any]:
    """
    Perform a quick check for basic completeness of required sections.

    Args:
        plan_content: The plan text to check

    Returns:
        Dict with completeness results and missing sections
    """
    if not plan_content:
        return {"error": "No content provided", "complete": False}

    required_keywords = {
        "project_name": ["project name", "plan on a page:"],
        "executive_sponsor": ["executive sponsor"],
        "project_lead": ["project lead"],
        "din": ["d/i/n", "decide", "input", "notify"],
        "grl": ["g/r/l", "global:", "regional:", "local:"],
        "objectives": ["marketing objectives", "okr"],
        "audience": ["audience"],
        "key_messages": ["key messages"],
        "investment": ["investment"],
        "milestones": ["milestones", "key activities"],
        "risks": ["risks", "blockers"],
        "activation": ["activation components"],
        "kpis": ["kpis", "measurement", "impact"]
    }

    content_lower = plan_content.lower()
    results = {}
    missing = []

    for section, keywords in required_keywords.items():
        found = any(keyword in content_lower for keyword in keywords)
        results[section] = found
        if not found:
            missing.append(section)

    completeness_pct = (len([v for v in results.values() if v]) / len(results)) * 100

    return {
        "complete": len(missing) == 0,
        "completeness_percentage": round(completeness_pct, 1),
        "sections_found": [k for k, v in results.items() if v],
        "sections_missing": missing,
        "details": results
    }


def get_grl_specific_feedback(plan_content: str) -> Dict[str, Any]:
    """
    Provide focused feedback specifically on the G/R/L section.

    Args:
        plan_content: The plan content containing G/R/L section

    Returns:
        Dict with G/R/L-specific analysis and recommendations
    """
    if not plan_content:
        return {"error": "No content provided"}

    content_lower = plan_content.lower()

    # Check for G/R/L presence
    has_grl_section = "g/r/l" in content_lower or ("global:" in content_lower and "regional:" in content_lower)

    if not has_grl_section:
        return {
            "has_grl_section": False,
            "message": "G/R/L section not found in the plan. This is a critical section for cross-geography alignment.",
            "recommendation": "Add a G/R/L table with named leads for Global, Regional, and Local, along with Adopt/Adapt/Invent assignments for each activation component."
        }

    # Check for key elements
    checks = {
        "has_global_lead": "global:" in content_lower and any(word in content_lower for word in ["lead", "name", "owner"]),
        "has_regional_lead": "regional:" in content_lower and any(word in content_lower for word in ["lead", "name", "owner"]),
        "has_local_lead": "local:" in content_lower and any(word in content_lower for word in ["lead", "name", "owner"]),
        "has_adopt": "adopt" in content_lower,
        "has_adapt": "adapt" in content_lower,
        "has_invent": "invent" in content_lower,
        "has_notes": len(plan_content) > 200  # Rough proxy for having detailed notes
    }

    issues = []
    if not checks["has_global_lead"]:
        issues.append("Global lead name not clearly specified")
    if not checks["has_regional_lead"]:
        issues.append("Regional lead name not clearly specified")
    if not checks["has_local_lead"]:
        issues.append("Local lead name not clearly specified")
    if not (checks["has_adopt"] or checks["has_adapt"] or checks["has_invent"]):
        issues.append("Adopt/Adapt/Invent framework not applied")

    quality_score = (sum(checks.values()) / len(checks)) * 10

    return {
        "has_grl_section": True,
        "quality_score": round(quality_score, 1),
        "checks_passed": checks,
        "issues_identified": issues,
        "recommendation": "Ensure each geography has a named lead, and for each activation component, specify which team will Adopt, Adapt, or Invent. Add detailed notes explaining the rationale." if issues else "G/R/L section looks comprehensive. Verify that notes explain the rationale for each assignment.",
        "status": "needs_improvement" if issues else "good"
    }
