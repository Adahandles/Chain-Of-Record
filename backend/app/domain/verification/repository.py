# Verification repository for data access
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from datetime import datetime

from .models import VerificationRequest, VerificationDocument, VerificationLiveness, VerificationStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class VerificationRepository:
    """Repository for verification request operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        entity_id: Optional[int] = None,
        person_id: Optional[int] = None,
        personal_info: Optional[dict] = None
    ) -> VerificationRequest:
        """Create a new verification request."""
        verification = VerificationRequest(
            user_id=user_id,
            entity_id=entity_id,
            person_id=person_id,
            status=VerificationStatus.PENDING,
            personal_info=personal_info
        )
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        logger.info(f"Created verification request: {verification.id} for user: {user_id}")
        return verification

    def get_by_id(self, verification_id: int) -> Optional[VerificationRequest]:
        """Get verification request by ID."""
        return self.db.query(VerificationRequest).filter(
            VerificationRequest.id == verification_id
        ).first()

    def get_by_id_with_relations(self, verification_id: int) -> Optional[VerificationRequest]:
        """Get verification request with all related data."""
        return self.db.query(VerificationRequest).options(
            joinedload(VerificationRequest.documents),
            joinedload(VerificationRequest.liveness_checks)
        ).filter(VerificationRequest.id == verification_id).first()

    def get_by_user_id(self, user_id: int, limit: int = 50) -> List[VerificationRequest]:
        """Get all verification requests for a user."""
        return self.db.query(VerificationRequest).filter(
            VerificationRequest.user_id == user_id
        ).order_by(desc(VerificationRequest.created_at)).limit(limit).all()

    def get_pending_reviews(self, limit: int = 100) -> List[VerificationRequest]:
        """Get verification requests pending admin review."""
        return self.db.query(VerificationRequest).filter(
            VerificationRequest.status.in_([VerificationStatus.SUBMITTED, VerificationStatus.NEEDS_REVIEW])
        ).order_by(VerificationRequest.submitted_at).limit(limit).all()

    def update_status(
        self,
        verification_id: int,
        status: str,
        reviewed_by: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Optional[VerificationRequest]:
        """Update verification request status."""
        verification = self.get_by_id(verification_id)
        if not verification:
            return None

        verification.status = status
        verification.updated_at = datetime.now()

        if status == VerificationStatus.SUBMITTED:
            verification.submitted_at = datetime.now()

        if reviewed_by:
            verification.reviewed_by = reviewed_by
            verification.reviewed_at = datetime.now()

        if notes:
            verification.notes = notes

        self.db.commit()
        self.db.refresh(verification)
        logger.info(f"Updated verification {verification_id} status to: {status}")
        return verification

    def delete(self, verification_id: int) -> bool:
        """Delete a verification request."""
        verification = self.get_by_id(verification_id)
        if verification:
            self.db.delete(verification)
            self.db.commit()
            logger.info(f"Deleted verification request: {verification_id}")
            return True
        return False


class VerificationDocumentRepository:
    """Repository for verification document operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        verification_request_id: int,
        document_type: str,
        file_path: str,
        file_name: str,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        encrypted: bool = True
    ) -> VerificationDocument:
        """Create a new verification document record."""
        document = VerificationDocument(
            verification_request_id=verification_request_id,
            document_type=document_type,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            encrypted=encrypted
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        logger.info(f"Created document record: {document.id} for verification: {verification_request_id}")
        return document

    def get_by_id(self, document_id: int) -> Optional[VerificationDocument]:
        """Get document by ID."""
        return self.db.query(VerificationDocument).filter(
            VerificationDocument.id == document_id
        ).first()

    def get_by_verification_id(self, verification_request_id: int) -> List[VerificationDocument]:
        """Get all documents for a verification request."""
        return self.db.query(VerificationDocument).filter(
            VerificationDocument.verification_request_id == verification_request_id
        ).all()

    def update_verification_status(
        self,
        document_id: int,
        verified: bool,
        notes: Optional[str] = None
    ) -> Optional[VerificationDocument]:
        """Update document verification status."""
        document = self.get_by_id(document_id)
        if not document:
            return None

        document.verified = verified
        if notes:
            document.verification_notes = notes

        self.db.commit()
        self.db.refresh(document)
        return document


class VerificationLivenessRepository:
    """Repository for liveness check operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        verification_request_id: int,
        image_path: str,
        liveness_score: Optional[float] = None,
        passed: bool = False,
        metadata: Optional[dict] = None,
        encrypted: bool = True
    ) -> VerificationLiveness:
        """Create a new liveness check record."""
        liveness = VerificationLiveness(
            verification_request_id=verification_request_id,
            image_path=image_path,
            liveness_score=liveness_score,
            passed=passed,
            metadata=metadata,
            encrypted=encrypted
        )
        self.db.add(liveness)
        self.db.commit()
        self.db.refresh(liveness)
        logger.info(f"Created liveness check: {liveness.id} for verification: {verification_request_id}")
        return liveness

    def get_by_id(self, liveness_id: int) -> Optional[VerificationLiveness]:
        """Get liveness check by ID."""
        return self.db.query(VerificationLiveness).filter(
            VerificationLiveness.id == liveness_id
        ).first()

    def get_by_verification_id(self, verification_request_id: int) -> List[VerificationLiveness]:
        """Get all liveness checks for a verification request."""
        return self.db.query(VerificationLiveness).filter(
            VerificationLiveness.verification_request_id == verification_request_id
        ).all()
