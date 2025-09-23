#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
**REVOLUTIONARY DEMO**: Judgment ID System + Performance Oracle

This example demonstrates the complete Circle of Trust functionality:
- Automatic Judgment ID generation in fusion operations
- Outcome Judgment creation for real-world results
- Linking decisions with outcomes for performance tracking
"""

from otp import (
    NeutrosophicJudgment, OutcomeJudgment, OutcomeType,
    conflict_aware_weighted_average, optimistic_fusion, pessimistic_fusion,
    generate_judgment_id, ensure_judgment_id, create_outcome_judgment
)


def main():
    print("🚀 **OPENTRUST PROTOCOL v3.0 - CIRCLE OF TRUST DEMO** 🚀\n")

    # **STEP 1**: Create initial judgments from different sources
    print("📊 **STEP 1: Creating Initial Judgments**")
    sensor_judgment = NeutrosophicJudgment(
        T=0.8, I=0.15, F=0.05,  # High confidence in positive outcome
        provenance_chain=[{"source_id": "sensor-network", "timestamp": "2023-01-01T10:00:00Z"}]
    )
    
    expert_judgment = NeutrosophicJudgment(
        T=0.6, I=0.25, F=0.15,  # Moderate confidence with some uncertainty
        provenance_chain=[{"source_id": "expert-analysis", "timestamp": "2023-01-01T10:01:00Z"}]
    )
    
    market_judgment = NeutrosophicJudgment(
        T=0.7, I=0.2, F=0.1,  # Good market conditions
        provenance_chain=[{"source_id": "market-data", "timestamp": "2023-01-01T10:02:00Z"}]
    )

    print(f"✅ Sensor Judgment: T={sensor_judgment.T:.1f}, I={sensor_judgment.I:.1f}, F={sensor_judgment.F:.1f}")
    print(f"✅ Expert Judgment: T={expert_judgment.T:.1f}, I={expert_judgment.I:.1f}, F={expert_judgment.F:.1f}")
    print(f"✅ Market Judgment: T={market_judgment.T:.1f}, I={market_judgment.I:.1f}, F={market_judgment.F:.1f}")

    # **STEP 2**: Fuse judgments with automatic Judgment ID generation
    print("\n🔄 **STEP 2: Fusion Operations with Automatic Judgment IDs**")
    
    judgments = [sensor_judgment, expert_judgment, market_judgment]
    weights = [0.4, 0.3, 0.3]  # Sensor gets highest weight

    # Conflict-Aware Weighted Average (Primary operator)
    fused_cawa = conflict_aware_weighted_average(judgments, weights)
    print(f"🎯 CAWA Result: T={fused_cawa.T:.3f}, I={fused_cawa.I:.3f}, F={fused_cawa.F:.3f}")
    
    # Extract judgment_id from provenance chain
    cawa_judgment_id = None
    for entry in fused_cawa.provenance_chain:
        if entry.get("judgment_id"):
            cawa_judgment_id = entry["judgment_id"]
            break
    print(f"🔐 Judgment ID: {cawa_judgment_id}")

    # Optimistic Fusion (Best-case scenario)
    fused_optimistic = optimistic_fusion(judgments)
    print(f"☀️ Optimistic Result: T={fused_optimistic.T:.3f}, I={fused_optimistic.I:.3f}, F={fused_optimistic.F:.3f}")
    
    optimistic_judgment_id = None
    for entry in fused_optimistic.provenance_chain:
        if entry.get("judgment_id"):
            optimistic_judgment_id = entry["judgment_id"]
            break
    print(f"🔐 Judgment ID: {optimistic_judgment_id}")

    # Pessimistic Fusion (Worst-case scenario)
    fused_pessimistic = pessimistic_fusion(judgments)
    print(f"🌧️ Pessimistic Result: T={fused_pessimistic.T:.3f}, I={fused_pessimistic.I:.3f}, F={fused_pessimistic.F:.3f}")
    
    pessimistic_judgment_id = None
    for entry in fused_pessimistic.provenance_chain:
        if entry.get("judgment_id"):
            pessimistic_judgment_id = entry["judgment_id"]
            break
    print(f"🔐 Judgment ID: {pessimistic_judgment_id}")

    # **STEP 3**: Simulate real-world outcomes
    print("\n🌍 **STEP 3: Real-World Outcome Tracking**")
    
    # Simulate successful outcome
    success_outcome = create_outcome_judgment(
        links_to_judgment_id=cawa_judgment_id,  # Link to original decision
        T=1.0, I=0.0, F=0.0,  # Complete success
        outcome_type=OutcomeType.SUCCESS,
        oracle_source="trading-oracle"
    )
    
    print("✅ Success Outcome Recorded!")
    print(f"🔗 Links to Decision ID: {success_outcome.links_to_judgment_id}")
    print(f"📊 Outcome: T={success_outcome.T:.1f}, I={success_outcome.I:.1f}, F={success_outcome.F:.1f}")
    print(f"🔐 Outcome Judgment ID: {success_outcome.judgment_id}")

    # **STEP 4**: Demonstrate manual Judgment ID generation
    print("\n🛠️ **STEP 4: Manual Judgment ID Operations**")
    
    # Create a judgment without ID
    manual_judgment = NeutrosophicJudgment(
        T=0.9, I=0.1, F=0.0,
        provenance_chain=[{"source_id": "manual-input", "timestamp": "2023-01-01T12:00:00Z"}]
    )
    
    print(f"📝 Manual Judgment (no ID): T={manual_judgment.T:.1f}, I={manual_judgment.I:.1f}, F={manual_judgment.F:.1f}")
    
    # Check if it has judgment_id
    has_judgment_id = any(entry.get("judgment_id") for entry in manual_judgment.provenance_chain)
    print(f"❓ Has Judgment ID: {has_judgment_id}")

    # Generate ID manually
    manual_id = generate_judgment_id(manual_judgment)
    print(f"🔐 Generated Manual ID: {manual_id}")

    # Ensure ID is set
    judgment_with_id = ensure_judgment_id(manual_judgment)
    print(f"✅ Judgment with ID: T={judgment_with_id.T:.1f}, I={judgment_with_id.I:.1f}, F={judgment_with_id.F:.1f}")
    
    # Extract final judgment ID
    final_judgment_id = None
    for entry in judgment_with_id.provenance_chain:
        if entry.get("judgment_id"):
            final_judgment_id = entry["judgment_id"]
            break
    print(f"🔐 Final Judgment ID: {final_judgment_id}")

    # **STEP 5**: Performance Oracle Analysis
    print("\n📈 **STEP 5: Performance Oracle Analysis**")
    
    # Simulate multiple outcomes for analysis
    outcomes = [
        ("Decision 1", fused_cawa, success_outcome),
        ("Decision 2", fused_optimistic, success_outcome),
        ("Decision 3", fused_pessimistic, success_outcome),
    ]

    print("📊 Performance Analysis:")
    for name, decision, outcome in outcomes:
        if decision.T > 0.7 and outcome.T == 1.0:
            calibration = "✅ Well Calibrated"
        elif decision.T <= 0.5 and outcome.T == 1.0:
            calibration = "⚠️ Underconfident"
        elif decision.T > 0.8 and outcome.T == 0.0:
            calibration = "❌ Overconfident"
        else:
            calibration = "📊 Neutral"
        
        print(f"  {name}: {calibration} (Decision T={decision.T:.2f}, Outcome T={outcome.T:.1f})")

    print("\n🎉 **CIRCLE OF TRUST COMPLETE!** 🎉")
    print("✅ All judgments have unique IDs for tracking")
    print("✅ Real-world outcomes are linked to decisions")
    print("✅ Performance can be measured and analyzed")
    print("✅ The mathematical embodiment of trust is achieved!")


if __name__ == "__main__":
    main()
