# Verification API endpoints
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import io

from app.core.db import get_db
from app.domain.verification.service import VerificationService
from app.schemas.verification import (
    VerificationRequestCreate,
    VerificationRequestOut,
    DocumentUploadResponse,
    LivenessCheckResponse,
    VerificationStatusResponse,
    VerificationSubmitResponse,
    AdminVerificationQueueItem,
    AdminReviewRequest,
    AdminReviewResponse,
    VerificationDetailOut,
    PersonalInfoCreate
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/verification", tags=["verification"])


# Helper function to get current user ID (placeholder for actual auth)
def get_current_user_id() -> int:
    """Get current user ID from authentication context."""
    # TODO: Implement actual authentication
    # For now, return a placeholder user ID
    return 1


def get_current_admin_user_id() -> int:
    """Get current admin user ID from authentication context."""
    # TODO: Implement actual admin authentication
    # For now, return a placeholder admin user ID
    return 1


@router.post("/start", response_model=VerificationRequestOut, status_code=201)
def start_verification(
    request_data: VerificationRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Start a new verification request.
    
    Creates a new verification request for the current user.
    """
    try:
        service = VerificationService(db)
        user_id = get_current_user_id()

        # Convert personal info to dict if provided
        personal_info = None
        if request_data.personal_info:
            personal_info = request_data.personal_info.dict()

        result = service.create_verification_request(
            user_id=user_id,
            entity_id=request_data.entity_id,
            person_id=request_data.person_id,
            personal_info=personal_info
        )

        logger.info(
            f"Verification started for user {user_id}",
            extra={"verification_id": result["id"], "user_id": user_id}
        )

        return result

    except Exception as e:
        logger.error(f"Error starting verification: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{verification_id}/upload-document", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    verification_id: int,
    document_type: str = Form(..., description="Type of document (drivers_license, passport, etc.)"),
    file: UploadFile = File(..., description="Document file (PDF, JPG, PNG)"),
    db: Session = Depends(get_db)
):
    """
    Upload a verification document.
    
    Accepts document uploads (driver's license, passport, utility bills, etc.).
    Supported formats: PDF, JPG, JPEG, PNG
    """
    try:
        # Validate file type
        allowed_mime_types = [
            "application/pdf",
            "image/jpeg",
            "image/jpg",
            "image/png"
        ]
        
        if file.content_type not in allowed_mime_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: PDF, JPG, PNG"
            )

        # Read file content
        file_content = await file.read()
        file_stream = io.BytesIO(file_content)

        service = VerificationService(db)
        result = service.upload_document(
            verification_id=verification_id,
            document_type=document_type,
            file_content=file_stream,
            file_name=file.filename or "document",
            mime_type=file.content_type
        )

        logger.info(
            f"Document uploaded for verification {verification_id}",
            extra={
                "verification_id": verification_id,
                "document_type": document_type,
                "file_size": len(file_content)
            }
        )

        return result

    except ValueError as e:
        logger.error(f"Validation error uploading document: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error uploading document")


@router.post("/{verification_id}/liveness-check", response_model=LivenessCheckResponse, status_code=201)
async def liveness_check(
    verification_id: int,
    image: UploadFile = File(..., description="Selfie/liveness image"),
    db: Session = Depends(get_db)
):
    """
    Submit liveness/selfie check.
    
    Performs biometric liveness verification using uploaded selfie image.
    Supported formats: JPG, JPEG, PNG
    """
    try:
        # Validate file type
        allowed_mime_types = ["image/jpeg", "image/jpg", "image/png"]
        
        if image.content_type not in allowed_mime_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Allowed types: JPG, PNG"
            )

        # Read image content
        image_content = await image.read()
        image_stream = io.BytesIO(image_content)

        service = VerificationService(db)
        result = service.verify_liveness(
            verification_id=verification_id,
            image_content=image_stream,
            image_name=image.filename or "selfie.jpg"
        )

        logger.info(
            f"Liveness check completed for verification {verification_id}",
            extra={
                "verification_id": verification_id,
                "passed": result["passed"],
                "score": result["liveness_score"]
            }
        )

        return result

    except ValueError as e:
        logger.error(f"Validation error in liveness check: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing liveness check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing liveness check")


@router.get("/{verification_id}/status", response_model=VerificationStatusResponse)
def get_verification_status(
    verification_id: int,
    db: Session = Depends(get_db)
):
    """
    Get verification request status.
    
    Returns the current status and progress of a verification request.
    """
    try:
        service = VerificationService(db)
        result = service.get_verification_status(verification_id)

        return result

    except ValueError as e:
        logger.error(f"Verification not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting verification status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error getting verification status")


@router.post("/{verification_id}/submit", response_model=VerificationSubmitResponse)
def submit_verification(
    verification_id: int,
    db: Session = Depends(get_db)
):
    """
    Submit verification for admin review.
    
    Submits a completed verification request for manual review by admin.
    Requires at least one document and liveness check to be completed.
    """
    try:
        service = VerificationService(db)
        result = service.submit_for_review(verification_id)

        logger.info(
            f"Verification submitted",
            extra={"verification_id": verification_id}
        )

        return result

    except ValueError as e:
        logger.error(f"Validation error submitting verification: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting verification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error submitting verification")


@router.get("/admin/queue", response_model=List[AdminVerificationQueueItem])
def get_admin_verification_queue(
    limit: int = Query(100, description="Maximum number of requests to return", le=500),
    db: Session = Depends(get_db)
):
    """
    Get verification requests pending admin review (Admin only).
    
    Returns a list of verification requests that need manual review.
    """
    try:
        # TODO: Check if user is admin
        # admin_user_id = get_current_admin_user_id()

        service = VerificationService(db)
        results = service.get_admin_queue(limit=limit)

        logger.info(f"Admin queue retrieved with {len(results)} items")

        return results

    except Exception as e:
        logger.error(f"Error getting admin queue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error getting admin queue")


@router.get("/admin/{verification_id}", response_model=VerificationDetailOut)
def get_verification_details(
    verification_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed verification information (Admin only).
    
    Returns complete verification details including all documents and checks.
    """
    try:
        # TODO: Check if user is admin
        # admin_user_id = get_current_admin_user_id()

        service = VerificationService(db)
        result = service.get_verification_details(verification_id)

        return result

    except ValueError as e:
        logger.error(f"Verification not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting verification details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error getting verification details")


@router.post("/admin/{verification_id}/review", response_model=AdminReviewResponse)
def admin_review_verification(
    verification_id: int,
    review_data: AdminReviewRequest,
    db: Session = Depends(get_db)
):
    """
    Review and approve/reject verification (Admin only).
    
    Allows admin to approve, reject, or request more information for a verification.
    """
    try:
        # TODO: Check if user is admin
        admin_user_id = get_current_admin_user_id()

        service = VerificationService(db)
        result = service.admin_review(
            verification_id=verification_id,
            admin_user_id=admin_user_id,
            decision=review_data.decision,
            notes=review_data.notes
        )

        logger.info(
            f"Verification reviewed",
            extra={
                "verification_id": verification_id,
                "admin_user_id": admin_user_id,
                "decision": review_data.decision
            }
        )

        return result

    except ValueError as e:
        logger.error(f"Validation error in review: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error reviewing verification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error reviewing verification")
