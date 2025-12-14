from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import func

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: A simple status message indicating the API is healthy
    """
    return {
        "status": "healthy",
        "message": "API is running"
    }

@router.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)):
    """
    Database health check endpoint.
    
    Verifies that the database connection is working by executing a simple query.
    
    Args:
        db: Database session dependency
        
    Returns:
        dict: Status message indicating database health
        
    Raises:
        HTTPException: If database connection fails
    """
    try:
        # Execute a simple query to verify database connectivity
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "message": "Database connection is working"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

@router.get("/health/stats")
async def get_system_statistics(db: Session = Depends(get_db)):
    """
    Get system statistics including database metrics.
    
    Returns information about the number of records in key tables.
    
    Args:
        db: Database session dependency
        
    Returns:
        dict: System statistics including table counts
        
    Raises:
        HTTPException: If unable to retrieve statistics
    """
    try:
        # Import models here to avoid circular imports
        from app.models.record import Record
        from app.models.user import User
        
        # Get counts from database
        record_count = db.query(func.count(Record.id)).scalar()
        user_count = db.query(func.count(User.id)).scalar()
        
        return {
            "status": "healthy",
            "statistics": {
                "total_records": record_count,
                "total_users": user_count
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system statistics: {str(e)}"
        )
