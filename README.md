# OpenTrust Protocol (OTP) Python SDK

> 🚀 **CI/CD Active**: Automated testing, linting, security audits, and PyPI publishing

[![PyPI version](https://badge.fury.io/py/opentrustprotocol.svg)](https://badge.fury.io/py/opentrustprotocol)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**The Open Standard for Auditable Trust**

This is the official Python SDK for the OpenTrust Protocol (OTP). It enables developers to create, manipulate, and fuse Neutrosophic Judgments to build more transparent, robust, and auditable systems.

OTP transforms uncertainty from a "black box" into a measurable metric (T, I, F) with a complete audit trail (`provenance_chain`).

## Features

- **Neutrosophic Judgments**: Represent evidence with Truth (T), Indeterminacy (I), and Falsity (F) components
- **Fusion Operators**: Multiple strategies for combining judgments (conflict-aware, optimistic, pessimistic)
- **Audit Trail**: Complete provenance tracking for every decision
- **Python 3.8+**: Modern Python support with type hints
- **MIT Licensed**: Open source and free to use

Official Website & Full Documentation: https://opentrustprotocol.com

Scientific Foundation: https://neutrosofia.com

## Installation

```bash
pip install opentrustprotocol
```

## Quick Start

Start using OTP in just a few lines of code:

```python
from otp import NeutrosophicJudgment, fuse

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
```

## Use Cases

- **Financial Risk Assessment**: Evaluate investment opportunities with multiple data sources
- **Identity Verification**: Multi-factor authentication with confidence scoring
- **AI Model Validation**: Assess reliability of machine learning predictions
- **Blockchain Auditing**: Verify transaction legitimacy with multiple validators
- **Reputation Systems**: Build trust networks with auditable metrics

## Fusion Operators

### 1. Conflict-Aware Weighted Average (Recommended)
```python
result = fuse.conflict_aware_weighted_average(
    judgments=[judgment1, judgment2, judgment3],
    weights=[0.5, 0.3, 0.2]
)
```
Automatically adjusts weights based on internal conflicts in judgments.

### 2. Optimistic Fusion
```python
result = fuse.optimistic_fusion(judgments)
```
Takes maximum T and minimum F - useful for opportunity analysis.

### 3. Pessimistic Fusion
```python
result = fuse.pessimistic_fusion(judgments)
```
Takes minimum T and maximum F - useful for risk analysis.

## What's Next?

- Visit the [Technical Guide](https://opentrustprotocol.com) to learn about all available fusion operators
- Explore the [Practical Guide](https://opentrustprotocol.com) for advanced examples of data mapping
- [Contribute to the project on GitHub](https://github.com/draxork/opentrustprotocol)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
