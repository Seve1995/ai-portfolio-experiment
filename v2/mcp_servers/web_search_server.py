"""
MCP Tool: Brave Web Search
Source: Brave Search API (free tier: 2,000 queries/month)
Purpose: Standardized web search for all models (replaces native browser search from V1).
"""

import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"

TOOL_DEFINITION = {
    "name": "web_search",
    "description": (
        "Search the web for financial news, stock analysis, market catalysts, company information, "
        "or any other topic. Returns the top results with title, URL, and snippet. "
        "Use this to discover information not available through the specialized financial tools. "
        "Budget: use wisely, you have limited searches per day."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query. Be specific for better results. Example: 'IOVA FDA approval catalyst 2026'"
            },
            "count": {
                "type": "integer",
                "minimum": 3,
                "maximum": 10,
                "default": 5,
                "description": "Number of results to return (3-10)"
            },
            "freshness": {
                "type": "string",
                "enum": ["pd", "pw", "pm"],
                "description": "Filter by recency: 'pd' = past day, 'pw' = past week, 'pm' = past month. Omit for all time."
            }
        },
        "required": ["query"]
    }
}


def execute(query: str, count: int = 5, freshness: Optional[str] = None) -> dict:
    """
    Execute a web search via Brave Search API.
    
    Returns:
        {
            "query": "IOVA FDA approval",
            "results": [
                {
                    "title": "Iovance Biotherapeutics Announces FDA...",
                    "url": "https://...",
                    "snippet": "...",
                    "age": "2 days ago"
                },
                ...
            ],
            "total_results": 5
        }
    """
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return {"error": "BRAVE_API_KEY not set. Get one free at https://brave.com/search/api/"}

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }

    params = {
        "q": query,
        "count": min(count, 10),
        "text_decorations": False,
        "search_lang": "en",
    }
    if freshness:
        params["freshness"] = freshness

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(BRAVE_API_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
                "age": item.get("age", ""),
            })

        logger.info(f"Brave search '{query}': {len(results)} results")

        return {
            "query": query,
            "results": results,
            "total_results": len(results),
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"Brave search HTTP error: {e.response.status_code}")
        return {"error": f"Search API error: {e.response.status_code}", "query": query}
    except Exception as e:
        logger.error(f"Brave search error: {e}")
        return {"error": str(e), "query": query}
