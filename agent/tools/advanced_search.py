import json, requests
from google.adk.tools import ToolContext
from .oauth_support import retrieve_user_auth
from ..config.config import AGENT_SPACE_DISCOVERY_ENGINE_URL


def search_using_vertex(query: str, tool_context: ToolContext) -> str:
    access_token = retrieve_user_auth(tool_context).token

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "pageSize": 10,
        "spellCorrectionSpec": {"mode": "AUTO"},
        "languageCode": "en-US",
        "relevanceScoreSpec": {"returnRelevanceScore": True},
        "userInfo": {"timeZone": "America/Chicago"},
        "contentSearchSpec": {"snippetSpec": {"returnSnippet": True}},
        "naturalLanguageQueryUnderstandingSpec": {
            "filterExtractionCondition": "ENABLED"
        },
    }

    resp = requests.post(
        AGENT_SPACE_DISCOVERY_ENGINE_URL, headers=headers, data=json.dumps(payload)
    )
    return json.dumps(resp.json(), indent=2)
