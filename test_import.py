#!/usr/bin/env python3
"""
Test script to verify that all imports work correctly.
This script is used in CI/CD to ensure the package exports are correct.
"""

def test_imports():
    """Test that all required imports work correctly."""
    try:
        # Test basic import
        from otp import NeutrosophicJudgment
        print("✅ NeutrosophicJudgment import successful")
        
        # Test fusion function imports
        from otp import conflict_aware_weighted_average
        print("✅ conflict_aware_weighted_average import successful")
        
        from otp import optimistic_fusion
        print("✅ optimistic_fusion import successful")
        
        from otp import pessimistic_fusion
        print("✅ pessimistic_fusion import successful")
        
        # Test fuse module import
        from otp import fuse
        print("✅ fuse module import successful")
        
        # Test version
        from otp import __version__
        print(f"✅ Version: {__version__}")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)
