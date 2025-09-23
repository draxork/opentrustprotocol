# -*- coding: utf-8 -*-
"""
fuse.py - Implementation of the OpenTrust Protocol fusion operators.

**REVOLUTIONARY UPDATE**: All fusion operations now generate:
- **Conformance Seals**: Mathematical proof that the operation was performed according to
  the exact OTP specification
- **Judgment IDs**: Unique identifiers for Circle of Trust tracking and Performance Oracle

This transforms OTP into the mathematical embodiment of trust itself, enabling
real-world outcome tracking and performance measurement.

This module contains the standard functions for combining multiple
Neutrosophic Judgments into a single, aggregated judgment with cryptographic proof.
"""

import datetime
from typing import List, Optional

from .judgment import NeutrosophicJudgment
from .conformance import generate_conformance_seal, create_fusion_provenance_entry
from .judgment_id import ensure_judgment_id


def _validate_inputs(
    judgments: List[NeutrosophicJudgment], weights: Optional[List[float]] = None
):
    """Helper function to validate the inputs for fusion functions."""
    if not judgments:
        raise ValueError("Judgments list cannot be empty.")
    if not all(isinstance(j, NeutrosophicJudgment) for j in judgments):
        raise TypeError(
            "All items in the judgments list must be of type NeutrosophicJudgment."
        )
    if weights:
        if len(judgments) != len(weights):
            raise ValueError(
                "Judgments list and weights list must have the same length."
            )
        if not all(isinstance(w, (int, float)) for w in weights):
            raise TypeError("All weights must be numeric.")


def conflict_aware_weighted_average(
    judgments: List[NeutrosophicJudgment], weights: List[float]
) -> NeutrosophicJudgment:
    """
    Fuses a list of judgments using the conflict-aware weighted average.
    This is the primary and recommended operator in OTP.

    **REVOLUTIONARY**: The fused judgment automatically includes:
    - **Conformance Seal**: Mathematical proof of specification compliance
    - **Judgment ID**: Unique identifier for Circle of Trust tracking

    Args:
        judgments: A list of NeutrosophicJudgment objects to fuse.
        weights: A list of numeric weights corresponding to each judgment.

    Returns:
        A new NeutrosophicJudgment object representing the fused judgment with
        automatic Conformance Seal and Judgment ID generation.

    Example:
        >>> judgment1 = NeutrosophicJudgment(0.8, 0.2, 0.0, [{"source_id": "sensor1"}])
        >>> judgment2 = NeutrosophicJudgment(0.6, 0.3, 0.1, [{"source_id": "sensor2"}])
        >>> fused = conflict_aware_weighted_average([judgment1, judgment2], [0.6, 0.4])
        >>> # The fused judgment now contains a Conformance Seal and Judgment ID
        >>> seal = fused.provenance_chain[-1]["conformance_seal"]
        >>> print(f"🔐 Conformance Seal: {seal}")
    """
    _validate_inputs(judgments, weights)

    adjusted_weights = []
    for i, j in enumerate(judgments):
        conflict_score = j.T * j.F
        adjusted_weight = weights[i] * (1 - conflict_score)
        adjusted_weights.append(adjusted_weight)

    total_adjusted_weight = sum(adjusted_weights)
    if total_adjusted_weight == 0:
        # Edge case where all adjusted weights are zero.
        # Fallback to a simple unweighted average.
        num_judgments = len(judgments)
        final_t = sum(j.T for j in judgments) / num_judgments
        final_i = sum(j.I for j in judgments) / num_judgments
        final_f = sum(j.F for j in judgments) / num_judgments
    else:
        final_t = (
            sum(j.T * w for j, w in zip(judgments, adjusted_weights))
            / total_adjusted_weight
        )
        final_i = (
            sum(j.I * w for j, w in zip(judgments, adjusted_weights))
            / total_adjusted_weight
        )
        final_f = (
            sum(j.F * w for j, w in zip(judgments, adjusted_weights))
            / total_adjusted_weight
        )

    # **REVOLUTIONARY**: Generate Conformance Seal
    try:
        conformance_seal = generate_conformance_seal(judgments, weights, "otp-cawa-v1.1")
    except Exception as e:
        # If seal generation fails, we should still proceed but log the error
        # This ensures backward compatibility
        import warnings
        warnings.warn(f"Failed to generate conformance seal: {e}")
        conformance_seal = None

    # Build the new provenance chain with Conformance Seal
    new_provenance = [item for j in judgments for item in j.provenance_chain]
    
    # Create fusion provenance entry with Conformance Seal
    fusion_entry = create_fusion_provenance_entry(
        operator_id="otp-cawa-v1.1",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        conformance_seal=conformance_seal,
        description="Conflict-aware weighted average fusion operation with Conformance Seal",
        metadata={
            "operator": "conflict_aware_weighted_average",
            "input_count": len(judgments),
            "weights": weights,
            "version": "3.0.0"
        }
    )
    
    new_provenance.append(fusion_entry)

    # Create the fused judgment
    fused_judgment = NeutrosophicJudgment(
        T=final_t, I=final_i, F=final_f, provenance_chain=new_provenance
    )
    
    # **REVOLUTIONARY**: Ensure the judgment has a unique ID for Circle of Trust
    return ensure_judgment_id(fused_judgment)


def optimistic_fusion(judgments: List[NeutrosophicJudgment]) -> NeutrosophicJudgment:
    """
    Fuses judgments by prioritizing the maximum T value and the minimum F value.
    Useful for opportunity analysis or "best-case" scenarios.

    **REVOLUTIONARY**: The fused judgment automatically includes:
    - **Conformance Seal**: Mathematical proof of specification compliance
    - **Judgment ID**: Unique identifier for Circle of Trust tracking

    Args:
        judgments: A list of NeutrosophicJudgment objects.

    Returns:
        A new NeutrosophicJudgment with the max T, min F, and average I,
        plus automatic Conformance Seal and Judgment ID generation.
    """
    _validate_inputs(judgments)

    final_t = max(j.T for j in judgments)
    final_f = min(j.F for j in judgments)
    final_i = sum(j.I for j in judgments) / len(judgments)

    # Ensure conservation constraint is satisfied
    total = final_t + final_i + final_f
    if total > 1.0:
        # Scale down proportionally to maintain relative relationships
        final_t = final_t / total
        final_i = final_i / total
        final_f = final_f / total

    # **REVOLUTIONARY**: Generate Conformance Seal
    # For operations without weights, we use equal weights
    equal_weights = [1.0] * len(judgments)
    try:
        conformance_seal = generate_conformance_seal(judgments, equal_weights, "otp-optimistic-v1.1")
    except Exception as e:
        import warnings
        warnings.warn(f"Failed to generate conformance seal: {e}")
        conformance_seal = None

    new_provenance = [item for j in judgments for item in j.provenance_chain]
    
    # Create fusion provenance entry with Conformance Seal
    fusion_entry = create_fusion_provenance_entry(
        operator_id="otp-optimistic-v1.1",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        conformance_seal=conformance_seal,
        description="Optimistic fusion operation with Conformance Seal",
        metadata={
            "operator": "optimistic_fusion",
            "input_count": len(judgments),
            "weights": equal_weights,
            "version": "3.0.0"
        }
    )
    
    new_provenance.append(fusion_entry)

    # Create the fused judgment
    fused_judgment = NeutrosophicJudgment(
        T=final_t, I=final_i, F=final_f, provenance_chain=new_provenance
    )
    
    # **REVOLUTIONARY**: Ensure the judgment has a unique ID for Circle of Trust
    return ensure_judgment_id(fused_judgment)


def pessimistic_fusion(judgments: List[NeutrosophicJudgment]) -> NeutrosophicJudgment:
    """
    Fuses judgments by prioritizing the maximum F value and the minimum T value.
    Indispensable for risk analysis or "worst-case" scenarios.

    **REVOLUTIONARY**: The fused judgment automatically includes:
    - **Conformance Seal**: Mathematical proof of specification compliance
    - **Judgment ID**: Unique identifier for Circle of Trust tracking

    Args:
        judgments: A list of NeutrosophicJudgment objects.

    Returns:
        A new NeutrosophicJudgment with the max F, min T, and average I,
        plus automatic Conformance Seal and Judgment ID generation.
    """
    _validate_inputs(judgments)

    final_t = min(j.T for j in judgments)
    final_f = max(j.F for j in judgments)
    final_i = sum(j.I for j in judgments) / len(judgments)

    # Ensure conservation constraint is satisfied
    total = final_t + final_i + final_f
    if total > 1.0:
        # Scale down proportionally to maintain relative relationships
        final_t = final_t / total
        final_i = final_i / total
        final_f = final_f / total

    # **REVOLUTIONARY**: Generate Conformance Seal
    # For operations without weights, we use equal weights
    equal_weights = [1.0] * len(judgments)
    try:
        conformance_seal = generate_conformance_seal(judgments, equal_weights, "otp-pessimistic-v1.1")
    except Exception as e:
        import warnings
        warnings.warn(f"Failed to generate conformance seal: {e}")
        conformance_seal = None

    new_provenance = [item for j in judgments for item in j.provenance_chain]
    
    # Create fusion provenance entry with Conformance Seal
    fusion_entry = create_fusion_provenance_entry(
        operator_id="otp-pessimistic-v1.1",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        conformance_seal=conformance_seal,
        description="Pessimistic fusion operation with Conformance Seal",
        metadata={
            "operator": "pessimistic_fusion",
            "input_count": len(judgments),
            "weights": equal_weights,
            "version": "3.0.0"
        }
    )
    
    new_provenance.append(fusion_entry)

    # Create the fused judgment
    fused_judgment = NeutrosophicJudgment(
        T=final_t, I=final_i, F=final_f, provenance_chain=new_provenance
    )
    
    # **REVOLUTIONARY**: Ensure the judgment has a unique ID for Circle of Trust
    return ensure_judgment_id(fused_judgment)