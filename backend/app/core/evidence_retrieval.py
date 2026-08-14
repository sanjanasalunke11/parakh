import logging
from typing import Any, Dict, List

from ..config import settings
from .source_reliability import RELIABILITY_SORT_ORDER

logger = logging.getLogger("parakh.evidence")


def retrieve_evidence(search_provider, query: str) -> List[Dict[str, Any]]:
    """Fetch + rank evidence. Any provider failure degrades to an empty
    list (→ UNVERIFIED downstream) rather than crashing the request —
    a flaky search API should never take down verification.
    """
    try:
        raw_results = search_provider.search(query, max_results=settings.MAX_EVIDENCE_RESULTS)
    except Exception as exc:
        logger.warning("Evidence retrieval failed for query %r: %s", query, exc)
        return []

    cleaned = [r for r in raw_results if r.get("url") and r.get("snippet")]
    cleaned.sort(key=lambda r: RELIABILITY_SORT_ORDER.get(r.get("reliability", "LOW"), 2))
    return cleaned[: settings.MAX_EVIDENCE_RESULTS]
