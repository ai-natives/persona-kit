"""API routers."""
from .feedback import router as feedback_router
from .health import router as health_router
from .narratives import router as narrative_router
from .observations import router as observation_router
from .personas import router as persona_router
from .mappers import router as mapper_router

__all__ = [
    "health_router",
    "observation_router",
    "persona_router",
    "feedback_router",
    "mapper_router",
    "narrative_router",
]
