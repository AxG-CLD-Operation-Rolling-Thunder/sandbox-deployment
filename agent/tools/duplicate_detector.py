"""
Duplicate Detector Tool - Searches for similar Plan on a Page documents to prevent duplicate work
"""
from typing import Dict, Any, List, Optional
from google.adk.tools import ToolContext
from .drive_search_supporter import search_all_drive_sources, get_drive_service


def search_similar_plans(
    project_name: str,
    project_description: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Search Google Drive for similar Plan on a Page documents to detect potential duplicates.

    This tool helps prevent duplicate work by finding existing plans that might be:
    - The same initiative
    - A feature extension of existing work
    - Related work that could be coordinated

    Args:
        project_name: Name of the project/campaign to search for
        project_description: Optional description for more context in search
        tool_context: Google ADK tool context (required for Drive access)

    Returns:
        Dict containing similar plans found, with recommendations
    """
    if not project_name or not project_name.strip():
        return {
            "error": "Please provide a project name to search for",
            "similar_plans": [],
            "status": "error"
        }

    if not tool_context:
        return {
            "error": "Tool context required for Drive search",
            "similar_plans": [],
            "status": "error"
        }

    try:
        # Search for similar plan documents
        drive_service = get_drive_service(tool_context)

        # Build search query - look for "Plan on a Page" documents with similar names
        search_terms = _extract_search_keywords(project_name, project_description)

        similar_plans = []

        for term in search_terms[:3]:  # Search top 3 most relevant terms
            query_results = search_all_drive_sources(term, drive_service)

            for file in query_results[:5]:  # Top 5 results per term
                # Check if it's likely a Plan on a Page document
                if _is_likely_plan_document(file['name']):
                    similar_plans.append({
                        'file_id': file['id'],
                        'name': file['name'],
                        'mime_type': file.get('mimeType', 'unknown'),
                        'owners': file.get('owners', []),
                        'search_term': term
                    })

        # Deduplicate by file ID
        unique_plans = {plan['file_id']: plan for plan in similar_plans}.values()
        unique_plans_list = list(unique_plans)

        # Calculate similarity scores
        scored_plans = []
        for plan in unique_plans_list:
            similarity_score = _calculate_similarity(project_name, plan['name'])
            scored_plans.append({
                **plan,
                'similarity_score': similarity_score
            })

        # Sort by similarity score
        scored_plans.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Generate recommendations
        recommendations = _generate_duplicate_recommendations(scored_plans, project_name)

        return {
            "search_query": project_name,
            "similar_plans_found": len(scored_plans),
            "plans": scored_plans[:10],  # Return top 10 most similar
            "recommendations": recommendations,
            "action_needed": len(scored_plans) > 0,
            "status": "completed"
        }

    except Exception as e:
        return {
            "error": f"Duplicate search failed: {str(e)}",
            "similar_plans": [],
            "status": "error"
        }


def _extract_search_keywords(project_name: str, description: Optional[str] = None) -> List[str]:
    """Extract key search terms from project name and description."""
    keywords = []

    # Add full project name
    keywords.append(project_name)

    # Extract key words from project name (words 4+ chars)
    words = [w.strip() for w in project_name.split() if len(w.strip()) >= 4]
    keywords.extend(words[:3])

    # Add key words from description if provided
    if description:
        desc_words = [w.strip() for w in description.split() if len(w.strip()) >= 5]
        keywords.extend(desc_words[:2])

    # Add "Plan on a Page" to ensure we're finding plan documents
    keywords = [f"{kw} Plan" for kw in keywords[:3]]

    return keywords


def _is_likely_plan_document(filename: str) -> bool:
    """Determine if a file is likely a Plan on a Page document."""
    filename_lower = filename.lower()

    plan_indicators = [
        'plan on a page',
        'plan-on-a-page',
        'poap',
        'campaign plan',
        'marketing plan',
        'launch plan'
    ]

    return any(indicator in filename_lower for indicator in plan_indicators)


def _calculate_similarity(query: str, candidate: str) -> float:
    """
    Calculate similarity score between query and candidate string.

    Simple word overlap similarity (could be enhanced with more sophisticated algorithms).

    Args:
        query: Search query string
        candidate: Candidate string to compare

    Returns:
        Similarity score between 0 and 1
    """
    query_words = set(query.lower().split())
    candidate_words = set(candidate.lower().split())

    if not query_words or not candidate_words:
        return 0.0

    # Calculate Jaccard similarity
    intersection = query_words.intersection(candidate_words)
    union = query_words.union(candidate_words)

    similarity = len(intersection) / len(union) if union else 0.0

    # Boost score if exact phrases match
    if query.lower() in candidate.lower():
        similarity = min(1.0, similarity + 0.3)

    return round(similarity, 2)


def _generate_duplicate_recommendations(similar_plans: List[Dict], project_name: str) -> List[str]:
    """Generate recommendations based on duplicate search results."""
    if not similar_plans:
        return [
            "No similar plans found - this appears to be a unique initiative",
            "Proceed with creating your Plan on a Page"
        ]

    high_similarity = [p for p in similar_plans if p.get('similarity_score', 0) > 0.5]

    recommendations = []

    if high_similarity:
        recommendations.append(
            f"Found {len(high_similarity)} highly similar plan(s) - review to determine if this is:"
        )
        recommendations.append("  1. The same initiative (coordinate with existing team)")
        recommendations.append("  2. A feature extension (build on existing plan)")
        recommendations.append("  3. A distinct initiative (proceed with new plan)")

        # List top 3 most similar
        for plan in high_similarity[:3]:
            recommendations.append(
                f"  - '{plan['name']}' (similarity: {plan['similarity_score']*100:.0f}%)"
            )
    else:
        recommendations.append(
            f"Found {len(similar_plans)} potentially related plan(s), but similarity is low"
        )
        recommendations.append("Review these plans for coordination opportunities, then proceed")

    recommendations.append(
        "💡 Tip: Coordinate with teams on similar initiatives to maximize efficiency using Adopt/Adapt/Invent framework"
    )

    return recommendations


def check_for_duplicates_simple(
    project_keywords: List[str],
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Simple duplicate check using keyword list.

    Args:
        project_keywords: List of keywords that describe the project
        tool_context: Google ADK tool context

    Returns:
        Dict with duplicate check results
    """
    if not project_keywords:
        return {"error": "No keywords provided", "duplicates_found": False}

    if not tool_context:
        return {"error": "Tool context required", "duplicates_found": False}

    try:
        drive_service = get_drive_service(tool_context)

        # Combine keywords for search
        search_query = " ".join(project_keywords[:3])

        results = search_all_drive_sources(search_query, drive_service)

        # Filter for plan documents
        plan_docs = [r for r in results if _is_likely_plan_document(r['name'])]

        return {
            "duplicates_found": len(plan_docs) > 0,
            "potential_duplicates_count": len(plan_docs),
            "documents": plan_docs[:5],  # Top 5
            "recommendation": "Review these documents before creating a new plan" if plan_docs else "No duplicates found - proceed with plan creation"
        }

    except Exception as e:
        return {
            "error": f"Duplicate check failed: {str(e)}",
            "duplicates_found": False
        }
