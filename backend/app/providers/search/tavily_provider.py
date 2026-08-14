from typing import Any, Dict, List

import httpx

from ...config import settings
from ...core.source_reliability import get_reliability_tier
from .base import SearchProvider

TAVILY_URL = "https://api.tavily.com/search"


class TavilySearchProvider(SearchProvider):
    """Live web evidence retrieval via the Tavily search API.

    Returns raw search results only — reliability tiers are computed
    locally from the source domain, never asserted by the search API
    or the LLM.
    """

    def search(self, query: str, max_results: int = 6) -> List[Dict[str, Any]]:
        try:
            response = httpx.post(
                TAVILY_URL,
                json={
                    "api_key": settings.TAVILY_API_KEY,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": max_results,
                    "include_answer": False,
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:  # network / auth / rate-limit failures
            raise RuntimeError(f"Evidence search provider (Tavily) failed: {exc}") from exc

        results: List[Dict[str, Any]] = []
        for item in data.get("results", []):
            url = item.get("url", "")
            results.append(
                {
                    "source_name": (item.get("title") or url)[:256],
                    "url": url,
                    "snippet": (item.get("content") or "")[:600],
                    "reliability": get_reliability_tier(url),
                }
            )
        return results
