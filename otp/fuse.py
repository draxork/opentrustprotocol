# -*- coding: utf-8 -*-
"""
fuse.py - Implementation of the OpenTrust Protocol fusion operators.

This module contains the standard functions for combining multiple
Neutrosophic Judgments into a single, aggregated judgment.
"""

import datetime
from typing import List, Optional

from .judgment import NeutrosophicJudgment


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

    Args:
        judgments: A list of NeutrosophicJudgment objects to fuse.
        weights: A list of numeric weights corresponding to each judgment.

    Returns:
        A new NeutrosophicJudgment object representing the fused judgment.
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

    # Build the new provenance chain
    new_provenance = [item for j in judgments for item in j.provenance_chain]
    new_provenance.append(
        {
            "source_id": "otp-cawa-v1.1",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "description": "Conflict-aware weighted average fusion operation",
        }
    )

    return NeutrosophicJudgment(
        T=final_t, I=final_i, F=final_f, provenance_chain=new_provenance
    )


def optimistic_fusion(judgments: List[NeutrosophicJudgment]) -> NeutrosophicJudgment:
    """
    Fuses judgments by prioritizing the maximum T value and the minimum F value.
    Useful for opportunity analysis or "best-case" scenarios.

    Args:
        judgments: A list of NeutrosophicJudgment objects.

    Returns:
        A new NeutrosophicJudgment with the max T, min F, and average I.
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

    new_provenance = [item for j in judgments for item in j.provenance_chain]
    new_provenance.append(
        {
            "source_id": "otp-optimistic-v1.1",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "description": "Optimistic fusion operation",
        }
    )

    return NeutrosophicJudgment(
        T=final_t, I=final_i, F=final_f, provenance_chain=new_provenance
    )


def pessimistic_fusion(judgments: List[NeutrosophicJudgment]) -> NeutrosophicJudgment:
    """
    Fuses judgments by prioritizing the maximum F value and the minimum T value.
    Indispensable for risk analysis or "worst-case" scenarios.

    Args:
        judgments: A list of NeutrosophicJudgment objects.

    Returns:
        A new NeutrosophicJudgment with the max F, min T, and average I.
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

    new_provenance = [item for j in judgments for item in j.provenance_chain]
    new_provenance.append(
        {
            "source_id": "otp-pessimistic-v1.1",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "description": "Pessimistic fusion operation",
        }
    )

    return NeutrosophicJudgment(
        T=final_t, I=final_i, F=final_f, provenance_chain=new_provenance
    )
