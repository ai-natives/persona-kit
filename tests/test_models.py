"""Simple model tests without database."""
import uuid
from datetime import UTC, datetime

from src.models.feedback import Feedback
from src.models.mindscape import Mindscape
from src.models.observation import Observation, ObservationType
from src.models.persona import Persona


def test_observation_model():
    """Test observation model creation."""
    observation = Observation(
        id=uuid.uuid4(),
        person_id=uuid.uuid4(),
        type=ObservationType.WORK_SESSION,
        content={"test": "data"},
        meta={"source": "test"},
        created_at=datetime.now(UTC),
    )
    
    assert observation.type == ObservationType.WORK_SESSION
    assert observation.content == {"test": "data"}
    assert str(observation).startswith("<Observation(")


def test_mindscape_model():
    """Test mindscape model creation."""
    mindscape = Mindscape(
        person_id=uuid.uuid4(),
        traits={"focus_time": "morning"},
        version=1,
        updated_at=datetime.now(UTC),
    )
    
    assert mindscape.traits == {"focus_time": "morning"}
    assert mindscape.version == 1


def test_persona_model():
    """Test persona model creation."""
    persona = Persona(
        id=uuid.uuid4(),
        person_id=uuid.uuid4(),
        mapper_id="test_mapper",
        core={"type": "optimizer"},
        overlay={"focus": "productivity"},
        expires_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    
    assert persona.mapper_id == "test_mapper"
    assert persona.core == {"type": "optimizer"}
    assert str(persona).startswith("<Persona(")


def test_feedback_model():
    """Test feedback model creation."""
    feedback = Feedback(
        id=uuid.uuid4(),
        persona_id=uuid.uuid4(),
        rating=5,
        helpful=True,
        context={"action": "suggestion_applied"},
        created_at=datetime.now(UTC),
    )
    
    assert feedback.rating == 5
    assert feedback.helpful is True
    assert str(feedback).startswith("<Feedback(")