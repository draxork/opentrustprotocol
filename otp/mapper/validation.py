"""
Mapper Validation
==================

This module provides comprehensive validation for mappers, ensuring
they conform to the OTP v2.0 specification and maintain data integrity.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .types import Mapper, MapperError, ValidationError


class MapperValidator:
    """
    Comprehensive validator for OTP mappers.
    
    This validator ensures that mappers conform to the OTP v2.0 specification
    and maintain mathematical correctness and data integrity.
    """
    
    # JSON Schema for OTP Mapper v2.0
    MAPPER_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "OTP Mapper v2.0",
        "type": "object",
        "properties": {
            "version": {"type": "string", "const": "2.0"},
            "id": {"type": "string", "pattern": "^[a-zA-Z0-9_-]+$"},
            "type": {"type": "string", "enum": ["numerical", "categorical", "boolean"]},
            "parameters": {"type": "object"},
            "metadata": {"type": "object"}
        },
        "required": ["version", "id", "type", "parameters"]
    }
    
    # Numerical mapper parameters schema
    NUMERICAL_PARAMS_SCHEMA = {
        "type": "object",
        "properties": {
            "falsity_point": {"type": "number"},
            "indeterminacy_point": {"type": "number"},
            "truth_point": {"type": "number"},
            "clamp_to_range": {"type": "boolean"}
        },
        "required": ["falsity_point", "indeterminacy_point", "truth_point"],
        "additionalProperties": False
    }
    
    # Categorical mapper parameters schema
    CATEGORICAL_PARAMS_SCHEMA = {
        "type": "object",
        "properties": {
            "mappings": {
                "type": "object",
                "patternProperties": {
                    "^.*$": {
                        "type": "array",
                        "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "minItems": 3,
                        "maxItems": 3
                    }
                }
            },
            "default_judgment": {
                "type": "array",
                "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "minItems": 3,
                "maxItems": 3
            }
        },
        "required": ["mappings"],
        "additionalProperties": False
    }
    
    # Boolean mapper parameters schema
    BOOLEAN_PARAMS_SCHEMA = {
        "type": "object",
        "properties": {
            "true_map": {
                "type": "array",
                "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "minItems": 3,
                "maxItems": 3
            },
            "false_map": {
                "type": "array",
                "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "minItems": 3,
                "maxItems": 3
            }
        },
        "required": ["true_map", "false_map"],
        "additionalProperties": False
    }
    
    @classmethod
    def validate_mapper(cls, mapper: Mapper) -> List[str]:
        """
        Validate a mapper instance.
        
        Args:
            mapper: The mapper instance to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Basic structure validation
        errors.extend(cls._validate_basic_structure(mapper))
        
        # Type-specific validation
        if mapper.mapper_type.value == "numerical":
            errors.extend(cls._validate_numerical_mapper(mapper))
        elif mapper.mapper_type.value == "categorical":
            errors.extend(cls._validate_categorical_mapper(mapper))
        elif mapper.mapper_type.value == "boolean":
            errors.extend(cls._validate_boolean_mapper(mapper))
        
        # Mathematical validation
        errors.extend(cls._validate_mathematical_properties(mapper))
        
        return errors
    
    @classmethod
    def validate_json(cls, json_str: str) -> List[str]:
        """
        Validate mapper JSON string.
        
        Args:
            json_str: JSON string to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return [f"Invalid JSON: {e}"]
        
        # Basic schema validation
        errors.extend(cls._validate_json_schema(data))
        
        # Type-specific validation
        mapper_type = data.get("type")
        parameters = data.get("parameters", {})
        
        if mapper_type == "numerical":
            errors.extend(cls._validate_numerical_parameters(parameters))
        elif mapper_type == "categorical":
            errors.extend(cls._validate_categorical_parameters(parameters))
        elif mapper_type == "boolean":
            errors.extend(cls._validate_boolean_parameters(parameters))
        
        return errors
    
    @classmethod
    def is_valid(cls, mapper: Mapper) -> bool:
        """
        Check if a mapper is valid.
        
        Args:
            mapper: The mapper instance to check
            
        Returns:
            True if mapper is valid, False otherwise
        """
        return len(cls.validate_mapper(mapper)) == 0
    
    @classmethod
    def is_json_valid(cls, json_str: str) -> bool:
        """
        Check if mapper JSON is valid.
        
        Args:
            json_str: JSON string to check
            
        Returns:
            True if JSON is valid, False otherwise
        """
        return len(cls.validate_json(json_str)) == 0
    
    @classmethod
    def _validate_basic_structure(cls, mapper: Mapper) -> List[str]:
        """Validate basic mapper structure."""
        errors = []
        
        # Version validation
        if mapper.version != "2.0":
            errors.append(f"Unsupported mapper version: {mapper.version}")
        
        # ID validation
        if not mapper.id or not isinstance(mapper.id, str):
            errors.append("Mapper ID must be a non-empty string")
        elif not cls._is_valid_id(mapper.id):
            errors.append(f"Mapper ID '{mapper.id}' contains invalid characters")
        
        # Type validation
        if not hasattr(mapper, 'mapper_type'):
            errors.append("Mapper type is required")
        
        # Parameters validation
        if not hasattr(mapper, 'parameters'):
            errors.append("Mapper parameters are required")
        
        return errors
    
    @classmethod
    def _validate_numerical_mapper(cls, mapper: Mapper) -> List[str]:
        """Validate numerical mapper specific properties."""
        errors = []
        
        try:
            params = mapper.parameters
            
            # Check parameter types
            if not hasattr(params, 'falsity_point'):
                errors.append("Numerical mapper missing falsity_point")
            elif not isinstance(params.falsity_point, (int, float)):
                errors.append("falsity_point must be a number")
            
            if not hasattr(params, 'indeterminacy_point'):
                errors.append("Numerical mapper missing indeterminacy_point")
            elif not isinstance(params.indeterminacy_point, (int, float)):
                errors.append("indeterminacy_point must be a number")
            
            if not hasattr(params, 'truth_point'):
                errors.append("Numerical mapper missing truth_point")
            elif not isinstance(params.truth_point, (int, float)):
                errors.append("truth_point must be a number")
            
            # Check for degenerate cases
            if hasattr(params, 'falsity_point') and hasattr(params, 'indeterminacy_point') and hasattr(params, 'truth_point'):
                if params.falsity_point == params.indeterminacy_point == params.truth_point:
                    errors.append("All reference points cannot be identical")
                
                # Check that indeterminacy_point is between falsity and truth
                min_point = min(params.falsity_point, params.truth_point)
                max_point = max(params.falsity_point, params.truth_point)
                
                if not (min_point <= params.indeterminacy_point <= max_point):
                    errors.append(
                        f"indeterminacy_point {params.indeterminacy_point} must be between "
                        f"falsity_point {params.falsity_point} and truth_point {params.truth_point}"
                    )
        
        except Exception as e:
            errors.append(f"Error validating numerical mapper: {e}")
        
        return errors
    
    @classmethod
    def _validate_categorical_mapper(cls, mapper: Mapper) -> List[str]:
        """Validate categorical mapper specific properties."""
        errors = []
        
        try:
            params = mapper.parameters
            
            # Check mappings
            if not hasattr(params, 'mappings'):
                errors.append("Categorical mapper missing mappings")
            elif not isinstance(params.mappings, dict):
                errors.append("mappings must be a dictionary")
            elif not params.mappings:
                errors.append("mappings cannot be empty")
            else:
                # Validate each mapping
                for category, judgment in params.mappings.items():
                    if not isinstance(category, str):
                        errors.append(f"Category '{category}' must be a string")
                    
                    if not isinstance(judgment, (tuple, list)) or len(judgment) != 3:
                        errors.append(f"Judgment for '{category}' must be a (T, I, F) tuple")
                    else:
                        t, i, f = judgment
                        if not all(isinstance(x, (int, float)) for x in [t, i, f]):
                            errors.append(f"Judgment values for '{category}' must be numbers")
                        elif not all(0.0 <= x <= 1.0 for x in [t, i, f]):
                            errors.append(f"Judgment values for '{category}' must be in [0.0, 1.0]")
                        elif abs(t + i + f - 1.0) > 1e-10:
                            errors.append(f"Judgment for '{category}' must satisfy T + I + F = 1.0")
            
            # Validate default judgment if present
            if hasattr(params, 'default_judgment') and params.default_judgment is not None:
                default = params.default_judgment
                if not isinstance(default, (tuple, list)) or len(default) != 3:
                    errors.append("default_judgment must be a (T, I, F) tuple")
                else:
                    t, i, f = default
                    if not all(isinstance(x, (int, float)) for x in [t, i, f]):
                        errors.append("default_judgment values must be numbers")
                    elif not all(0.0 <= x <= 1.0 for x in [t, i, f]):
                        errors.append("default_judgment values must be in [0.0, 1.0]")
                    elif abs(t + i + f - 1.0) > 1e-10:
                        errors.append("default_judgment must satisfy T + I + F = 1.0")
        
        except Exception as e:
            errors.append(f"Error validating categorical mapper: {e}")
        
        return errors
    
    @classmethod
    def _validate_boolean_mapper(cls, mapper: Mapper) -> List[str]:
        """Validate boolean mapper specific properties."""
        errors = []
        
        try:
            params = mapper.parameters
            
            # Validate true_map
            if not hasattr(params, 'true_map'):
                errors.append("Boolean mapper missing true_map")
            else:
                errors.extend(cls._validate_judgment_tuple(params.true_map, "true_map"))
            
            # Validate false_map
            if not hasattr(params, 'false_map'):
                errors.append("Boolean mapper missing false_map")
            else:
                errors.extend(cls._validate_judgment_tuple(params.false_map, "false_map"))
        
        except Exception as e:
            errors.append(f"Error validating boolean mapper: {e}")
        
        return errors
    
    @classmethod
    def _validate_judgment_tuple(cls, judgment: tuple, name: str) -> List[str]:
        """Validate a judgment tuple (T, I, F)."""
        errors = []
        
        if not isinstance(judgment, (tuple, list)) or len(judgment) != 3:
            errors.append(f"{name} must be a (T, I, F) tuple")
            return errors
        
        t, i, f = judgment
        
        if not all(isinstance(x, (int, float)) for x in [t, i, f]):
            errors.append(f"{name} values must be numbers")
        elif not all(0.0 <= x <= 1.0 for x in [t, i, f]):
            errors.append(f"{name} values must be in [0.0, 1.0]")
        elif abs(t + i + f - 1.0) > 1e-10:
            errors.append(f"{name} must satisfy T + I + F = 1.0")
        
        return errors
    
    @classmethod
    def _validate_mathematical_properties(cls, mapper: Mapper) -> List[str]:
        """Validate mathematical properties of the mapper."""
        errors = []
        
        # This could include more sophisticated mathematical validation
        # For now, we rely on the type-specific validations
        
        return errors
    
    @classmethod
    def _validate_json_schema(cls, data: Dict[str, Any]) -> List[str]:
        """Validate JSON against basic schema."""
        errors = []
        
        # Check required fields
        required_fields = ["version", "id", "type", "parameters"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check version
        if "version" in data and data["version"] != "2.0":
            errors.append(f"Unsupported version: {data['version']}")
        
        # Check ID format
        if "id" in data and not cls._is_valid_id(data["id"]):
            errors.append(f"Invalid ID format: {data['id']}")
        
        # Check type
        valid_types = ["numerical", "categorical", "boolean"]
        if "type" in data and data["type"] not in valid_types:
            errors.append(f"Invalid type: {data['type']}. Must be one of {valid_types}")
        
        return errors
    
    @classmethod
    def _validate_numerical_parameters(cls, params: Dict[str, Any]) -> List[str]:
        """Validate numerical mapper parameters."""
        errors = []
        
        required_fields = ["falsity_point", "indeterminacy_point", "truth_point"]
        for field in required_fields:
            if field not in params:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(params[field], (int, float)):
                errors.append(f"{field} must be a number")
        
        # Check for degenerate cases
        if all(field in params for field in required_fields):
            if params["falsity_point"] == params["indeterminacy_point"] == params["truth_point"]:
                errors.append("All reference points cannot be identical")
        
        return errors
    
    @classmethod
    def _validate_categorical_parameters(cls, params: Dict[str, Any]) -> List[str]:
        """Validate categorical mapper parameters."""
        errors = []
        
        if "mappings" not in params:
            errors.append("Missing required field: mappings")
        elif not isinstance(params["mappings"], dict):
            errors.append("mappings must be a dictionary")
        elif not params["mappings"]:
            errors.append("mappings cannot be empty")
        
        return errors
    
    @classmethod
    def _validate_boolean_parameters(cls, params: Dict[str, Any]) -> List[str]:
        """Validate boolean mapper parameters."""
        errors = []
        
        required_fields = ["true_map", "false_map"]
        for field in required_fields:
            if field not in params:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(params[field], list) or len(params[field]) != 3:
                errors.append(f"{field} must be a list of 3 numbers")
        
        return errors
    
    @classmethod
    def _is_valid_id(cls, mapper_id: str) -> bool:
        """Check if mapper ID is valid."""
        import re
        pattern = r"^[a-zA-Z0-9_-]+$"
        return bool(re.match(pattern, mapper_id))


