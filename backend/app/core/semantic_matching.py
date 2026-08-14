from typing import Optional

from sqlalchemy.orm import Session

from ..config import settings
from ..models import Claim


def find_similar_claim(db: Session, embedder, query_embedding) -> Optional[Claim]:
    """Scan recent ledger entries for a semantically equivalent claim.

    In-memory cosine scan is fine at hackathon/demo scale (thousands of
    rows); swap for a proper vector index (pgvector, Milvus, etc.) if
    the ledger grows large in production.
    """
    candidates = (
        db.query(Claim)
        .filter(Claim.embedding.isnot(None))
        .order_by(Claim.id.desc())
        .limit(settings.SEMANTIC_SCAN_LIMIT)
        .all()
    )

    best_claim, best_score = None, 0.0
    for candidate in candidates:
        score = embedder.similarity(query_embedding, candidate.embedding)
        if score > best_score:
            best_score, best_claim = score, candidate

    if best_claim is not None and best_score >= settings.SIMILARITY_THRESHOLD:
        return best_claim
    return None
