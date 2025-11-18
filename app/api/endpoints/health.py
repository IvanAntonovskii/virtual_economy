from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
import time

router = APIRouter(prefix="/health", tags=["health"])

class HealthCheck:
    def __init__(self):
        self.start_time = time.time()

    async def check_database(self, db: AsyncSession) -> dict:
        try:
            start = time.time()
            await db.execute(text("SELECT 1"))
            db_latency = (time.time() - start) * 1000
            return {"status": "healthy", "latency_ms": round(db_latency, 2)}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def check_application(self) -> dict:
        uptime = time.time() - self.start_time
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "uptime_seconds": round(uptime, 2)
        }

health_check = HealthCheck()

@router.get("/", summary="Basic health check")
async def health_basic():
    """Basic health check without external dependencies"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "virtual_economy"
    }

@router.get("/detailed", summary="Detailed health check")
async def health_detailed(db: AsyncSession = Depends(get_db)):
    """Detailed health check with all dependencies"""
    db_status = await health_check.check_database(db)
    app_status = health_check.check_application()

    overall_status = "healthy"
    if db_status["status"] != "healthy":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "application": app_status,
        "database": db_status,
        "timestamp": time.time()
    }
