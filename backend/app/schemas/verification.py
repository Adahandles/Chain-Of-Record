# Pydantic schemas for verification API
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VerificationStatusEnum(str, Enum):
    """Verification status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class DocumentTypeEnum(str, Enum):
    """Document type enumeration."""
    DRIVERS_LICENSE = "drivers_license"
    PASSPORT = "passport"
    NATIONAL_ID = "national_id"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"
    OTHER = "other"


class PersonalInfoCreate(BaseModel):
    """Personal information for verification."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: str = Field(..., description="Date of birth in YYYY-MM-DD format")
    ssn_last_4: Optional[str] = Field(None, min_length=4, max_length=4, description="Last 4 digits of SSN")
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    postal_code: str = Field(..., min_length=5, max_length=10)
    country: str = Field(default="US", min_length=2, max_length=2)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)

    @validator('date_of_birth')
    def validate_dob(cls, v):
        """Validate date of birth format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date of birth must be in YYYY-MM-DD format')
        return v

    @validator('ssn_last_4')
    def validate_ssn(cls, v):
        """Validate SSN last 4 digits."""
        if v and not v.isdigit():
            raise ValueError('SSN last 4 must contain only digits')
        return v


class VerificationRequestCreate(BaseModel):
    """Create a new verification request."""
    entity_id: Optional[int] = None
    person_id: Optional[int] = None
    personal_info: Optional[PersonalInfoCreate] = None


class VerificationRequestOut(BaseModel):
    """Verification request output schema."""
    id: int
    user_id: int
    entity_id: Optional[int]
    person_id: Optional[int]
    status: VerificationStatusEnum
    personal_info: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    id: int
    verification_request_id: int
    document_type: DocumentTypeEnum
    file_name: str
    file_size: Optional[int]
    uploaded_at: datetime
    verified: bool

    class Config:
        from_attributes = True


class LivenessCheckCreate(BaseModel):
    """Liveness check data."""
    verification_request_id: int


class LivenessCheckResponse(BaseModel):
    """Response after liveness check."""
    id: int
    verification_request_id: int
    liveness_score: Optional[float]
    passed: bool
    checked_at: datetime

    class Config:
        from_attributes = True


class VerificationStatusResponse(BaseModel):
    """Verification status response."""
    id: int
    status: VerificationStatusEnum
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    documents_count: int
    liveness_checks_count: int
    can_submit: bool


class VerificationSubmitResponse(BaseModel):
    """Response after submitting verification."""
    id: int
    status: VerificationStatusEnum
    submitted_at: datetime
    message: str


class AdminVerificationQueueItem(BaseModel):
    """Verification queue item for admin view."""
    id: int
    user_id: int
    status: VerificationStatusEnum
    created_at: datetime
    submitted_at: Optional[datetime]
    documents_count: int
    liveness_checks_count: int


class AdminReviewRequest(BaseModel):
    """Admin review decision."""
    decision: str = Field(..., description="approve, reject, or request_more_info")
    notes: Optional[str] = Field(None, max_length=2000)

    @validator('decision')
    def validate_decision(cls, v):
        """Validate admin decision."""
        valid_decisions = ['approve', 'reject', 'request_more_info']
        if v not in valid_decisions:
            raise ValueError(f'Decision must be one of: {valid_decisions}')
        return v


class AdminReviewResponse(BaseModel):
    """Response after admin review."""
    id: int
    status: VerificationStatusEnum
    reviewed_by: int
    reviewed_at: datetime
    notes: Optional[str]
    message: str


class VerificationDetailOut(BaseModel):
    """Detailed verification information for admin."""
    id: int
    user_id: int
    entity_id: Optional[int]
    person_id: Optional[int]
    status: VerificationStatusEnum
    personal_info: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    notes: Optional[str]
    documents: List[DocumentUploadResponse]
    liveness_checks: List[LivenessCheckResponse]

    class Config:
        from_attributes = True
