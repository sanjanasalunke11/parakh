from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMProvider(ABC):
    """Reasoning layer. Never touches the internet directly and never
    invents evidence — verify_claim() must be judged only on the evidence
    snippets it is given.
    """

    @abstractmethod
    def extract_claim(self, raw_text: str) -> Dict[str, Any]:
        """Return {"normalized_claim": str, "category": str}."""
        raise NotImplementedError

    @abstractmethod
    def verify_claim(self, claim: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return {"verdict": str, "evidence_strength": str, "explanation": str, "category": str}."""
        raise NotImplementedError
