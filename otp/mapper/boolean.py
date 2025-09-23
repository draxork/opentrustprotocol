"""
Boolean Mapper Implementation
==============================

This module implements the boolean mapper for transforming boolean values
into Neutrosophic Judgments using predefined mappings for True and False.

The boolean mapper provides the simplest form of transformation, mapping
binary boolean values to specific trust judgments. This is useful for
cases where the relationship between boolean states and trust levels
is well-defined.
"""

from __future__ import annotations

from typing import Union

from ..judgment import NeutrosophicJudgment
from .types import Mapper, BooleanParams, MapperType, MapperError, InputError, ValidationError


class BooleanMapper(Mapper):
    """
    Boolean mapper for transforming boolean values.
    
    This mapper provides direct mapping from boolean inputs to predefined
    Neutrosophic Judgments. It's the simplest mapper type, ideal for
    binary trust decisions.
    
    Example:
        >>> mapper = BooleanMapper(
        ...     id="ssl-certificate",
        ...     true_map=(1.0, 0.0, 0.0),   # Valid cert = complete trust
        ...     false_map=(0.0, 0.0, 1.0)  # Invalid cert = complete falsity
        ... )
        >>> judgment = mapper.apply(True)
        >>> print(f"T={judgment.T:.2f}, I={judgment.I:.2f}, F={judgment.F:.2f}")
        T=1.00, I=0.00, F=0.00
    """
    
    def __init__(
        self,
        id: str,
        true_map: tuple[float, float, float],
        false_map: tuple[float, float, float],
        metadata: dict = None
    ):
        """
        Initialize boolean mapper.
        
        Args:
            id: Unique identifier for the mapper
            true_map: Judgment for True input (T, I, F)
            false_map: Judgment for False input (T, I, F)
            metadata: Optional metadata dictionary
        """
        parameters = BooleanParams(
            true_map=true_map,
            false_map=false_map
        )
        
        super().__init__(
            id=id,
            mapper_type=MapperType.BOOLEAN,
            parameters=parameters,
            metadata=metadata or {}
        )
    
    def apply(self, input_value: Union[bool, int, str]) -> NeutrosophicJudgment:
        """
        Transform boolean input into Neutrosophic Judgment.
        
        Args:
            input_value: The boolean value to transform
                        (accepts bool, int, or string representations)
            
        Returns:
            NeutrosophicJudgment with mapped T, I, F values
            
        Raises:
            InputError: If input validation fails
            MapperError: If transformation fails
        """
        # Validate and convert input to boolean
        boolean_value = self._convert_to_boolean(input_value)
        
        # Get appropriate judgment
        if boolean_value:
            t, i, f = self.parameters.true_map
        else:
            t, i, f = self.parameters.false_map
        
        # Create provenance entry
        provenance = self.create_provenance_entry(input_value)
        
        # Create and return NeutrosophicJudgment
        return NeutrosophicJudgment(
            T=t,
            I=i,
            F=f,
            provenance_chain=[provenance]
        )
    
    def _convert_to_boolean(self, value: Union[bool, int, str]) -> bool:
        """
        Convert various input types to boolean.
        
        Args:
            value: Input value to convert
            
        Returns:
            Boolean representation of the input
            
        Raises:
            InputError: If input cannot be converted to boolean
        """
        if isinstance(value, bool):
            return value
        
        elif isinstance(value, int):
            if value == 0:
                return False
            elif value == 1:
                return True
            else:
                raise InputError(f"Integer input must be 0 or 1, got {value}")
        
        elif isinstance(value, str):
            value_lower = value.lower().strip()
            
            # True values
            if value_lower in ('true', 't', 'yes', 'y', '1', 'on', 'enabled'):
                return True
            
            # False values
            elif value_lower in ('false', 'f', 'no', 'n', '0', 'off', 'disabled'):
                return False
            
            else:
                raise InputError(
                    f"String input must be a valid boolean representation, got '{value}'. "
                    f"Valid values: true/false, t/f, yes/no, y/n, 1/0, on/off, enabled/disabled"
                )
        
        else:
            raise InputError(f"Input must be bool, int, or str, got {type(value)}")
    
    def get_true_judgment(self) -> tuple[float, float, float]:
        """
        Get the judgment for True input.
        
        Returns:
            Tuple of (T, I, F) values for True input
        """
        return self.parameters.true_map
    
    def get_false_judgment(self) -> tuple[float, float, float]:
        """
        Get the judgment for False input.
        
        Returns:
            Tuple of (T, I, F) values for False input
        """
        return self.parameters.false_map
    
    def update_mappings(
        self, 
        true_map: tuple[float, float, float] = None,
        false_map: tuple[float, float, float] = None
    ) -> BooleanMapper:
        """
        Create a new mapper with updated mappings.
        
        Args:
            true_map: New judgment for True input (optional)
            false_map: New judgment for False input (optional)
            
        Returns:
            New BooleanMapper instance with updated mappings
            
        Raises:
            ValidationError: If judgment validation fails
        """
        new_true_map = true_map if true_map is not None else self.parameters.true_map
        new_false_map = false_map if false_map is not None else self.parameters.false_map
        
        # Validate judgments
        for name, judgment in [("true_map", new_true_map), ("false_map", new_false_map)]:
            t, i, f = judgment
            if not all(isinstance(x, (int, float)) for x in [t, i, f]):
                raise ValidationError(f"{name} values must be numbers")
            if not all(0.0 <= x <= 1.0 for x in [t, i, f]):
                raise ValidationError(f"{name} values must be in [0.0, 1.0]")
            if abs(t + i + f - 1.0) > 1e-10:
                raise ValidationError(f"{name} must satisfy T + I + F = 1.0")
        
        # Create new mapper
        return BooleanMapper(
            id=self.id,
            true_map=new_true_map,
            false_map=new_false_map,
            metadata=self.metadata.copy()
        )
    
    def __str__(self) -> str:
        """String representation of the mapper."""
        return f"BooleanMapper(id='{self.id}', true={self.parameters.true_map}, false={self.parameters.false_map})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"BooleanMapper(id='{self.id}', "
            f"true_map={self.parameters.true_map}, "
            f"false_map={self.parameters.false_map})"
        )
