"""The Truth Agent core loop:

Input -> Extract Claim -> Check Ledger -> Retrieve Evidence -> Verify -> Explain -> Save to Ledger

This module is transport-agnostic: it takes a raw string and returns a
ClaimResult. FastAPI routers call it today; a future WhatsApp webhook
(or any other channel) can call the exact same function with zero
changes to this file.
"""

import logging

from sqlalchemy.orm import Session

from ..models import Claim, EvidenceItem, InputType, VerificationHistory
from ..providers.factory import get_embedding_provider, get_llm_provider, get_search_provider
from ..schemas import ClaimResult
from ..utils.validation import (
    validate_category,
    validate_explanation,
    validate_strength,
    validate_verdict,
)
from .evidence_retrieval import retrieve_evidence
from .semantic_matching import find_similar_claim

logger = logging.getLogger("parakh.pipeline")


def run_verification_pipeline(
    db: Session,
    raw_text: str,
    input_type: InputType,
    source_url: str | None = None,
) -> ClaimResult:
    raw_text = raw_text.strip()

    llm = get_llm_provider()
    embedder = get_embedding_provider()
    search = get_search_provider()

    # 1. Extract Claim
    # A transient extraction failure (rate limit, timeout, provider outage)
    # degrades to using the raw input verbatim rather than failing the whole
    # request — verification can still proceed on the unprocessed text.
    try:
        extraction = llm.extract_claim(raw_text)
    except Exception as exc:
        logger.warning("Claim extraction failed, falling back to raw text: %s", exc)
        extraction = {}
    normalized_claim = (extraction.get("normalized_claim") or raw_text).strip()[:500]
    category_hint = validate_category(extraction.get("category", "Other"))

    # 2. Check Ledger (semantic dedup — differently worded versions of the
    #    same claim resolve to the same ledger entry)
    query_embedding = embedder.embed(normalized_claim)
    existing = find_similar_claim(db, embedder, query_embedding)

    if existing is not None:
        existing.check_count += 1
        db.add(
            VerificationHistory(
                claim_id=existing.id,
                raw_input=raw_text,
                input_type=input_type,
                matched_existing=True,
            )
        )
        db.commit()
        db.refresh(existing)
        return _to_claim_result(existing, previously_verified=True)

    # 3. Retrieve Evidence (ranked by reliability; never LLM-invented)
    evidence = retrieve_evidence(search, normalized_claim)

    # 4 + 5. Verify & Explain
    # Category is decided once, during extraction (which is enum-constrained) —
    # verification only ever judges the verdict/strength/explanation, so there's
    # no second, unconstrained category guess to drift out of sync or collapse
    # to "Other" when it doesn't match the fixed list.
    category = category_hint

    if not evidence:
        verdict = "UNVERIFIED"
        strength = "LOW"
        explanation = (
            "No reliable evidence could be found for this claim from trusted sources. "
            "Treat it with caution until it can be confirmed officially."
        )
    else:
        try:
            result = llm.verify_claim(normalized_claim, evidence)
            verdict = result.get("verdict", "UNVERIFIED")
            strength = result.get("evidence_strength", "LOW")
            explanation = result.get("explanation", "")
        except Exception as exc:
            logger.warning("Verification call failed, defaulting to UNVERIFIED: %s", exc)
            verdict, strength = "UNVERIFIED", "LOW"
            explanation = (
                "The verification engine could not complete analysis for this claim. "
                "Please try again shortly."
            )

    verdict = validate_verdict(verdict)
    strength = validate_strength(strength)
    explanation = validate_explanation(explanation)

    # 6. Save to Ledger
    claim = Claim(
        original_text=raw_text,
        normalized_claim=normalized_claim,
        verdict=verdict,
        evidence_strength=strength,
        explanation=explanation,
        category=category,
        input_type=input_type,
        source_url=source_url,
        embedding=query_embedding,
        check_count=1,
    )
    db.add(claim)
    db.flush()

    for item in evidence:
        db.add(
            EvidenceItem(
                claim_id=claim.id,
                source_name=item.get("source_name", "Unknown source")[:256],
                source_url=item.get("url", "")[:1024],
                snippet=item.get("snippet", "")[:2000],
                reliability=item.get("reliability", "LOW"),
            )
        )

    db.add(
        VerificationHistory(
            claim_id=claim.id,
            raw_input=raw_text,
            input_type=input_type,
            matched_existing=False,
        )
    )

    db.commit()
    db.refresh(claim)
    return _to_claim_result(claim, previously_verified=False)


def _to_claim_result(claim: Claim, previously_verified: bool) -> ClaimResult:
    return ClaimResult(
        id=claim.id,
        original_text=claim.original_text,
        normalized_claim=claim.normalized_claim,
        verdict=claim.verdict,
        evidence_strength=claim.evidence_strength,
        explanation=claim.explanation,
        category=claim.category,
        input_type=claim.input_type,
        source_url=claim.source_url,
        sources=list(claim.evidence_items),
        previously_verified=previously_verified,
        check_count=claim.check_count,
        created_at=claim.created_at,
    )
