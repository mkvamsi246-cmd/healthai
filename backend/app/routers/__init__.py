from app.routers.auth import router as auth_router
from app.routers.reports import router as reports_router
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router

__all__ = [
    "auth_router",
    "reports_router",
    "dashboard_router",
    "health_router"
]
