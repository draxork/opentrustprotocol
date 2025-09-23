# -*- coding: utf-8 -*-
"""
judgment_id.py - Judgment ID System for Circle of Trust

This module implements the Judgment ID system that enables the Performance Oracle
and Circle of Trust functionality. The Judgment ID is a SHA-256 hash of the
canonical representation of a Neutrosophic Judgment, used to link decisions
with their real-world outcomes.
"""

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .judgment import NeutrosophicJudgment, ProvenanceChain


class OutcomeType(Enum):
    """Type of outcome for Performance Oracle"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


@dataclass(frozen=True)
class OutcomeJudgment:
    """
    Outcome Judgment for Performance Oracle
    
    An Outcome Judgment represents the real-world result of a decision
    that was informed by a Neutrosophic Judgment. It links back to the
    original decision through the `links_to_judgment_id` field.
    """
    
    judgment_id: str
    links_to_judgment_id: str
    T: float
    I: float
    F: float
    outcome_type: OutcomeType
    oracle_source: str
    provenance_chain: ProvenanceChain = field(default_factory=list)
    
    def __post_init__(self):
        """Validate the outcome judgment parameters"""
        # Range validation
        if not (0.0 <= self.T <= 1.0):
            raise ValueError(f"T value must be between 0 and 1, but got {self.T}")
        if not (0.0 <= self.I <= 1.0):
            raise ValueError(f"I value must be between 0 and 1, but got {self.I}")
        if not (0.0 <= self.F <= 1.0):
            raise ValueError(f"F value must be between 0 and 1, but got {self.F}")

        # Conservation constraint validation
        total = self.T + self.I + self.F
        if total > 1.0:
            raise ValueError(f"Conservation constraint violated: T + I + F = {total} > 1.0")
    
    def to_neutrosophic_judgment(self) -> NeutrosophicJudgment:
        """
        Converts this Outcome Judgment to a regular Neutrosophic Judgment
        (without the oracle-specific fields)
        """
        return NeutrosophicJudgment(
            T=self.T,
            I=self.I,
            F=self.F,
            provenance_chain=self.provenance_chain
        )


def generate_judgment_id(judgment: NeutrosophicJudgment) -> str:
    """
    Generates a Judgment ID for a Neutrosophic Judgment
    
    The Judgment ID is a SHA-256 hash of the canonical representation
    of the judgment, excluding the judgment_id field itself to avoid
    recursive hashing.
    
    Args:
        judgment: The Neutrosophic Judgment to generate an ID for
        
    Returns:
        A SHA-256 hash as a hexadecimal string
        
    Example:
        >>> from otp import NeutrosophicJudgment, generate_judgment_id
        >>> judgment = NeutrosophicJudgment(
        ...     T=0.8, I=0.2, F=0.0,
        ...     provenance_chain=[{"source_id": "sensor1", "timestamp": "2023-01-01T00:00:00Z"}]
        ... )
        >>> judgment_id = generate_judgment_id(judgment)
        >>> print(f"Judgment ID: {judgment_id}")
    """
    # Create canonical representation without judgment_id
    canonical = {
        "T": judgment.T,
        "I": judgment.I,
        "F": judgment.F,
        "provenance_chain": [
            {
                "source_id": entry.get("source_id", ""),
                "timestamp": entry.get("timestamp", ""),
                "description": entry.get("description"),
                "metadata": entry.get("metadata"),
                # Exclude conformance_seal for consistency with existing system
            }
            for entry in judgment.provenance_chain
        ]
    }
    
    # Serialize to canonical JSON
    canonical_json = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
    
    # Generate SHA-256 hash
    hash_obj = hashlib.sha256(canonical_json.encode('utf-8'))
    return hash_obj.hexdigest()


def ensure_judgment_id(judgment: NeutrosophicJudgment) -> NeutrosophicJudgment:
    """
    Ensures a Neutrosophic Judgment has a Judgment ID
    
    If the judgment already has a judgment_id in its provenance_chain,
    returns it unchanged. If not, generates a new judgment_id and returns
    a new judgment with it added to the provenance chain.
    
    Args:
        judgment: The Neutrosophic Judgment to ensure has an ID
        
    Returns:
        A Neutrosophic Judgment with a judgment_id in its provenance chain
    """
    # Check if judgment already has a judgment_id in provenance
    for entry in judgment.provenance_chain:
        if entry.get("judgment_id"):
            return judgment
    
    # Generate new judgment_id
    judgment_id = generate_judgment_id(judgment)
    
    # Create new provenance entry with judgment_id
    new_provenance_entry = {
        "source_id": "otp-judgment-id-generator",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "description": "Automatic Judgment ID generation for Circle of Trust",
        "judgment_id": judgment_id,
        "metadata": {
            "generator": "otp-python-v3.0",
            "purpose": "circle-of-trust-tracking"
        }
    }
    
    # Create new judgment with updated provenance chain
    new_provenance_chain = judgment.provenance_chain + [new_provenance_entry]
    
    return NeutrosophicJudgment(
        T=judgment.T,
        I=judgment.I,
        F=judgment.F,
        provenance_chain=new_provenance_chain
    )


def create_outcome_judgment(
    links_to_judgment_id: str,
    T: float,
    I: float,
    F: float,
    outcome_type: OutcomeType,
    oracle_source: str,
    provenance_chain: Optional[ProvenanceChain] = None
) -> OutcomeJudgment:
    """
    Creates a new Outcome Judgment for Performance Oracle tracking
    
    Args:
        links_to_judgment_id: The ID of the original decision judgment
        T: Truth degree (usually binary: 1.0 for success, 0.0 for failure)
        I: Indeterminacy degree (usually 0.0 for outcomes)
        F: Falsity degree (usually binary: 0.0 for success, 1.0 for failure)
        outcome_type: Type of outcome (SUCCESS, FAILURE, PARTIAL)
        oracle_source: Source of the oracle that recorded this outcome
        provenance_chain: Optional provenance chain for this outcome
        
    Returns:
        A new OutcomeJudgment with automatic judgment_id generation
        
    Example:
        >>> from otp import create_outcome_judgment, OutcomeType
        >>> outcome = create_outcome_judgment(
        ...     links_to_judgment_id="original_decision_id",
        ...     T=1.0, I=0.0, F=0.0,
        ...     outcome_type=OutcomeType.SUCCESS,
        ...     oracle_source="trading-oracle"
        ... )
        >>> print(f"Outcome ID: {outcome.judgment_id}")
    """
    if provenance_chain is None:
        provenance_chain = []
    
    # Add oracle provenance entry
    oracle_entry = {
        "source_id": oracle_source,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "description": f"Outcome recorded by {oracle_source}",
        "metadata": {
            "outcome_type": outcome_type.value,
            "links_to_judgment_id": links_to_judgment_id,
            "oracle_version": "otp-python-v3.0"
        }
    }
    
    updated_provenance = provenance_chain + [oracle_entry]
    
    # Create temporary NeutrosophicJudgment to generate ID
    temp_judgment = NeutrosophicJudgment(
        T=T, I=I, F=F,
        provenance_chain=updated_provenance
    )
    
    judgment_id = generate_judgment_id(temp_judgment)
    
    return OutcomeJudgment(
        judgment_id=judgment_id,
        links_to_judgment_id=links_to_judgment_id,
        T=T, I=I, F=F,
        outcome_type=outcome_type,
        oracle_source=oracle_source,
        provenance_chain=updated_provenance
    )


# Import datetime for timestamp generation
import datetime
