from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import EvidenceStrength, InputType, ReliabilityTier, Verdict


class EvidenceItemOut(BaseModel):
    source_name: str
    source_url: str
    snippet: str
    reliability: ReliabilityTier

    model_config = {"from_attributes": True}


class ClaimResult(BaseModel):
    id: int
    original_text: str
    normalized_claim: str
    verdict: Verdict
    evidence_strength: EvidenceStrength
    explanation: str
    category: str
    input_type: InputType
    source_url: Optional[str] = None
    sources: List[EvidenceItemOut] = []
    previously_verified: bool
    check_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TextVerifyRequest(BaseModel):
    text: str = Field(min_length=3, max_length=5000)


class VoiceVerifyRequest(BaseModel):
    text: str = Field(min_length=3, max_length=5000)
    language: Optional[str] = "en"


class UrlVerifyRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)


class LedgerListItem(BaseModel):
    id: int
    normalized_claim: str
    verdict: Verdict
    evidence_strength: EvidenceStrength
    category: str
    input_type: InputType
    check_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LedgerListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[LedgerListItem]


class LedgerDetail(ClaimResult):
    pass


class CategoryCount(BaseModel):
    category: str
    count: int


class DashboardStats(BaseModel):
    total_claims: int
    verified_count: int
    false_count: int
    misleading_count: int
    unverified_count: int
    total_checks: int
    categories: List[CategoryCount]
    most_checked: List[LedgerListItem]
    recent: List[LedgerListItem]
