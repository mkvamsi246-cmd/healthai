from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.utils.response_utils import success_response, error_response

router = APIRouter(prefix="/health", tags=["System Health Check"])

@router.get("")
def check_health(db: Session = Depends(get_db)):
    """
    Standard diagnostic route checking connection pool and operational state.
    """
    try:
        # Run a lightweight raw query to verify DB connection is active
        db.execute(text("SELECT 1"))
        return success_response(
            status_code=status.HTTP_200_OK,
            data={"status": "healthy", "database": "connected"},
            message="HealthInsight AI backend is running smoothly."
        )
    except Exception as e:
        return error_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=f"Database connection degraded: {str(e)}",
            error_code="DATABASE_OFFLINE"
        )
