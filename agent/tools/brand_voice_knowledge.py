"""
Brand Voice Knowledge Tool - Integration with Google Cloud brand guidelines and style guide
"""
from typing import Dict, Any, List, Optional
from google.adk.tools import ToolContext
import os


def retrieve_brand_voice_guidelines(
    topic_area: str = "general",
    content_type: str = "blog_post",
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Retrieve Google Cloud brand voice guidelines and style information.

    Args:
        topic_area: Specific area of interest (security, AI/ML, infrastructure, etc.)
        content_type: Type of content being created
        tool_context: Google ADK tool context for RAG integration

    Returns:
        Dict containing brand guidelines and style recommendations
    """

    # Core Google Cloud brand voice principles (embedded knowledge)
    core_guidelines = {
        "voice_principles": {
            "clear_and_accessible": {
                "description": "Use plain language that anyone can understand",
                "guidelines": [
                    "Avoid technical jargon unless necessary for the audience",
                    "Explain complex concepts in simple terms",
                    "Use active voice and conversational tone",
                    "Break up long sentences and paragraphs"
                ]
            },
            "helpful_and_solution_oriented": {
                "description": "Focus on solving customer problems and providing value",
                "guidelines": [
                    "Start with the customer's problem or need",
                    "Provide actionable solutions and next steps",
                    "Include practical examples and use cases",
                    "Offer multiple approaches when appropriate"
                ]
            },
            "confident_but_humble": {
                "description": "Show expertise without being arrogant",
                "guidelines": [
                    "Use confident language about capabilities",
                    "Acknowledge limitations or considerations honestly",
                    "Avoid superlatives and marketing hyperbole",
                    "Let results and customer success speak for themselves"
                ]
            },
            "innovation_focused": {
                "description": "Highlight cutting-edge technology and forward-thinking solutions",
                "guidelines": [
                    "Emphasize Google Cloud's technological advantages",
                    "Discuss future trends and emerging technologies",
                    "Show how solutions enable innovation",
                    "Connect to broader industry transformation"
                ]
            },
            "inclusive_and_welcoming": {
                "description": "Use language that welcomes all audiences",
                "guidelines": [
                    "Use inclusive pronouns and examples",
                    "Avoid assumptions about user background or expertise",
                    "Provide context for industry-specific terms",
                    "Welcome newcomers while respecting experts"
                ]
            }
        },
        "style_guidelines": {
            "writing_mechanics": [
                "Use sentence case for headlines (not title case)",
                "Write in active voice whenever possible",
                "Use contractions for conversational tone (it's, we're, you'll)",
                "Use parallel structure in lists and series",
                "Keep paragraphs to 3-4 sentences maximum"
            ],
            "terminology": [
                "Use 'Google Cloud' not 'GCP' in customer-facing content",
                "Refer to 'customers' not 'users' when appropriate",
                "Use 'AI and machine learning' not just 'AI/ML'",
                "Say 'multicloud' not 'multi-cloud'",
                "Use 'on-premises' not 'on-premise'"
            ],
            "content_structure": [
                "Start with a hook that identifies a real problem",
                "Use descriptive subheadings every 2-3 paragraphs",
                "Include bullet points for scannable content",
                "End with clear next steps or calls-to-action",
                "Use short sentences and varied sentence length"
            ]
        }
    }

    # Topic-specific guidelines
    topic_guidelines = {
        "security": {
            "voice_adjustments": "More serious tone, emphasize trust and reliability",
            "key_messages": ["Zero-trust security", "Compliance and governance", "Threat protection"],
            "avoid": ["Fearmonger language", "Overly technical security jargon"]
        },
        "ai_ml": {
            "voice_adjustments": "Excited but grounded, focus on practical applications",
            "key_messages": ["Democratize AI", "Responsible AI", "Business transformation"],
            "avoid": ["Hype without substance", "Sci-fi language", "Over-promising AI capabilities"]
        },
        "infrastructure": {
            "voice_adjustments": "Practical and performance-focused",
            "key_messages": ["Scalability", "Reliability", "Cost optimization"],
            "avoid": ["Overly technical architecture details", "Feature lists without benefits"]
        },
        "data_analytics": {
            "voice_adjustments": "Data-driven and insight-focused",
            "key_messages": ["Data-driven decisions", "Real-time insights", "Data democratization"],
            "avoid": ["Complex statistical jargon", "Abstract data concepts"]
        }
    }

    # Content type specific guidelines
    content_guidelines = {
        "blog_post": {
            "length": "800-1500 words typically",
            "structure": "Hook, problem, solution, examples, conclusion, CTA",
            "tone": "Conversational but professional"
        },
        "email": {
            "length": "150-300 words typically",
            "structure": "Clear subject, brief context, main point, single CTA",
            "tone": "Direct and helpful"
        },
        "social_media": {
            "length": "Varies by platform",
            "structure": "Hook, key insight, engagement question",
            "tone": "Casual but informative"
        },
        "case_study": {
            "length": "1000-2000 words typically",
            "structure": "Challenge, solution, results, lessons learned",
            "tone": "Professional with customer focus"
        }
    }

    # Try to use RAG system if available
    rag_guidelines = {}
    if tool_context:
        try:
            # Import the search tool function
            from .brand_voice_search_tool import retrieve_brand_voice_knowledge

            # Check if RAG corpus is available
            rag_corpus = os.getenv('RAG_CORPUS')
            search_engine_id = os.getenv('VERTEX_SEARCH_ENGINE_ID')

            if rag_corpus and search_engine_id:
                # Search for topic-specific guidelines using the dedicated search tool
                query = f"Google Cloud brand voice guidelines for {topic_area} {content_type}"
                rag_results = retrieve_brand_voice_knowledge(
                    query=query,
                    content_type=content_type,
                    tool_context=tool_context
                )
                if rag_results and rag_results.get("status") == "success":
                    rag_guidelines = {
                        "rag_results": rag_results,
                        "source": "Brand Voice RAG knowledge base",
                        "search_query": query,
                        "corpus_id": rag_corpus
                    }
        except Exception as e:
            # RAG not available, continue with embedded knowledge
            pass

    return {
        "core_guidelines": core_guidelines,
        "topic_specific": topic_guidelines.get(topic_area, {}),
        "content_type_guidelines": content_guidelines.get(content_type, content_guidelines["blog_post"]),
        "rag_guidelines": rag_guidelines,
        "topic_area": topic_area,
        "content_type": content_type,
        "status": "completed"
    }


def check_brand_voice_compliance(
    content: str,
    guidelines: Dict[str, Any] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Check content against Google Cloud brand voice guidelines.

    Args:
        content: Content to check
        guidelines: Specific guidelines to check against
        tool_context: Google ADK tool context

    Returns:
        Dict containing compliance analysis and recommendations
    """
    if not content or not content.strip():
        return {
            "error": "Please provide content to analyze",
            "compliance_score": 0,
            "status": "error"
        }

    # Get guidelines if not provided
    if not guidelines:
        guidelines = retrieve_brand_voice_guidelines()

    # Basic compliance checks (can be enhanced with NLP)
    compliance_issues = []
    compliance_score = 100

    # Check for common issues
    content_lower = content.lower()

    # Jargon check
    common_jargon = [
        "leverage", "synergy", "paradigm", "utilize", "facilitate",
        "optimize", "streamline", "robust", "scalable", "enterprise-grade"
    ]

    jargon_found = [word for word in common_jargon if word in content_lower]
    if jargon_found:
        compliance_issues.append({
            "type": "jargon",
            "severity": "medium",
            "message": f"Consider replacing corporate jargon: {', '.join(jargon_found)}",
            "impact": -10
        })
        compliance_score -= 10

    # Passive voice check (simplified)
    passive_indicators = ["was", "were", "been", "being"]
    passive_count = sum(content_lower.count(indicator) for indicator in passive_indicators)
    total_sentences = content.count('.') + content.count('!') + content.count('?')

    if total_sentences > 0 and (passive_count / total_sentences) > 0.3:
        compliance_issues.append({
            "type": "passive_voice",
            "severity": "low",
            "message": "Consider using more active voice to sound more engaging",
            "impact": -5
        })
        compliance_score -= 5

    # Length check for paragraphs
    paragraphs = content.split('\n\n')
    long_paragraphs = [p for p in paragraphs if len(p.split()) > 100]

    if long_paragraphs:
        compliance_issues.append({
            "type": "paragraph_length",
            "severity": "low",
            "message": f"{len(long_paragraphs)} paragraph(s) may be too long for easy scanning",
            "impact": -5
        })
        compliance_score -= 5

    # Check for inclusive language (basic)
    exclusive_terms = ["guys", "blacklist", "whitelist", "master", "slave"]
    exclusive_found = [term for term in exclusive_terms if term in content_lower]

    if exclusive_found:
        compliance_issues.append({
            "type": "inclusive_language",
            "severity": "high",
            "message": f"Consider more inclusive alternatives to: {', '.join(exclusive_found)}",
            "impact": -15
        })
        compliance_score -= 15

    # Positive aspects
    positive_aspects = []

    if "google cloud" in content_lower:
        positive_aspects.append("Uses correct 'Google Cloud' terminology")

    if content.count('?') > 0:
        positive_aspects.append("Engages readers with questions")

    if any(word in content_lower for word in ["example", "case study", "use case"]):
        positive_aspects.append("Includes practical examples")

    return {
        "compliance_score": max(0, compliance_score),
        "issues_found": compliance_issues,
        "positive_aspects": positive_aspects,
        "total_issues": len(compliance_issues),
        "recommendations": [
            "Review flagged jargon terms for simpler alternatives",
            "Convert passive voice to active where possible",
            "Break up long paragraphs for better readability",
            "Use more inclusive language throughout"
        ],
        "status": "completed"
    }


def get_google_cloud_terminology() -> Dict[str, Any]:
    """
    Return the official Google Cloud terminology and preferred usage.

    Returns:
        Dict containing preferred terms and usage guidelines
    """
    return {
        "preferred_terms": {
            "Google Cloud": "Use instead of GCP, Google Cloud Platform",
            "AI and machine learning": "Use instead of AI/ML in customer content",
            "multicloud": "One word, not multi-cloud",
            "on-premises": "Use instead of on-premise",
            "real time": "Two words as noun, real-time as adjective"
        },
        "service_names": {
            "BigQuery": "Correct capitalization",
            "Compute Engine": "Two words",
            "Cloud Storage": "Two words",
            "Kubernetes Engine": "Not GKE in customer content"
        },
        "avoid": {
            "GCP": "Use Google Cloud instead",
            "users": "Prefer customers when appropriate",
            "solutions": "Often overused, be more specific",
            "enterprise-grade": "Vague marketing term"
        },
        "industry_terms": {
            "DevOps": "Correct capitalization",
            "MLOps": "Correct capitalization",
            "CI/CD": "All caps with slashes",
            "API": "All caps"
        }
    }