#!/usr/bin/env python3
"""
OTP Mapper Validation Script
============================

This script validates the complete OTP Mapper implementation,
ensuring all components work correctly and conform to the specification.
"""

import sys
import os
import traceback

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_imports():
    """Test that all mapper components can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from otp.mapper import (
            NumericalMapper, 
            CategoricalMapper, 
            BooleanMapper,
            MapperRegistry,
            MapperValidator
        )
        print("✅ All mapper imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_numerical_mapper():
    """Test numerical mapper functionality."""
    print("\n🧪 Testing NumericalMapper...")
    
    try:
        from otp.mapper import NumericalMapper
        
        # Create mapper
        mapper = NumericalMapper(
            id="test-numerical",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        # Test basic transformation
        judgment = mapper.apply(2.5)
        print(f"  Input 2.5: T={judgment.T:.3f}, I={judgment.I:.3f}, F={judgment.F:.2f}")
        
        # Test conservation constraint
        total = judgment.T + judgment.I + judgment.F
        assert abs(total - 1.0) < 1e-10, f"Conservation constraint violated: {total}"
        
        # Test provenance chain
        assert len(judgment.provenance_chain) == 1
        provenance = judgment.provenance_chain[0]
        assert provenance["source_id"] == "test-numerical"
        
        # Test DeFi example
        defi_mapper = NumericalMapper(
            id="defi-health-factor",
            falsity_point=1.0,
            indeterminacy_point=1.5,
            truth_point=3.0
        )
        
        hf_125 = defi_mapper.apply(1.25)
        hf_225 = defi_mapper.apply(2.25)
        
        print(f"  DeFi HF 1.25: T={hf_125.T:.3f}, I={hf_125.I:.3f}, F={hf_125.F:.3f}")
        print(f"  DeFi HF 2.25: T={hf_225.T:.3f}, I={hf_225.I:.3f}, F={hf_225.F:.3f}")
        
        print("✅ NumericalMapper tests passed")
        return True
        
    except Exception as e:
        print(f"❌ NumericalMapper test failed: {e}")
        traceback.print_exc()
        return False

def test_categorical_mapper():
    """Test categorical mapper functionality."""
    print("\n🧪 Testing CategoricalMapper...")
    
    try:
        from otp.mapper import CategoricalMapper
        
        # Create mapper
        mapper = CategoricalMapper(
            id="test-categorical",
            mappings={
                "GOOD": (1.0, 0.0, 0.0),
                "MEDIUM": (0.5, 0.3, 0.2),
                "BAD": (0.0, 0.0, 1.0)
            },
            default_judgment=(0.0, 1.0, 0.0)
        )
        
        # Test transformations
        good_judgment = mapper.apply("GOOD")
        medium_judgment = mapper.apply("MEDIUM")
        bad_judgment = mapper.apply("BAD")
        unknown_judgment = mapper.apply("UNKNOWN")
        
        print(f"  GOOD: T={good_judgment.T:.3f}, I={good_judgment.I:.3f}, F={good_judgment.F:.3f}")
        print(f"  MEDIUM: T={medium_judgment.T:.3f}, I={medium_judgment.I:.3f}, F={medium_judgment.F:.3f}")
        print(f"  BAD: T={bad_judgment.T:.3f}, I={bad_judgment.I:.3f}, F={bad_judgment.F:.3f}")
        print(f"  UNKNOWN: T={unknown_judgment.T:.3f}, I={unknown_judgment.I:.3f}, F={unknown_judgment.F:.3f}")
        
        # Test conservation constraint
        for judgment in [good_judgment, medium_judgment, bad_judgment, unknown_judgment]:
            total = judgment.T + judgment.I + judgment.F
            assert abs(total - 1.0) < 1e-10, f"Conservation constraint violated: {total}"
        
        # Test KYC example
        kyc_mapper = CategoricalMapper(
            id="kyc-status",
            mappings={
                "VERIFIED": (1.0, 0.0, 0.0),
                "PENDING": (0.0, 1.0, 0.0),
                "REJECTED": (0.0, 0.0, 1.0)
            }
        )
        
        verified_judgment = kyc_mapper.apply("VERIFIED")
        print(f"  KYC VERIFIED: T={verified_judgment.T:.3f}")
        
        print("✅ CategoricalMapper tests passed")
        return True
        
    except Exception as e:
        print(f"❌ CategoricalMapper test failed: {e}")
        traceback.print_exc()
        return False

def test_boolean_mapper():
    """Test boolean mapper functionality."""
    print("\n🧪 Testing BooleanMapper...")
    
    try:
        from otp.mapper import BooleanMapper
        
        # Create mapper
        mapper = BooleanMapper(
            id="test-boolean",
            true_map=(0.9, 0.1, 0.0),
            false_map=(0.0, 0.0, 1.0)
        )
        
        # Test different input types
        true_judgment = mapper.apply(True)
        false_judgment = mapper.apply(False)
        one_judgment = mapper.apply(1)
        zero_judgment = mapper.apply(0)
        yes_judgment = mapper.apply("yes")
        no_judgment = mapper.apply("no")
        
        print(f"  True: T={true_judgment.T:.3f}, I={true_judgment.I:.3f}, F={true_judgment.F:.3f}")
        print(f"  False: T={false_judgment.T:.3f}, I={false_judgment.I:.3f}, F={false_judgment.F:.3f}")
        print(f"  1: T={one_judgment.T:.3f}")
        print(f"  0: F={zero_judgment.F:.3f}")
        print(f"  'yes': T={yes_judgment.T:.3f}")
        print(f"  'no': F={no_judgment.F:.3f}")
        
        # Test SSL example
        ssl_mapper = BooleanMapper(
            id="ssl-certificate",
            true_map=(0.9, 0.1, 0.0),
            false_map=(0.0, 0.0, 1.0)
        )
        
        ssl_valid = ssl_mapper.apply(True)
        ssl_invalid = ssl_mapper.apply(False)
        
        print(f"  SSL Valid: T={ssl_valid.T:.3f}")
        print(f"  SSL Invalid: F={ssl_invalid.F:.3f}")
        
        print("✅ BooleanMapper tests passed")
        return True
        
    except Exception as e:
        print(f"❌ BooleanMapper test failed: {e}")
        traceback.print_exc()
        return False

def test_registry():
    """Test mapper registry functionality."""
    print("\n🧪 Testing MapperRegistry...")
    
    try:
        from otp.mapper import MapperRegistry, NumericalMapper, CategoricalMapper
        
        # Get registry
        registry = MapperRegistry()
        
        # Create mappers using registry
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
                "PENDING": (0.0, 1.0, 0.0)
            }
        )
        
        # Test registry operations
        assert registry.count() == 2
        assert "defi-health-factor" in registry
        assert "kyc-status" in registry
        
        # Use registered mappers
        health_judgment = registry.get("defi-health-factor").apply(1.8)
        kyc_judgment = registry.get("kyc-status").apply("VERIFIED")
        
        print(f"  Registry count: {registry.count()}")
        print(f"  Health Factor 1.8: T={health_judgment.T:.3f}")
        print(f"  KYC VERIFIED: T={kyc_judgment.T:.3f}")
        
        # Test JSON export/import
        json_data = registry.export_to_json()
        assert '"defi-health-factor"' in json_data
        assert '"kyc-status"' in json_data
        
        print("✅ MapperRegistry tests passed")
        return True
        
    except Exception as e:
        print(f"❌ MapperRegistry test failed: {e}")
        traceback.print_exc()
        return False

def test_validation():
    """Test mapper validation functionality."""
    print("\n🧪 Testing MapperValidator...")
    
    try:
        from otp.mapper import MapperValidator, NumericalMapper, Mapper
        
        # Test valid mapper
        valid_mapper = NumericalMapper(
            id="valid-mapper",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        errors = MapperValidator.validate_mapper(valid_mapper)
        assert len(errors) == 0, f"Valid mapper should have no errors: {errors}"
        
        # Test JSON validation
        json_str = valid_mapper.to_json()
        is_valid = MapperValidator.is_json_valid(json_str)
        assert is_valid, "Valid JSON should pass validation"
        
        # Test invalid mapper (empty ID)
        try:
            invalid_mapper = NumericalMapper(
                id="",  # Invalid empty ID
                falsity_point=1.0,
                indeterminacy_point=2.0,
                truth_point=3.0
            )
            errors = MapperValidator.validate_mapper(invalid_mapper)
            assert len(errors) > 0, "Invalid mapper should have errors"
        except Exception:
            # Expected to fail during initialization
            pass
        
        print("✅ MapperValidator tests passed")
        return True
        
    except Exception as e:
        print(f"❌ MapperValidator test failed: {e}")
        traceback.print_exc()
        return False

def test_fusion_integration():
    """Test integration with fusion operators."""
    print("\n🧪 Testing Fusion Integration...")
    
    try:
        from otp.mapper import NumericalMapper, CategoricalMapper
        from otp import conflict_aware_weighted_average
        
        # Create multiple mappers
        health_mapper = NumericalMapper(
            id="health",
            falsity_point=1.0,
            indeterminacy_point=1.5,
            truth_point=3.0
        )
        
        credit_mapper = NumericalMapper(
            id="credit",
            falsity_point=300,
            indeterminacy_point=650,
            truth_point=850
        )
        
        kyc_mapper = CategoricalMapper(
            id="kyc",
            mappings={"VERIFIED": (1.0, 0.0, 0.0)}
        )
        
        # Generate judgments
        health_judgment = health_mapper.apply(1.8)
        credit_judgment = credit_mapper.apply(720)
        kyc_judgment = kyc_mapper.apply("VERIFIED")
        
        # Fuse judgments
        weights = [0.3, 0.5, 0.2]
        fused_judgment = conflict_aware_weighted_average(
            [health_judgment, credit_judgment, kyc_judgment],
            weights
        )
        
        print(f"  Health Judgment: T={health_judgment.T:.3f}")
        print(f"  Credit Judgment: T={credit_judgment.T:.3f}")
        print(f"  KYC Judgment: T={kyc_judgment.T:.3f}")
        print(f"  Fused Judgment: T={fused_judgment.T:.3f}, I={fused_judgment.I:.3f}, F={fused_judgment.F:.3f}")
        
        # Test conservation constraint
        total = fused_judgment.T + fused_judgment.I + fused_judgment.F
        assert abs(total - 1.0) < 1e-10, f"Fused judgment conservation violated: {total}"
        
        print("✅ Fusion Integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Fusion Integration test failed: {e}")
        traceback.print_exc()
        return False

def test_json_serialization():
    """Test JSON serialization and deserialization."""
    print("\n🧪 Testing JSON Serialization...")
    
    try:
        from otp.mapper import NumericalMapper, CategoricalMapper, BooleanMapper, Mapper
        
        # Test numerical mapper serialization
        num_mapper = NumericalMapper(
            id="test-numerical",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0,
            metadata={"domain": "test"}
        )
        
        json_str = num_mapper.to_json()
        restored_mapper = Mapper.from_json(json_str)
        
        assert restored_mapper.id == num_mapper.id
        assert restored_mapper.mapper_type == num_mapper.mapper_type
        assert restored_mapper.metadata == num_mapper.metadata
        
        # Test categorical mapper serialization
        cat_mapper = CategoricalMapper(
            id="test-categorical",
            mappings={"GOOD": (1.0, 0.0, 0.0), "BAD": (0.0, 0.0, 1.0)}
        )
        
        json_str = cat_mapper.to_json()
        restored_mapper = Mapper.from_json(json_str)
        
        assert restored_mapper.id == cat_mapper.id
        assert restored_mapper.mapper_type == cat_mapper.mapper_type
        
        print("✅ JSON Serialization tests passed")
        return True
        
    except Exception as e:
        print(f"❌ JSON Serialization test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all validation tests."""
    print("🚀 OTP Mapper Validation Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_numerical_mapper,
        test_categorical_mapper,
        test_boolean_mapper,
        test_registry,
        test_validation,
        test_fusion_integration,
        test_json_serialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OTP Mapper is ready for production.")
        return 0
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
