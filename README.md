OpenTrust Protocol (OTP) SDK

The Open Standard for Auditable Trust.
This is the official Python SDK for the OpenTrust Protocol (OTP). It enables developers to create, manipulate, and fuse Neutrosophic Judgments to build more transparent, robust, and auditable systems.

OTP transforms uncertainty from a "black box" into a measurable metric (T, I, F) with a complete audit trail (provenance_chain).

Official Website & Full Documentation: https://opentrustprotocol.com

Scientific Foundation: https://neutrosofia.com

Installationpip install opentrustprotocol

Quick StartStart using OTP in just a few lines of code.from otp import NeutrosophicJudgment, fuse

# 1. Create Neutrosophic Judgments from your evidence
# Source 1: An AI model's confidence score
judgment_from_model = NeutrosophicJudgment(
    T=0.85, 
    I=0.15, 
    F=0.0,
    provenance_chain=[{
        "source_id": "model-text-bison-v1.2",
        "timestamp": "2025-09-20T20:30:00Z"
    }]
)

# Source 2: A human expert's verdict
judgment_from_expert = NeutrosophicJudgment(
    T=0.7, 
    I=0.1, 
    F=0.2,
    provenance_chain=[{
        "source_id": "expert-auditor-jane-doe",
        "timestamp": "2025-09-20T20:32:15Z"
    }]
)

# 2. Fuse the evidence to get an auditable conclusion
# We use the standard, conflict-aware operator.
# We give more weight to the human expert (60%) than the model (40%).
fused_judgment = fuse.conflict_aware_weighted_average(
    judgments=[judgment_from_model, judgment_from_expert],
    weights=[0.4, 0.6]
)

# 3. Analyze the result and its audit trail
print(f"Fused Judgment: {fused_judgment}")
# Fused Judgment: NeutrosophicJudgment(T=0.76, I=0.12, F=0.12)

# The provenance_chain now contains the full history
print("\nComplete Audit Trail:")
for entry in fused_judgment.provenance_chain:
    print(f"- {entry}")

# - {'source_id': 'model-text-bison-v1.2', ...}
# - {'source_id': 'expert-auditor-jane-doe', ...}
# - {'operator_id': 'otp-cawa-v1.1', ...}
What's Next?Visit the Technical Guide to learn about all available fusion operators.Explore the Practical Guide for advanced examples of data mapping.Contribute to the project on GitHub.