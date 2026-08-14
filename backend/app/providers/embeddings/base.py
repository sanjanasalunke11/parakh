from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError

    @abstractmethod
    def similarity(self, a: List[float], b: List[float]) -> float:
        raise NotImplementedError
