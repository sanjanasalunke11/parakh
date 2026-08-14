import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class Verdict(str, enum.Enum):
    VERIFIED = "VERIFIED"
    FALSE = "FALSE"
    MISLEADING = "MISLEADING"
    UNVERIFIED = "UNVERIFIED"


class EvidenceStrength(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InputType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    URL = "url"
    VOICE = "voice"


class ReliabilityTier(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Claim(Base):
    """The persistent verification ledger. One row per unique underlying claim."""

    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    normalized_claim = Column(Text, nullable=False)
    verdict = Column(SAEnum(Verdict, native_enum=False, length=32), nullable=False, default=Verdict.UNVERIFIED, index=True)
    evidence_strength = Column(SAEnum(EvidenceStrength, native_enum=False, length=16), nullable=False, default=EvidenceStrength.LOW)
    explanation = Column(Text, nullable=False)
    category = Column(String(64), nullable=False, default="Other", index=True)
    input_type = Column(SAEnum(InputType, native_enum=False, length=16), nullable=False, default=InputType.TEXT)
    source_url = Column(String(1024), nullable=True)
    embedding = Column(JSON, nullable=True)
    check_count = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    evidence_items = relationship("EvidenceItem", back_populates="claim", cascade="all, delete-orphan")
    history = relationship("VerificationHistory", back_populates="claim", cascade="all, delete-orphan")


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False, index=True)
    source_name = Column(String(256), nullable=False)
    source_url = Column(String(1024), nullable=False)
    snippet = Column(Text, nullable=False)
    reliability = Column(SAEnum(ReliabilityTier, native_enum=False, length=16), nullable=False, default=ReliabilityTier.LOW)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="evidence_items")


class VerificationHistory(Base):
    """Log of every raw submission, even ones that matched an existing ledger entry."""

    __tablename__ = "verification_history"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False, index=True)
    raw_input = Column(Text, nullable=False)
    input_type = Column(SAEnum(InputType, native_enum=False, length=16), nullable=False)
    matched_existing = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    claim = relationship("Claim", back_populates="history")
