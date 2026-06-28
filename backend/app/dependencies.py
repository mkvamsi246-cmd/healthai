from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.utils.jwt_utils import decode_token
from app.utils.response_utils import CustomHTTPException
from app.models.user import User

# Token URL corresponds to the token generation path
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = CustomHTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        error_code="UNAUTHORIZED",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None or payload.get("refresh") is True:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user
