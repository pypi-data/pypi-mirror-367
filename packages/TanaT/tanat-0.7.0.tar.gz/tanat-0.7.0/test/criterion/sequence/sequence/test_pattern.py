#!/usr/bin/env python3
"""
Test pattern criterion applied to a single sequence.
"""

import pytest

from tanat.criterion.mixin.pattern.settings import PatternCriterion


class TestPatternCriterion:
    """
    Test the match method applied to individual sequence using pattern criterion.
    """

    @pytest.mark.parametrize(
        "pool_type,pattern,sequence_id,expected_result",
        [
            ("event", {"event_type": "EMERGENCY"}, 1, True),
            ("event", {"event_type": "FAKE_EVENT"}, 4, False),
            ("state", {"health_state": "HEALTHY"}, 1, True),
            ("state", {"health_state": "FAKE_STATE"}, 8, False),
            ("interval", {"medication": "ANTIBIOTIC"}, 4, True),
            ("interval", {"medication": "FAKE_MEDICATION"}, 6, False),
        ],
    )
    def test_match_with_pattern_criterion(
        self, sequence_pools, pool_type, pattern, sequence_id, expected_result
    ):
        """
        Test if a specific sequence matches pattern criterion.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        # Test with PatternCriterion object
        criterion = PatternCriterion(pattern=pattern)
        result = sequence.match(criterion)
        assert result == expected_result

        # Test with dictionary
        criterion_dict = {"pattern": pattern}
        result = sequence.match(criterion_dict, criterion_type="pattern")
        assert result == expected_result

    @pytest.mark.parametrize(
        "pool_type,pattern,sequence_id,expected_result",
        [
            ("event", {"event_type": ["EMERGENCY", "CONSULTATION"]}, 5, True),
            ("event", {"event_type": ["ROUTINE", "FAKE_EVENT"]}, 6, False),
            ("state", {"health_state": ["TREATMENT", "CONVALESCENCE"]}, 6, True),
            ("state", {"health_state": ["FAKE_STATE", "HEALTHY"]}, 4, False),
            (
                "interval",
                {"medication": ["ANTIBIOTIC", "PAIN_RELIEVER"]},
                3,
                True,
            ),
            ("interval", {"medication": ["FAKE_MEDICATION", "ANALGESIC"]}, 2, False),
        ],
    )
    def test_match_with_multiple_pattern_values(
        self, sequence_pools, pool_type, pattern, sequence_id, expected_result
    ):
        """
        Test if a specific sequence matches pattern criterion with multiple possible values.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        # Test with PatternCriterion object
        criterion = PatternCriterion(pattern=pattern, contains=True)
        result = sequence.match(criterion)
        assert result == expected_result

        # Test with dictionary
        criterion_dict = {"pattern": pattern, "contains": True}
        result = sequence.match(criterion_dict, criterion_type="pattern")
        assert result == expected_result

    @pytest.mark.parametrize(
        "pool_type,pattern,sequence_id,expected_result",
        [
            ("event", {"event_type": ["FAKE_EVENT", "CONSULTATION"]}, 2, True),
            ("event", {"event_type": ["EMERGENCY", "CONSULTATION"]}, 5, False),
            ("state", {"health_state": ["HEALTHY", "FAKE_STATE"]}, 9, True),
            ("state", {"health_state": ["TREATMENT", "CONVALESCENCE"]}, 6, False),
            ("interval", {"medication": ["ANTIBIOTIC", "FAKE_MEDICATION"]}, 3, True),
            ("interval", {"medication": ["ANTIBIOTIC", "PAIN_RELIEVER"]}, 3, False),
        ],
    )
    def test_match_with_not_contains_pattern(
        self, sequence_pools, pool_type, pattern, sequence_id, expected_result
    ):
        """
        Test if a specific sequence matches pattern criterion with contains=False.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        # Test with PatternCriterion object
        criterion = PatternCriterion(pattern=pattern, contains=False)
        result = sequence.match(criterion)
        assert result == expected_result

        # Test with dictionary
        criterion_dict = {"pattern": pattern, "contains": False}
        result = sequence.match(criterion_dict, criterion_type="pattern")
        assert result == expected_result

    @pytest.mark.parametrize(
        "pool_type,base_pattern,override_pattern",
        [
            ("event", {"event_type": "FAKE_EVENT"}, {"event_type": "EMERGENCY"}),
            ("state", {"health_state": "FAKE_STATE"}, {"health_state": "REMISSION"}),
            (
                "interval",
                {"medication": "FAKE_MEDICATION"},
                {"medication": "ANTIBIOTIC"},
            ),
        ],
    )
    def test_match_with_criterion_kwargs_override(
        self, sequence_pools, pool_type, base_pattern, override_pattern
    ):
        """
        Test if kwargs can override criterion parameters.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[4]

        # Create base criterion
        base_criterion = PatternCriterion(pattern=base_pattern)

        # Check that sequence doesn't match base criterion
        assert not sequence.match(base_criterion)

        # Override the pattern with a parameter that should match
        result = sequence.match(base_criterion, pattern=override_pattern)
        assert result

        # Do the same with a dictionary
        base_dict = {"pattern": base_pattern}
        result = sequence.match(
            base_dict, criterion_type="pattern", pattern=override_pattern
        )
        assert result

    @pytest.mark.parametrize(
        "pool_type,sequence_id,criterion_kwargs",
        [
            ("event", 1, {"pattern": {"event_type": "EMERGENCY"}}),
            ("interval", 4, {"pattern": {"medication": "ANTIBIOTIC"}}),
        ],
    )
    def test_filter_entities_inplace(
        self, sequence_pools, pool_type, sequence_id, criterion_kwargs, snapshot
    ):
        """
        Filter at entity level.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]
        criterion = PatternCriterion(**criterion_kwargs)
        result = sequence.filter(criterion, inplace=True)

        assert result is None
        snapshot.assert_match(sequence.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,sequence_id,criterion_kwargs",
        [
            ("event", 1, {"pattern": {"event_type": "EMERGENCY"}}),
            ("interval", 4, {"pattern": {"medication": "ANTIBIOTIC"}}),
        ],
    )
    def test_filter_entities_non_inplace(
        self, sequence_pools, pool_type, sequence_id, criterion_kwargs, snapshot
    ):
        """
        Filter at entity level with non-inplace.
        """
        pool = sequence_pools[pool_type]
        sequence_copy = pool[sequence_id].copy()
        criterion = PatternCriterion(**criterion_kwargs)
        sequence = sequence_copy.filter(criterion, inplace=False)
        snapshot.assert_match(sequence.sequence_data.to_csv())

    def test_filter_entities_on_state_sequence_raises_not_implemented_error(
        self, sequence_pools
    ):
        """
        Filter entities should raise a NotImplementedError.
        """
        state_pool = sequence_pools["state"]
        sequence = state_pool[1]
        criterion_kwargs = {"pattern": {"FAKE_COL": "dummy_pattern"}}
        criterion = PatternCriterion(**criterion_kwargs)

        with pytest.raises(NotImplementedError):
            sequence.filter(criterion)

        ## -- from dict
        with pytest.raises(NotImplementedError):
            sequence.filter(criterion_kwargs, criterion_type="pattern")
