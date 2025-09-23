#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the judgment_id module - Judgment ID System for Circle of Trust
"""

import unittest
from otp.judgment import NeutrosophicJudgment
from otp.judgment_id import (
    generate_judgment_id, ensure_judgment_id, create_outcome_judgment,
    OutcomeJudgment, OutcomeType
)


class TestJudgmentIDSystem(unittest.TestCase):
    """Test cases for the Judgment ID System"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_judgment = NeutrosophicJudgment(
            T=0.8, I=0.2, F=0.0,
            provenance_chain=[{"source_id": "test-sensor", "timestamp": "2023-01-01T00:00:00Z"}]
        )

    def test_generate_judgment_id_basic(self):
        """Test basic judgment ID generation"""
        judgment_id = generate_judgment_id(self.test_judgment)
        
        # Should be a valid SHA-256 hash (64 hex characters)
        self.assertEqual(len(judgment_id), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in judgment_id))

    def test_generate_judgment_id_deterministic(self):
        """Test that identical judgments generate identical IDs"""
        judgment1 = NeutrosophicJudgment(
            T=0.8, I=0.2, F=0.0,
            provenance_chain=[{"source_id": "sensor1", "timestamp": "2023-01-01T00:00:00Z"}]
        )
        
        judgment2 = NeutrosophicJudgment(
            T=0.8, I=0.2, F=0.0,
            provenance_chain=[{"source_id": "sensor1", "timestamp": "2023-01-01T00:00:00Z"}]
        )
        
        id1 = generate_judgment_id(judgment1)
        id2 = generate_judgment_id(judgment2)
        
        # Should be identical for identical judgments
        self.assertEqual(id1, id2)

    def test_generate_judgment_id_different_judgments(self):
        """Test that different judgments generate different IDs"""
        judgment1 = NeutrosophicJudgment(
            T=0.8, I=0.2, F=0.0,
            provenance_chain=[{"source_id": "sensor1", "timestamp": "2023-01-01T00:00:00Z"}]
        )
        
        judgment2 = NeutrosophicJudgment(
            T=0.7, I=0.3, F=0.0,
            provenance_chain=[{"source_id": "sensor1", "timestamp": "2023-01-01T00:00:00Z"}]
        )
        
        id1 = generate_judgment_id(judgment1)
        id2 = generate_judgment_id(judgment2)
        
        # Should be different for different judgments
        self.assertNotEqual(id1, id2)

    def test_ensure_judgment_id_new(self):
        """Test ensuring judgment ID for a judgment without one"""
        judgment = NeutrosophicJudgment(
            T=0.8, I=0.2, F=0.0,
            provenance_chain=[{"source_id": "sensor1", "timestamp": "2023-01-01T00:00:00Z"}]
        )
        
        # Should not have judgment_id initially
        has_judgment_id = any(entry.get("judgment_id") for entry in judgment.provenance_chain)
        self.assertFalse(has_judgment_id)
        
        judgment_with_id = ensure_judgment_id(judgment)
        
        # Should have judgment_id after ensuring
        has_judgment_id = any(entry.get("judgment_id") for entry in judgment_with_id.provenance_chain)
        self.assertTrue(has_judgment_id)
        
        # Extract the judgment_id
        judgment_id = None
        for entry in judgment_with_id.provenance_chain:
            if entry.get("judgment_id"):
                judgment_id = entry["judgment_id"]
                break
        
        self.assertIsNotNone(judgment_id)
        self.assertEqual(len(judgment_id), 64)

    def test_ensure_judgment_id_existing(self):
        """Test ensuring judgment ID for a judgment that already has one"""
        # Create judgment with existing judgment_id
        judgment_with_existing_id = NeutrosophicJudgment(
            T=0.8, I=0.2, F=0.0,
            provenance_chain=[
                {"source_id": "sensor1", "timestamp": "2023-01-01T00:00:00Z"},
                {"source_id": "otp-judgment-id-generator", "timestamp": "2023-01-01T00:00:01Z", "judgment_id": "existing_id"}
            ]
        )
        
        result = ensure_judgment_id(judgment_with_existing_id)
        
        # Should return the same judgment without modification
        self.assertEqual(result, judgment_with_existing_id)

    def test_outcome_judgment_creation(self):
        """Test OutcomeJudgment creation"""
        outcome = create_outcome_judgment(
            links_to_judgment_id="original_judgment_id",
            T=1.0, I=0.0, F=0.0,
            outcome_type=OutcomeType.SUCCESS,
            oracle_source="test-oracle"
        )
        
        self.assertEqual(outcome.links_to_judgment_id, "original_judgment_id")
        self.assertEqual(outcome.T, 1.0)
        self.assertEqual(outcome.I, 0.0)
        self.assertEqual(outcome.F, 0.0)
        self.assertEqual(outcome.outcome_type, OutcomeType.SUCCESS)
        self.assertEqual(outcome.oracle_source, "test-oracle")
        self.assertIsNotNone(outcome.judgment_id)
        self.assertEqual(len(outcome.judgment_id), 64)

    def test_outcome_judgment_validation(self):
        """Test OutcomeJudgment validation"""
        # Test invalid T value
        with self.assertRaises(ValueError):
            create_outcome_judgment(
                links_to_judgment_id="original_judgment_id",
                T=1.5, I=0.0, F=0.0,  # Invalid T > 1.0
                outcome_type=OutcomeType.SUCCESS,
                oracle_source="test-oracle"
            )

    def test_outcome_judgment_to_neutrosophic_judgment(self):
        """Test converting OutcomeJudgment to NeutrosophicJudgment"""
        outcome = create_outcome_judgment(
            links_to_judgment_id="original_judgment_id",
            T=1.0, I=0.0, F=0.0,
            outcome_type=OutcomeType.SUCCESS,
            oracle_source="test-oracle"
        )
        
        neutrosophic = outcome.to_neutrosophic_judgment()
        
        self.assertEqual(neutrosophic.T, 1.0)
        self.assertEqual(neutrosophic.I, 0.0)
        self.assertEqual(neutrosophic.F, 0.0)
        self.assertEqual(neutrosophic.provenance_chain, outcome.provenance_chain)

    def test_outcome_type_enum(self):
        """Test OutcomeType enum values"""
        self.assertEqual(OutcomeType.SUCCESS.value, "success")
        self.assertEqual(OutcomeType.FAILURE.value, "failure")
        self.assertEqual(OutcomeType.PARTIAL.value, "partial")


class TestFusionOperatorsWithJudgmentID(unittest.TestCase):
    """Test fusion operators with automatic Judgment ID generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.judgment1 = NeutrosophicJudgment(
            T=0.8, I=0.2, F=0.0,
            provenance_chain=[{"source_id": "sensor1", "timestamp": "2023-01-01T00:00:00Z"}]
        )
        self.judgment2 = NeutrosophicJudgment(
            T=0.6, I=0.3, F=0.1,
            provenance_chain=[{"source_id": "sensor2", "timestamp": "2023-01-01T00:00:01Z"}]
        )

    def test_conflict_aware_weighted_average_generates_judgment_id(self):
        """Test that conflict_aware_weighted_average generates judgment_id"""
        from otp import conflict_aware_weighted_average
        
        fused = conflict_aware_weighted_average([self.judgment1, self.judgment2], [0.6, 0.4])
        
        # Should have judgment_id in provenance chain
        has_judgment_id = any(entry.get("judgment_id") for entry in fused.provenance_chain)
        self.assertTrue(has_judgment_id)
        
        # Extract judgment_id
        judgment_id = None
        for entry in fused.provenance_chain:
            if entry.get("judgment_id"):
                judgment_id = entry["judgment_id"]
                break
        
        self.assertIsNotNone(judgment_id)
        self.assertEqual(len(judgment_id), 64)

    def test_optimistic_fusion_generates_judgment_id(self):
        """Test that optimistic_fusion generates judgment_id"""
        from otp import optimistic_fusion
        
        fused = optimistic_fusion([self.judgment1, self.judgment2])
        
        # Should have judgment_id in provenance chain
        has_judgment_id = any(entry.get("judgment_id") for entry in fused.provenance_chain)
        self.assertTrue(has_judgment_id)

    def test_pessimistic_fusion_generates_judgment_id(self):
        """Test that pessimistic_fusion generates judgment_id"""
        from otp import pessimistic_fusion
        
        fused = pessimistic_fusion([self.judgment1, self.judgment2])
        
        # Should have judgment_id in provenance chain
        has_judgment_id = any(entry.get("judgment_id") for entry in fused.provenance_chain)
        self.assertTrue(has_judgment_id)


if __name__ == "__main__":
    unittest.main()
