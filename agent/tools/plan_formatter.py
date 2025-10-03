"""
Plan Formatter Tool - Formats Plan on a Page documents according to the standard template
"""
from typing import Dict, Any, Optional, List
from .plan_template_knowledge import PLAN_TEMPLATE


def format_plan_output(
    plan_data: Dict[str, Any],
    output_format: str = "markdown"
) -> Dict[str, Any]:
    """
    Format a complete Plan on a Page document according to the standard template.

    Takes structured plan data and formats it into a polished, template-compliant
    markdown document ready for submission.

    Args:
        plan_data: Dictionary containing all plan sections and data
        output_format: Output format ('markdown', 'plain_text')

    Returns:
        Dict containing formatted plan and metadata
    """
    if not plan_data:
        return {
            "error": "No plan data provided to format",
            "status": "error"
        }

    try:
        formatted_plan = _build_formatted_plan(plan_data)

        return {
            "formatted_plan": formatted_plan,
            "output_format": output_format,
            "sections_included": list(plan_data.keys()),
            "word_count": len(formatted_plan.split()),
            "status": "completed"
        }

    except Exception as e:
        return {
            "error": f"Formatting failed: {str(e)}",
            "status": "error"
        }


def _build_formatted_plan(data: Dict[str, Any]) -> str:
    """Build the formatted plan from structured data."""

    plan = f"Plan On a Page: **{data.get('project_name', '[Project Name]')}**\n\n"

    # Leadership & Teams
    plan += f"**Executive Sponsor:** {data.get('executive_sponsor', '[Name]')}\n\n"
    plan += f"**Project Lead:** {data.get('project_lead', '[Name]')}\n\n"
    plan += f"**Project Manager:** {data.get('project_manager', '[Name]')}\n\n"

    # Vendor/Agency
    vendor_info = data.get('vendor_agency', '[If using agency / vendor to deliver the work, list the name, describe services that will be provided; confirm if agency is approved by Director+]')
    plan += f"**Vendor / Agency Details:** {vendor_info}\n\n"

    # Creative Teams
    creative_teams = data.get('creative_teams', '[name, if applicable]')
    plan += f"**Internal Creative Team(s):** {creative_teams}\n\n"

    # D/I/N
    din_data = data.get('din', {})
    decide = din_data.get('decide', '[e.g., 1-2 people who have the final say]')
    input_people = din_data.get('input', '[e.g., 3-5 people who will provide input into the decision]')
    notify = din_data.get('notify', '[e.g., anyone else impacted by the decision]')
    plan += f"**D/I/N: Decide,** {decide} **Input,** {input_people} **Notify**, {notify}\n\n"

    # G/R/L Table
    grl_data = data.get('grl', {})
    plan += "**G/R/L**\t\t\t\t        **Notes including Adopt, Adapt, Invent**\n\n"
    plan += "| " + grl_data.get('global_lead', 'Global: [Lead name]') + " | " + grl_data.get('global_notes', '[Clarify role based on activation components]') + " |\n"
    plan += "| :---- | :---- |\n"
    plan += "| " + grl_data.get('regional_lead', 'Regional: [Lead name]') + " | " + grl_data.get('regional_notes', '[Clarify role based on activation components]') + " |\n"
    plan += "| " + grl_data.get('local_lead', 'Local: [Lead name]') + " | " + grl_data.get('local_notes', '[Clarify role based on activation components]') + " |\n\n"

    # Marketing Objectives
    objectives = data.get('objectives', '[1-2 sentences on the OKRs it ladders to and how at a high level]')
    plan += f"**Marketing objectives:** {objectives}\n\n"

    # Project Description
    description = data.get('description', '[1-3 sentence description of the project or program]')
    plan += f"**Project description:** {description}\n\n"

    # Audience
    audience = data.get('audience', '[Who is the audience and why does this matter to them?]')
    plan += f"**Audience:** {audience}\n\n"

    # Key Messages
    key_messages = data.get('key_messages', '[2-4 key messages we will deliver (i.e. what do we want the audience to take away?)]')
    if isinstance(key_messages, list):
        key_messages = '\n'.join(f"- {msg}" for msg in key_messages)
    plan += f"**Key messages:** {key_messages}\n\n"

    # Investment
    investment = data.get('investment', '[$XX | XX FTEs]')
    plan += f"**Investment:** {investment}\n\n"

    # Milestones
    milestones = data.get('milestones', [])
    plan += "**Milestones | Key activities**\n\n"
    if isinstance(milestones, list) and milestones:
        for milestone in milestones:
            if isinstance(milestone, dict):
                activity = milestone.get('activity', '[Activity]')
                date = milestone.get('date', '[Date]')
                plan += f"{activity} | {date}\n"
            else:
                plan += f"{milestone}\n"
    else:
        plan += "[Deliverables or key activities] | [Date]\n"
    plan += "\n"

    # Risks/Blockers
    risks = data.get('risks', '[List program risks/blockers that might impact the program. Maintain these updated throughout the project]')
    if isinstance(risks, list):
        risks = '\n'.join(f"- {risk}" for risk in risks)
    plan += f"**Risks / Blockers**\n\n{risks}\n\n"

    # Activation Components
    activation = data.get('activation_components', [])
    plan += "**Activation Components** [focusing on audience, why they care]\n"
    if isinstance(activation, list) and activation:
        for component in activation:
            plan += f"- {component}\n"
    else:
        plan += "[Channel 1: (e.g., social, OOH, physical, etc.)]\n"
        plan += "[Channel 2: (e.g., social, OOH, physical, etc.)]\n"
        plan += "[Channel 3: (e.g., social, OOH, physical, etc.)]\n"
    plan += "\n"

    # KPIs
    kpis = data.get('kpis', [])
    plan += "**KPIs, Anticipated Impact & Measurement**\n\n"
    if isinstance(kpis, list) and kpis:
        for kpi in kpis:
            plan += f"- {kpi}\n"
    else:
        plan += "[~1 sentence of quantified impact against key metrics]\n"
        plan += "[~1 sentence of quantified impact against key metrics]\n"
        plan += "[~1 sentence of quantified impact against key metrics]\n"

    return plan


def extract_plan_data_from_text(plan_text: str) -> Dict[str, Any]:
    """
    Extract structured data from a Plan on a Page text document.

    Parses an existing plan document and extracts data into structured format
    that can be modified and reformatted.

    Args:
        plan_text: Raw plan document text

    Returns:
        Dict containing extracted structured data
    """
    if not plan_text:
        return {"error": "No plan text provided"}

    # This is a simple extraction - could be enhanced with more sophisticated parsing
    data = {}

    lines = plan_text.split('\n')

    for i, line in enumerate(lines):
        # Extract project name
        if 'Plan On a Page:' in line or 'Plan on a Page:' in line:
            data['project_name'] = line.split(':', 1)[1].strip().strip('*').strip()

        # Extract other fields
        elif line.startswith('**Executive Sponsor:**'):
            data['executive_sponsor'] = line.split(':', 1)[1].strip().strip('*').strip()
        elif line.startswith('**Project Lead:**'):
            data['project_lead'] = line.split(':', 1)[1].strip().strip('*').strip()
        elif line.startswith('**Project Manager:**'):
            data['project_manager'] = line.split(':', 1)[1].strip().strip('*').strip()
        elif line.startswith('**Marketing objectives:**'):
            data['objectives'] = line.split(':', 1)[1].strip()
        elif line.startswith('**Project description:**'):
            data['description'] = line.split(':', 1)[1].strip()
        elif line.startswith('**Audience:**'):
            data['audience'] = line.split(':', 1)[1].strip()
        elif line.startswith('**Investment:**'):
            data['investment'] = line.split(':', 1)[1].strip()

    return data


def validate_format_compliance(plan_text: str) -> Dict[str, Any]:
    """
    Validate that a plan document follows the standard template format.

    Args:
        plan_text: Plan document text to validate

    Returns:
        Dict containing validation results and non-compliant sections
    """
    if not plan_text:
        return {"compliant": False, "error": "No plan text provided"}

    required_headers = [
        "Executive Sponsor:",
        "Project Lead:",
        "Project Manager:",
        "D/I/N",
        "G/R/L",
        "Marketing objectives:",
        "Project description:",
        "Audience:",
        "Key messages:",
        "Investment:",
        "Milestones",
        "Risks",
        "Activation Components",
        "KPIs"
    ]

    found_headers = []
    missing_headers = []

    for header in required_headers:
        if header in plan_text:
            found_headers.append(header)
        else:
            missing_headers.append(header)

    compliance_score = (len(found_headers) / len(required_headers)) * 100

    return {
        "compliant": len(missing_headers) == 0,
        "compliance_score": round(compliance_score, 1),
        "found_headers": found_headers,
        "missing_headers": missing_headers,
        "recommendations": [
            f"Add {header} section" for header in missing_headers
        ] if missing_headers else ["Plan appears to follow standard template format"]
    }


def clean_plan_formatting(plan_text: str) -> str:
    """
    Clean up formatting issues in a plan document.

    Args:
        plan_text: Plan text with potential formatting issues

    Returns:
        Cleaned plan text
    """
    if not plan_text:
        return ""

    # Remove excessive blank lines
    import re
    cleaned = re.sub(r'\n{3,}', '\n\n', plan_text)

    # Ensure consistent header formatting
    cleaned = cleaned.replace('**Executive Sponsor**:', '**Executive Sponsor:**')
    cleaned = cleaned.replace('**Project Lead**:', '**Project Lead:**')
    cleaned = cleaned.replace('**Project Manager**:', '**Project Manager:**')

    # Ensure consistent spacing after headers
    cleaned = re.sub(r'\*\*([^*]+)\*\*:([^\n])', r'**\1:** \2', cleaned)

    return cleaned.strip()
