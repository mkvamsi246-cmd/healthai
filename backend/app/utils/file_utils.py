import os
import uuid
from fastapi import UploadFile, status
from app.config import settings
from app.utils.response_utils import CustomHTTPException

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/jpg"}

def validate_file(file: UploadFile) -> str:
    """
    Validates file extension, mime type, and file size.
    Returns the file extension.
    """
    filename = file.filename or ""
    ext = os.path.splitext(filename.lower())[1]
    
    # Check extension
    if ext not in ALLOWED_EXTENSIONS:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions: PDF, PNG, JPG, JPEG.",
            error_code="INVALID_FILE_EXTENSION"
        )
        
    # Check mime type (if available)
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type '{file.content_type}'.",
            error_code="INVALID_FILE_TYPE"
        )
        
    return ext

def save_uploaded_file(file: UploadFile, user_id: int) -> tuple[str, str]:
    """
    Saves upload file inside user-specific local storage folder.
    Returns (saved_filename, saved_filepath).
    """
    ext = validate_file(file)
    
    # Create unique filename
    unique_id = uuid.uuid4().hex
    filename = f"user_{user_id}_{unique_id}{ext}"
    
    # Resolve upload directory
    upload_path = settings.upload_path / str(user_id)
    upload_path.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_path / filename
    
    # Save file contents chunk by chunk to limit memory usage
    try:
        size = 0
        with open(file_path, "wb") as f:
            while chunk := file.file.read(8192):
                size += len(chunk)
                if size > settings.MAX_FILE_SIZE:
                    # Clean up file on limit breach
                    f.close()
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise CustomHTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024 * 1024):.1f}MB.",
                        error_code="FILE_TOO_LARGE"
                    )
                f.write(chunk)
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}",
            error_code="FILE_SAVE_ERROR"
        )
        
    return filename, str(file_path)
