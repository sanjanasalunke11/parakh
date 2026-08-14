from abc import ABC, abstractmethod
from typing import Any, Dict, List


class SearchProvider(ABC):
    """Evidence retrieval layer. Returns raw search results only —
    never a verdict. Each result must include a url so reliability can
    be computed independently of the provider.
    """

    @abstractmethod
    def search(self, query: str, max_results: int = 6) -> List[Dict[str, Any]]:
        """Return a list of {"source_name": str, "url": str, "snippet": str}."""
        raise NotImplementedError
