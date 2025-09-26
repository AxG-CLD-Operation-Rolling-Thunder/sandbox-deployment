"""
Content Reviewer Tool - Analyzes existing content for Google Cloud brand voice compliance
"""
from typing import Dict, Any, Optional
from google.adk.tools import ToolContext
from ..prompts.brand_voice_instructions import CONTENT_REVIEWER_PROMPT


def review_content_for_brand_voice(
    content: str,
    content_type: str = "blog_post",
    target_audience: str = "technical professionals",
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Analyze existing content and provide specific suggestions to improve
    alignment with Google Cloud brand voice and style guidelines.

    Args:
        content: The text content to analyze
        content_type: Type of content (blog_post, email, social_media, etc.)
        target_audience: Intended audience (technical professionals, executives, developers, etc.)
        tool_context: Google ADK tool context

    Returns:
        Dict containing analysis results and improvement suggestions
    """
    if not content or not content.strip():
        return {
            "error": "Please provide content to analyze",
            "suggestions": [],
            "brand_voice_score": 0
        }

    # Construct the analysis prompt
    analysis_prompt = f"""
{CONTENT_REVIEWER_PROMPT}

## Content to Analyze:
**Content Type:** {content_type}
**Target Audience:** {target_audience}

**Content:**
{content}

Please provide your analysis following the specified format.
"""

    try:
        # Use the tool context to get LLM response if available
        if tool_context and hasattr(tool_context, 'llm_client'):
            response = tool_context.llm_client.generate_content(analysis_prompt)
            analysis_text = response.text if hasattr(response, 'text') else str(response)
        else:
            # Fallback - return structured template for manual completion
            analysis_text = f"""
## Brand Voice Analysis Results

### 3 Key Improvements:
1. **Clarity Enhancement**: [Specific suggestion for making content clearer]
2. **Brand Voice Alignment**: [Specific suggestion for better Google Cloud voice]
3. **Structure Optimization**: [Specific suggestion for better organization]

### Before/After Examples:
**Before**: [Original sentence]
**After**: [Improved version]

**Before**: [Another original sentence]
**After**: [Another improved version]

### Brand Voice Score: [Score]/10
**Explanation**: [Brief explanation of score]

### Additional Recommendations:
- [Specific actionable item]
- [Another specific actionable item]
"""

        return {
            "analysis": analysis_text,
            "content_type": content_type,
            "target_audience": target_audience,
            "word_count": len(content.split()),
            "status": "completed"
        }

    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "suggestions": [],
            "brand_voice_score": 0,
            "status": "error"
        }


def get_quick_brand_voice_tips(content_type: str = "blog_post") -> Dict[str, Any]:
    """
    Provide quick brand voice tips for specific content types.

    Args:
        content_type: The type of content being created

    Returns:
        Dict containing quick tips and guidelines
    """
    tips_by_type = {
        "blog_post": {
            "voice_tips": [
                "Use conversational but professional tone",
                "Start with a problem or question your audience faces",
                "Include specific examples and use cases",
                "Avoid excessive corporate jargon",
                "End with clear next steps"
            ],
            "structure_tips": [
                "Hook readers in the first 2 sentences",
                "Use subheadings every 2-3 paragraphs",
                "Include bullet points for scanability",
                "Add code examples or screenshots when relevant"
            ]
        },
        "email": {
            "voice_tips": [
                "Get to the point quickly",
                "Use active voice and clear subject lines",
                "Personalize when possible",
                "Focus on reader benefits"
            ],
            "structure_tips": [
                "Clear subject line with value proposition",
                "Brief intro with context",
                "Main content in bullet points or short paragraphs",
                "Single, clear call-to-action"
            ]
        },
        "social_media": {
            "voice_tips": [
                "Be concise and engaging",
                "Use inclusive, accessible language",
                "Show personality while staying professional",
                "Focus on value and insights"
            ],
            "structure_tips": [
                "Hook in first line",
                "Use line breaks for readability",
                "Include relevant hashtags naturally",
                "End with engagement question"
            ]
        }
    }

    return tips_by_type.get(content_type, tips_by_type["blog_post"])