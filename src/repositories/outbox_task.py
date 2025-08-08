"""Repository for outbox task operations."""
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.outbox_task import OutboxTask, TaskStatus
from .base import BaseRepository


class OutboxTaskRepository(BaseRepository[OutboxTask]):
    """Repository for outbox task operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository."""
        super().__init__(OutboxTask, db)

    async def enqueue(
        self,
        task_type: str,
        payload: dict[str, Any],
        run_after: datetime | None = None,
    ) -> OutboxTask:
        """Add a new task to the outbox queue."""
        task = OutboxTask(
            task_type=task_type,
            payload=payload,
            run_after=run_after or datetime.now(UTC),
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def dequeue_next(self) -> OutboxTask | None:
        """
        Get next pending task using FOR UPDATE SKIP LOCKED.

        This ensures only one worker processes each task.
        """
        query = (
            select(OutboxTask)
            .where(
                and_(
                    OutboxTask.status == TaskStatus.PENDING.value,
                    OutboxTask.run_after <= datetime.now(UTC),
                )
            )
            .order_by(OutboxTask.created_at)
            .limit(1)
            .with_for_update(skip_locked=True)
        )

        result = await self.session.execute(query)
        task = result.scalar_one_or_none()

        if task:
            # Mark as in progress
            task.status = TaskStatus.IN_PROGRESS.value
            task.updated_at = datetime.now(UTC)
            await self.session.commit()
            await self.session.refresh(task)

        return task

    async def mark_completed(self, task_id: str | uuid.UUID) -> None:
        """Mark a task as completed."""
        # Convert string to UUID if needed
        if isinstance(task_id, str):
            task_id = uuid.UUID(task_id)

        stmt = (
            update(OutboxTask)
            .where(OutboxTask.task_id == task_id)
            .values(
                status=TaskStatus.DONE.value,
                completed_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def mark_failed(
        self, task_id: str, error: str, retry_after: datetime | None = None
    ) -> None:
        """Mark a task as failed with error details."""
        task = await self.get(task_id)
        if not task:
            return

        task.attempts += 1
        task.last_error = error[:500]  # Truncate to field limit
        task.updated_at = datetime.now(UTC)

        # If we haven't exceeded max attempts and retry_after is set, reset to pending
        if task.attempts < 3 and retry_after:
            task.status = TaskStatus.PENDING.value
            task.run_after = retry_after
        else:
            task.status = TaskStatus.FAILED.value

        await self.session.commit()

    async def cleanup_old_tasks(self, days: int = 7) -> int:
        """Delete completed or failed tasks older than specified days."""
        cutoff_date = datetime.now(UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

        stmt = (
            select(OutboxTask)
            .where(
                and_(
                    OutboxTask.status.in_([TaskStatus.DONE.value, TaskStatus.FAILED.value]),
                    OutboxTask.updated_at < cutoff_date,
                )
            )
        )

        result = await self.session.execute(stmt)
        tasks = result.scalars().all()

        for task in tasks:
            await self.session.delete(task)

        await self.session.commit()
        return len(tasks)

    async def get_pending_count(self) -> int:
        """Get count of pending tasks."""
        stmt = select(OutboxTask).where(OutboxTask.status == TaskStatus.PENDING.value)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
