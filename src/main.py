"""Main entry point for PersonaKit API."""
import asyncio
import logging
import signal
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import feedback_router, health_router, observation_router, persona_router
from .config import settings
from .database import async_session_maker, engine
from .logging_config import setup_logging
from .services import BackgroundWorker

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_event = asyncio.Event()
background_worker: BackgroundWorker | None = None
worker_task: asyncio.Task[None] | None = None


def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    shutdown_event.set()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle."""
    global background_worker, worker_task

    # Startup
    setup_logging()
    logger.info("Starting PersonaKit API")

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start background worker
    background_worker = BackgroundWorker(async_session_maker, shutdown_event)
    worker_task = asyncio.create_task(background_worker.start())
    logger.info("Background worker task created")

    yield

    # Shutdown
    logger.info("Shutting down PersonaKit API")

    # Stop background worker
    if background_worker:
        await background_worker.stop()

    # Wait for worker to finish
    if worker_task:
        try:
            await asyncio.wait_for(worker_task, timeout=10.0)
        except TimeoutError:
            logger.warning("Background worker didn't stop gracefully in time")
            worker_task.cancel()

    # Close database connections
    await engine.dispose()
    logger.info("Shutdown complete")


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
