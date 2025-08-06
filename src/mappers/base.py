"""Base mapper class for persona generation."""
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any

from ..models.mindscape import Mindscape
from ..models.persona import Persona


class PersonaMapper(ABC):
    """
    Abstract base class for persona mappers.

    Mappers transform mindscape traits into task-specific personas.
    Each mapper focuses on a specific use case (e.g., daily work optimization).
    """

    def __init__(self, mapper_id: str, ttl_hours: int = 24) -> None:
        """
        Initialize mapper.

        Args:
            mapper_id: Unique identifier for this mapper type
            ttl_hours: Default time-to-live for generated personas
        """
        self.mapper_id = mapper_id
        self.ttl_hours = ttl_hours

    @abstractmethod
    def get_required_traits(self) -> list[str]:
        """
        Get list of trait names required by this mapper.

        Returns:
            List of trait names (e.g., ["work.energy_patterns", "work.focus_duration"])
        """
        pass

    @abstractmethod
    def map_to_persona(
        self, mindscape: Mindscape, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Transform mindscape traits into persona configuration.

        Args:
            mindscape: Source mindscape with traits
            context: Optional context data (e.g., time of day, current task)

        Returns:
            Dict containing:
            - core: Core persona configuration
            - overlay: Context-specific adjustments
        """
        pass

    def create_persona(
        self,
        person_id: uuid.UUID,
        mindscape: Mindscape,
        context: dict[str, Any] | None = None,
        ttl_hours: int | None = None,
    ) -> Persona:
        """
        Create a new persona from mindscape.

        Args:
            person_id: ID of the person
            mindscape: Source mindscape
            context: Optional context data
            ttl_hours: Override default TTL

        Returns:
            New Persona instance (not persisted)
        """
        # Validate required traits
        missing_traits = self._validate_traits(mindscape)
        if missing_traits:
            raise ValueError(
                f"Missing required traits for {self.mapper_id}: {missing_traits}"
            )

        # Generate persona data
        persona_data = self.map_to_persona(mindscape, context)

        # Create persona instance
        expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours or self.ttl_hours)

        return Persona(
            person_id=person_id,
            mapper_id=self.mapper_id,
            core=persona_data.get("core", {}),
            overlay=persona_data.get("overlay", {}),
            expires_at=expires_at,
        )

    def _validate_traits(self, mindscape: Mindscape) -> list[str]:
        """
        Validate that mindscape has required traits.

        Returns:
            List of missing trait names
        """
        required = set(self.get_required_traits())
        available = set(mindscape.traits.keys()) if mindscape.traits else set()
        return list(required - available)

    def _extract_trait_value(
        self, mindscape: Mindscape, trait_name: str, default: Any = None
    ) -> Any:
        """
        Extract trait value from mindscape.

        Handles the nested structure of traits with confidence/value.

        Args:
            mindscape: Source mindscape
            trait_name: Name of trait to extract
            default: Default value if trait not found

        Returns:
            The trait value or default
        """
        if not mindscape.traits or trait_name not in mindscape.traits:
            return default

        trait_data = mindscape.traits[trait_name]

        # Handle trait structures with value/confidence
        if isinstance(trait_data, dict) and "value" in trait_data:
            return trait_data["value"]

        # Direct value
        return trait_data
