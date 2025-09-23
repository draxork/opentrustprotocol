"""
Mapper Registry
===============

This module provides a centralized registry for managing and reusing mappers
across the application. The registry allows for efficient storage, retrieval,
and management of mapper instances with built-in validation and serialization.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional, Union
from threading import Lock

from .types import Mapper, ValidationError
from .numerical import NumericalMapper
from .categorical import CategoricalMapper
from .boolean import BooleanMapper


class MapperRegistry:
    """
    Central registry for managing mapper instances.
    
    The registry provides thread-safe storage and retrieval of mappers,
    enabling reuse and efficient management across the application.
    
    Example:
        >>> registry = MapperRegistry()
        >>> 
        >>> # Register a DeFi health factor mapper
        >>> health_mapper = NumericalMapper(
        ...     id="defi-health-factor",
        ...     falsity_point=1.0,
        ...     indeterminacy_point=1.5,
        ...     truth_point=3.0
        ... )
        >>> registry.register(health_mapper)
        >>> 
        >>> # Use the mapper
        >>> mapper = registry.get("defi-health-factor")
        >>> judgment = mapper.apply(1.8)
    """
    
    _instance: Optional[MapperRegistry] = None
    _lock = Lock()
    
    def __new__(cls) -> MapperRegistry:
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry."""
        if not hasattr(self, '_initialized') or not self._initialized:
            self._mappers: Dict[str, Mapper] = {}
            self._lock = Lock()
            self._initialized = True
    
    def register(self, mapper: Mapper) -> None:
        """
        Register a mapper in the registry.
        
        Args:
            mapper: The mapper instance to register
            
        Raises:
            ValueError: If mapper ID already exists
            ValidationError: If mapper validation fails
        """
        if not isinstance(mapper, Mapper):
            raise ValueError("Only Mapper instances can be registered")
        
        with self._lock:
            if mapper.id in self._mappers:
                raise ValueError(f"Mapper with ID '{mapper.id}' already registered")
            
            self._mappers[mapper.id] = mapper
    
    def get(self, mapper_id: str) -> Mapper:
        """
        Retrieve a mapper by ID.
        
        Args:
            mapper_id: The ID of the mapper to retrieve
            
        Returns:
            The mapper instance
            
        Raises:
            KeyError: If mapper ID not found
        """
        with self._lock:
            if mapper_id not in self._mappers:
                raise KeyError(f"Mapper with ID '{mapper_id}' not found in registry")
            
            return self._mappers[mapper_id]
    
    def remove(self, mapper_id: str) -> Mapper:
        """
        Remove a mapper from the registry.
        
        Args:
            mapper_id: The ID of the mapper to remove
            
        Returns:
            The removed mapper instance
            
        Raises:
            KeyError: If mapper ID not found
        """
        with self._lock:
            if mapper_id not in self._mappers:
                raise KeyError(f"Mapper with ID '{mapper_id}' not found in registry")
            
            return self._mappers.pop(mapper_id)
    
    def list_mappers(self) -> List[str]:
        """
        Get list of all registered mapper IDs.
        
        Returns:
            List of mapper IDs
        """
        with self._lock:
            return list(self._mappers.keys())
    
    def has_mapper(self, mapper_id: str) -> bool:
        """
        Check if a mapper is registered.
        
        Args:
            mapper_id: The ID to check
            
        Returns:
            True if mapper is registered, False otherwise
        """
        with self._lock:
            return mapper_id in self._mappers
    
    def count(self) -> int:
        """
        Get the number of registered mappers.
        
        Returns:
            Number of registered mappers
        """
        with self._lock:
            return len(self._mappers)
    
    def clear(self) -> None:
        """Remove all mappers from the registry."""
        with self._lock:
            self._mappers.clear()
    
    def get_mappers_by_type(self, mapper_type: str) -> List[Mapper]:
        """
        Get all mappers of a specific type.
        
        Args:
            mapper_type: The type of mappers to retrieve
            
        Returns:
            List of mapper instances of the specified type
        """
        with self._lock:
            return [
                mapper for mapper in self._mappers.values()
                if mapper.mapper_type.value == mapper_type
            ]
    
    def export_to_json(self) -> str:
        """
        Export all registered mappers to JSON.
        
        Returns:
            JSON string containing all mapper definitions
        """
        with self._lock:
            mappers_data = {
                "version": "1.0",
                "registry_type": "otp_mappers",
                "mappers": {}
            }
            
            for mapper_id, mapper in self._mappers.items():
                mappers_data["mappers"][mapper_id] = json.loads(mapper.to_json())
            
            return json.dumps(mappers_data, indent=2)
    
    def import_from_json(self, json_str: str) -> int:
        """
        Import mappers from JSON string.
        
        Args:
            json_str: JSON string containing mapper definitions
            
        Returns:
            Number of mappers imported
            
        Raises:
            ValidationError: If JSON is invalid or mappers fail validation
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")
        
        if not isinstance(data, dict) or "mappers" not in data:
            raise ValidationError("JSON must contain 'mappers' object")
        
        imported_count = 0
        
        with self._lock:
            for mapper_id, mapper_data in data["mappers"].items():
                try:
                    mapper = Mapper.from_dict(mapper_data)
                    
                    # Override ID if different
                    if mapper.id != mapper_id:
                        mapper = mapper._replace(id=mapper_id)
                    
                    # Register (will raise if ID already exists)
                    if mapper_id not in self._mappers:
                        self._mappers[mapper_id] = mapper
                        imported_count += 1
                
                except Exception as e:
                    raise ValidationError(f"Failed to import mapper '{mapper_id}': {e}")
        
        return imported_count
    
    def create_numerical_mapper(
        self,
        mapper_id: str,
        falsity_point: float,
        indeterminacy_point: float,
        truth_point: float,
        clamp_to_range: bool = True,
        metadata: dict = None
    ) -> NumericalMapper:
        """
        Create and register a numerical mapper.
        
        Args:
            mapper_id: Unique identifier for the mapper
            falsity_point: Input value where F=1.0
            indeterminacy_point: Input value where I=1.0
            truth_point: Input value where T=1.0
            clamp_to_range: Whether to clamp inputs outside valid range
            metadata: Optional metadata dictionary
            
        Returns:
            The created and registered NumericalMapper instance
        """
        mapper = NumericalMapper(
            id=mapper_id,
            falsity_point=falsity_point,
            indeterminacy_point=indeterminacy_point,
            truth_point=truth_point,
            clamp_to_range=clamp_to_range,
            metadata=metadata
        )
        
        self.register(mapper)
        return mapper
    
    def create_categorical_mapper(
        self,
        mapper_id: str,
        mappings: dict[str, tuple[float, float, float]],
        default_judgment: tuple[float, float, float] = None,
        metadata: dict = None
    ) -> CategoricalMapper:
        """
        Create and register a categorical mapper.
        
        Args:
            mapper_id: Unique identifier for the mapper
            mappings: Dictionary mapping categories to (T, I, F) tuples
            default_judgment: Optional default judgment for unknown categories
            metadata: Optional metadata dictionary
            
        Returns:
            The created and registered CategoricalMapper instance
        """
        mapper = CategoricalMapper(
            id=mapper_id,
            mappings=mappings,
            default_judgment=default_judgment,
            metadata=metadata
        )
        
        self.register(mapper)
        return mapper
    
    def create_boolean_mapper(
        self,
        mapper_id: str,
        true_map: tuple[float, float, float],
        false_map: tuple[float, float, float],
        metadata: dict = None
    ) -> BooleanMapper:
        """
        Create and register a boolean mapper.
        
        Args:
            mapper_id: Unique identifier for the mapper
            true_map: Judgment for True input (T, I, F)
            false_map: Judgment for False input (T, I, F)
            metadata: Optional metadata dictionary
            
        Returns:
            The created and registered BooleanMapper instance
        """
        mapper = BooleanMapper(
            id=mapper_id,
            true_map=true_map,
            false_map=false_map,
            metadata=metadata
        )
        
        self.register(mapper)
        return mapper
    
    def __len__(self) -> int:
        """Return the number of registered mappers."""
        return self.count()
    
    def __contains__(self, mapper_id: str) -> bool:
        """Check if a mapper ID is registered."""
        return self.has_mapper(mapper_id)
    
    def __str__(self) -> str:
        """String representation of the registry."""
        return f"MapperRegistry(count={self.count()})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        mappers_list = self.list_mappers()
        return f"MapperRegistry(mappers={mappers_list})"


# Global registry instance
mapper_registry = MapperRegistry()
