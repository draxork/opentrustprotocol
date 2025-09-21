# -*- coding: utf-8 -*-
"""
judgment.py - Defines the core data structure of the OpenTrust Protocol.

This module contains the `NeutrosophicJudgment` class, which is the
standard representation of evidence with its Truth (T), Indeterminacy (I),
and Falsity (F) components, along with its audit trail (provenance_chain).
"""

import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List

# Define a type alias for the provenance chain for clarity.
ProvenanceChain = List[Dict[str, Any]]


@dataclass(frozen=True)
class NeutrosophicJudgment:
    """
    Represents a Neutrosophic Judgment, the atomic unit of evidence in OTP.

    This class is immutable (`frozen=True`) to ensure that evidence
    cannot be altered after its creation.

    Attributes:
        T (float): Degree of Truth/Support. Must be in the range [0, 1].
        I (float): Degree of Indeterminacy/Uncertainty. Must be in the range [0, 1].
        F (float): Degree of Falsity/Contradiction. Must be in the range [0, 1].
        provenance_chain (ProvenanceChain): A list of dictionaries documenting
            the origin and history of the judgment.
    """

    T: float
    I: float
    F: float
    provenance_chain: ProvenanceChain = field(default_factory=list)

    def __post_init__(self):
        """
        Performs validation checks after the object has been initialized.
        """
        # Range validation
        if not (0.0 <= self.T <= 1.0):
            raise ValueError(f"T value must be between 0 and 1, but got {self.T}")
        if not (0.0 <= self.I <= 1.0):
            raise ValueError(f"I value must be between 0 and 1, but got {self.I}")
        if not (0.0 <= self.F <= 1.0):
            raise ValueError(f"F value must be between 0 and 1, but got {self.F}")

        # Conservation constraint validation
        if self.T + self.I + self.F > 1.0:
            raise ValueError(
                f"Conservation constraint violated: T + I + F > 1.0 (got {self.T + self.I + self.F:.2f})"
            )

        # Provenance chain validation
        if not isinstance(self.provenance_chain, list):
            raise TypeError("provenance_chain must be a list of dictionaries.")

        if len(self.provenance_chain) == 0:
            raise ValueError("Provenance chain cannot be empty")

        # Validate provenance entries
        for i, entry in enumerate(self.provenance_chain):
            if not isinstance(entry, dict):
                raise TypeError(f"Provenance entry {i} must be a dictionary")
            if "source_id" not in entry or not entry["source_id"]:
                raise ValueError(f"Provenance entry {i} must have source_id")
            if "timestamp" not in entry or not entry["timestamp"]:
                raise ValueError(f"Provenance entry {i} must have timestamp")

    def __repr__(self) -> str:
        """
        Custom string representation for a cleaner display.
        """
        return f"NeutrosophicJudgment(T={self.T:.2f}, I={self.I:.2f}, F={self.F:.2f})"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NeutrosophicJudgment":
        """
        Creates a NeutrosophicJudgment instance from a dictionary.
        Useful for deserializing data (e.g., from JSON).
        """
        return cls(
            T=data.get("T", 0.0),
            I=data.get("I", 0.0),
            F=data.get("F", 0.0),
            provenance_chain=data.get("provenance_chain", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the NeutrosophicJudgment instance to a dictionary.
        Useful for serializing data (e.g., to JSON).
        """
        return {
            "T": self.T,
            "I": self.I,
            "F": self.F,
            "provenance_chain": self.provenance_chain,
        }
