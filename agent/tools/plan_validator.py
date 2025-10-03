"""
Plan Validator Tool - Validates Plan on a Page documents for completeness and quality
"""
from typing import Dict, Any, List, Tuple
from .plan_template_knowledge import get_quality_checklist, get_common_mistakes


def validate_plan_completeness(plan_content: str) -> Dict[str, Any]:
    """
    Validate that a Plan on a Page document is complete and ready for submission.

    Performs comprehensive validation checks including:
    - Required section presence
    - Field completeness (no TBDs or blanks)
    - G/R/L section quality
    - Quantified metrics
    - Named individuals

    Args:
        plan_content: Full text of the Plan on a Page document

    Returns:
        Dict containing validation results, score, and specific issues
    """
    if not plan_content or not plan_content.strip():
        return {
            "valid": False,
            "error": "No plan content provided",
            "score": 0,
            "status": "error"
        }

    validation_results = {
        "sections": _validate_sections(plan_content),
        "grl_quality": _validate_grl_section(plan_content),
        "completeness": _validate_no_tbds(plan_content),
        "specificity": _validate_specificity(plan_content),
        "quantification": _validate_quantified_metrics(plan_content)
    }

    # Calculate overall score
    category_scores = []
    for category, results in validation_results.items():
        if isinstance(results, dict) and 'score' in results:
            category_scores.append(results['score'])

    overall_score = sum(category_scores) / len(category_scores) if category_scores else 0

    # Determine if valid (threshold: 80%)
    is_valid = overall_score >= 80

    # Collect all issues
    all_issues = []
    for category, results in validation_results.items():
        if isinstance(results, dict) and 'issues' in results:
            all_issues.extend(results['issues'])

    # Get quality checklist
    quality_checklist = get_quality_checklist()

    return {
        "valid": is_valid,
        "overall_score": round(overall_score, 1),
        "validation_results": validation_results,
        "issues_found": all_issues,
        "issue_count": len(all_issues),
        "recommendations": _generate_recommendations(validation_results, is_valid),
        "quality_checklist": quality_checklist,
        "status": "completed",
        "ready_for_submission": is_valid and len(all_issues) <= 2
    }


def _validate_sections(plan_content: str) -> Dict[str, Any]:
    """Validate presence of all required sections."""
    required_sections = {
        "project_name": ["Plan On a Page:", "Plan on a Page:"],
        "executive_sponsor": ["Executive Sponsor:"],
        "project_lead": ["Project Lead:"],
        "project_manager": ["Project Manager:"],
        "din": ["D/I/N"],
        "grl": ["G/R/L"],
        "objectives": ["Marketing objectives:"],
        "description": ["Project description:"],
        "audience": ["Audience:"],
        "key_messages": ["Key messages:"],
        "investment": ["Investment:"],
        "milestones": ["Milestones", "Key activities"],
        "risks": ["Risks", "Blockers"],
        "activation": ["Activation Components"],
        "kpis": ["KPIs", "Impact", "Measurement"]
    }

    content_lower = plan_content.lower()
    present = []
    missing = []

    for section_name, keywords in required_sections.items():
        if any(keyword.lower() in content_lower for keyword in keywords):
            present.append(section_name)
        else:
            missing.append(section_name)

    score = (len(present) / len(required_sections)) * 100

    issues = [f"Missing required section: {section}" for section in missing]

    return {
        "score": score,
        "present_sections": present,
        "missing_sections": missing,
        "issues": issues
    }


def _validate_grl_section(plan_content: str) -> Dict[str, Any]:
    """Validate G/R/L section quality."""
    content_lower = plan_content.lower()

    checks = {
        "has_grl_header": "g/r/l" in content_lower,
        "has_global": "global:" in content_lower,
        "has_regional": "regional:" in content_lower,
        "has_local": "local:" in content_lower,
        "has_adopt": "adopt" in content_lower,
        "has_adapt": "adapt" in content_lower,
        "has_invent": "invent" in content_lower
    }

    passed_checks = sum(checks.values())
    total_checks = len(checks)
    score = (passed_checks / total_checks) * 100

    issues = []
    if not checks["has_grl_header"]:
        issues.append("G/R/L section header not found")
    if not checks["has_global"]:
        issues.append("Global role not defined in G/R/L")
    if not checks["has_regional"]:
        issues.append("Regional role not defined in G/R/L")
    if not checks["has_local"]:
        issues.append("Local role not defined in G/R/L")
    if not (checks["has_adopt"] or checks["has_adapt"] or checks["has_invent"]):
        issues.append("Adopt/Adapt/Invent framework not applied in G/R/L section")

    return {
        "score": score,
        "checks_passed": checks,
        "issues": issues
    }


def _validate_no_tbds(plan_content: str) -> Dict[str, Any]:
    """Check for TBD, blank, or placeholder text."""
    content_lower = plan_content.lower()

    tbd_indicators = ["tbd", "to be determined", "to be provided", "[name]", "[date]", "***"]

    found_tbds = []
    for indicator in tbd_indicators:
        if indicator in content_lower:
            found_tbds.append(indicator)

    # Count brackets which often indicate placeholders
    bracket_count = plan_content.count('[') + plan_content.count(']')

    score = 100 if not found_tbds else max(0, 100 - (len(found_tbds) * 10))

    issues = []
    if found_tbds:
        issues.append(f"Document contains {len(found_tbds)} TBD/placeholder entries")
    if bracket_count > 10:
        issues.append(f"Document contains {bracket_count//2} placeholder brackets - fill in specific information")

    return {
        "score": score,
        "tbd_indicators_found": found_tbds,
        "placeholder_count": bracket_count // 2,
        "issues": issues
    }


def _validate_specificity(plan_content: str) -> Dict[str, Any]:
    """Validate that specific names, dates, and details are provided."""
    content_lower = plan_content.lower()

    # Check for vague language
    vague_terms = ["team", "someone", "various", "multiple", "several", "appropriate", "relevant"]

    vague_count = sum(content_lower.count(term) for term in vague_terms)

    # Check for actual names (simple heuristic: capitalized words that aren't common words)
    lines = plan_content.split('\n')
    name_indicators = 0
    for line in lines:
        if 'Lead:' in line or 'Sponsor:' in line or 'Manager:' in line:
            # Check if there's a capitalized word after the colon
            parts = line.split(':')
            if len(parts) > 1 and any(word[0].isupper() for word in parts[1].split() if word and word[0].isalpha()):
                name_indicators += 1

    score = 100 if vague_count < 5 and name_indicators >= 3 else max(50, 100 - vague_count * 5)

    issues = []
    if vague_count > 5:
        issues.append(f"Document contains {vague_count} vague terms - be more specific")
    if name_indicators < 3:
        issues.append("Not enough specific names identified - name individuals, not teams")

    return {
        "score": score,
        "vague_term_count": vague_count,
        "named_individuals_found": name_indicators,
        "issues": issues
    }


def _validate_quantified_metrics(plan_content: str) -> Dict[str, Any]:
    """Validate that KPIs and metrics are quantified."""
    import re

    # Look for numbers in KPI section
    kpi_section = ""
    lines = plan_content.split('\n')
    in_kpi_section = False

    for line in lines:
        if 'kpi' in line.lower() or 'impact' in line.lower() or 'measurement' in line.lower():
            in_kpi_section = True
        elif line.startswith('**') and in_kpi_section:
            break
        elif in_kpi_section:
            kpi_section += line + "\n"

    # Count numbers in KPI section
    numbers = re.findall(r'\d+', kpi_section)
    percentage_signs = kpi_section.count('%')
    dollar_signs = kpi_section.count('$')

    quantified_metrics = len(numbers) + percentage_signs + dollar_signs

    score = min(100, quantified_metrics * 20)  # Up to 5 quantified metrics = 100

    issues = []
    if quantified_metrics < 3:
        issues.append(f"KPIs section has only {quantified_metrics} quantified metrics - add specific numbers and targets")

    return {
        "score": score,
        "quantified_metrics_count": quantified_metrics,
        "issues": issues
    }


def _generate_recommendations(validation_results: Dict[str, Any], is_valid: bool) -> List[str]:
    """Generate specific recommendations based on validation results."""
    recommendations = []

    # Section recommendations
    sections_result = validation_results.get('sections', {})
    if sections_result.get('missing_sections'):
        recommendations.append(f"Add missing sections: {', '.join(sections_result['missing_sections'][:3])}")

    # G/R/L recommendations
    grl_result = validation_results.get('grl_quality', {})
    if grl_result.get('score', 0) < 80:
        recommendations.append("Improve G/R/L section: add specific leads and Adopt/Adapt/Invent assignments")

    # TBD recommendations
    completeness_result = validation_results.get('completeness', {})
    if completeness_result.get('tbd_indicators_found'):
        recommendations.append("Replace all TBD and placeholder text with specific information")

    # Specificity recommendations
    specificity_result = validation_results.get('specificity', {})
    if specificity_result.get('score', 0) < 75:
        recommendations.append("Add more specific names, dates, and details throughout the plan")

    # Quantification recommendations
    quantification_result = validation_results.get('quantification', {})
    if quantification_result.get('score', 0) < 60:
        recommendations.append("Add quantified targets to KPIs (numbers, percentages, dollar amounts)")

    # If valid, provide final polish recommendations
    if is_valid:
        recommendations.append("Plan looks complete - review for clarity and alignment with stakeholders")

    return recommendations[:5]  # Return top 5 recommendations


def quick_validation(plan_content: str) -> Dict[str, bool]:
    """
    Perform quick validation checks for essential elements.

    Args:
        plan_content: Plan text to validate

    Returns:
        Dict with boolean results for key validation checks
    """
    if not plan_content:
        return {"error": True, "has_content": False}

    content_lower = plan_content.lower()

    return {
        "has_project_name": "plan on a page:" in content_lower,
        "has_grl_section": "g/r/l" in content_lower,
        "has_objectives": "marketing objectives:" in content_lower or "okr" in content_lower,
        "has_kpis": "kpi" in content_lower or "measurement" in content_lower,
        "has_activation_components": "activation" in content_lower,
        "appears_complete": all([
            "executive sponsor:" in content_lower,
            "g/r/l" in content_lower,
            "objectives" in content_lower,
            "kpi" in content_lower
        ]),
        "has_placeholders": any(x in content_lower for x in ["tbd", "[name]", "[date]"])
    }
