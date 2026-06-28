import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import engine, Base
from app.routers.auth import router as auth_router
from app.routers.reports import router as reports_router
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router
from app.utils.response_utils import CustomHTTPException, error_response

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database tables on startup (optional fallback if migrations are skipped)
try:
    logger.info("Initializing MySQL database tables if not exists...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize database tables on startup: {e}")

# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend clinical analytical core for HealthInsight AI system.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Setup CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to specific client domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")

# Global Exception Handlers
@app.exception_handler(CustomHTTPException)
def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    """
    Standard envelope handler for CustomHTTPException.
    """
    logger.warning(f"Custom HTTP Exception on {request.url.path}: {exc.detail}")
    return error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=exc.error_code
    )

@app.exception_handler(SQLAlchemyError)
def db_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Catches relational queries and driver connection issues.
    """
    logger.error(f"SQLAlchemy Database error on {request.url.path}: {exc}")
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="A database execution error occurred. Please try again later.",
        error_code="DATABASE_ERROR"
    )

@app.exception_handler(Exception)
def general_exception_handler(request: Request, exc: Exception):
    """
    Catches any other unhandled systemic issues.
    """
    logger.error(f"Unhandled system error on {request.url.path}: {exc}", exc_info=True)
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected system failure occurred.",
        error_code="INTERNAL_SERVER_ERROR"
    )

# Root Endpoint
@app.get("/")
def read_root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "documentation": "/docs"
    }
