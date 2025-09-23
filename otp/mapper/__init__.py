"""
OTP Mapper Module
=================

This module provides the OTP Mapper functionality for transforming raw data
into Neutrosophic Judgments using standardized, auditable algorithms.

The OTP Mapper is the heart of data transformation in the OpenTrust Protocol,
enabling any real-world data to be converted into rich, contextual judgments.

Core Components:
- Mapper: Base class for all mapper implementations
- NumericalMapper: Transforms continuous numerical values
- CategoricalMapper: Transforms categorical/string values  
- BooleanMapper: Transforms boolean values
- MapperRegistry: Central registry for managing mappers

Example Usage:
    from otp.mapper import NumericalMapper, MapperRegistry
    
    # Create a DeFi Health Factor mapper
    health_mapper = NumericalMapper(
        id="defi-health-factor",
        falsity_point=1.0,    # Liquidation imminent
        indeterminacy_point=1.5,  # Risk zone
        truth_point=3.0       # Safe position
    )
    
    # Transform a health factor value
    judgment = health_mapper.apply(1.8)
    print(f"Health Factor 1.8: T={judgment.T:.2f}, I={judgment.I:.2f}, F={judgment.F:.2f}")
    
    # Register mapper for reuse
    MapperRegistry.register(health_mapper)
"""

from .types import (
    Mapper,
    MapperType,
    NumericalParams,
    CategoricalParams,
    BooleanParams,
    MapperError,
    ValidationError,
)
from .numerical import NumericalMapper
from .categorical import CategoricalMapper
from .boolean import BooleanMapper
from .registry import MapperRegistry
from .validation import MapperValidator

__all__ = [
    # Core types
    "Mapper",
    "MapperType", 
    "NumericalParams",
    "CategoricalParams",
    "BooleanParams",
    "MapperError",
    "ValidationError",
    
    # Mapper implementations
    "NumericalMapper",
    "CategoricalMapper", 
    "BooleanMapper",
    
    # Registry and validation
    "MapperRegistry",
    "MapperValidator",
]

__version__ = "1.0.0"


