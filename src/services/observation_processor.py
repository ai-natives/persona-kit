"""Observation processing service."""
import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories import MindscapeRepository, ObservationRepository
from .trait_extraction import TraitExtractor

logger = logging.getLogger(__name__)


class ObservationProcessor:
    """Process observations and update mindscapes."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize processor."""
        self.db = db
        self.observation_repo = ObservationRepository(db)
        self.mindscape_repo = MindscapeRepository(db)
        self.trait_extractor = TraitExtractor()

    async def process_observation(self, observation_id: str) -> dict[str, Any]:
        """
        Process a single observation.

        Returns:
            Dict with processing results including extracted traits
        """
        # Get the observation
        observation = await self.observation_repo.get(observation_id)
        if not observation:
            raise ValueError(f"Observation {observation_id} not found")

        logger.info(
            "Processing observation",
            extra={
                "observation_id": observation_id,
                "person_id": str(observation.person_id),
                "type": observation.type,
            },
        )

        # Extract traits
        extracted_traits = self.trait_extractor.extract_traits(
            observation.type, observation.content
        )

        if not extracted_traits:
            logger.warning(
                "No traits extracted from observation",
                extra={"observation_id": observation_id},
            )
            return {
                "observation_id": observation_id,
                "traits_extracted": {},
                "mindscape_updated": False,
            }

        # Update mindscape with new traits
        mindscape = await self._update_mindscape_traits(
            observation.person_id, extracted_traits
        )

        logger.info(
            "Observation processed successfully",
            extra={
                "observation_id": observation_id,
                "traits_count": len(extracted_traits),
                "mindscape_version": mindscape.version,
            },
        )

        return {
            "observation_id": observation_id,
            "traits_extracted": extracted_traits,
            "mindscape_updated": True,
            "mindscape_version": mindscape.version,
        }

    async def _update_mindscape_traits(
        self, person_id: uuid.UUID, new_traits: dict[str, dict[str, Any]]
    ) -> Any:
        """Update mindscape with new trait values."""
        # Get existing mindscape
        mindscape = await self.mindscape_repo.get_by_person(person_id)

        # Merge traits with confidence-weighted averaging
        current_traits = mindscape.traits if mindscape else {}

        for trait_name, new_value in new_traits.items():
            if trait_name in current_traits:
                # Merge with existing trait
                current_traits[trait_name] = self._merge_trait_values(
                    current_traits[trait_name], new_value
                )
            else:
                # New trait
                current_traits[trait_name] = new_value

        # Update mindscape (this increments version)
        mindscape = await self.mindscape_repo.upsert(person_id, current_traits)

        return mindscape

    def _merge_trait_values(
        self, existing: dict[str, Any], new: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Merge trait values using confidence-weighted averaging.

        For numeric values: weighted average
        For categorical/list values: take higher confidence
        """
        existing_confidence = existing.get("confidence", 0.5)
        new_confidence = new.get("confidence", 0.5)
        existing_samples = existing.get("sample_size", 1)
        new_samples = new.get("sample_size", 1)

        # Calculate new confidence based on sample sizes
        total_samples = existing_samples + new_samples
        merged_confidence = (
            (existing_confidence * existing_samples + new_confidence * new_samples)
            / total_samples
        )

        # Merge values based on type
        existing_value = existing.get("value")
        new_value = new.get("value")

        if isinstance(existing_value, int | float) and isinstance(new_value, int | float):
            # Numeric values: weighted average
            merged_value = (
                (existing_value * existing_samples + new_value * new_samples)
                / total_samples
            )
        elif isinstance(existing_value, list) and isinstance(new_value, list):
            # Lists: combine and deduplicate
            merged_value = list(set(existing_value + new_value))
        else:
            # Categorical: take value with higher confidence
            if new_confidence > existing_confidence:
                merged_value = new_value
            else:
                merged_value = existing_value

        return {
            "value": merged_value,
            "confidence": round(merged_confidence, 3),
            "sample_size": total_samples,
        }
