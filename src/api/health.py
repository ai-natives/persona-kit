"""Health check endpoints."""
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db

router = APIRouter()


@router.get("/")
async def health_check() -> dict[str, Any]:
    """Basic health check."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Readiness check including database connectivity."""
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        db_status = "connected" if result.scalar() == 1 else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ready" if db_status == "connected" else "not ready",
        "database": db_status,
        "timestamp": datetime.now(UTC).isoformat(),
    }
