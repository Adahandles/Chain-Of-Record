# Verification service layer for business logic
from typing import Optional, List, Dict, Any, BinaryIO
from sqlalchemy.orm import Session
from datetime import datetime

from .repository import (
    VerificationRepository,
    VerificationDocumentRepository,
    VerificationLivenessRepository
)
from .models import VerificationStatus, DocumentType
from .storage import file_storage
from app.core.logging import get_logger

logger = get_logger(__name__)


class VerificationService:
    """Service layer for verification business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.verification_repo = VerificationRepository(db)
        self.document_repo = VerificationDocumentRepository(db)
        self.liveness_repo = VerificationLivenessRepository(db)

    def create_verification_request(
        self,
        user_id: int,
        entity_id: Optional[int] = None,
        person_id: Optional[int] = None,
        personal_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new verification request.
        
        Args:
            user_id: ID of the user requesting verification
            entity_id: Optional entity ID to link verification to
            person_id: Optional person ID to link verification to
            personal_info: Personal information submitted by user
            
        Returns:
            Dictionary with verification request details
        """
        verification = self.verification_repo.create(
            user_id=user_id,
            entity_id=entity_id,
            person_id=person_id,
            personal_info=personal_info
        )

        logger.info(
            f"Verification request created",
            extra={
                "verification_id": verification.id,
                "user_id": user_id,
                "entity_id": entity_id,
                "person_id": person_id
            }
        )

        return self._format_verification_response(verification)

    def upload_document(
        self,
        verification_id: int,
        document_type: str,
        file_content: BinaryIO,
        file_name: str,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a verification document.
        
        Args:
            verification_id: Verification request ID
            document_type: Type of document (drivers_license, passport, etc.)
            file_content: File content as binary stream
            file_name: Original file name
            mime_type: MIME type of the file
            
        Returns:
            Dictionary with document details
        """
        # Verify the verification request exists
        verification = self.verification_repo.get_by_id(verification_id)
        if not verification:
            raise ValueError(f"Verification request {verification_id} not found")

        # Validate document type
        if document_type not in [dt.value for dt in DocumentType]:
            raise ValueError(f"Invalid document type: {document_type}")

        # Save file to storage
        file_path, file_size = file_storage.save_file(
            file_content=file_content,
            verification_id=verification_id,
            file_name=file_name,
            document_type=document_type,
            encrypt=True
        )

        # Create document record
        document = self.document_repo.create(
            verification_request_id=verification_id,
            document_type=document_type,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            encrypted=True
        )

        # Update verification status to in_progress if it was pending
        if verification.status == VerificationStatus.PENDING:
            self.verification_repo.update_status(verification_id, VerificationStatus.IN_PROGRESS)

        logger.info(
            f"Document uploaded",
            extra={
                "verification_id": verification_id,
                "document_id": document.id,
                "document_type": document_type,
                "file_size": file_size
            }
        )

        return {
            "id": document.id,
            "verification_request_id": document.verification_request_id,
            "document_type": document.document_type,
            "file_name": document.file_name,
            "file_size": document.file_size,
            "uploaded_at": document.uploaded_at,
            "verified": document.verified
        }

    def verify_liveness(
        self,
        verification_id: int,
        image_content: BinaryIO,
        image_name: str
    ) -> Dict[str, Any]:
        """
        Process liveness/selfie check.
        
        Args:
            verification_id: Verification request ID
            image_content: Image content as binary stream
            image_name: Original image name
            
        Returns:
            Dictionary with liveness check results
        """
        # Verify the verification request exists
        verification = self.verification_repo.get_by_id(verification_id)
        if not verification:
            raise ValueError(f"Verification request {verification_id} not found")

        # Save image to storage
        file_path, _ = file_storage.save_file(
            file_content=image_content,
            verification_id=verification_id,
            file_name=image_name,
            document_type="liveness",
            encrypt=True
        )

        # TODO: Implement actual liveness detection logic
        # For now, use a simple placeholder score
        liveness_score = 85.0  # Placeholder score
        passed = liveness_score >= 70.0

        # Create liveness record
        liveness = self.liveness_repo.create(
            verification_request_id=verification_id,
            image_path=file_path,
            liveness_score=liveness_score,
            passed=passed,
            metadata={"method": "placeholder"},
            encrypted=True
        )

        logger.info(
            f"Liveness check processed",
            extra={
                "verification_id": verification_id,
                "liveness_id": liveness.id,
                "score": liveness_score,
                "passed": passed
            }
        )

        return {
            "id": liveness.id,
            "verification_request_id": liveness.verification_request_id,
            "liveness_score": float(liveness.liveness_score) if liveness.liveness_score else None,
            "passed": liveness.passed,
            "checked_at": liveness.checked_at
        }

    def get_verification_status(self, verification_id: int) -> Dict[str, Any]:
        """
        Get verification request status.
        
        Args:
            verification_id: Verification request ID
            
        Returns:
            Dictionary with verification status details
        """
        verification = self.verification_repo.get_by_id_with_relations(verification_id)
        if not verification:
            raise ValueError(f"Verification request {verification_id} not found")

        documents = verification.documents
        liveness_checks = verification.liveness_checks

        # Determine if verification can be submitted
        can_submit = (
            len(documents) > 0 and
            len(liveness_checks) > 0 and
            verification.status not in [VerificationStatus.SUBMITTED, VerificationStatus.APPROVED, VerificationStatus.REJECTED]
        )

        return {
            "id": verification.id,
            "status": verification.status,
            "created_at": verification.created_at,
            "updated_at": verification.updated_at,
            "submitted_at": verification.submitted_at,
            "documents_count": len(documents),
            "liveness_checks_count": len(liveness_checks),
            "can_submit": can_submit
        }

    def submit_for_review(self, verification_id: int) -> Dict[str, Any]:
        """
        Submit verification request for admin review.
        
        Args:
            verification_id: Verification request ID
            
        Returns:
            Dictionary with submission details
        """
        verification = self.verification_repo.get_by_id_with_relations(verification_id)
        if not verification:
            raise ValueError(f"Verification request {verification_id} not found")

        # Validate that verification can be submitted
        if verification.status in [VerificationStatus.SUBMITTED, VerificationStatus.APPROVED, VerificationStatus.REJECTED]:
            raise ValueError(f"Verification already submitted or processed")

        documents = verification.documents
        liveness_checks = verification.liveness_checks

        if len(documents) == 0:
            raise ValueError("At least one document must be uploaded")

        if len(liveness_checks) == 0:
            raise ValueError("Liveness check must be completed")

        # Update status to submitted
        verification = self.verification_repo.update_status(
            verification_id=verification_id,
            status=VerificationStatus.SUBMITTED
        )

        logger.info(f"Verification submitted for review: {verification_id}")

        return {
            "id": verification.id,
            "status": verification.status,
            "submitted_at": verification.submitted_at,
            "message": "Verification submitted for review successfully"
        }

    def get_admin_queue(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get verification requests pending admin review.
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            List of verification requests in the admin queue
        """
        verifications = self.verification_repo.get_pending_reviews(limit)

        return [
            {
                "id": v.id,
                "user_id": v.user_id,
                "status": v.status,
                "created_at": v.created_at,
                "submitted_at": v.submitted_at,
                "documents_count": len(v.documents),
                "liveness_checks_count": len(v.liveness_checks)
            }
            for v in verifications
        ]

    def admin_review(
        self,
        verification_id: int,
        admin_user_id: int,
        decision: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Admin review and decision on verification request.
        
        Args:
            verification_id: Verification request ID
            admin_user_id: ID of the admin user reviewing
            decision: Decision (approve, reject, request_more_info)
            notes: Optional notes from admin
            
        Returns:
            Dictionary with review result
        """
        verification = self.verification_repo.get_by_id(verification_id)
        if not verification:
            raise ValueError(f"Verification request {verification_id} not found")

        # Map decision to status
        status_mapping = {
            "approve": VerificationStatus.APPROVED,
            "reject": VerificationStatus.REJECTED,
            "request_more_info": VerificationStatus.NEEDS_REVIEW
        }

        if decision not in status_mapping:
            raise ValueError(f"Invalid decision: {decision}")

        new_status = status_mapping[decision]

        # Update verification status
        verification = self.verification_repo.update_status(
            verification_id=verification_id,
            status=new_status,
            reviewed_by=admin_user_id,
            notes=notes
        )

        # TODO: Update entity/person verification status if approved
        if new_status == VerificationStatus.APPROVED:
            self._update_entity_verification_status(verification)

        logger.info(
            f"Verification reviewed by admin",
            extra={
                "verification_id": verification_id,
                "admin_user_id": admin_user_id,
                "decision": decision,
                "new_status": new_status
            }
        )

        return {
            "id": verification.id,
            "status": verification.status,
            "reviewed_by": verification.reviewed_by,
            "reviewed_at": verification.reviewed_at,
            "notes": verification.notes,
            "message": f"Verification {decision}d successfully"
        }

    def get_verification_details(self, verification_id: int) -> Dict[str, Any]:
        """
        Get detailed verification information (for admin).
        
        Args:
            verification_id: Verification request ID
            
        Returns:
            Dictionary with complete verification details
        """
        verification = self.verification_repo.get_by_id_with_relations(verification_id)
        if not verification:
            raise ValueError(f"Verification request {verification_id} not found")

        return {
            "id": verification.id,
            "user_id": verification.user_id,
            "entity_id": verification.entity_id,
            "person_id": verification.person_id,
            "status": verification.status,
            "personal_info": verification.personal_info,
            "created_at": verification.created_at,
            "updated_at": verification.updated_at,
            "submitted_at": verification.submitted_at,
            "reviewed_by": verification.reviewed_by,
            "reviewed_at": verification.reviewed_at,
            "notes": verification.notes,
            "documents": [
                {
                    "id": doc.id,
                    "verification_request_id": doc.verification_request_id,
                    "document_type": doc.document_type,
                    "file_name": doc.file_name,
                    "file_size": doc.file_size,
                    "uploaded_at": doc.uploaded_at,
                    "verified": doc.verified
                }
                for doc in verification.documents
            ],
            "liveness_checks": [
                {
                    "id": lc.id,
                    "verification_request_id": lc.verification_request_id,
                    "liveness_score": float(lc.liveness_score) if lc.liveness_score else None,
                    "passed": lc.passed,
                    "checked_at": lc.checked_at
                }
                for lc in verification.liveness_checks
            ]
        }

    def _update_entity_verification_status(self, verification):
        """Update entity or person verification status after approval."""
        # Update entity if linked
        if verification.entity_id:
            from app.domain.entities.models import Entity
            entity = self.db.query(Entity).filter(Entity.id == verification.entity_id).first()
            if entity:
                entity.verification_status = "verified"
                entity.verified_at = datetime.now()
                self.db.commit()
                logger.info(f"Updated entity {entity.id} verification status")

        # Update person if linked
        if verification.person_id:
            from app.domain.entities.models import Person
            person = self.db.query(Person).filter(Person.id == verification.person_id).first()
            if person:
                person.verification_status = "verified"
                person.verified_at = datetime.now()
                self.db.commit()
                logger.info(f"Updated person {person.id} verification status")

    def _format_verification_response(self, verification) -> Dict[str, Any]:
        """Format verification request for response."""
        return {
            "id": verification.id,
            "user_id": verification.user_id,
            "entity_id": verification.entity_id,
            "person_id": verification.person_id,
            "status": verification.status,
            "personal_info": verification.personal_info,
            "created_at": verification.created_at,
            "updated_at": verification.updated_at,
            "submitted_at": verification.submitted_at,
            "reviewed_by": verification.reviewed_by,
            "reviewed_at": verification.reviewed_at,
            "notes": verification.notes
        }
