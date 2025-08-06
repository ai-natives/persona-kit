"""Main entry point for PersonaKit API."""
import asyncio
import signal
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import feedback_router, health_router, observation_router, persona_router
from .config import settings
from .database import engine
from .logging_config import setup_logging

# Global flag for graceful shutdown
shutdown_event = asyncio.Event()


def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals."""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    shutdown_event.set()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle."""
    # Startup
    setup_logging()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    yield

    # Shutdown
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(observation_router, prefix="/observations", tags=["observations"])
app.include_router(persona_router, prefix="/personas", tags=["personas"])
app.include_router(feedback_router, prefix="/feedback", tags=["feedback"])


def main() -> None:
    """Run the application."""
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload and settings.is_development,
        log_config=None,  # We handle logging ourselves
        timeout_graceful_shutdown=30,
    )


if __name__ == "__main__":
    main()
