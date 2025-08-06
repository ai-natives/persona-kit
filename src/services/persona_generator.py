"""
Persona generation service using configuration-driven mappers.

This module handles persona generation by evaluating mapper configurations
against mindscape data using the rule engine.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ..models.mapper_config import MapperConfig, MapperStatus
from ..models.mindscape import Mindscape
from ..models.persona import Persona
from .rule_engine import RuleEngine

logger = logging.getLogger(__name__)


class PersonaGenerator:
    """Generates personas using configuration-driven mappers."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rule_engine = RuleEngine()
    
    async def generate_persona(
        self,
        person_id: uuid.UUID,
        mapper_id: str,
        mindscape: Mindscape,
        context: Optional[Dict[str, Any]] = None,
        ttl_hours: Optional[int] = None
    ) -> Persona:
        """
        Generate a persona using a mapper configuration.
        
        Args:
            person_id: ID of the person
            mapper_id: ID of the mapper configuration to use
            mindscape: The mindscape containing traits
            context: Optional context for rule evaluation
            ttl_hours: Optional TTL override (default from mapper or 24h)
            
        Returns:
            Generated persona
            
        Raises:
            ValueError: If mapper not found or missing required traits
        """
        # Get active mapper configuration
        result = await self.db.execute(
            select(MapperConfig).where(
                MapperConfig.config_id == mapper_id,
                MapperConfig.status == MapperStatus.ACTIVE
            ).order_by(MapperConfig.version.desc())
        )
        mapper_config = result.scalar_one_or_none()
        
        if not mapper_config:
            raise ValueError(f"No active mapper configuration found for '{mapper_id}'")
            
        config = mapper_config.configuration
        
        # Check required traits
        self._validate_required_traits(mindscape, config.get("required_traits", []))
        
        # Evaluate rules to generate suggestions
        suggestions = self.rule_engine.evaluate_rules(config, mindscape, context)
        
        # Build persona core (low-volatility traits)
        persona_core = self._build_persona_core(mindscape, config)
        
        # Build contextual overlay (high-volatility state + suggestions)
        contextual_overlay = self._build_contextual_overlay(
            mindscape, suggestions, context
        )
        
        # Determine TTL
        if ttl_hours is None:
            # Get from mapper config or default to 24 hours
            ttl_hours = config.get("metadata", {}).get("default_ttl_hours", 24)
        
        # Create persona
        persona = Persona(
            person_id=person_id,
            mapper_id=mapper_id,
            mapper_config_id=mapper_config.id,
            mapper_version=mapper_config.version,
            core=persona_core,
            overlay=contextual_overlay,
            expires_at=datetime.utcnow() + timedelta(hours=ttl_hours),
            metadata={
                "generated_at": datetime.utcnow().isoformat(),
                "rule_count": len(config.get("rules", [])),
                "suggestion_count": len(suggestions),
                "context": context or {}
            }
        )
        
        # Track mapper usage (Note: This should ideally be done after successful persona save)
        # For now, we'll just increment the counter but not commit here
        # The calling code should handle the commit
        mapper_config.usage_count += 1
        mapper_config.last_used_at = datetime.utcnow()
        self.db.add(mapper_config)
        
        return persona
    
    def _validate_required_traits(
        self,
        mindscape: Mindscape,
        required_traits: list[str]
    ) -> None:
        """Validate that mindscape has all required traits."""
        traits = mindscape.traits or {}
        missing = []
        
        for trait_path in required_traits:
            # Navigate trait path
            current = traits
            parts = trait_path.split(".")
            found = True
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    found = False
                    break
                    
            if not found:
                missing.append(trait_path)
                
        if missing:
            raise ValueError(
                f"Mindscape missing required traits: {', '.join(missing)}"
            )
    
    def _build_persona_core(
        self,
        mindscape: Mindscape,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build the persona core from low-volatility traits."""
        traits = mindscape.traits or {}
        
        # Extract work-related patterns (example structure)
        work_style = {}
        if "work" in traits:
            work_traits = traits["work"]
            work_style = {
                "energy_patterns": work_traits.get("energy_patterns", {}),
                "focus_duration": work_traits.get("focus_duration", {}),
                "peak_hours": work_traits.get("peak_hours", []),
                "task_switching_cost": work_traits.get("task_switching_cost", "medium"),
                "meeting_recovery": work_traits.get("meeting_recovery", {})
            }
        
        # Extract productivity patterns
        productivity_style = {}
        if "productivity" in traits:
            prod_traits = traits["productivity"]
            productivity_style = {
                "flow_state_triggers": prod_traits.get("flow_state", {}).get("triggers", []),
                "best_task_types": prod_traits.get("flow_state", {}).get("best_task_types", []),
                "productive_environments": prod_traits.get("environments", [])
            }
        
        return {
            "work_style": work_style,
            "productivity_style": productivity_style,
            "core_preferences": {
                "communication": traits.get("communication", {}),
                "learning_style": traits.get("learning", {})
            },
            "generated_from_mindscape_version": mindscape.version
        }
    
    def _build_contextual_overlay(
        self,
        mindscape: Mindscape,
        suggestions: list[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build the contextual overlay with current state and suggestions."""
        traits = mindscape.traits or {}
        context = context or {}
        
        # Extract current state
        current_state = traits.get("current_state", {})
        
        # Sort suggestions by weight and priority
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: (
                -s.get("weight", 1.0),  # Higher weight first
                {"high": 3, "medium": 2, "low": 1}.get(s.get("priority", "medium"), 2)
            )
        )
        
        return {
            "current_state": {
                "energy_level": current_state.get("energy_level", "unknown"),
                "focus_available": current_state.get("focus_available", True),
                "recent_activity": current_state.get("recent_activity", []),
                "context": context
            },
            "suggestions": sorted_suggestions[:5],  # Top 5 suggestions
            "active_patterns": {
                "time_of_day": context.get("time_of_day", "unknown"),
                "day_of_week": context.get("day_of_week", "unknown"),
                "workload": current_state.get("workload", "normal")
            }
        }