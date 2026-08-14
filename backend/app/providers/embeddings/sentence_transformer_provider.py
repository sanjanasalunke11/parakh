from typing import List

import numpy as np

from .base import EmbeddingProvider


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Real semantic embeddings via a local sentence-transformers model.

    Runs fully locally (no API key, no external calls) once the model
    weights are downloaded on first use.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer  # heavy import, done lazily

        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> List[float]:
        vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def similarity(self, a: List[float], b: List[float]) -> float:
        a_arr, b_arr = np.array(a), np.array(b)
        denom = (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)) or 1e-8
        return float(np.dot(a_arr, b_arr) / denom)
