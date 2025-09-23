"""
Numerical Mapper Implementation
===============================

This module implements the numerical mapper algorithm as specified in the
OTP v2.0 specification. It provides precise interpolation between three
reference points to transform continuous numerical values into Neutrosophic
Judgments.

The algorithm uses a "geometry of judgment" approach where any input value
is positioned within a triangle defined by three reference points:
- Falsity Point (F=1.0)
- Indeterminacy Point (I=1.0)  
- Truth Point (T=1.0)

Mathematical Foundation:
The interpolation works by determining which "transition zone" the input
falls into and calculating the proportional distance within that zone.
"""

from __future__ import annotations

import math
from typing import Union

from ..judgment import NeutrosophicJudgment
from .types import Mapper, NumericalParams, MapperType, MapperError, InputError


class NumericalMapper(Mapper):
    """
    Numerical mapper for transforming continuous numerical values.
    
    This mapper implements the interpolation algorithm specified in OTP v2.0,
    using three reference points to create a "geometry of judgment" that
    transforms any numerical input into a Neutrosophic Judgment.
    
    The algorithm works by:
    1. Defining three reference points (falsity, indeterminacy, truth)
    2. Determining which transition zone the input falls into
    3. Calculating proportional interpolation within that zone
    4. Ensuring conservation constraint (T + I + F = 1.0)
    
    Example:
        >>> mapper = NumericalMapper(
        ...     id="health-factor",
        ...     falsity_point=1.0,    # Liquidation
        ...     indeterminacy_point=1.5,  # Risk zone
        ...     truth_point=3.0       # Safe position
        ... )
        >>> judgment = mapper.apply(1.25)
        >>> print(f"T={judgment.T:.2f}, I={judgment.I:.2f}, F={judgment.F:.2f}")
        T=0.00, I=0.50, F=0.50
    """
    
    def __init__(
        self,
        id: str,
        falsity_point: float,
        indeterminacy_point: float,
        truth_point: float,
        clamp_to_range: bool = True,
        metadata: dict = None
    ):
        """
        Initialize numerical mapper.
        
        Args:
            id: Unique identifier for the mapper
            falsity_point: Input value where F=1.0
            indeterminacy_point: Input value where I=1.0
            truth_point: Input value where T=1.0
            clamp_to_range: Whether to clamp inputs outside valid range
            metadata: Optional metadata dictionary
        """
        parameters = NumericalParams(
            falsity_point=falsity_point,
            indeterminacy_point=indeterminacy_point,
            truth_point=truth_point,
            clamp_to_range=clamp_to_range
        )
        
        super().__init__(
            id=id,
            mapper_type=MapperType.NUMERICAL,
            parameters=parameters,
            metadata=metadata or {}
        )
    
    def apply(self, input_value: Union[int, float]) -> NeutrosophicJudgment:
        """
        Transform numerical input into Neutrosophic Judgment.
        
        This method implements the precise interpolation algorithm from
        the OTP v2.0 specification, ensuring mathematical correctness
        and conservation constraint compliance.
        
        Args:
            input_value: The numerical value to transform
            
        Returns:
            NeutrosophicJudgment with calculated T, I, F values
            
        Raises:
            InputError: If input validation fails
            MapperError: If transformation fails
        """
        # Validate input
        if not isinstance(input_value, (int, float)):
            raise InputError(f"Input must be a number, got {type(input_value)}")
        
        if math.isnan(input_value) or math.isinf(input_value):
            raise InputError("Input cannot be NaN or infinite")
        
        # Extract parameters
        params = self.parameters
        p_f = params.falsity_point
        p_i = params.indeterminacy_point
        p_t = params.truth_point
        
        # Clamp input to valid range if requested
        min_point = min(p_f, p_t)
        max_point = max(p_f, p_t)
        
        if params.clamp_to_range:
            input_value = max(min_point, min(max_point, input_value))
        else:
            if input_value < min_point or input_value > max_point:
                raise InputError(
                    f"Input value {input_value} is outside valid range "
                    f"[{min_point}, {max_point}] and clamp_to_range is False"
                )
        
        # Calculate T, I, F using interpolation algorithm
        t, i, f = self._calculate_interpolation(input_value, p_f, p_i, p_t)
        
        # Create provenance entry
        provenance = self.create_provenance_entry(input_value)
        
        # Create and return NeutrosophicJudgment
        return NeutrosophicJudgment(
            T=t,
            I=i,
            F=f,
            provenance_chain=[provenance]
        )
    
    def _calculate_interpolation(
        self, 
        input_value: float, 
        p_f: float, 
        p_i: float, 
        p_t: float
    ) -> tuple[float, float, float]:
        """
        Calculate T, I, F using the interpolation algorithm.
        
        This implements the exact algorithm from OTP v2.0 specification:
        1. Determine which transition zone the input falls into
        2. Calculate proportional distance within that zone
        3. Apply interpolation formula
        
        Args:
            input_value: The input value to process
            p_f: Falsity point
            p_i: Indeterminacy point  
            p_t: Truth point
            
        Returns:
            Tuple of (T, I, F) values
        """
        # Initialize result
        t = 0.0
        i = 0.0
        f = 0.0
        
        # Determine transition zone and apply interpolation
        if self._is_between_inclusive(input_value, p_f, p_i):
            # Zone: Falsity <-> Indeterminacy
            t, i, f = self._interpolate_falsity_indeterminacy(input_value, p_f, p_i)
        elif self._is_between_inclusive(input_value, p_i, p_t):
            # Zone: Indeterminacy <-> Truth
            t, i, f = self._interpolate_indeterminacy_truth(input_value, p_i, p_t)
        else:
            # Handle edge cases and exact matches
            t, i, f = self._handle_exact_matches(input_value, p_f, p_i, p_t)
        
        # Ensure conservation constraint with high precision
        total = t + i + f
        if abs(total - 1.0) > 1e-12:
            # Normalize to ensure T + I + F = 1.0
            t = t / total
            i = i / total
            f = f / total
        
        return t, i, f
    
    def _is_between_inclusive(self, value: float, point1: float, point2: float) -> bool:
        """Check if value is between two points (inclusive)."""
        min_val = min(point1, point2)
        max_val = max(point1, point2)
        return min_val <= value <= max_val
    
    def _interpolate_falsity_indeterminacy(self, input_value: float, p_f: float, p_i: float) -> tuple[float, float, float]:
        """
        Interpolate in the Falsity <-> Indeterminacy zone.
        
        As input moves from falsity_point to indeterminacy_point:
        - F decreases from 1.0 to 0.0
        - I increases from 0.0 to 1.0
        - T remains 0.0
        """
        range_dist = abs(p_i - p_f)
        
        if range_dist == 0:
            # Degenerate case: both points are the same
            if input_value == p_f:
                return 0.0, 1.0, 0.0  # I=1.0 at indeterminacy point
            else:
                return 0.0, 0.0, 1.0  # F=1.0 elsewhere
        
        # Calculate proportional distance from falsity point
        dist_from_f = abs(input_value - p_f)
        i = dist_from_f / range_dist
        f = 1.0 - i
        
        return 0.0, i, f  # T=0.0, I=proportional, F=complement
    
    def _interpolate_indeterminacy_truth(self, input_value: float, p_i: float, p_t: float) -> tuple[float, float, float]:
        """
        Interpolate in the Indeterminacy <-> Truth zone.
        
        As input moves from indeterminacy_point to truth_point:
        - I decreases from 1.0 to 0.0
        - T increases from 0.0 to 1.0
        - F remains 0.0
        """
        range_dist = abs(p_t - p_i)
        
        if range_dist == 0:
            # Degenerate case: both points are the same
            if input_value == p_t:
                return 1.0, 0.0, 0.0  # T=1.0 at truth point
            else:
                return 0.0, 1.0, 0.0  # I=1.0 elsewhere
        
        # Calculate proportional distance from indeterminacy point
        dist_from_i = abs(input_value - p_i)
        t = dist_from_i / range_dist
        i = 1.0 - t
        
        return t, i, 0.0  # T=proportional, I=complement, F=0.0
    
    def _handle_exact_matches(self, input_value: float, p_f: float, p_i: float, p_t: float) -> tuple[float, float, float]:
        """
        Handle exact matches with reference points.
        
        When input exactly matches a reference point, return the pure judgment
        for that point.
        """
        if input_value == p_f:
            return 0.0, 0.0, 1.0  # Pure falsity
        elif input_value == p_i:
            return 0.0, 1.0, 0.0  # Pure indeterminacy
        elif input_value == p_t:
            return 1.0, 0.0, 0.0  # Pure truth
        else:
            # This should not happen if clamping is enabled
            raise MapperError(f"Input {input_value} does not fall into any transition zone")
    
    def get_valid_range(self) -> tuple[float, float]:
        """
        Get the valid input range for this mapper.
        
        Returns:
            Tuple of (min_value, max_value) representing the valid input range
        """
        params = self.parameters
        return min(params.falsity_point, params.truth_point), max(params.falsity_point, params.truth_point)
    
    def is_in_valid_range(self, value: float) -> bool:
        """
        Check if a value is within the valid range.
        
        Args:
            value: The value to check
            
        Returns:
            True if value is within valid range, False otherwise
        """
        min_val, max_val = self.get_valid_range()
        return min_val <= value <= max_val
    
    def get_reference_points(self) -> dict[str, float]:
        """
        Get the reference points for this mapper.
        
        Returns:
            Dictionary with reference point values
        """
        params = self.parameters
        return {
            "falsity_point": params.falsity_point,
            "indeterminacy_point": params.indeterminacy_point,
            "truth_point": params.truth_point
        }
    
    def __str__(self) -> str:
        """String representation of the mapper."""
        params = self.parameters
        return (
            f"NumericalMapper(id='{self.id}', "
            f"falsity={params.falsity_point}, "
            f"indeterminacy={params.indeterminacy_point}, "
            f"truth={params.truth_point})"
        )
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"NumericalMapper(id='{self.id}', "
            f"falsity_point={self.parameters.falsity_point}, "
            f"indeterminacy_point={self.parameters.indeterminacy_point}, "
            f"truth_point={self.parameters.truth_point}, "
            f"clamp_to_range={self.parameters.clamp_to_range})"
        )
