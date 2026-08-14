import hashlib
import math
import re
from typing import List

from .base import EmbeddingProvider

VECTOR_SIZE = 512


class HashingEmbeddingProvider(EmbeddingProvider):
    """Zero-dependency fallback embedding used when sentence-transformers
    (and its torch dependency) isn't installed.

    A deterministic hashed bag-of-words vector. It won't catch deep
    paraphrases as well as real sentence embeddings, but it reliably
    catches near-duplicate/reworded claims that share most content words,
    which is the common case for reworded WhatsApp forwards.
    """

    def embed(self, text: str) -> List[float]:
        vector = [0.0] * VECTOR_SIZE
        words = re.findall(r"[a-zA-Z0-9₹]+", text.lower())
        for word in words:
            idx = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % VECTOR_SIZE
            vector[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def similarity(self, a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            return 0.0
        return sum(x * y for x, y in zip(a, b))
