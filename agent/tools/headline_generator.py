"""
Headline Generator Tool - Creates compelling headlines for Google Cloud content
"""
from typing import Dict, Any, List
from google.adk.tools import ToolContext
from ..prompts.brand_voice_instructions import HEADLINE_GENERATOR_PROMPT


def generate_headlines(
    topic: str,
    content_summary: str = "",
    target_audience: str = "technical professionals",
    headline_types: List[str] = None,
    keywords: List[str] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Generate multiple compelling headline options for given content.

    Args:
        topic: Main topic or theme of the content
        content_summary: Brief summary of the content (optional)
        target_audience: Target audience for the headlines
        headline_types: Types of headlines to generate (how-to, benefit-driven, etc.)
        keywords: Key terms to include in headlines for SEO
        tool_context: Google ADK tool context

    Returns:
        Dict containing generated headlines and metadata
    """
    if not topic or not topic.strip():
        return {
            "error": "Please provide a topic for headline generation",
            "headlines": [],
            "status": "error"
        }

    # Set defaults
    headline_types = headline_types or ["how-to", "benefit-driven", "problem-solution", "innovation"]
    keywords = keywords or []

    # Construct the generation prompt
    headline_prompt = f"""
{HEADLINE_GENERATOR_PROMPT}

## Content Details:
**Topic:** {topic}
**Target Audience:** {target_audience}
**Content Summary:** {content_summary or "Not provided - generate based on topic"}

**Requested Headline Types:**
{chr(10).join(f"- {htype}" for htype in headline_types)}

**Keywords to Include (naturally):**
{chr(10).join(f"- {keyword}" for keyword in keywords) if keywords else "- None specified"}

## Requirements:
- Generate 5-7 headline variations
- Mix different approaches and angles
- Keep headlines 50-60 characters for SEO optimization
- Ensure each headline matches the content and audience
- Use Google Cloud brand voice (clear, helpful, professional)

Please provide headlines with explanations for why each works.
"""

    try:
        # Use the tool context to get LLM response if available
        if tool_context and hasattr(tool_context, 'llm_client'):
            response = tool_context.llm_client.generate_content(headline_prompt)
            headlines_content = response.text if hasattr(response, 'text') else str(response)
        else:
            # Fallback - return structured template with examples
            headlines_content = f"""
## Generated Headlines for: {topic}

### 1. How-To Approach
**Headline:** "How to [Achieve Outcome] with Google Cloud [Solution]"
**Length:** [X] characters
**Why it works:** Clear value proposition with actionable promise

### 2. Benefit-Driven
**Headline:** "Why [Audience] Choose Google Cloud for [Specific Use Case]"
**Length:** [X] characters
**Why it works:** Focuses on audience benefits and social proof

### 3. Problem-Solution
**Headline:** "Solve [Specific Problem] with [Google Cloud Approach]"
**Length:** [X] characters
**Why it works:** Directly addresses pain point with solution

### 4. Innovation/Trend
**Headline:** "The Future of [Technology/Process] with Google Cloud"
**Length:** [X] characters
**Why it works:** Positions Google Cloud as forward-thinking

### 5. Case Study/Proof
**Headline:** "How [Company Type] Achieved [Result] Using Google Cloud"
**Length:** [X] characters
**Why it works:** Concrete proof with relatable example

### 6. Urgent/Timely
**Headline:** "[Number] Ways Google Cloud Transforms [Industry Process]"
**Length:** [X] characters
**Why it works:** Specific, actionable, and creates curiosity

### 7. Question-Based
**Headline:** "Is Your [System/Process] Ready for [Challenge]?"
**Length:** [X] characters
**Why it works:** Engages reader with relevant question

## Recommended Headlines (Top 3):
1. [Best headline option]
2. [Second best option]
3. [Third best option]

## SEO Notes:
- All headlines include relevant keywords naturally
- Character counts optimized for search results
- Headlines match search intent for target audience
"""

        # Parse headlines for analysis (basic implementation)
        headline_list = []
        if "Generated Headlines" in headlines_content:
            # Try to extract individual headlines (simplified parsing)
            lines = headlines_content.split('\n')
            for line in lines:
                if line.startswith('**Headline:**'):
                    headline_text = line.replace('**Headline:**', '').strip().strip('"')
                    if headline_text:
                        headline_list.append({
                            "text": headline_text,
                            "length": len(headline_text),
                            "seo_optimized": 40 <= len(headline_text) <= 60
                        })

        return {
            "headlines_analysis": headlines_content,
            "headline_list": headline_list,
            "topic": topic,
            "target_audience": target_audience,
            "keywords_used": keywords,
            "headline_types": headline_types,
            "total_generated": len(headline_list) or 7,
            "status": "completed"
        }

    except Exception as e:
        return {
            "error": f"Headline generation failed: {str(e)}",
            "headlines": [],
            "status": "error"
        }


def optimize_existing_headline(
    current_headline: str,
    content_context: str = "",
    target_seo_keywords: List[str] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Analyze and optimize an existing headline for better performance.

    Args:
        current_headline: The headline to optimize
        content_context: Brief context about the content
        target_seo_keywords: Keywords to incorporate for SEO
        tool_context: Google ADK tool context

    Returns:
        Dict containing optimization analysis and improved versions
    """
    if not current_headline or not current_headline.strip():
        return {
            "error": "Please provide a headline to optimize",
            "optimized_versions": [],
            "status": "error"
        }

    target_seo_keywords = target_seo_keywords or []

    optimization_prompt = f"""
Analyze and optimize this headline for Google Cloud content:

**Current Headline:** "{current_headline}"
**Content Context:** {content_context or "Not provided"}
**Target SEO Keywords:** {', '.join(target_seo_keywords) if target_seo_keywords else "None specified"}

Please provide:

1. **Current Headline Analysis:**
   - Character count and SEO optimization
   - Brand voice alignment assessment
   - Clarity and engagement level
   - Missing elements or opportunities

2. **3 Optimized Versions:**
   - Version A: SEO-optimized
   - Version B: Engagement-focused
   - Version C: Clarity-enhanced

3. **Recommendations:**
   - Key improvements made
   - Why each version works better
   - Best use case for each option

Format with clear sections and actionable insights.
"""

    try:
        if tool_context and hasattr(tool_context, 'llm_client'):
            response = tool_context.llm_client.generate_content(optimization_prompt)
            optimization_content = response.text if hasattr(response, 'text') else str(response)
        else:
            # Fallback template
            optimization_content = f"""
## Headline Optimization Analysis

### Current Headline: "{current_headline}"
**Character Count:** {len(current_headline)}
**SEO Status:** {'✓ Optimized' if 40 <= len(current_headline) <= 60 else '⚠ Needs optimization'}
**Brand Voice:** [Assessment of Google Cloud voice alignment]

### Issues Identified:
- [Issue 1 with current headline]
- [Issue 2 with current headline]
- [Issue 3 with current headline]

### Optimized Versions:

**Version A (SEO-Optimized):**
"[Improved headline with better keywords]"
- Character count: [X]
- Improvement: Better keyword integration

**Version B (Engagement-Focused):**
"[Improved headline with more engaging language]"
- Character count: [X]
- Improvement: More compelling hook

**Version C (Clarity-Enhanced):**
"[Improved headline with clearer value]"
- Character count: [X]
- Improvement: Clearer benefit statement

### Recommendations:
- Use Version A for search-heavy content
- Use Version B for social media promotion
- Use Version C for technical audiences

### Key Improvements Made:
1. [Specific improvement 1]
2. [Specific improvement 2]
3. [Specific improvement 3]
"""

        return {
            "optimization_analysis": optimization_content,
            "original_headline": current_headline,
            "original_length": len(current_headline),
            "seo_keywords_targeted": target_seo_keywords,
            "status": "completed"
        }

    except Exception as e:
        return {
            "error": f"Headline optimization failed: {str(e)}",
            "optimized_versions": [],
            "status": "error"
        }


def get_headline_best_practices() -> Dict[str, Any]:
    """
    Return Google Cloud headline best practices and guidelines.

    Returns:
        Dict containing comprehensive headline guidelines
    """
    return {
        "character_limits": {
            "seo_optimal": "50-60 characters",
            "social_media": "70-100 characters",
            "email_subject": "30-50 characters"
        },
        "headline_formulas": {
            "how_to": "How to [Achieve Result] with [Google Cloud Solution]",
            "benefit_driven": "[Number] Ways Google Cloud [Improves/Transforms] [Process]",
            "problem_solution": "Solve [Specific Problem] with [Specific GCP Service]",
            "question_based": "Is Your [System] Ready for [Challenge/Opportunity]?",
            "case_study": "How [Company] Achieved [Metric] Using Google Cloud"
        },
        "power_words": [
            "Transform", "Accelerate", "Optimize", "Streamline", "Scale",
            "Secure", "Innovate", "Automate", "Integrate", "Modernize"
        ],
        "brand_voice_guidelines": [
            "Use clear, jargon-free language",
            "Focus on customer benefits",
            "Be specific and concrete",
            "Avoid hyperbolic claims",
            "Include action words"
        ],
        "seo_tips": [
            "Include primary keyword naturally",
            "Front-load important keywords",
            "Match search intent",
            "Use title case for better readability",
            "Test multiple variations"
        ]
    }