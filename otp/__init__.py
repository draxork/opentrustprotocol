"""
OpenTrust Protocol (OTP) SDK
============================

This package is the reference implementation of the OpenTrust Protocol.

It provides the necessary tools to create, validate, and fuse
Neutrosophic Judgments.

Core Components:
----------------
- NeutrosophicJudgment: The main class for representing evidence (T, I, F).
- fuse: A module containing all standard fusion operators.

For more information, please visit the official documentation at https://opentrustprotocol.com
"""

from . import fuse
from .fuse import (
    conflict_aware_weighted_average,
    optimistic_fusion,
    pessimistic_fusion,
)

# Import the main components to make them easily accessible
# to the end-user via `from otp import ...`
from .judgment import NeutrosophicJudgment

# Define what is exported when a user does `from otp import *`
__all__ = [
    "NeutrosophicJudgment",
    "fuse",
    "conflict_aware_weighted_average",
    "optimistic_fusion",
    "pessimistic_fusion",
]

# Define the package version
__version__ = "1.0.5"

// CI/CD Test - Sun Sep 21 10:57:55 -03 2025
