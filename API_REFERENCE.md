# Brand Voice Agent API Reference

## Overview

This document provides detailed API reference for all tools and functions available in the Google Cloud Brand Voice Agent.

## Tool Categories

- [Core Content Tools](#core-content-tools)
- [Knowledge & Reference Tools](#knowledge--reference-tools)
- [Helper Tools](#helper-tools)
- [User Management Tools](#user-management-tools)

---

## Core Content Tools

### review_content_for_brand_voice

Analyzes existing content for Google Cloud brand voice compliance and provides specific improvement suggestions.

```python
def review_content_for_brand_voice(
    content: str,
    content_type: str = "blog_post",
    target_audience: str = "technical professionals",
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `content` (str, required): The text content to analyze
- `content_type` (str, optional): Type of content - "blog_post", "email", "social_media", etc. Default: "blog_post"
- `target_audience` (str, optional): Intended audience. Default: "technical professionals"
- `tool_context` (ToolContext, optional): Google ADK tool context

**Returns:**
```python
{
    "analysis": str,           # Detailed analysis text
    "content_type": str,       # Content type processed
    "target_audience": str,    # Target audience
    "word_count": int,         # Word count of input
    "status": str             # "completed" or "error"
}
```

**Example:**
```python
result = review_content_for_brand_voice(
    content="Our enterprise-grade solution leverages cutting-edge technology...",
    content_type="blog_post",
    target_audience="technical professionals"
)
```

---

### generate_blog_content

Creates new blog post content from scratch based on topic and key points.

```python
def generate_blog_content(
    topic: str,
    key_points: Optional[List[str]] = None,
    target_audience: str = "technical professionals",
    content_length: str = "medium",
    google_cloud_services: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `topic` (str, required): Main topic or title for the blog post
- `key_points` (List[str], optional): List of key points to cover
- `target_audience` (str, optional): Target audience. Default: "technical professionals"
- `content_length` (str, optional): "short" (400-800), "medium" (800-1500), "long" (1500+). Default: "medium"
- `google_cloud_services` (List[str], optional): GCP services to highlight
- `tool_context` (ToolContext, optional): Google ADK tool context

**Returns:**
```python
{
    "content": str,                    # Generated blog content
    "topic": str,                      # Topic processed
    "target_audience": str,            # Target audience
    "word_count": int,                 # Generated word count
    "estimated_read_time": str,        # Estimated reading time
    "key_points_covered": int,         # Number of key points addressed
    "status": str,                     # "completed" or "error"
    "metadata": Dict[str, Any]         # Additional metadata
}
```

**Example:**
```python
result = generate_blog_content(
    topic="How to optimize Google Cloud costs",
    key_points=["Right-sizing instances", "Using preemptible VMs", "Storage optimization"],
    target_audience="technical professionals",
    content_length="medium",
    google_cloud_services=["Compute Engine", "Cloud Storage"]
)
```

---

### generate_content_outline

Creates a structured outline for a blog post before writing full content.

```python
def generate_content_outline(
    topic: str,
    target_audience: str = "technical professionals",
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `topic` (str, required): Main topic for the blog post
- `target_audience` (str, optional): Target audience. Default: "technical professionals"
- `tool_context` (ToolContext, optional): Google ADK tool context

**Returns:**
```python
{
    "outline": str,            # Structured outline content
    "topic": str,              # Topic processed
    "target_audience": str,    # Target audience
    "sections_count": int,     # Number of main sections
    "status": str             # "completed" or "error"
}
```

---

### generate_headlines

Creates multiple compelling headline options for given content.

```python
def generate_headlines(
    topic: str,
    content_summary: str = "",
    target_audience: str = "technical professionals",
    headline_types: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `topic` (str, required): Main topic or theme of the content
- `content_summary` (str, optional): Brief summary of the content
- `target_audience` (str, optional): Target audience. Default: "technical professionals"
- `headline_types` (List[str], optional): Types to generate - "how-to", "benefit-driven", "problem-solution", "innovation". Default: all types
- `keywords` (List[str], optional): Keywords to include for SEO
- `tool_context` (ToolContext, optional): Google ADK tool context

**Returns:**
```python
{
    "headlines_analysis": str,         # Detailed analysis with headlines
    "headline_list": List[Dict],       # List of headline objects
    "topic": str,                      # Topic processed
    "target_audience": str,            # Target audience
    "keywords_used": List[str],        # Keywords incorporated
    "headline_types": List[str],       # Types generated
    "total_generated": int,            # Number of headlines created
    "status": str                     # "completed" or "error"
}
```

**Headline Object Structure:**
```python
{
    "text": str,           # Headline text
    "length": int,        # Character count
    "seo_optimized": bool # True if 40-60 characters
}
```

---

### optimize_existing_headline

Analyzes and optimizes an existing headline for better performance.

```python
def optimize_existing_headline(
    current_headline: str,
    content_context: str = "",
    target_seo_keywords: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `current_headline` (str, required): The headline to optimize
- `content_context` (str, optional): Brief context about the content
- `target_seo_keywords` (List[str], optional): Keywords to incorporate for SEO
- `tool_context` (ToolContext, optional): Google ADK tool context

**Returns:**
```python
{
    "optimization_analysis": str,      # Detailed optimization analysis
    "original_headline": str,          # Original headline
    "original_length": int,            # Original character count
    "seo_keywords_targeted": List[str], # Target keywords
    "status": str                     # "completed" or "error"
}
```

---

## Knowledge & Reference Tools

### search_brand_voice_knowledge

Searches the Google Cloud brand voice knowledge base for specific guidelines and examples.

```python
def search_brand_voice_knowledge(
    query: str,
    content_type: str = "general",
    max_results: int = 5,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Note:** This is a VertexAiSearchTool when RAG is configured, fallback function when not.

**Parameters:**
- `query` (str, required): Search query for knowledge retrieval
- `content_type` (str, optional): Content context - "blog_post", "email", "social_media", "guidelines", "examples", "terminology", "general"
- `max_results` (int, optional): Maximum results to return. Default: 5
- `tool_context` (ToolContext, optional): Google ADK tool context

---

### retrieve_brand_voice_guidelines

Retrieves Google Cloud brand voice guidelines and style information.

```python
def retrieve_brand_voice_guidelines(
    topic_area: str = "general",
    content_type: str = "blog_post",
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `topic_area` (str, optional): Specific area - "security", "ai_ml", "infrastructure", "data_analytics", "general"
- `content_type` (str, optional): Type of content being created
- `tool_context` (ToolContext, optional): Google ADK tool context

**Returns:**
```python
{
    "core_guidelines": Dict[str, Any],       # Core brand voice principles
    "topic_specific": Dict[str, Any],        # Topic-specific guidelines
    "content_type_guidelines": Dict[str, Any], # Content type guidelines
    "rag_guidelines": Dict[str, Any],        # RAG results if available
    "topic_area": str,                       # Topic area processed
    "content_type": str,                     # Content type processed
    "status": str                           # "completed"
}
```

---

### check_brand_voice_compliance

Checks content against Google Cloud brand voice guidelines.

```python
def check_brand_voice_compliance(
    content: str,
    guidelines: Optional[Dict[str, Any]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `content` (str, required): Content to check
- `guidelines` (Dict[str, Any], optional): Specific guidelines to check against
- `tool_context` (ToolContext, optional): Google ADK tool context

**Returns:**
```python
{
    "compliance_score": int,              # Score 0-100
    "issues_found": List[Dict],           # List of compliance issues
    "positive_aspects": List[str],        # Good aspects identified
    "total_issues": int,                  # Number of issues found
    "recommendations": List[str],         # Improvement recommendations
    "status": str                        # "completed" or "error"
}
```

**Issue Object Structure:**
```python
{
    "type": str,         # "jargon", "passive_voice", "paragraph_length", "inclusive_language"
    "severity": str,     # "low", "medium", "high"
    "message": str,      # Specific feedback message
    "impact": int        # Score impact (negative)
}
```

---

### search_brand_voice_examples

Searches for specific examples of Google Cloud content that match the user's goal.

```python
def search_brand_voice_examples(
    content_goal: str,
    audience: str = "technical professionals",
    format_type: str = "blog_post",
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]
```

**Parameters:**
- `content_goal` (str, required): What the user wants to achieve (e.g., "explain AI/ML benefits")
- `audience` (str, optional): Target audience. Default: "technical professionals"
- `format_type` (str, optional): Content format needed. Default: "blog_post"
- `tool_context` (ToolContext, optional): Google ADK tool context

---

### get_google_cloud_terminology

Returns the official Google Cloud terminology and preferred usage.

```python
def get_google_cloud_terminology() -> Dict[str, Any]
```

**Returns:**
```python
{
    "preferred_terms": Dict[str, str],    # Preferred terminology
    "service_names": Dict[str, str],      # Service name standards
    "avoid": Dict[str, str],              # Terms to avoid
    "industry_terms": Dict[str, str]      # Industry standard terms
}
```

**Example Return:**
```python
{
    "preferred_terms": {
        "Google Cloud": "Use instead of GCP, Google Cloud Platform",
        "AI and machine learning": "Use instead of AI/ML in customer content",
        "multicloud": "One word, not multi-cloud"
    },
    "service_names": {
        "BigQuery": "Correct capitalization",
        "Compute Engine": "Two words"
    }
}
```

---

## Helper Tools

### get_quick_brand_voice_tips

Provides quick brand voice tips for specific content types.

```python
def get_quick_brand_voice_tips(content_type: str = "blog_post") -> Dict[str, Any]
```

**Parameters:**
- `content_type` (str, optional): Type of content - "blog_post", "email", "social_media"

**Returns:**
```python
{
    "voice_tips": List[str],      # Voice guidelines for content type
    "structure_tips": List[str]   # Structure guidelines for content type
}
```

---

### get_headline_best_practices

Returns Google Cloud headline best practices and guidelines.

```python
def get_headline_best_practices() -> Dict[str, Any]
```

**Returns:**
```python
{
    "character_limits": Dict[str, str],   # Character limits for different platforms
    "headline_formulas": Dict[str, str],  # Proven headline formulas
    "power_words": List[str],             # Effective words to use
    "brand_voice_guidelines": List[str],  # Brand voice specific guidelines
    "seo_tips": List[str]                # SEO optimization tips
}
```

---

## User Management Tools

### get_users_name

Gets the authenticated user's name and email.

```python
def get_users_name(tool_context: ToolContext) -> dict
```

**Parameters:**
- `tool_context` (ToolContext, required): Google ADK tool context with OAuth token

**Returns:**
```python
{
    "email": str,  # User's email address
    "name": str    # User's display name
}
```

---

### self_report

Reports the agent version and capabilities.

```python
def self_report() -> Dict[str, Any]
```

**Returns:**
```python
{
    "name": str,                    # Agent name
    "version": str,                 # Version number
    "capabilities": List[str],      # List of capabilities
    "description": str             # Agent description
}
```

---

## Error Handling

All tools follow consistent error handling patterns:

### Success Response
```python
{
    # Tool-specific data fields
    "status": "completed"
}
```

### Error Response
```python
{
    "error": str,        # Error message
    "status": "error"
    # May include partial data if applicable
}
```

### Common Error Types
- **Missing Required Parameters**: When required fields are not provided
- **Invalid Content**: When content is empty or malformed
- **Configuration Errors**: When RAG or other services are misconfigured
- **Authentication Errors**: When OAuth tokens are invalid or expired

---

## Usage Examples

### Complete Content Creation Workflow

```python
# 1. Generate outline first
outline = generate_content_outline(
    topic="Google Cloud security best practices",
    target_audience="security professionals"
)

# 2. Generate full content
content = generate_blog_content(
    topic="Google Cloud security best practices",
    key_points=["Zero-trust security", "IAM best practices", "Data encryption"],
    target_audience="security professionals",
    content_length="medium",
    google_cloud_services=["IAM", "Cloud KMS", "Security Command Center"]
)

# 3. Generate headlines
headlines = generate_headlines(
    topic="Google Cloud security best practices",
    content_summary="Comprehensive guide to securing Google Cloud environments",
    target_audience="security professionals",
    headline_types=["how-to", "benefit-driven"]
)

# 4. Review final content
review = review_content_for_brand_voice(
    content=content["content"],
    content_type="blog_post",
    target_audience="security professionals"
)
```

### Content Optimization Workflow

```python
# 1. Check compliance
compliance = check_brand_voice_compliance(
    content="Your existing content..."
)

# 2. Get specific guidelines
guidelines = retrieve_brand_voice_guidelines(
    topic_area="security",
    content_type="blog_post"
)

# 3. Optimize headline
optimized_headline = optimize_existing_headline(
    current_headline="Your current headline",
    content_context="Brief content summary",
    target_seo_keywords=["security", "best practices", "Google Cloud"]
)
```

---

## Rate Limits & Performance

### Expected Response Times
- **Content Review**: 2-5 seconds
- **Content Generation**: 10-30 seconds
- **Headline Generation**: 5-15 seconds
- **Knowledge Retrieval**: 1-3 seconds
- **Compliance Checking**: 2-5 seconds

### Best Practices
- Use content outlines for complex topics before full generation
- Batch multiple headline requests when possible
- Cache frequently used guidelines and terminology
- Monitor token usage for cost optimization

---

This API reference provides complete documentation for integrating with and extending the Google Cloud Brand Voice Agent.