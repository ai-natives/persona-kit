"""
Rule Engine for evaluating mapper configurations.

This module provides the core logic for evaluating configuration-driven
mapper rules and generating suggestions based on mindscape traits.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from ..models.mindscape import Mindscape

logger = logging.getLogger(__name__)


class RuleEngine:
    """Evaluates mapper configuration rules against mindscape data."""
    
    def evaluate_rules(
        self,
        config: Dict[str, Any],
        mindscape: Mindscape,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluate all rules in a mapper configuration.
        
        Args:
            config: Mapper configuration dictionary
            mindscape: Mindscape containing traits
            context: Optional context (time of day, etc.)
            
        Returns:
            List of generated suggestions
        """
        suggestions = []
        context = context or {}
        
        # Extract traits for easier access
        traits = mindscape.traits or {}
        
        for rule in config.get("rules", []):
            try:
                if self._evaluate_conditions(rule["conditions"], traits, context):
                    # Apply weight to determine if we should generate suggestion
                    weight = rule.get("weight", 1.0)
                    if weight > 0:  # Only generate if weight is positive
                        for action in rule.get("actions", []):
                            if action["type"] == "generate_suggestion":
                                suggestion = self._generate_suggestion(
                                    action["generate_suggestion"],
                                    config.get("templates", {}),
                                    traits,
                                    context
                                )
                                if suggestion:
                                    suggestion["rule_id"] = rule["id"]
                                    suggestion["weight"] = weight
                                    suggestions.append(suggestion)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.get('id')}: {e}")
                
        return suggestions
    
    def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        traits: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate rule conditions."""
        condition_type = conditions.get("type", "single")
        
        if condition_type == "single":
            # Direct condition checks
            if "trait_check" in conditions:
                return self._evaluate_trait_check(conditions["trait_check"], traits)
            elif "time_check" in conditions:
                return self._evaluate_time_check(conditions["time_check"], context)
            elif "context_check" in conditions:
                return self._evaluate_context_check(conditions["context_check"], context)
            return False
            
        elif condition_type == "all":
            # All conditions must be true
            return all(
                self._evaluate_conditions(cond, traits, context)
                for cond in conditions.get("conditions", [])
            )
            
        elif condition_type == "any":
            # Any condition must be true
            return any(
                self._evaluate_conditions(cond, traits, context)
                for cond in conditions.get("conditions", [])
            )
            
        return False
    
    def _evaluate_trait_check(
        self,
        check: Dict[str, Any],
        traits: Dict[str, Any]
    ) -> bool:
        """Evaluate a trait-based condition."""
        path = check["path"]
        operator = check["operator"]
        expected_value = check.get("value")
        
        # Navigate trait path (e.g., "work.energy_patterns.morning")
        current = traits
        for part in path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                # Trait doesn't exist
                return operator == "not_exists"
        
        # Evaluate operator
        if operator == "exists":
            return True  # We got here, so it exists
        elif operator == "not_exists":
            return False  # We got here, so it does exist
        elif operator == "equals":
            return current == expected_value
        elif operator == "not_equals":
            return current != expected_value
        elif operator == "greater":
            try:
                return float(current) > float(expected_value)
            except (ValueError, TypeError):
                logger.warning(f"Cannot compare non-numeric values: {current} > {expected_value}")
                return False
        elif operator == "less":
            try:
                return float(current) < float(expected_value)
            except (ValueError, TypeError):
                logger.warning(f"Cannot compare non-numeric values: {current} < {expected_value}")
                return False
        elif operator == "contains":
            try:
                return expected_value in current
            except TypeError:
                return False
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    def _evaluate_time_check(
        self,
        check: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a time-based condition."""
        # Get current time from context or system
        if "current_time" in context:
            current_time = context["current_time"]
            if isinstance(current_time, str):
                current_time = datetime.fromisoformat(current_time)
        else:
            current_time = datetime.now()
            
        # Apply timezone if specified
        if "timezone" in check and current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=ZoneInfo(check["timezone"]))
            
        # Check period
        if "period" in check:
            hour = current_time.hour
            period_ranges = {
                "morning": (5, 12),
                "afternoon": (12, 17),
                "evening": (17, 21),
                "night": (21, 5)
            }
            if check["period"] in period_ranges:
                start, end = period_ranges[check["period"]]
                if start <= end:
                    if not (start <= hour < end):
                        return False
                else:  # Night case (crosses midnight)
                    if not (hour >= start or hour < end):
                        return False
                        
        # Check hour range
        if "hour_range" in check:
            start, end = check["hour_range"]
            hour = current_time.hour
            if start <= end:
                if not (start <= hour < end):
                    return False
            else:  # Crosses midnight
                if not (hour >= start or hour < end):
                    return False
                    
        # Check day of week
        if "day_of_week" in check:
            day_name = current_time.strftime("%A").lower()
            if day_name not in [d.lower() for d in check["day_of_week"]]:
                return False
                
        return True
    
    def _evaluate_context_check(
        self,
        check: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a context-based condition."""
        field = check["field"]
        operator = check["operator"]
        expected_value = check.get("value")
        
        # Navigate context path
        current = context
        for part in field.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return operator == "not_exists"
                
        # Same operators as trait check
        if operator == "exists":
            return True
        elif operator == "not_exists":
            return False
        elif operator == "equals":
            return current == expected_value
        elif operator == "not_equals":
            return current != expected_value
        elif operator == "greater":
            try:
                return float(current) > float(expected_value)
            except (ValueError, TypeError):
                logger.warning(f"Cannot compare non-numeric values: {current} > {expected_value}")
                return False
        elif operator == "less":
            try:
                return float(current) < float(expected_value)
            except (ValueError, TypeError):
                logger.warning(f"Cannot compare non-numeric values: {current} < {expected_value}")
                return False
        elif operator == "contains":
            try:
                return expected_value in current
            except TypeError:
                return False
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    def _generate_suggestion(
        self,
        action: Dict[str, Any],
        templates: Dict[str, Any],
        traits: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate a suggestion from an action."""
        template_id = action.get("template")
        if not template_id or template_id not in templates:
            logger.warning(f"Template {template_id} not found")
            return None
            
        template = templates[template_id]
        parameters = action.get("parameters", {})
        
        # Resolve parameters
        resolved_params = {}
        for param_name, param_source in parameters.items():
            value = self._resolve_parameter(param_source, traits, context)
            if value is not None:
                resolved_params[param_name] = value
                
        # Format template strings
        title = self._format_template_string(
            template.get("title", ""),
            resolved_params
        )
        description = self._format_template_string(
            template.get("description", ""),
            resolved_params
        )
        
        return {
            "type": action.get("type"),
            "title": title,
            "description": description,
            "priority": template.get("priority", "medium"),
            "metadata": template.get("metadata", {}),
            "parameters": resolved_params
        }
    
    def _resolve_parameter(
        self,
        source: Dict[str, Any],
        traits: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """Resolve a parameter value from its source."""
        # From trait
        if "from_trait" in source:
            path = source["from_trait"]
            current = traits
            for part in path.split("."):
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return source.get("default")
            value = current
        # From context
        elif "from_context" in source:
            path = source["from_context"]
            current = context
            for part in path.split("."):
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return source.get("default")
            value = current
        # Default only
        else:
            value = source.get("default")
            
        # Apply transformation if specified
        if value is not None and "transform" in source:
            transform = source["transform"]
            try:
                if transform == "minutes_to_hours":
                    value = f"{float(value) / 60:.1f} hours"
                elif transform == "capitalize":
                    value = str(value).capitalize()
                elif transform == "lower":
                    value = str(value).lower()
                # Add more transformations as needed
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to apply transformation {transform} to {value}: {e}")
                # Return untransformed value
                
        return value
    
    def _format_template_string(
        self,
        template: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Format a template string with parameters."""
        result = template
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result


class ConfigurationValidator:
    """Validates mapper configuration against schema."""
    
    @staticmethod
    def validate(config: Dict[str, Any]) -> List[str]:
        """
        Validate a mapper configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required top-level fields
        if "metadata" not in config:
            errors.append("Missing required field: metadata")
        else:
            # Validate metadata
            metadata = config["metadata"]
            for field in ["id", "name", "description"]:
                if field not in metadata:
                    errors.append(f"Missing required metadata field: {field}")
                    
        if "rules" not in config:
            errors.append("Missing required field: rules")
        else:
            # Validate each rule
            for i, rule in enumerate(config["rules"]):
                if "id" not in rule:
                    errors.append(f"Rule {i} missing required field: id")
                if "conditions" not in rule:
                    errors.append(f"Rule {i} missing required field: conditions")
                if "actions" not in rule:
                    errors.append(f"Rule {i} missing required field: actions")
                if "weight" not in rule:
                    errors.append(f"Rule {i} missing required field: weight")
                    
        if "templates" not in config:
            errors.append("Missing required field: templates")
            
        # Validate all template references exist
        if "rules" in config and "templates" in config:
            templates = config["templates"]
            for rule in config["rules"]:
                for action in rule.get("actions", []):
                    if action.get("type") == "generate_suggestion":
                        template_id = action.get("generate_suggestion", {}).get("template")
                        if template_id and template_id not in templates:
                            errors.append(
                                f"Rule {rule.get('id')} references non-existent "
                                f"template: {template_id}"
                            )
                            
        return errors