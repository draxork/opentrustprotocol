"""
OTP Mapper Types and Data Structures
====================================

This module defines the core data structures and types used throughout
the OTP Mapper system, ensuring type safety and validation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ..judgment import NeutrosophicJudgment


@dataclass(frozen=True)
class ProvenanceEntry:
    """
    Represents a single entry in the provenance chain.
    
    This class documents the origin and transformation history of a judgment,
    providing complete auditability for OTP operations.
    
    Args:
        source_id: Unique identifier of the source
        timestamp: ISO 8601 timestamp of the operation
        description: Optional description of the operation
        metadata: Optional metadata dictionary
    """
    source_id: str
    timestamp: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MapperType(Enum):
    """Enumeration of supported mapper types."""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"


@dataclass(frozen=True)
class NumericalParams:
    """
    Parameters for numerical mappers.
    
    Defines the three reference points for interpolation:
    - falsity_point: Input value where F=1.0
    - indeterminacy_point: Input value where I=1.0  
    - truth_point: Input value where T=1.0
    
    Args:
        falsity_point: The value representing complete falsity
        indeterminacy_point: The value representing maximum uncertainty
        truth_point: The value representing complete truth
        clamp_to_range: Whether to clamp inputs outside [min, max] range
    """
    falsity_point: float
    indeterminacy_point: float
    truth_point: float
    clamp_to_range: bool = True
    
    def __post_init__(self):
        """Validate numerical parameters."""
        if not isinstance(self.falsity_point, (int, float)):
            raise ValueError("falsity_point must be a number")
        if not isinstance(self.indeterminacy_point, (int, float)):
            raise ValueError("indeterminacy_point must be a number")
        if not isinstance(self.truth_point, (int, float)):
            raise ValueError("truth_point must be a number")
        
        # Check for degenerate cases
        if (self.falsity_point == self.indeterminacy_point == self.truth_point):
            raise ValueError("All reference points cannot be identical")
        
        # Validate that indeterminacy_point is between falsity and truth
        min_point = min(self.falsity_point, self.truth_point)
        max_point = max(self.falsity_point, self.truth_point)
        
        if not (min_point <= self.indeterminacy_point <= max_point):
            raise ValueError(
                f"indeterminacy_point {self.indeterminacy_point} must be between "
                f"falsity_point {self.falsity_point} and truth_point {self.truth_point}"
            )


@dataclass(frozen=True)
class CategoricalParams:
    """
    Parameters for categorical mappers.
    
    Maps string categories to predefined Neutrosophic Judgments.
    
    Args:
        mappings: Dictionary mapping categories to (T, I, F) tuples
        default_judgment: Optional default judgment for unknown categories
    """
    mappings: Dict[str, tuple[float, float, float]]
    default_judgment: Optional[tuple[float, float, float]] = None
    
    def __post_init__(self):
        """Validate categorical parameters."""
        if not isinstance(self.mappings, dict):
            raise ValueError("mappings must be a dictionary")
        
        if not self.mappings:
            raise ValueError("mappings cannot be empty")
        
        # Validate each mapping
        for category, judgment in self.mappings.items():
            if not isinstance(category, str):
                raise ValueError(f"Category '{category}' must be a string")
            
            if not isinstance(judgment, (tuple, list)) or len(judgment) != 3:
                raise ValueError(f"Judgment for '{category}' must be a (T, I, F) tuple")
            
            t, i, f = judgment
            if not all(isinstance(x, (int, float)) for x in [t, i, f]):
                raise ValueError(f"Judgment values for '{category}' must be numbers")
            
            if not all(0.0 <= x <= 1.0 for x in [t, i, f]):
                raise ValueError(f"Judgment values for '{category}' must be in [0.0, 1.0]")
            
            if abs(t + i + f - 1.0) > 1e-10:
                raise ValueError(f"Judgment for '{category}' must satisfy T + I + F = 1.0")
        
        # Validate default judgment if provided
        if self.default_judgment is not None:
            t, i, f = self.default_judgment
            if not all(isinstance(x, (int, float)) for x in [t, i, f]):
                raise ValueError("Default judgment values must be numbers")
            if not all(0.0 <= x <= 1.0 for x in [t, i, f]):
                raise ValueError("Default judgment values must be in [0.0, 1.0]")
            if abs(t + i + f - 1.0) > 1e-10:
                raise ValueError("Default judgment must satisfy T + I + F = 1.0")


@dataclass(frozen=True)
class BooleanParams:
    """
    Parameters for boolean mappers.
    
    Maps boolean values to predefined Neutrosophic Judgments.
    
    Args:
        true_map: Judgment for True input
        false_map: Judgment for False input
    """
    true_map: tuple[float, float, float]
    false_map: tuple[float, float, float]
    
    def __post_init__(self):
        """Validate boolean parameters."""
        for name, judgment in [("true_map", self.true_map), ("false_map", self.false_map)]:
            if not isinstance(judgment, (tuple, list)) or len(judgment) != 3:
                raise ValueError(f"{name} must be a (T, I, F) tuple")
            
            t, i, f = judgment
            if not all(isinstance(x, (int, float)) for x in [t, i, f]):
                raise ValueError(f"{name} values must be numbers")
            
            if not all(0.0 <= x <= 1.0 for x in [t, i, f]):
                raise ValueError(f"{name} values must be in [0.0, 1.0]")
            
            if abs(t + i + f - 1.0) > 1e-10:
                raise ValueError(f"{name} must satisfy T + I + F = 1.0")


class MapperError(Exception):
    """Base exception for mapper-related errors."""
    pass


class ValidationError(MapperError):
    """Raised when mapper validation fails."""
    pass


class InputError(MapperError):
    """Raised when input validation fails."""
    pass


@dataclass(frozen=True)
class Mapper:
    """
    Immutable mapper definition following OTP v2.0 specification.
    
    A mapper is a JSON-serializable object that describes a transformation
    logic for converting raw data into Neutrosophic Judgments.
    
    Args:
        version: Mapper specification version (must be "2.0")
        id: Unique identifier for the mapper
        mapper_type: Type of mapper (numerical, categorical, boolean)
        parameters: Type-specific parameters
        metadata: Optional metadata dictionary
    """
    version: str = "2.0"
    id: str = field(default="")
    mapper_type: MapperType = field(default=MapperType.NUMERICAL)
    parameters: Union[NumericalParams, CategoricalParams, BooleanParams] = field(default_factory=NumericalParams)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate mapper configuration."""
        if self.version != "2.0":
            raise ValidationError(f"Unsupported mapper version: {self.version}")
        
        if not self.id or not isinstance(self.id, str):
            raise ValidationError("Mapper id must be a non-empty string")
        
        if not isinstance(self.mapper_type, MapperType):
            raise ValidationError("Invalid mapper type")
        
        # Validate parameters match mapper type
        if self.mapper_type == MapperType.NUMERICAL:
            if not isinstance(self.parameters, NumericalParams):
                raise ValidationError("Numerical mapper requires NumericalParams")
        elif self.mapper_type == MapperType.CATEGORICAL:
            if not isinstance(self.parameters, CategoricalParams):
                raise ValidationError("Categorical mapper requires CategoricalParams")
        elif self.mapper_type == MapperType.BOOLEAN:
            if not isinstance(self.parameters, BooleanParams):
                raise ValidationError("Boolean mapper requires BooleanParams")
    
    def to_json(self) -> str:
        """Serialize mapper to JSON string."""
        data = {
            "version": self.version,
            "id": self.id,
            "type": self.mapper_type.value,
            "parameters": self._serialize_parameters(),
            "metadata": self.metadata
        }
        return json.dumps(data, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> Mapper:
        """Deserialize mapper from JSON string."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")
        
        return cls._from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Mapper:
        """Create mapper from dictionary."""
        return cls._from_dict(data)
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> Mapper:
        """Internal method to create mapper from dictionary."""
        version = data.get("version", "2.0")
        mapper_id = data.get("id", "")
        mapper_type = MapperType(data.get("type", "numerical"))
        parameters_data = data.get("parameters", {})
        metadata = data.get("metadata", {})
        
        # Create appropriate parameters object
        if mapper_type == MapperType.NUMERICAL:
            parameters = NumericalParams(
                falsity_point=parameters_data["falsity_point"],
                indeterminacy_point=parameters_data["indeterminacy_point"],
                truth_point=parameters_data["truth_point"],
                clamp_to_range=parameters_data.get("clamp_to_range", True)
            )
        elif mapper_type == MapperType.CATEGORICAL:
            mappings = {
                k: tuple(v) for k, v in parameters_data["mappings"].items()
            }
            default = None
            if "default_judgment" in parameters_data:
                default = tuple(parameters_data["default_judgment"])
            parameters = CategoricalParams(mappings=mappings, default_judgment=default)
        elif mapper_type == MapperType.BOOLEAN:
            parameters = BooleanParams(
                true_map=tuple(parameters_data["true_map"]),
                false_map=tuple(parameters_data["false_map"])
            )
        else:
            raise ValidationError(f"Unsupported mapper type: {mapper_type}")
        
        return cls(
            version=version,
            id=mapper_id,
            mapper_type=mapper_type,
            parameters=parameters,
            metadata=metadata
        )
    
    def _serialize_parameters(self) -> Dict[str, Any]:
        """Serialize parameters to dictionary."""
        if self.mapper_type == MapperType.NUMERICAL:
            params = self.parameters
            return {
                "falsity_point": params.falsity_point,
                "indeterminacy_point": params.indeterminacy_point,
                "truth_point": params.truth_point,
                "clamp_to_range": params.clamp_to_range
            }
        elif self.mapper_type == MapperType.CATEGORICAL:
            params = self.parameters
            result = {
                "mappings": {k: list(v) for k, v in params.mappings.items()}
            }
            if params.default_judgment:
                result["default_judgment"] = list(params.default_judgment)
            return result
        elif self.mapper_type == MapperType.BOOLEAN:
            params = self.parameters
            return {
                "true_map": list(params.true_map),
                "false_map": list(params.false_map)
            }
        else:
            raise ValidationError(f"Cannot serialize parameters for type: {self.mapper_type}")
    
    def create_provenance_entry(self, input_value: Any, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """Create provenance entry for mapper application."""
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        return {
            "source_id": self.id,
            "timestamp": timestamp,
            "description": f"Mapper transformation using {self.id}",
            "metadata": {
                "mapper_version": self.version,
                "mapper_type": self.mapper_type.value,
                "original_input": {
                    "value": str(input_value),
                    "type": self.mapper_type.value
                }
            }
        }
