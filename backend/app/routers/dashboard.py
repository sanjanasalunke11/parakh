from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Claim, Verdict, VerificationHistory
from ..schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_claims = db.query(Claim).count()

    def count_for(verdict: Verdict) -> int:
        return db.query(Claim).filter(Claim.verdict == verdict).count()

    total_checks = db.query(VerificationHistory).count()

    category_rows = (
        db.query(Claim.category, func.count(Claim.id))
        .group_by(Claim.category)
        .order_by(func.count(Claim.id).desc())
        .all()
    )
    categories = [{"category": cat, "count": cnt} for cat, cnt in category_rows]

    most_checked = (
        db.query(Claim)
        .order_by(Claim.check_count.desc(), Claim.created_at.desc())
        .limit(8)
        .all()
    )
    recent = db.query(Claim).order_by(Claim.created_at.desc()).limit(10).all()

    return DashboardStats(
        total_claims=total_claims,
        verified_count=count_for(Verdict.VERIFIED),
        false_count=count_for(Verdict.FALSE),
        misleading_count=count_for(Verdict.MISLEADING),
        unverified_count=count_for(Verdict.UNVERIFIED),
        total_checks=total_checks,
        categories=categories,
        most_checked=most_checked,
        recent=recent,
    )
