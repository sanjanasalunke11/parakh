import logging

from ..models import EvidenceStrength, Verdict

logger = logging.getLogger("parakh.validation")

VALID_CATEGORIES = {
    "Health", "Government Scheme", "Politics", "Finance",
    "Science & Technology", "Communal/Social", "Crime & Safety",
    "Entertainment", "Other",
}


def validate_verdict(value: str) -> Verdict:
    try:
        return Verdict(str(value).upper())
    except ValueError:
        logger.warning("LLM returned invalid verdict %r; defaulting to UNVERIFIED", value)
        return Verdict.UNVERIFIED


def validate_strength(value: str) -> EvidenceStrength:
    try:
        return EvidenceStrength(str(value).upper())
    except ValueError:
        logger.warning("LLM returned invalid evidence_strength %r; defaulting to LOW", value)
        return EvidenceStrength.LOW


def validate_category(value: str) -> str:
    if isinstance(value, str) and value in VALID_CATEGORIES:
        return value
    return "Other"


def validate_explanation(value: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()[:2000]
    return "No explanation was provided by the verification engine."
