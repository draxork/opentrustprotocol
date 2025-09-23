"""
OpenTrust Protocol (OTP) SDK
============================

**REVOLUTIONARY UPDATE**: OTP v3.0 introduces:
- **Zero Pillar**: Proof-of-Conformance Seals (cryptographic proof of specification compliance)
- **First Pillar**: Performance Oracle (Circle of Trust for real-world outcome tracking)

This package is the reference implementation of the OpenTrust Protocol with
**mathematical proof of conformance** and **Performance Oracle capabilities**.
Every fusion operation now generates a cryptographic SHA-256 hash that proves
the operation was performed according to the exact OTP specification.
Additionally, the Performance Oracle system enables tracking real-world outcomes
to measure the effectiveness of OTP-based decisions.

This transforms OTP from a trust protocol into **the mathematical embodiment of trust itself**.

Core Components:
----------------
- NeutrosophicJudgment: The main class for representing evidence (T, I, F).
- fuse: A module containing all standard fusion operators with Conformance Seals.
- conformance: The revolutionary Conformance Seal module for cryptographic verification.
- judgment_id: The Performance Oracle module for Circle of Trust tracking.

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

# **REVOLUTIONARY**: Import Judgment ID module for Performance Oracle
from . import judgment_id
from .judgment_id import (
    generate_judgment_id,
    ensure_judgment_id,
    create_outcome_judgment,
    OutcomeJudgment,
    OutcomeType,
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
    "judgment_id",
    "generate_judgment_id",
    "ensure_judgment_id",
    "create_outcome_judgment",
    "OutcomeJudgment",
    "OutcomeType",
    "mapper",
    "NumericalMapper",
    "CategoricalMapper", 
    "BooleanMapper",
    "MapperRegistry",
    "MapperValidator",
]

# Define the package version - **REVOLUTIONARY UPDATE**
__version__ = "3.0.0"
