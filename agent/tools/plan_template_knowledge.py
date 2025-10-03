"""
Plan Template Knowledge - Core template and best practices for Plan on a Page documents
"""
from typing import Dict, Any, List

# Plan on a Page Template
PLAN_TEMPLATE = """Plan On a Page: **[Project name]**

**Executive Sponsor:** [name]

**Project Lead:** [name]

**Project Manager:** [name]

**Vendor / Agency Details:** [If using agency / vendor to deliver the work, list the name, describe services that the will be provided; confirm if agency is approved by Director+]

**Internal Creative Team(s):** [name, if applicable]

**D/I/N: Decide,** [e.g., 1-2 people who have the final say] **Input,** [e.g., 3-5 people who will provide input into the decision] **Notify**, [e.g., anyone else impacted by the decision]

**G/R/L**				        **Notes including Adopt, Adapt, Invent**

| Global: [Lead name] | [Clarify role based on activation components] |
| :---- | :---- |
| Regional: [Lead name] | [Clarify role based on activation components] |
| Local: [Lead name] | [Clarify role based on activation components] |

**Marketing objectives:** [1-2 sentences on the OKRs it ladders to and how at a high level]

**Project description:** [1-3 sentence description of the project or program]

**Audience:** [Who is the audience and why does this matter to them?]

**Key messages:** [2-4 key messages we will deliver (i.e. what do we want the audience to take away?)]

**Investment:** [$XX | XX FTEs]

**Milestones | Key activities**

[Deliverables or key activities] | [Date]

**Risks / Blockers**

[List program risks/blockers that might impact the program. Maintain these updated throughout the project]

**Activation Components** [focusing on audience, why they care]
[Channel 1: (e.g., social, OOH, physical, etc.)]
[Channel 2: (e.g., social, OOH, physical, etc.)]
[Channel 3: (e.g., social, OOH, physical, etc.)]

**KPIs, Anticipated Impact & Measurement**

[~1 sentence of quantified impact against key metrics]
[~1 sentence of quantified impact against key metrics]
[~1 sentence of quantified impact against key metrics]
"""


# Core knowledge base for Plan on a Page
PLAN_KNOWLEDGE = {
    "template_sections": {
        "project_identifiers": {
            "fields": ["Project Name", "Executive Sponsor", "Project Lead", "Project Manager"],
            "description": "Core project leadership and ownership",
            "best_practice": "Name specific individuals with their full names and titles for clarity",
            "common_mistakes": ["Using team names instead of individuals", "Missing Project Manager designation"]
        },
        "vendor_agency": {
            "fields": ["Vendor/Agency Details"],
            "description": "External partner information if applicable",
            "best_practice": "Include agency name, scope of services, and Director+ approval status",
            "required_when": "Using external vendors or agencies"
        },
        "decision_framework": {
            "fields": ["D/I/N (Decide/Input/Notify)"],
            "description": "Decision-making roles and stakeholders",
            "components": {
                "Decide": "1-2 people with final say (decision makers)",
                "Input": "3-5 people who provide input before decisions",
                "Notify": "Anyone else who should be informed of decisions"
            },
            "best_practice": "Keep Decide group small (1-2 people) to avoid decision paralysis"
        },
        "grl_section": {
            "fields": ["G/R/L Table", "Adopt/Adapt/Invent Notes"],
            "description": "THE MOST CRITICAL SECTION - defines cross-geography alignment",
            "geographies": {
                "Global": "Centrally created work for worldwide deployment",
                "Regional": "Work for specific regions (EMEA, APAC, Americas, etc.)",
                "Local": "Market-specific work for individual countries"
            },
            "framework": {
                "Adopt": "Use the work/asset exactly as created by another team",
                "Adapt": "Modify existing work for local needs (translation, cultural adaptation)",
                "Invent": "Create entirely new work specific to this geography"
            },
            "best_practice": [
                "Name a specific lead for each geography",
                "For each activation component, specify which team leads and which teams Adopt/Adapt/Invent",
                "Include detailed notes explaining the rationale for each assignment",
                "Default to Adopt when possible for efficiency",
                "Use Adapt for localization needs (language, culture)",
                "Use Invent only when market needs are truly unique"
            ],
            "common_mistakes": [
                "Not specifying individual lead names",
                "Vague descriptions like 'TBD' or 'Regional teams'",
                "Missing Adopt/Adapt/Invent designations",
                "No explanatory notes for decisions",
                "Not mapping activation components to G/R/L roles"
            ]
        },
        "objectives_description": {
            "fields": ["Marketing Objectives", "Project Description", "Audience"],
            "marketing_objectives": {
                "length": "1-2 sentences",
                "content": "How this ladders to OKRs",
                "best_practice": "Be specific about which OKRs and how the project contributes"
            },
            "project_description": {
                "length": "1-3 sentences",
                "content": "Clear, concise description of the project or program",
                "best_practice": "Focus on what, not why (that's in objectives)"
            },
            "audience": {
                "content": "Who is the audience and why does this matter to them",
                "best_practice": "Be specific (not just 'developers' but 'senior developers at enterprise companies')"
            }
        },
        "key_messages": {
            "fields": ["Key Messages"],
            "count": "2-4 messages",
            "description": "What you want the audience to take away",
            "best_practice": "Make them specific, memorable, and action-oriented",
            "example": "Good: 'Google Cloud reduces infrastructure costs by 30%' vs Bad: 'Google Cloud is cost effective'"
        },
        "investment_milestones": {
            "fields": ["Investment", "Milestones | Key Activities"],
            "investment": {
                "format": "$XX | XX FTEs",
                "description": "Budget and people resources",
                "best_practice": "Be as specific as possible; include both $ and people"
            },
            "milestones": {
                "format": "Activity/Deliverable | Date",
                "description": "Key activities with specific dates",
                "best_practice": "Include actual dates, not 'Q2' or 'TBD'"
            }
        },
        "risks_blockers": {
            "fields": ["Risks / Blockers"],
            "description": "Potential issues that might impact the program",
            "best_practice": [
                "Be honest and specific",
                "Update throughout the project lifecycle",
                "Include mitigation strategies when possible"
            ],
            "common_risks": [
                "Resource constraints",
                "Technical dependencies",
                "Legal/compliance reviews",
                "External partner delays",
                "Budget limitations"
            ]
        },
        "activation_components": {
            "fields": ["Activation Components"],
            "description": "Channels and tactics to reach the audience",
            "examples": [
                "Social media (LinkedIn, Twitter)",
                "Content marketing (blogs, whitepapers)",
                "Events (conferences, webinars)",
                "Paid advertising (Google Ads, display)",
                "PR and thought leadership",
                "Email campaigns",
                "Partner co-marketing",
                "Out-of-home (OOH) advertising"
            ],
            "best_practice": [
                "List 3-7 key components",
                "Be specific about channels/platforms",
                "Consider audience preferences",
                "Each component should map to G/R/L assignments"
            ],
            "grl_mapping": "CRITICAL: For each activation component, clarify in the G/R/L table which team leads and which teams Adopt/Adapt/Invent"
        },
        "kpis_measurement": {
            "fields": ["KPIs, Anticipated Impact & Measurement"],
            "description": "Quantified impact against key metrics",
            "count": "3-5 metrics",
            "best_practice": [
                "Make them quantified (numbers, percentages)",
                "Tie to business outcomes, not just activity metrics",
                "Include how you'll measure (tools, methodology)"
            ],
            "examples": [
                "Good: 'Drive 50K impressions and 2K clicks to product page'",
                "Good: 'Generate 500 qualified leads with 15% conversion rate'",
                "Bad: 'Increase awareness'",
                "Bad: 'Get more engagement'"
            ]
        }
    },

    "grl_framework_detailed": {
        "purpose": "Ensure cross-geography alignment and prevent duplication of effort",
        "when_to_use": "For any initiative that spans multiple geographies or markets",
        "benefits": [
            "Prevents duplicated work across teams",
            "Clarifies ownership and responsibilities",
            "Enables efficient scaling of successful initiatives",
            "Facilitates early alignment and collaboration",
            "Makes dependencies explicit"
        ],
        "common_scenarios": {
            "global_campaign_local_execution": {
                "pattern": "Global creates, Regional/Local Adopt or Adapt",
                "example": "Global creates core social media content, Regional teams adapt for language/culture, Local markets adopt regional versions"
            },
            "regional_customization": {
                "pattern": "Regional creates, Local Adopts or Adapts",
                "example": "EMEA creates event strategy, Local markets adopt and execute with local vendors"
            },
            "local_innovation": {
                "pattern": "Local Invents, may scale to Regional/Global",
                "example": "Japan team creates unique partnership program, evaluates for regional/global scaling"
            }
        },
        "decision_tree": {
            "question_1": "Does existing work from another geography meet our needs?",
            "if_yes": "Choose ADOPT",
            "if_mostly": "Choose ADAPT - specify what modifications are needed",
            "if_no": "Choose INVENT - but verify if similar work exists first"
        }
    },

    "quality_checklist": {
        "completeness": [
            "All 15 required sections have content (not blank or TBD)",
            "Specific individual names are provided (not 'team' or 'TBD')",
            "Dates are actual dates, not 'Q2' or 'upcoming'",
            "Investment includes both $ and FTE estimates",
            "KPIs are quantified with numbers"
        ],
        "grl_quality": [
            "Each geography (G, R, L) has a named lead",
            "Each activation component is mapped to G/R/L in notes",
            "Adopt/Adapt/Invent is specified for each component",
            "Notes explain the rationale for assignments",
            "Dependencies between teams are noted"
        ],
        "clarity": [
            "Objectives clearly state OKR alignment",
            "Audience is specific, not generic",
            "Key messages are memorable and specific",
            "Activation components are concrete (not vague)",
            "Risks are honest and specific"
        ],
        "strategic_alignment": [
            "Plan aligns with broader marketing strategy",
            "G/R/L assignments promote efficiency (Adopt > Adapt > Invent)",
            "Evidence of cross-geography coordination",
            "Measurement ties to business outcomes"
        ]
    }
}


def get_template() -> str:
    """Return the blank Plan on a Page template."""
    return PLAN_TEMPLATE


def get_section_guidance(section_name: str) -> Dict[str, Any]:
    """
    Get detailed guidance for a specific section of the template.

    Args:
        section_name: Name of the section (e.g., 'grl_section', 'key_messages')

    Returns:
        Dict containing section guidance, best practices, and examples
    """
    sections = PLAN_KNOWLEDGE.get("template_sections", {})
    return sections.get(section_name, {
        "error": f"Section '{section_name}' not found",
        "available_sections": list(sections.keys())
    })


def get_grl_framework_guide() -> Dict[str, Any]:
    """
    Get comprehensive guidance on the G/R/L framework and Adopt/Adapt/Invent model.

    Returns:
        Dict containing detailed G/R/L framework information
    """
    return PLAN_KNOWLEDGE["grl_framework_detailed"]


def get_quality_checklist() -> Dict[str, List[str]]:
    """
    Get the quality checklist for validating Plan on a Page documents.

    Returns:
        Dict containing checklist items by category
    """
    return PLAN_KNOWLEDGE["quality_checklist"]


def get_activation_component_examples() -> List[str]:
    """
    Get examples of common activation components.

    Returns:
        List of activation component examples
    """
    return PLAN_KNOWLEDGE["template_sections"]["activation_components"]["examples"]


def get_common_mistakes(section: str = "all") -> Dict[str, List[str]]:
    """
    Get common mistakes to avoid, optionally for a specific section.

    Args:
        section: Section name or 'all' for all sections

    Returns:
        Dict of section names to lists of common mistakes
    """
    sections = PLAN_KNOWLEDGE["template_sections"]
    mistakes = {}

    for section_name, section_data in sections.items():
        if "common_mistakes" in section_data:
            if section == "all" or section == section_name:
                mistakes[section_name] = section_data["common_mistakes"]

    return mistakes


def get_best_practices(section: str = "all") -> Dict[str, Any]:
    """
    Get best practices, optionally for a specific section.

    Args:
        section: Section name or 'all' for all sections

    Returns:
        Dict of section names to best practice information
    """
    sections = PLAN_KNOWLEDGE["template_sections"]
    practices = {}

    for section_name, section_data in sections.items():
        if "best_practice" in section_data:
            if section == "all" or section == section_name:
                practices[section_name] = section_data["best_practice"]

    return practices
