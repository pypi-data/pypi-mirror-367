#!/usr/bin/env python3
"""
Test length criterion applied to single trajectories.
"""

import pytest

from tanat.criterion.sequence.type.length.settings import LengthCriterion
from tanat.criterion.base.exception import InvalidCriterionError


class TestLengthCriterion:
    """
    Test length criterion applied to single trajectory.
    """

    @pytest.fixture
    def single_trajectory(self, trajectory_pool):
        """
        Get a single trajectory for testing.
        """
        return trajectory_pool[3].copy()

    @pytest.mark.parametrize(
        "sequence_name",
        [
            "event",
            "state",
            "interval",
        ],
    )
    def test_filter_single_trajectory_raises_error_with_length_criterion(
        self, single_trajectory, sequence_name
    ):
        """
        Test that filtering a single trajectory with LengthCriterion raises an error.
        Length criterion are only applicable at sequence level, not entity level.
        """
        length_criterion = LengthCriterion(gt=5)

        # Test inplace=False - should raise error
        with pytest.raises(InvalidCriterionError):
            single_trajectory.filter(
                criterion=length_criterion,
                sequence_name=sequence_name,
                inplace=False,
            )

        # Test inplace=True - should also raise error
        trajectory_copy = single_trajectory.copy()
        with pytest.raises(InvalidCriterionError):
            trajectory_copy.filter(
                criterion=length_criterion,
                sequence_name=sequence_name,
                inplace=True,
            )

    @pytest.mark.parametrize(
        "sequence_name",
        [
            "event",
            "interval",
        ],
    )
    def test_filter_single_trajectory_raises_error_with_dict_length_criterion(
        self, single_trajectory, sequence_name
    ):
        """
        Test that filtering a single trajectory with dict-based LengthCriterion raises an error.
        Length criterion are only applicable at sequence level, not entity level.
        """
        # Dictionary criterion for length
        dict_criterion = {"gt": 5}

        # Test inplace=False - should raise error
        with pytest.raises(InvalidCriterionError):
            single_trajectory.filter(
                criterion=dict_criterion,
                criterion_type="length",
                sequence_name=sequence_name,
                inplace=False,
            )

        # Test inplace=True - should also raise error
        trajectory_copy = single_trajectory.copy()
        with pytest.raises(InvalidCriterionError):
            trajectory_copy.filter(
                criterion=dict_criterion,
                criterion_type="length",
                sequence_name=sequence_name,
                inplace=True,
            )

    def test_match_method_raises_error(self, single_trajectory):
        """
        Test match method raises an error.
        Match method is only applicable for 'trajectory' compatible criterion.
        """
        criterion = LengthCriterion(gt=5)

        with pytest.raises(InvalidCriterionError):
            single_trajectory.match(criterion=criterion)

        ## -- from dict
        with pytest.raises(InvalidCriterionError):
            single_trajectory.match(criterion={"gt": 5}, criterion_type="length")
