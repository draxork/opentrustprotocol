"""
Tests for Numerical Mapper
==========================

Comprehensive test suite for the NumericalMapper implementation,
covering all edge cases, mathematical correctness, and specification compliance.
"""

import pytest
import math
from unittest.mock import patch

from otp.mapper import NumericalMapper, MapperError, InputError, ValidationError
from otp.judgment import NeutrosophicJudgment


class TestNumericalMapper:
    """Test suite for NumericalMapper class."""
    
    def test_basic_initialization(self):
        """Test basic mapper initialization."""
        mapper = NumericalMapper(
            id="test-mapper",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        assert mapper.id == "test-mapper"
        assert mapper.mapper_type.value == "numerical"
        assert mapper.parameters.falsity_point == 1.0
        assert mapper.parameters.indeterminacy_point == 2.0
        assert mapper.parameters.truth_point == 3.0
        assert mapper.parameters.clamp_to_range is True
    
    def test_initialization_with_metadata(self):
        """Test initialization with custom metadata."""
        metadata = {"domain": "defi", "version": "1.0"}
        mapper = NumericalMapper(
            id="test-mapper",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0,
            metadata=metadata
        )
        
        assert mapper.metadata == metadata
    
    def test_initialization_validation_errors(self):
        """Test initialization validation."""
        # Invalid ID
        with pytest.raises(ValidationError, match="Mapper id must be a non-empty string"):
            NumericalMapper(id="", falsity_point=1.0, indeterminacy_point=2.0, truth_point=3.0)
        
        # All points identical
        with pytest.raises(ValidationError, match="All reference points cannot be identical"):
            NumericalMapper(
                id="test", 
                falsity_point=2.0, 
                indeterminacy_point=2.0, 
                truth_point=2.0
            )
        
        # Indeterminacy point outside range
        with pytest.raises(ValidationError, match="indeterminacy_point.*must be between"):
            NumericalMapper(
                id="test", 
                falsity_point=1.0, 
                indeterminacy_point=5.0, 
                truth_point=3.0
            )
    
    def test_falsity_to_indeterminacy_interpolation(self):
        """Test interpolation in falsity -> indeterminacy zone."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        # Exact falsity point
        judgment = mapper.apply(1.0)
        assert judgment.T == 0.0
        assert judgment.I == 0.0
        assert judgment.F == 1.0
        
        # Exact indeterminacy point
        judgment = mapper.apply(2.0)
        assert judgment.T == 0.0
        assert judgment.I == 1.0
        assert judgment.F == 0.0
        
        # Midpoint (50% falsity, 50% indeterminacy)
        judgment = mapper.apply(1.5)
        assert abs(judgment.T - 0.0) < 1e-10
        assert abs(judgment.I - 0.5) < 1e-10
        assert abs(judgment.F - 0.5) < 1e-10
    
    def test_indeterminacy_to_truth_interpolation(self):
        """Test interpolation in indeterminacy -> truth zone."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        # Exact indeterminacy point
        judgment = mapper.apply(2.0)
        assert judgment.T == 0.0
        assert judgment.I == 1.0
        assert judgment.F == 0.0
        
        # Exact truth point
        judgment = mapper.apply(3.0)
        assert judgment.T == 1.0
        assert judgment.I == 0.0
        assert judgment.F == 0.0
        
        # Midpoint (50% indeterminacy, 50% truth)
        judgment = mapper.apply(2.5)
        assert abs(judgment.T - 0.5) < 1e-10
        assert abs(judgment.I - 0.5) < 1e-10
        assert abs(judgment.F - 0.0) < 1e-10
    
    def test_reverse_order_points(self):
        """Test mapper with points in reverse order."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=3.0,  # Higher values are bad
            indeterminacy_point=2.0,
            truth_point=1.0  # Lower values are good
        )
        
        # Exact truth point (lowest value)
        judgment = mapper.apply(1.0)
        assert judgment.T == 1.0
        assert judgment.I == 0.0
        assert judgment.F == 0.0
        
        # Exact falsity point (highest value)
        judgment = mapper.apply(3.0)
        assert judgment.T == 0.0
        assert judgment.I == 0.0
        assert judgment.F == 1.0
        
        # Midpoint in truth-indeterminacy zone
        judgment = mapper.apply(1.5)
        assert abs(judgment.T - 0.5) < 1e-10
        assert abs(judgment.I - 0.5) < 1e-10
        assert abs(judgment.F - 0.0) < 1e-10
    
    def test_clamp_to_range_enabled(self):
        """Test clamping behavior when enabled."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0,
            clamp_to_range=True
        )
        
        # Input below range should be clamped to falsity point
        judgment = mapper.apply(0.5)
        assert judgment.T == 0.0
        assert judgment.I == 0.0
        assert judgment.F == 1.0
        
        # Input above range should be clamped to truth point
        judgment = mapper.apply(4.0)
        assert judgment.T == 1.0
        assert judgment.I == 0.0
        assert judgment.F == 0.0
    
    def test_clamp_to_range_disabled(self):
        """Test behavior when clamping is disabled."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0,
            clamp_to_range=False
        )
        
        # Input below range should raise error
        with pytest.raises(InputError, match="Input value.*is outside valid range"):
            mapper.apply(0.5)
        
        # Input above range should raise error
        with pytest.raises(InputError, match="Input value.*is outside valid range"):
            mapper.apply(4.0)
    
    def test_conservation_constraint(self):
        """Test that conservation constraint is always satisfied."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        # Test various input values
        test_values = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]
        
        for value in test_values:
            judgment = mapper.apply(value)
            total = judgment.T + judgment.I + judgment.F
            assert abs(total - 1.0) < 1e-10, f"Conservation constraint violated for input {value}"
    
    def test_provenance_chain(self):
        """Test that provenance chain is correctly created."""
        mapper = NumericalMapper(
            id="test-mapper",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        judgment = mapper.apply(2.5)
        
        assert len(judgment.provenance_chain) == 1
        provenance = judgment.provenance_chain[0]
        
        assert provenance.source_id == "test-mapper"
        assert provenance.description == "Mapper transformation using test-mapper"
        assert provenance.metadata["mapper_type"] == "numerical"
        assert provenance.metadata["original_input"]["value"] == "2.5"
        assert provenance.metadata["original_input"]["type"] == "numerical"
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=1.0,
            indeterminacy_point=1.5,
            truth_point=2.0
        )
        
        # Very small differences between points
        judgment = mapper.apply(1.25)
        total = judgment.T + judgment.I + judgment.F
        assert abs(total - 1.0) < 1e-10
        
        # Test with floating point precision
        judgment = mapper.apply(1.4999999999999999)
        assert abs(judgment.I - 1.0) < 1e-10
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        # Non-numeric input
        with pytest.raises(InputError, match="Input must be a number"):
            mapper.apply("invalid")
        
        # None input
        with pytest.raises(InputError, match="Input must be a number"):
            mapper.apply(None)
        
        # NaN input
        with pytest.raises(InputError, match="Input cannot be NaN or infinite"):
            mapper.apply(float('nan'))
        
        # Infinite input
        with pytest.raises(InputError, match="Input cannot be NaN or infinite"):
            mapper.apply(float('inf'))
    
    def test_get_valid_range(self):
        """Test getting valid input range."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=3.0,
            indeterminacy_point=2.0,
            truth_point=1.0
        )
        
        min_val, max_val = mapper.get_valid_range()
        assert min_val == 1.0
        assert max_val == 3.0
    
    def test_is_in_valid_range(self):
        """Test checking if value is in valid range."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        assert mapper.is_in_valid_range(1.5) is True
        assert mapper.is_in_valid_range(2.5) is True
        assert mapper.is_in_valid_range(0.5) is False
        assert mapper.is_in_valid_range(3.5) is False
        assert mapper.is_in_valid_range(1.0) is True
        assert mapper.is_in_valid_range(3.0) is True
    
    def test_get_reference_points(self):
        """Test getting reference points."""
        mapper = NumericalMapper(
            id="test",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        points = mapper.get_reference_points()
        assert points["falsity_point"] == 1.0
        assert points["indeterminacy_point"] == 2.0
        assert points["truth_point"] == 3.0
    
    def test_string_representations(self):
        """Test string representations."""
        mapper = NumericalMapper(
            id="test-mapper",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0
        )
        
        str_repr = str(mapper)
        assert "test-mapper" in str_repr
        assert "falsity=1.0" in str_repr
        assert "indeterminacy=2.0" in str_repr
        assert "truth=3.0" in str_repr
        
        repr_str = repr(mapper)
        assert "test-mapper" in repr_str
        assert "falsity_point=1.0" in repr_str
    
    def test_defi_health_factor_example(self):
        """Test real-world DeFi health factor example."""
        mapper = NumericalMapper(
            id="defi-health-factor",
            falsity_point=1.0,    # Liquidation imminent
            indeterminacy_point=1.5,  # Risk zone
            truth_point=3.0       # Safe position
        )
        
        # Test case from documentation
        judgment = mapper.apply(1.25)
        assert abs(judgment.T - 0.0) < 1e-10
        assert abs(judgment.I - 0.5) < 1e-10
        assert abs(judgment.F - 0.5) < 1e-10
        
        judgment = mapper.apply(2.25)
        assert abs(judgment.T - 0.5) < 1e-10
        assert abs(judgment.I - 0.5) < 1e-10
        assert abs(judgment.F - 0.0) < 1e-10
    
    def test_credit_score_example(self):
        """Test credit score example."""
        mapper = NumericalMapper(
            id="credit-score",
            falsity_point=300,    # Poor credit
            indeterminacy_point=650,  # Average credit
            truth_point=850      # Excellent credit
        )
        
        # Poor credit
        judgment = mapper.apply(400)
        assert judgment.F > judgment.I > judgment.T
        
        # Excellent credit
        judgment = mapper.apply(800)
        assert judgment.T > judgment.I > judgment.F
        
        # Average credit
        judgment = mapper.apply(650)
        assert judgment.I == 1.0
        assert judgment.T == 0.0
        assert judgment.F == 0.0
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        original_mapper = NumericalMapper(
            id="test-mapper",
            falsity_point=1.0,
            indeterminacy_point=2.0,
            truth_point=3.0,
            clamp_to_range=False,
            metadata={"domain": "test"}
        )
        
        # Serialize to JSON
        json_str = original_mapper.to_json()
        assert '"version": "2.0"' in json_str
        assert '"id": "test-mapper"' in json_str
        assert '"type": "numerical"' in json_str
        assert '"falsity_point": 1.0' in json_str
        
        # Deserialize from JSON
        from otp.mapper.types import Mapper
        restored_mapper = Mapper.from_json(json_str)
        
        assert restored_mapper.id == original_mapper.id
        assert restored_mapper.mapper_type == original_mapper.mapper_type
        assert restored_mapper.parameters.falsity_point == original_mapper.parameters.falsity_point
        assert restored_mapper.parameters.indeterminacy_point == original_mapper.parameters.indeterminacy_point
        assert restored_mapper.parameters.truth_point == original_mapper.parameters.truth_point
        assert restored_mapper.metadata == original_mapper.metadata


if __name__ == "__main__":
    pytest.main([__file__])


