"""
OpenTrust Protocol (OTP) SDK
============================

**REVOLUTIONARY UPDATE**: OTP v2.0 introduces the **Zero Pillar: Conformance Seals**

This package is the reference implementation of the OpenTrust Protocol with
**mathematical proof of conformance**. Every fusion operation now generates a
cryptographic SHA-256 hash that proves the operation was performed according
to the exact OTP specification.

This transforms OTP from a trust protocol into **the mathematical embodiment of trust itself**.

Core Components:
----------------
- NeutrosophicJudgment: The main class for representing evidence (T, I, F).
- fuse: A module containing all standard fusion operators with Conformance Seals.
- conformance: The revolutionary Conformance Seal module for cryptographic verification.

For more information, please visit the official documentation at https://opentrustprotocol.com
"""

from . import fuse
from .fuse import (
    conflict_aware_weighted_average,
    optimistic_fusion,
    pessimistic_fusion,
)

# **REVOLUTIONARY**: Import Conformance Seal module
from . import conformance
from .conformance import (
    generate_conformance_seal,
    verify_conformance_seal,
    verify_conformance_seal_with_inputs,
    create_fusion_provenance_entry,
    ConformanceError,
)

# Import the main components to make them easily accessible
# to the end-user via `from otp import ...`
from .judgment import NeutrosophicJudgment

# Import mapper components
from . import mapper
from .mapper import (
    NumericalMapper,
    CategoricalMapper,
    BooleanMapper,
    MapperRegistry,
    MapperValidator,
)

# Define what is exported when a user does `from otp import *`
__all__ = [
    "NeutrosophicJudgment",
    "fuse",
    "conflict_aware_weighted_average",
    "optimistic_fusion",
    "pessimistic_fusion",
    "conformance",
    "generate_conformance_seal",
    "verify_conformance_seal",
    "verify_conformance_seal_with_inputs",
    "create_fusion_provenance_entry",
    "ConformanceError",
    "mapper",
    "NumericalMapper",
    "CategoricalMapper", 
    "BooleanMapper",
    "MapperRegistry",
    "MapperValidator",
]

# Define the package version - **REVOLUTIONARY UPDATE**
__version__ = "2.0.0"
