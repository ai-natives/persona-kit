"""Background worker for processing outbox tasks."""
import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..repositories import OutboxTaskRepository
from .observation_processor import ObservationProcessor

logger = logging.getLogger(__name__)


class BackgroundWorker:
    """Background worker for processing outbox tasks."""

    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession], shutdown_event: asyncio.Event
    ) -> None:
        """Initialize worker."""
        self.session_factory = session_factory
        self.shutdown_event = shutdown_event
        self.is_running = False

    async def start(self) -> None:
        """Start the background worker."""
        self.is_running = True
        logger.info("Background worker started")

        try:
            while self.is_running and not self.shutdown_event.is_set():
                await self._process_next_task()

                # Wait before next poll (or exit if shutdown)
                try:
                    await asyncio.wait_for(
                        self.shutdown_event.wait(), timeout=5.0
                    )
                    # If we get here, shutdown was requested
                    break
                except TimeoutError:
                    # Normal timeout, continue processing
                    pass

        except Exception as e:
            logger.error(f"Background worker error: {e}", exc_info=True)
        finally:
            self.is_running = False
            logger.info("Background worker stopped")

    async def stop(self) -> None:
        """Stop the background worker."""
        self.is_running = False
        self.shutdown_event.set()

    async def _process_next_task(self) -> None:
        """Process the next available task from the queue."""
        async with self.session_factory() as db:
            outbox_repo = OutboxTaskRepository(db)

            # Get next task (with row lock)
            task = await outbox_repo.dequeue_next()
            if not task:
                return  # No tasks available

            logger.info(
                "Processing outbox task",
                extra={
                    "task_id": str(task.task_id),
                    "task_type": task.task_type,
                    "attempts": task.attempts,
                },
            )

            try:
                # Process based on task type
                if task.task_type == "process_observation":
                    await self._process_observation_task(db, task.payload)
                else:
                    logger.warning(f"Unknown task type: {task.task_type}")
                    raise ValueError(f"Unknown task type: {task.task_type}")

                # Mark as completed
                await outbox_repo.mark_completed(str(task.task_id))
                logger.info(
                    "Task completed successfully",
                    extra={"task_id": str(task.task_id)},
                )

            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"Task processing failed: {error_msg}",
                    extra={"task_id": str(task.task_id)},
                    exc_info=True,
                )

                # Calculate retry delay with exponential backoff
                retry_delay = min(60 * (2 ** task.attempts), 3600)  # Max 1 hour
                retry_after = datetime.now(UTC) + timedelta(seconds=retry_delay)

                await outbox_repo.mark_failed(
                    str(task.task_id), error_msg, retry_after
                )

    async def _process_observation_task(
        self, db: AsyncSession, payload: dict[str, Any]
    ) -> None:
        """Process an observation task."""
        observation_id = payload.get("observation_id")
        if not observation_id:
            raise ValueError("Missing observation_id in payload")

        processor = ObservationProcessor(db)
        result = await processor.process_observation(observation_id)

        logger.info(
            "Observation processed",
            extra={
                "observation_id": observation_id,
                "traits_count": len(result.get("traits_extracted", {})),
                "mindscape_updated": result.get("mindscape_updated"),
            },
        )
