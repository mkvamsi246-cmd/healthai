from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserRegister, UserLogin, UserUpdate, Token, UserResponse,
    ForgotPasswordRequest, ResetPasswordRequest, UserProfileUpdateResponse
)
from app.services.auth_service import auth_service
from app.utils.response_utils import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new patient profile.
    """
    return auth_service.register_user(db, user_data)

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates user and returns access + refresh tokens.
    """
    return auth_service.login_user(db, credentials)

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Retrieves currently logged-in user profile.
    """
    return current_user

@router.put("/profile", response_model=UserProfileUpdateResponse)
def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates the logged-in user's age, gender, or full name.
    """
    updated_user = auth_service.update_profile(db, current_user, update_data)
    return {
        "success": True,
        "message": "Profile updated successfully.",
        "user": updated_user
    }

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Triggered when a user forgets their password. Simulates a reset token response.
    """
    msg = auth_service.forgot_password(db, payload.email)
    return {"success": True, "message": msg}

@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Resets the password for a user.
    """
    auth_service.reset_password(db, payload.email, payload.new_password)
    return {"success": True, "message": "Password has been reset successfully."}
