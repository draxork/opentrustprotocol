"""
OTP Mapper Examples
===================

This module demonstrates practical usage of the OTP Mapper system
with real-world examples from various domains including DeFi, KYC/AML,
IoT sensors, and supply chain management.
"""

from otp.mapper import (
    NumericalMapper, 
    CategoricalMapper, 
    BooleanMapper,
    MapperRegistry
)
from otp import conflict_aware_weighted_average


def defi_health_factor_example():
    """
    DeFi Health Factor Example
    =========================
    
    Demonstrates how to use numerical mapper for DeFi protocol
    health factor assessment.
    """
    print("🏦 DeFi Health Factor Example")
    print("=" * 50)
    
    # Create health factor mapper
    health_mapper = NumericalMapper(
        id="defi-health-factor",
        falsity_point=1.0,    # Liquidation imminent
        indeterminacy_point=1.5,  # Risk zone
        truth_point=3.0       # Safe position
    )
    
    # Test various health factors
    health_factors = [1.05, 1.25, 1.5, 2.0, 2.5, 3.0]
    
    for hf in health_factors:
        judgment = health_mapper.apply(hf)
        print(f"Health Factor {hf:4.2f}: T={judgment.T:.3f}, I={judgment.I:.3f}, F={judgment.F:.3f}")
        
        # Interpret the result
        if judgment.T > 0.5:
            status = "🟢 Safe"
        elif judgment.I > 0.5:
            status = "🟡 Risky"
        else:
            status = "🔴 Dangerous"
        
        print(f"  → {status}")
        print()
    
    return health_mapper


def kyc_status_example():
    """
    KYC/AML Status Example
    ======================
    
    Demonstrates categorical mapper for KYC verification status.
    """
    print("🆔 KYC/AML Status Example")
    print("=" * 50)
    
    # Create KYC status mapper
    kyc_mapper = CategoricalMapper(
        id="kyc-verification",
        mappings={
            "VERIFIED": (1.0, 0.0, 0.0),    # Complete trust
            "PENDING": (0.0, 1.0, 0.0),    # Complete uncertainty
            "REJECTED": (0.0, 0.0, 1.0),   # Complete falsity
            "PARTIAL": (0.6, 0.3, 0.1),    # Mixed judgment
            "EXPIRED": (0.2, 0.6, 0.2)     # Mostly uncertain
        },
        default_judgment=(0.0, 0.0, 1.0)   # Unknown = falsity
    )
    
    # Test various KYC statuses
    statuses = ["VERIFIED", "PENDING", "REJECTED", "PARTIAL", "EXPIRED", "UNKNOWN"]
    
    for status in statuses:
        try:
            judgment = kyc_mapper.apply(status)
            print(f"KYC Status '{status:8s}': T={judgment.T:.3f}, I={judgment.I:.3f}, F={judgment.F:.3f}")
            
            # Interpret the result
            if judgment.T > 0.7:
                level = "🟢 High Trust"
            elif judgment.T > 0.3:
                level = "🟡 Medium Trust"
            elif judgment.I > 0.5:
                level = "🟡 Uncertain"
            else:
                level = "🔴 Low Trust"
            
            print(f"  → {level}")
            print()
            
        except Exception as e:
            print(f"KYC Status '{status:8s}': Error - {e}")
            print()
    
    return kyc_mapper


def iot_temperature_example():
    """
    IoT Temperature Sensor Example
    =============================
    
    Demonstrates numerical mapper for IoT temperature monitoring.
    """
    print("🌡️  IoT Temperature Sensor Example")
    print("=" * 50)
    
    # Create temperature mapper for server room monitoring
    temp_mapper = NumericalMapper(
        id="server-room-temp",
        falsity_point=35.0,   # Too hot - dangerous
        indeterminacy_point=22.0,  # Optimal range
        truth_point=18.0      # Too cold - also dangerous
    )
    
    # Test various temperatures
    temperatures = [15.0, 18.0, 20.0, 22.0, 25.0, 30.0, 35.0, 38.0]
    
    for temp in temperatures:
        judgment = temp_mapper.apply(temp)
        print(f"Temperature {temp:4.1f}°C: T={judgment.T:.3f}, I={judgment.I:.3f}, F={judgment.F:.3f}")
        
        # Interpret the result
        if judgment.T > 0.7:
            status = "🟢 Optimal"
        elif judgment.I > 0.5:
            status = "🟡 Warning"
        else:
            status = "🔴 Critical"
        
        print(f"  → {status}")
        print()
    
    return temp_mapper


def ssl_certificate_example():
    """
    SSL Certificate Example
    =======================
    
    Demonstrates boolean mapper for SSL certificate validation.
    """
    print("🔒 SSL Certificate Example")
    print("=" * 50)
    
    # Create SSL certificate mapper
    ssl_mapper = BooleanMapper(
        id="ssl-certificate",
        true_map=(0.9, 0.1, 0.0),   # Valid cert = high trust (with small uncertainty)
        false_map=(0.0, 0.0, 1.0)  # Invalid cert = complete falsity
    )
    
    # Test various certificate states
    cert_states = [True, False, "valid", "invalid", 1, 0]
    
    for state in cert_states:
        try:
            judgment = ssl_mapper.apply(state)
            print(f"SSL Cert '{str(state):6s}': T={judgment.T:.3f}, I={judgment.I:.3f}, F={judgment.F:.3f}")
            
            # Interpret the result
            if judgment.T > 0.8:
                status = "🟢 Secure"
            elif judgment.I > 0.5:
                status = "🟡 Uncertain"
            else:
                status = "🔴 Insecure"
            
            print(f"  → {status}")
            print()
            
        except Exception as e:
            print(f"SSL Cert '{str(state):6s}': Error - {e}")
            print()
    
    return ssl_mapper


def credit_score_example():
    """
    Credit Score Example
    ====================
    
    Demonstrates numerical mapper for credit scoring.
    """
    print("💳 Credit Score Example")
    print("=" * 50)
    
    # Create credit score mapper
    credit_mapper = NumericalMapper(
        id="credit-score",
        falsity_point=300,    # Poor credit
        indeterminacy_point=650,  # Average credit
        truth_point=850      # Excellent credit
    )
    
    # Test various credit scores
    scores = [250, 400, 550, 650, 720, 780, 820, 850]
    
    for score in scores:
        judgment = credit_mapper.apply(score)
        print(f"Credit Score {score:3d}: T={judgment.T:.3f}, I={judgment.I:.3f}, F={judgment.F:.3f}")
        
        # Interpret the result
        if judgment.T > 0.7:
            level = "🟢 Excellent"
        elif judgment.T > 0.3:
            level = "🟡 Good"
        elif judgment.I > 0.5:
            level = "🟡 Fair"
        else:
            level = "🔴 Poor"
        
        print(f"  → {level}")
        print()
    
    return credit_mapper


def registry_example():
    """
    Mapper Registry Example
    =======================
    
    Demonstrates how to use the mapper registry for managing
    multiple mappers across an application.
    """
    print("📋 Mapper Registry Example")
    print("=" * 50)
    
    # Get the global registry
    registry = MapperRegistry()
    
    # Create and register multiple mappers
    health_mapper = registry.create_numerical_mapper(
        mapper_id="defi-health-factor",
        falsity_point=1.0,
        indeterminacy_point=1.5,
        truth_point=3.0
    )
    
    kyc_mapper = registry.create_categorical_mapper(
        mapper_id="kyc-status",
        mappings={
            "VERIFIED": (1.0, 0.0, 0.0),
            "PENDING": (0.0, 1.0, 0.0),
            "REJECTED": (0.0, 0.0, 1.0)
        }
    )
    
    ssl_mapper = registry.create_boolean_mapper(
        mapper_id="ssl-cert",
        true_map=(0.9, 0.1, 0.0),
        false_map=(0.0, 0.0, 1.0)
    )
    
    # List all registered mappers
    print(f"Registered mappers: {registry.list_mappers()}")
    print(f"Total count: {registry.count()}")
    print()
    
    # Use registered mappers
    print("Using registered mappers:")
    
    # Health factor
    health_judgment = registry.get("defi-health-factor").apply(1.8)
    print(f"Health Factor 1.8: T={health_judgment.T:.3f}")
    
    # KYC status
    kyc_judgment = registry.get("kyc-status").apply("VERIFIED")
    print(f"KYC Status 'VERIFIED': T={kyc_judgment.T:.3f}")
    
    # SSL certificate
    ssl_judgment = registry.get("ssl-cert").apply(True)
    print(f"SSL Cert True: T={ssl_judgment.T:.3f}")
    
    print()
    
    return registry


def fusion_with_mappers_example():
    """
    Fusion with Mappers Example
    ===========================
    
    Demonstrates how to combine multiple mappers using fusion operators.
    """
    print("🔀 Fusion with Mappers Example")
    print("=" * 50)
    
    # Create multiple mappers for different risk factors
    health_mapper = NumericalMapper(
        id="health-factor",
        falsity_point=1.0,
        indeterminacy_point=1.5,
        truth_point=3.0
    )
    
    credit_mapper = NumericalMapper(
        id="credit-score",
        falsity_point=300,
        indeterminacy_point=650,
        truth_point=850
    )
    
    kyc_mapper = CategoricalMapper(
        id="kyc-status",
        mappings={
            "VERIFIED": (1.0, 0.0, 0.0),
            "PENDING": (0.5, 0.5, 0.0),
            "REJECTED": (0.0, 0.0, 1.0)
        }
    )
    
    # Generate judgments from different sources
    health_judgment = health_mapper.apply(1.8)      # Moderate risk
    credit_judgment = credit_mapper.apply(720)      # Good credit
    kyc_judgment = kyc_mapper.apply("VERIFIED")     # Verified identity
    
    print("Individual judgments:")
    print(f"Health Factor: T={health_judgment.T:.3f}, I={health_judgment.I:.3f}, F={health_judgment.F:.3f}")
    print(f"Credit Score:  T={credit_judgment.T:.3f}, I={credit_judgment.I:.3f}, F={credit_judgment.F:.3f}")
    print(f"KYC Status:    T={kyc_judgment.T:.3f}, I={kyc_judgment.I:.3f}, F={kyc_judgment.F:.3f}")
    print()
    
    # Fuse judgments using conflict-aware weighted average
    # Higher weight for credit score, lower for health factor
    weights = [0.3, 0.5, 0.2]  # health, credit, kyc
    
    fused_judgment = conflict_aware_weighted_average(
        [health_judgment, credit_judgment, kyc_judgment],
        weights
    )
    
    print("Fused judgment (weighted by importance):")
    print(f"Final Result:  T={fused_judgment.T:.3f}, I={fused_judgment.I:.3f}, F={fused_judgment.F:.3f}")
    
    # Interpret the final result
    if fused_judgment.T > 0.7:
        decision = "🟢 APPROVE"
    elif fused_judgment.I > 0.5:
        decision = "🟡 REVIEW"
    else:
        decision = "🔴 REJECT"
    
    print(f"Decision: {decision}")
    print()
    
    return fused_judgment


def main():
    """Run all examples."""
    print("🚀 OTP Mapper Examples")
    print("=" * 80)
    print()
    
    # Run individual examples
    defi_health_factor_example()
    kyc_status_example()
    iot_temperature_example()
    ssl_certificate_example()
    credit_score_example()
    registry_example()
    fusion_with_mappers_example()
    
    print("✅ All examples completed successfully!")
    print()
    print("The OTP Mapper system provides a powerful and flexible way to")
    print("transform any type of data into rich, contextual Neutrosophic")
    print("Judgments that can be combined using fusion operators for")
    print("sophisticated decision-making systems.")


if __name__ == "__main__":
    main()
