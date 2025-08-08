#!/usr/bin/env python3
"""
Test pattern criterion applied to single trajectories.
"""

import pytest

from tanat.criterion.mixin.pattern.settings import PatternCriterion
from tanat.criterion.mixin.pattern.exception import InvalidColumnPatternError
from tanat.criterion.base.exception import InvalidCriterionError


class TestPatternCriterion:
    """
    Test pattern criterion applied to single trajectory.
    """

    @pytest.fixture
    def single_trajectory(self, trajectory_pool):
        """
        Get a single trajectory for testing.
        """
        return trajectory_pool[3].copy()

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_single_trajectory(
        self, single_trajectory, sequence_name, pattern, snapshot
    ):
        """
        Test filtering a single trajectory with pattern criterion (inplace=False).
        """
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        # Filter the trajectory
        filtered_trajectory = single_trajectory.filter(
            criterion=pattern_criterion,
            sequence_name=sequence_name,
            inplace=False,
        )

        # Check filtered sequence data
        filtered_sequence_data = filtered_trajectory[sequence_name].sequence_data
        snapshot.assert_match(filtered_sequence_data.to_csv())

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_single_trajectory_inplace(
        self, single_trajectory, sequence_name, pattern, snapshot
    ):
        """
        Test filtering a single trajectory with pattern criterion (inplace=True).
        """
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        # Filter the trajectory inplace
        result = single_trajectory.filter(
            criterion=pattern_criterion,
            sequence_name=sequence_name,
            inplace=True,
        )

        # Inplace should return None
        assert result is None

        # Check that original trajectory was modified
        modified_sequence_data = single_trajectory[sequence_name].sequence_data
        snapshot.assert_match(modified_sequence_data.to_csv())

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_single_trajectory_consistency(
        self, single_trajectory, sequence_name, pattern
    ):
        """
        Test consistency between inplace=True and inplace=False filtering.
        """
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        # Non-inplace filtering
        filtered_trajectory = single_trajectory.filter(
            criterion=pattern_criterion,
            sequence_name=sequence_name,
            inplace=False,
        )
        non_inplace_result = filtered_trajectory[sequence_name].sequence_data

        # Inplace filtering
        trajectory_copy = single_trajectory.copy()
        trajectory_copy.filter(
            criterion=pattern_criterion,
            sequence_name=sequence_name,
            inplace=True,
        )
        inplace_result = trajectory_copy[sequence_name].sequence_data

        # Test consistency
        assert non_inplace_result.equals(inplace_result)

    def test_filter_state_sequence_raises_error(self, single_trajectory):
        """
        Test that filtering state sequences raises NotImplementedError.
        """
        state_criterion = PatternCriterion(
            pattern={"health_state": "CONVALESCENCE"}, contains=True
        )

        # Should raise NotImplementedError for state sequences
        with pytest.raises(NotImplementedError):
            single_trajectory.filter(
                criterion=state_criterion,
                sequence_name="state",
                inplace=False,
            )

        # Test inplace version as well
        trajectory_copy = single_trajectory.copy()
        with pytest.raises(NotImplementedError):
            trajectory_copy.filter(
                criterion=state_criterion,
                sequence_name="state",
                inplace=True,
            )

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": ["EMERGENCY", "EMERGENCY", "EMERGENCY"]}),
            ("interval", {"medication": ["ANTIBIOTIC", "PAIN_RELIEVER"]}),
        ],
    )
    def test_filter_single_trajectory_multiple_patterns(
        self, single_trajectory, sequence_name, pattern, snapshot
    ):
        """
        Test filtering single trajectory with multiple patterns.
        """
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        filtered_trajectory = single_trajectory.filter(
            criterion=pattern_criterion,
            sequence_name=sequence_name,
            inplace=False,
        )
        filtered_sequence_data = filtered_trajectory[sequence_name].sequence_data
        snapshot.assert_match(filtered_sequence_data.to_csv())

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "NONEXISTENT_EVENT"}),
            ("interval", {"medication": "NONEXISTENT_MEDICATION"}),
        ],
    )
    def test_filter_single_trajectory_no_matching_pattern(
        self, single_trajectory, sequence_name, pattern
    ):
        """
        Test filtering single trajectory with non-matching pattern criterion.
        Should return trajectory with empty sequence data.
        """
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        filtered_trajectory = single_trajectory.filter(
            criterion=pattern_criterion,
            sequence_name=sequence_name,
            inplace=False,
        )

        # Sequence data should be empty
        sequence = filtered_trajectory.sequences.get(sequence_name, None)
        assert sequence is None

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"NONEXISTENT_COLUMN": "EMERGENCY"}),
            ("interval", {"NONEXISTENT_COLUMN": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_single_trajectory_invalid_column(
        self, single_trajectory, sequence_name, pattern
    ):
        """
        Test filtering single trajectory with invalid column name.
        Should raise InvalidColumnPatternError.
        """
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        # Test inplace=False
        with pytest.raises(InvalidColumnPatternError):
            single_trajectory.filter(
                criterion=pattern_criterion,
                sequence_name=sequence_name,
                inplace=False,
            )

        # Test inplace=True
        trajectory_copy = single_trajectory.copy()
        with pytest.raises(InvalidColumnPatternError):
            trajectory_copy.filter(
                criterion=pattern_criterion,
                sequence_name=sequence_name,
                inplace=True,
            )

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_single_trajectory_via_dict_criterion(
        self, single_trajectory, sequence_name, pattern
    ):
        """
        Test filtering single trajectory using criterion defined as dictionary.
        """
        # Dictionary criterion
        dict_criterion = {"pattern": pattern, "contains": True}

        # Filter with dict criterion
        filtered_trajectory = single_trajectory.filter(
            criterion=dict_criterion,
            criterion_type="pattern",
            sequence_name=sequence_name,
            inplace=False,
        )

        # Filter with PatternCriterion object for comparison
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)
        filtered_trajectory_obj = single_trajectory.filter(
            criterion=pattern_criterion,
            sequence_name=sequence_name,
            inplace=False,
        )

        # Results should be identical
        dict_result = filtered_trajectory[sequence_name].sequence_data
        obj_result = filtered_trajectory_obj[sequence_name].sequence_data
        assert dict_result.equals(obj_result)

    def test_filter_preserves_non_targetted_sequence_data(self, single_trajectory):
        """
        Test that filtering preserves non-targetted sequence data.
        """
        pattern_criterion = PatternCriterion(
            pattern={"event_type": "EMERGENCY"}, contains=True
        )

        filtered_trajectory = single_trajectory.filter(
            criterion=pattern_criterion, sequence_name="event", inplace=False
        )

        # Check that other sequences are preserved
        for sequence_name in single_trajectory.sequences:
            if sequence_name != "event":
                original_sequence = single_trajectory[sequence_name].sequence_data
                filtered_sequence = filtered_trajectory[sequence_name].sequence_data
                assert original_sequence.equals(filtered_sequence)

    def test_match_method_raises_error(self, single_trajectory):
        """
        Test match method raises an error.
        Match method is only applicable for 'trajectory' compatible criterion.
        """
        criterion = PatternCriterion(pattern={"event_type": "EMERGENCY"}, contains=True)

        with pytest.raises(InvalidCriterionError):
            single_trajectory.match(criterion=criterion)

        ## -- from dict
        with pytest.raises(InvalidCriterionError):
            single_trajectory.match(
                criterion={"pattern": {"event_type": "EMERGENCY"}, "contains": True},
                criterion_type="pattern",
            )
