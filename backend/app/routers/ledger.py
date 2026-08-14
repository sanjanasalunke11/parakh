from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Claim
from ..schemas import LedgerDetail, LedgerListResponse

router = APIRouter(prefix="/api/ledger", tags=["ledger"])


@router.get("", response_model=LedgerListResponse)
def list_ledger(
    search: Optional[str] = Query(None, max_length=300),
    verdict: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Claim)

    if search:
        like = f"%{search}%"
        query = query.filter(or_(Claim.normalized_claim.ilike(like), Claim.original_text.ilike(like)))
    if verdict:
        query = query.filter(Claim.verdict == verdict.upper())
    if category:
        query = query.filter(Claim.category == category)

    total = query.count()
    items = (
        query.order_by(Claim.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return LedgerListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/{claim_id}", response_model=LedgerDetail)
def get_ledger_entry(claim_id: int, db: Session = Depends(get_db)):
    claim = db.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found")

    return LedgerDetail(
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
        previously_verified=claim.check_count > 1,
        check_count=claim.check_count,
        created_at=claim.created_at,
    )
