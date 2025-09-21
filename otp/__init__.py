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

# Import the main components to make them easily accessible
# to the end-user via `from otp import ...`
from .judgment import NeutrosophicJudgment

# Define what is exported when a user does `from otp import *`
__all__ = ["NeutrosophicJudgment", "fuse"]

# Define the package version
__version__ = "1.0.3"

// CI/CD Test - Sun Sep 21 04:35:51 -03 2025

# CI/CD Test - Sun Sep 21 09:45:20 -03 2025
