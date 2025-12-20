# Verification domain models
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.db import Base
from enum import Enum


class VerificationStatus(str, Enum):
    """Verification status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class DocumentType(str, Enum):
    """Document type enumeration."""
    DRIVERS_LICENSE = "drivers_license"
    PASSPORT = "passport"
    NATIONAL_ID = "national_id"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"
    OTHER = "other"


class VerificationRequest(Base):
    """
    Verification request model for KYC onboarding.
    Tracks the overall verification process for a user.
    """
    __tablename__ = "verification_requests"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id = Column(BigInteger, ForeignKey("entities.id", ondelete="SET NULL"), nullable=True, index=True)
    person_id = Column(BigInteger, ForeignKey("people.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(50), nullable=False, index=True, default=VerificationStatus.PENDING)
    personal_info = Column(JSONB, nullable=True)  # JSON blob for personal details
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    reviewed_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    documents = relationship("VerificationDocument", back_populates="verification_request", cascade="all, delete-orphan")
    liveness_checks = relationship("VerificationLiveness", back_populates="verification_request", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<VerificationRequest(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class VerificationDocument(Base):
    """
    Document uploads for verification (ID, passport, utility bills, etc.).
    """
    __tablename__ = "verification_documents"

    id = Column(BigInteger, primary_key=True, index=True)
    verification_request_id = Column(
        BigInteger, 
        ForeignKey("verification_requests.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    document_type = Column(String(50), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    mime_type = Column(String(100), nullable=True)
    encrypted = Column(Boolean, default=True, nullable=False)
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    verified = Column(Boolean, default=False, nullable=False)
    verification_notes = Column(Text, nullable=True)

    # Relationships
    verification_request = relationship("VerificationRequest", back_populates="documents")

    def __repr__(self) -> str:
        return f"<VerificationDocument(id={self.id}, type='{self.document_type}', verified={self.verified})>"


class VerificationLiveness(Base):
    """
    Liveness/selfie check results for biometric verification.
    """
    __tablename__ = "verification_liveness"

    id = Column(BigInteger, primary_key=True, index=True)
    verification_request_id = Column(
        BigInteger, 
        ForeignKey("verification_requests.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    image_path = Column(String(500), nullable=False)
    encrypted = Column(Boolean, default=True, nullable=False)
    liveness_score = Column(Numeric(5, 2), nullable=True)
    passed = Column(Boolean, default=False, nullable=False, index=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    check_metadata = Column(JSONB, nullable=True)  # Additional metadata from liveness check

    # Relationships
    verification_request = relationship("VerificationRequest", back_populates="liveness_checks")

    def __repr__(self) -> str:
        return f"<VerificationLiveness(id={self.id}, passed={self.passed}, score={self.liveness_score})>"
