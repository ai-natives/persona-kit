"""Integration tests for observation processing pipeline."""
import asyncio
import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.observation import ObservationType
from src.models.outbox_task import TaskStatus
from src.repositories import (
    MindscapeRepository,
    ObservationRepository,
    OutboxTaskRepository,
)
from src.services import ObservationProcessor
from src.services.background_worker import BackgroundWorker
from src.utils import MockDataGenerator


@pytest.mark.asyncio
async def test_observation_to_mindscape_flow(test_db: AsyncSession):
    """Test full flow from observation creation to mindscape update."""
    # Setup
    person_id = uuid.uuid4()
    observation_repo = ObservationRepository(test_db)
    mindscape_repo = MindscapeRepository(test_db)
    outbox_repo = OutboxTaskRepository(test_db)
    processor = ObservationProcessor(test_db)
    
    # Create observation
    observation = await observation_repo.create(
        person_id=person_id,
        type=ObservationType.WORK_SESSION,
        content={
            "start": "2024-01-15T09:00:00Z",
            "end": "2024-01-15T11:00:00Z",
            "duration_minutes": 120,
            "productivity_score": 5,
            "interruptions": 0,
        },
        meta={"source": "test"},
    )
    
    # Process it directly (simulating worker)
    result = await processor.process_observation(str(observation.id))
    
    # Verify traits were extracted
    assert result["mindscape_updated"] is True
    assert len(result["traits_extracted"]) > 0
    assert "work.focus_duration" in result["traits_extracted"]
    assert result["traits_extracted"]["work.focus_duration"]["value"] == 120
    
    # Verify mindscape was updated
    mindscape = await mindscape_repo.get_by_person(person_id)
    assert mindscape is not None
    assert mindscape.version == 1
    assert "work.focus_duration" in mindscape.traits


@pytest.mark.asyncio
async def test_trait_merging(test_db: AsyncSession):
    """Test that multiple observations merge traits correctly."""
    person_id = uuid.uuid4()
    observation_repo = ObservationRepository(test_db)
    processor = ObservationProcessor(test_db)
    mindscape_repo = MindscapeRepository(test_db)
    
    # Create first observation - 90 min focus
    obs1 = await observation_repo.create(
        person_id=person_id,
        type=ObservationType.WORK_SESSION,
        content={
            "duration_minutes": 90,
            "productivity_score": 4,
        },
        meta={},
    )
    await processor.process_observation(str(obs1.id))
    
    # Create second observation - 60 min focus
    obs2 = await observation_repo.create(
        person_id=person_id,
        type=ObservationType.WORK_SESSION,
        content={
            "duration_minutes": 60,
            "productivity_score": 5,
        },
        meta={},
    )
    await processor.process_observation(str(obs2.id))
    
    # Check merged result
    mindscape = await mindscape_repo.get_by_person(person_id)
    focus_trait = mindscape.traits["work.focus_duration"]
    
    # Should be weighted average: (90*1 + 60*1) / 2 = 75
    assert focus_trait["value"] == 75
    assert focus_trait["sample_size"] == 2
    assert mindscape.version == 2  # Two updates


@pytest.mark.asyncio
async def test_outbox_queue_processing(test_db: AsyncSession):
    """Test that outbox queue processes tasks correctly."""
    person_id = uuid.uuid4()
    observation_repo = ObservationRepository(test_db)
    outbox_repo = OutboxTaskRepository(test_db)
    
    # Create observation
    observation = await observation_repo.create(
        person_id=person_id,
        type=ObservationType.USER_INPUT,
        content={
            "type": "energy_check",
            "energy_level": "high",
        },
        meta={},
    )
    
    # Queue for processing
    task = await outbox_repo.enqueue(
        task_type="process_observation",
        payload={"observation_id": str(observation.id)},
    )
    
    # Verify task is pending
    assert task.status == TaskStatus.PENDING
    assert task.attempts == 0
    
    # Dequeue it
    dequeued = await outbox_repo.dequeue_next()
    assert dequeued is not None
    assert str(dequeued.task_id) == str(task.task_id)
    assert dequeued.status == TaskStatus.IN_PROGRESS
    
    # Verify no other worker can get it (skip locked)
    nothing = await outbox_repo.dequeue_next()
    assert nothing is None
    
    # Mark completed using the dequeued task ID
    await outbox_repo.mark_completed(str(dequeued.task_id))
    
    # Verify status
    completed_task = await outbox_repo.get(str(dequeued.task_id))
    assert completed_task.status == TaskStatus.DONE
    assert completed_task.completed_at is not None


@pytest.mark.asyncio
async def test_failed_task_retry(test_db: AsyncSession):
    """Test that failed tasks are retried correctly."""
    outbox_repo = OutboxTaskRepository(test_db)
    
    # Create a task
    task = await outbox_repo.enqueue(
        task_type="process_observation",
        payload={"observation_id": "invalid-id"},
    )
    
    # Mark it failed (with retry)
    retry_time = datetime.now(UTC)
    await outbox_repo.mark_failed(
        str(task.task_id),
        "Observation not found",
        retry_after=retry_time,
    )
    
    # Check it's back to pending with attempt count
    failed_task = await outbox_repo.get(str(task.task_id))
    assert failed_task.status == TaskStatus.PENDING
    assert failed_task.attempts == 1
    assert failed_task.last_error == "Observation not found"
    assert failed_task.run_after >= retry_time


@pytest.mark.asyncio
async def test_wizard_response_processing(test_db: AsyncSession):
    """Test processing wizard responses creates appropriate traits."""
    person_id = uuid.uuid4()
    observation_repo = ObservationRepository(test_db)
    processor = ObservationProcessor(test_db)
    mindscape_repo = MindscapeRepository(test_db)
    
    # Create wizard response observation
    observation = await observation_repo.create(
        person_id=person_id,
        type=ObservationType.USER_INPUT,
        content={
            "type": "wizard_response",
            "responses": {
                "most_productive": "morning",
                "focus_duration": "2hr+",
                "flow_disruptor": "meetings",
            },
        },
        meta={"wizard_version": "1.0"},
    )
    
    # Process it
    await processor.process_observation(str(observation.id))
    
    # Verify traits
    mindscape = await mindscape_repo.get_by_person(person_id)
    traits = mindscape.traits
    
    assert "work.energy_patterns" in traits
    assert traits["work.energy_patterns"]["value"] == ["06:00-12:00"]
    
    assert "work.focus_duration" in traits
    assert traits["work.focus_duration"]["value"] == 120  # 2hr+
    
    assert "work.task_switching_cost" in traits
    assert traits["work.task_switching_cost"]["value"] == "high"  # meetings = high cost


@pytest.mark.asyncio
async def test_concurrent_worker_safety(test_db: AsyncSession):
    """Test that FOR UPDATE SKIP LOCKED prevents double processing."""
    outbox_repo = OutboxTaskRepository(test_db)
    
    # Create multiple tasks
    task_ids = []
    for i in range(5):
        task = await outbox_repo.enqueue(
            task_type="process_observation",
            payload={"observation_id": f"obs-{i}"},
        )
        task_ids.append(str(task.task_id))
    
    # Simulate two workers trying to get tasks
    tasks_worker1 = []
    tasks_worker2 = []
    
    # Worker 1 gets first task
    if task := await outbox_repo.dequeue_next():
        tasks_worker1.append(str(task.task_id))
    
    # Worker 2 gets next task (not the same one)
    if task := await outbox_repo.dequeue_next():
        tasks_worker2.append(str(task.task_id))
    
    # Verify no overlap
    assert len(set(tasks_worker1) & set(tasks_worker2)) == 0
    assert len(tasks_worker1) == 1
    assert len(tasks_worker2) == 1


@pytest.mark.asyncio 
async def test_mock_data_generation(test_db: AsyncSession):
    """Test processing mock data pattern."""
    person_id = uuid.uuid4()
    generator = MockDataGenerator(person_id)
    observation_repo = ObservationRepository(test_db)
    processor = ObservationProcessor(test_db)
    mindscape_repo = MindscapeRepository(test_db)
    
    # Generate a week of data
    mock_observations = generator.generate_work_pattern(days=7)
    
    # Create observations from mock data
    for mock_obs in mock_observations[:10]:  # Process first 10
        obs = await observation_repo.create(
            person_id=person_id,
            type=ObservationType[mock_obs["type"].upper()],
            content=mock_obs["content"],
            meta=mock_obs["meta"],
        )
        await processor.process_observation(str(obs.id))
    
    # Check final mindscape
    mindscape = await mindscape_repo.get_by_person(person_id)
    traits = mindscape.traits
    
    # Should have various traits from the pattern
    assert len(traits) > 0
    assert any("work." in key for key in traits.keys())
    
    # Version should match number of updates
    assert mindscape.version >= 5  # At least some updates