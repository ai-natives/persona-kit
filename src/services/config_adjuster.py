"""
Configuration adjuster service for updating mapper weights based on feedback.

This module handles the automatic adjustment of rule weights in mapper
configurations based on user feedback patterns.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select

from ..models.mapper_config import MapperConfig, MapperStatus
from ..models.feedback import Feedback

logger = logging.getLogger(__name__)


class ConfigurationAdjuster:
    """Adjusts mapper configuration weights based on feedback."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def process_feedback(
        self,
        feedback: Feedback,
        mapper_config_id: str,
        rule_id: str
    ) -> bool:
        """
        Process feedback and potentially adjust configuration weights.
        
        Args:
            feedback: The feedback to process
            mapper_config_id: ID of the mapper configuration
            rule_id: ID of the rule that generated the suggestion
            
        Returns:
            True if configuration was updated, False otherwise
        """
        # Get the mapper configuration
        result = await self.db.execute(
            select(MapperConfig).where(
                MapperConfig.id == mapper_config_id
            )
        )
        mapper = result.scalar_one_or_none()
        
        if not mapper:
            logger.error(f"Mapper configuration {mapper_config_id} not found")
            return False
            
        config = mapper.configuration
        feedback_settings = config.get("feedback_settings", {})
        
        # Check if we should adjust based on feedback
        if feedback.helpful:
            # Positive feedback - consider immediate reinforcement
            return await self._apply_positive_adjustment(
                mapper, rule_id, feedback_settings
            )
        else:
            # Negative feedback - check threshold
            return await self._check_negative_threshold(
                mapper, rule_id, feedback, feedback_settings
            )
    
    async def _apply_positive_adjustment(
        self,
        mapper: MapperConfig,
        rule_id: str,
        settings: Dict
    ) -> bool:
        """Apply positive weight adjustment to a rule."""
        adjustment = settings.get("positive_adjustment", 0.1)
        max_weight = settings.get("max_weight", 2.0)
        
        # Find and update the rule
        config = mapper.configuration
        updated = False
        
        # Validate that the configuration has rules
        if "rules" not in config:
            logger.error(f"Mapper configuration {mapper_config_id} has no rules")
            return False
        
        for rule in config.get("rules", []):
            if rule["id"] == rule_id:
                current_weight = rule.get("weight", 1.0)
                new_weight = min(current_weight * (1 + adjustment), max_weight)
                
                # Update rule metadata
                if "metadata" not in rule:
                    rule["metadata"] = {}
                rule["metadata"]["last_adjusted"] = datetime.utcnow().isoformat()
                rule["metadata"]["adjustment_reason"] = "positive_feedback"
                rule["metadata"]["original_weight"] = rule["metadata"].get(
                    "original_weight", current_weight
                )
                
                rule["weight"] = new_weight
                updated = True
                
                logger.info(
                    f"Increased weight for rule {rule_id} from {current_weight} "
                    f"to {new_weight} based on positive feedback"
                )
                break
        
        if updated:
            # Create new version of the configuration
            return await self._create_new_version(mapper, config)
            
        return False
    
    async def _check_negative_threshold(
        self,
        mapper: MapperConfig,
        rule_id: str,
        feedback: Feedback,
        settings: Dict
    ) -> bool:
        """Check if negative feedback threshold is met and apply adjustment."""
        threshold = settings.get("negative_threshold", 5)
        window_days = settings.get("negative_window_days", 7)
        
        # Count negative feedback for this rule in the time window
        window_start = datetime.utcnow() - timedelta(days=window_days)
        
        result = await self.db.execute(
            select(Feedback).where(
                and_(
                    Feedback.rule_id == rule_id,
                    Feedback.helpful == False,
                    Feedback.created_at >= window_start
                )
            )
        )
        negative_count = len(result.scalars().all())
        
        logger.info(
            f"Rule {rule_id} has {negative_count} negative feedback "
            f"in the last {window_days} days (threshold: {threshold})"
        )
        
        if negative_count >= threshold:
            # Apply negative adjustment
            adjustment = settings.get("negative_adjustment", -0.2)
            min_weight = settings.get("min_weight", 0.1)
            
            # Find and update the rule
            config = mapper.configuration
            updated = False
            
            for rule in config.get("rules", []):
                if rule["id"] == rule_id:
                    current_weight = rule.get("weight", 1.0)
                    new_weight = max(current_weight * (1 + adjustment), min_weight)
                    
                    # Update rule metadata
                    if "metadata" not in rule:
                        rule["metadata"] = {}
                    rule["metadata"]["last_adjusted"] = datetime.utcnow().isoformat()
                    rule["metadata"]["adjustment_reason"] = f"negative_feedback_threshold_{negative_count}"
                    rule["metadata"]["original_weight"] = rule["metadata"].get(
                        "original_weight", current_weight
                    )
                    
                    rule["weight"] = new_weight
                    updated = True
                    
                    logger.info(
                        f"Decreased weight for rule {rule_id} from {current_weight} "
                        f"to {new_weight} based on {negative_count} negative feedback"
                    )
                    break
            
            if updated:
                # Create new version of the configuration
                return await self._create_new_version(mapper, config)
                
        return False
    
    async def _create_new_version(
        self,
        mapper: MapperConfig,
        new_config: Dict
    ) -> bool:
        """Create a new version of the mapper configuration."""
        try:
            # Create new version
            new_mapper = MapperConfig(
                config_id=mapper.config_id,
                version=mapper.version + 1,
                configuration=new_config,
                status=mapper.status,
                created_by="feedback_processor"
            )
            
            # If current version is active, new version should also be active
            # and old version should be deprecated
            if mapper.status == MapperStatus.ACTIVE:
                mapper.status = MapperStatus.DEPRECATED
                
            self.db.add(new_mapper)
            await self.db.commit()
            
            logger.info(
                f"Created new version {new_mapper.version} of mapper "
                f"{mapper.config_id} with adjusted weights"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create new mapper version: {e}")
            await self.db.rollback()
            return False
    
    async def get_weight_history(
        self,
        config_id: str,
        rule_id: str
    ) -> List[Dict]:
        """
        Get the weight adjustment history for a specific rule.
        
        Args:
            config_id: Mapper configuration ID
            rule_id: Rule ID
            
        Returns:
            List of weight changes over time
        """
        history = []
        
        # Get all versions of this mapper
        result = await self.db.execute(
            select(MapperConfig).where(
                MapperConfig.config_id == config_id
            ).order_by(MapperConfig.version)
        )
        versions = result.scalars().all()
        
        for version in versions:
            config = version.configuration
            for rule in config.get("rules", []):
                if rule["id"] == rule_id:
                    history.append({
                        "version": version.version,
                        "weight": rule.get("weight", 1.0),
                        "created_at": version.created_at.isoformat(),
                        "metadata": rule.get("metadata", {})
                    })
                    break
                    
        return history