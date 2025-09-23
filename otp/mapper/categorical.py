"""
Categorical Mapper Implementation
=================================

This module implements the categorical mapper for transforming string/categorical
values into Neutrosophic Judgments using predefined mappings.

The categorical mapper allows for direct mapping of discrete categories to
specific judgments, enabling domain-specific transformations where the
relationship between categories and trust levels is well-defined.
"""

from __future__ import annotations

from typing import Union

from ..judgment import NeutrosophicJudgment
from .types import Mapper, CategoricalParams, MapperType, MapperError, InputError, ValidationError


class CategoricalMapper(Mapper):
    """
    Categorical mapper for transforming string/categorical values.
    
    This mapper provides direct mapping from categorical inputs to predefined
    Neutrosophic Judgments. It's ideal for cases where the relationship
    between categories and trust levels is well-defined and doesn't require
    interpolation.
    
    Example:
        >>> mapper = CategoricalMapper(
        ...     id="kyc-status",
        ...     mappings={
        ...         "VERIFIED": (1.0, 0.0, 0.0),    # Complete trust
        ...         "PENDING": (0.0, 1.0, 0.0),    # Complete uncertainty
        ...         "REJECTED": (0.0, 0.0, 1.0),   # Complete falsity
        ...         "PARTIAL": (0.6, 0.3, 0.1)     # Mixed judgment
        ...     },
        ...     default_judgment=(0.0, 0.0, 1.0)   # Unknown = falsity
        ... )
        >>> judgment = mapper.apply("VERIFIED")
        >>> print(f"T={judgment.T:.2f}, I={judgment.I:.2f}, F={judgment.F:.2f}")
        T=1.00, I=0.00, F=0.00
    """
    
    def __init__(
        self,
        id: str,
        mappings: dict[str, tuple[float, float, float]],
        default_judgment: tuple[float, float, float] = None,
        metadata: dict = None
    ):
        """
        Initialize categorical mapper.
        
        Args:
            id: Unique identifier for the mapper
            mappings: Dictionary mapping categories to (T, I, F) tuples
            default_judgment: Optional default judgment for unknown categories
            metadata: Optional metadata dictionary
        """
        parameters = CategoricalParams(
            mappings=mappings,
            default_judgment=default_judgment
        )
        
        super().__init__(
            id=id,
            mapper_type=MapperType.CATEGORICAL,
            parameters=parameters,
            metadata=metadata or {}
        )
    
    def apply(self, input_value: Union[str, int, float]) -> NeutrosophicJudgment:
        """
        Transform categorical input into Neutrosophic Judgment.
        
        Args:
            input_value: The categorical value to transform
            
        Returns:
            NeutrosophicJudgment with mapped T, I, F values
            
        Raises:
            InputError: If input validation fails or category not found
            MapperError: If transformation fails
        """
        # Validate input
        if input_value is None:
            raise InputError("Input cannot be None")
        
        # Convert input to string for consistent lookup
        category = str(input_value).strip()
        
        if not category:
            raise InputError("Input cannot be empty or whitespace only")
        
        # Look up category in mappings
        params = self.parameters
        
        if category in params.mappings:
            # Found exact match
            t, i, f = params.mappings[category]
        elif params.default_judgment is not None:
            # Use default judgment
            t, i, f = params.default_judgment
        else:
            # No mapping found and no default
            available_categories = list(params.mappings.keys())
            raise InputError(
                f"Category '{category}' not found in mappings. "
                f"Available categories: {available_categories}"
            )
        
        # Create provenance entry
        provenance = self.create_provenance_entry(input_value)
        
        # Create and return NeutrosophicJudgment
        return NeutrosophicJudgment(
            T=t,
            I=i,
            F=f,
            provenance_chain=[provenance]
        )
    
    def get_categories(self) -> list[str]:
        """
        Get list of all mapped categories.
        
        Returns:
            List of category strings
        """
        return list(self.parameters.mappings.keys())
    
    def has_category(self, category: str) -> bool:
        """
        Check if a category is mapped.
        
        Args:
            category: The category to check
            
        Returns:
            True if category is mapped, False otherwise
        """
        return str(category).strip() in self.parameters.mappings
    
    def get_judgment_for_category(self, category: str) -> tuple[float, float, float]:
        """
        Get the judgment for a specific category.
        
        Args:
            category: The category to look up
            
        Returns:
            Tuple of (T, I, F) values for the category
            
        Raises:
            InputError: If category not found and no default
        """
        category = str(category).strip()
        params = self.parameters
        
        if category in params.mappings:
            return params.mappings[category]
        elif params.default_judgment is not None:
            return params.default_judgment
        else:
            raise InputError(f"Category '{category}' not found in mappings")
    
    def add_category(self, category: str, judgment: tuple[float, float, float]) -> CategoricalMapper:
        """
        Create a new mapper with an additional category mapping.
        
        Args:
            category: The category to add
            judgment: The (T, I, F) judgment for this category
            
        Returns:
            New CategoricalMapper instance with the additional mapping
            
        Raises:
            ValidationError: If judgment validation fails
        """
        # Validate judgment
        t, i, f = judgment
        if not all(isinstance(x, (int, float)) for x in [t, i, f]):
            raise ValidationError("Judgment values must be numbers")
        if not all(0.0 <= x <= 1.0 for x in [t, i, f]):
            raise ValidationError("Judgment values must be in [0.0, 1.0]")
        if abs(t + i + f - 1.0) > 1e-10:
            raise ValidationError("Judgment must satisfy T + I + F = 1.0")
        
        # Create new mappings dictionary
        new_mappings = self.parameters.mappings.copy()
        new_mappings[str(category).strip()] = judgment
        
        # Create new mapper
        return CategoricalMapper(
            id=self.id,
            mappings=new_mappings,
            default_judgment=self.parameters.default_judgment,
            metadata=self.metadata.copy()
        )
    
    def remove_category(self, category: str) -> CategoricalMapper:
        """
        Create a new mapper with a category mapping removed.
        
        Args:
            category: The category to remove
            
        Returns:
            New CategoricalMapper instance without the specified mapping
            
        Raises:
            InputError: If category doesn't exist
        """
        category = str(category).strip()
        
        if category not in self.parameters.mappings:
            raise InputError(f"Category '{category}' not found in mappings")
        
        # Create new mappings dictionary
        new_mappings = self.parameters.mappings.copy()
        del new_mappings[category]
        
        if not new_mappings:
            raise ValidationError("Cannot remove the last category mapping")
        
        # Create new mapper
        return CategoricalMapper(
            id=self.id,
            mappings=new_mappings,
            default_judgment=self.parameters.default_judgment,
            metadata=self.metadata.copy()
        )
    
    def __str__(self) -> str:
        """String representation of the mapper."""
        categories = list(self.parameters.mappings.keys())
        return f"CategoricalMapper(id='{self.id}', categories={len(categories)}, has_default={self.parameters.default_judgment is not None})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"CategoricalMapper(id='{self.id}', "
            f"mappings={len(self.parameters.mappings)}, "
            f"default_judgment={self.parameters.default_judgment is not None})"
        )
