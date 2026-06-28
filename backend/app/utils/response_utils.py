from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Any, Optional, Dict

class CustomHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or f"ERROR_{status_code}"

def error_response(status_code: int, message: str, error_code: Optional[str] = None) -> JSONResponse:
    content = {
        "success": False,
        "error": {
            "code": error_code or f"ERROR_{status_code}",
            "message": message
        }
    }
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(content)
    )

def success_response(data: Any, message: str = "Request processed successfully", status_code: int = 200) -> JSONResponse:
    content = {
        "success": True,
        "message": message,
        "data": data
    }
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(content)
    )
