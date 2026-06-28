from sqlalchemy.orm import Session
from fastapi import status
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserUpdate, Token
from app.utils.jwt_utils import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.utils.response_utils import CustomHTTPException

class AuthService:
    def register_user(self, db: Session, user_data: UserRegister) -> User:
        """
        Registers a new user, hashes password, saves to database.
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise CustomHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists.",
                error_code="EMAIL_ALREADY_REGISTERED"
            )
            
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            age=user_data.age,
            gender=user_data.gender
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            db.rollback()
            raise CustomHTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database registration failure: {str(e)}",
                error_code="DB_REGISTRATION_FAILED"
            )

    def login_user(self, db: Session, credentials: UserLogin) -> Token:
        """
        Authenticates user email and password. Returns JWT access & refresh tokens.
        """
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise CustomHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                error_code="INVALID_CREDENTIALS"
            )
            
        # Create access and refresh tokens
        token_data = {"sub": user.email}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def update_profile(self, db: Session, user: User, update_data: UserUpdate) -> User:
        """
        Updates profile info for a user.
        """
        if update_data.full_name is not None:
            user.full_name = update_data.full_name
        if update_data.age is not None:
            user.age = update_data.age
        if update_data.gender is not None:
            user.gender = update_data.gender
            
        try:
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise CustomHTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database update failure: {str(e)}",
                error_code="DB_UPDATE_FAILED"
            )

    def forgot_password(self, db: Session, email: str) -> str:
        """
        Simulates sending a password reset token.
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Prevent user enumeration by acting successfully
            return "If the email is registered, password reset instructions have been simulated."
            
        # In a real app, send an email. For this backend project, we return a success indicator.
        return f"Reset link generated successfully for {email}."

    def reset_password(self, db: Session, email: str, new_password: str) -> bool:
        """
        Performs password reset updates directly.
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise CustomHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
                error_code="USER_NOT_FOUND"
            )
            
        user.hashed_password = get_password_hash(new_password)
        try:
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise CustomHTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to reset password: {str(e)}",
                error_code="PASSWORD_RESET_FAILED"
            )

auth_service = AuthService()
