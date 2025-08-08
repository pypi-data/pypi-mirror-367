#!/usr/bin/env python3
"""
Test static criterion applied to single trajectories.
"""

import pytest

from tanat.criterion.mixin.static.settings import StaticCriterion
from tanat.criterion.base.exception import InvalidCriterionError


class TestStaticCriterion:
    """
    Test StaticCriterion applied to single trajectory.
    """

    @pytest.fixture
    def single_trajectory(self, trajectory_pool):
        """
        Returns a single trajectory instance for testing.
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
    def test_static_criterion_raises_on_single_trajectory(
        self, single_trajectory, sequence_name
    ):
        """
        Ensure that applying StaticCriterion to a single trajectory's sequence raises an error.
        """
        static_criterion = StaticCriterion(query="age > 50")

        # inplace=False: should raise InvalidCriterionError
        with pytest.raises(InvalidCriterionError):
            single_trajectory.filter(
                criterion=static_criterion,
                sequence_name=sequence_name,
                inplace=False,
            )

        # inplace=True: should also raise InvalidCriterionError
        trajectory_copy = single_trajectory.copy()
        with pytest.raises(InvalidCriterionError):
            trajectory_copy.filter(
                criterion=static_criterion,
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
    def test_dict_based_static_criterion_raises_on_single_trajectory(
        self, single_trajectory, sequence_name
    ):
        """
        Ensure that using a dictionary-based StaticCriterion on a single trajectory raises an error.
        """
        dict_criterion = {"query": "age > 50"}

        # inplace=False: should raise InvalidCriterionError
        with pytest.raises(InvalidCriterionError):
            single_trajectory.filter(
                criterion=dict_criterion,
                criterion_type="static",
                sequence_name=sequence_name,
                inplace=False,
            )

        # inplace=True: should also raise InvalidCriterionError
        trajectory_copy = single_trajectory.copy()
        with pytest.raises(InvalidCriterionError):
            trajectory_copy.filter(
                criterion=dict_criterion,
                criterion_type="static",
                sequence_name=sequence_name,
                inplace=True,
            )

    def test_match_method(self, single_trajectory):
        """
        Test the match method of the StaticCriterion class.
        """
        criterion = StaticCriterion(query="age < 50")
        assert single_trajectory.match(criterion)

        ## -- from dict
        criterion = {"query": "age < 50"}
        assert single_trajectory.match(criterion=criterion, criterion_type="static")
