#!/usr/bin/env python3
"""
Test time criterion applied to single trajectories.
"""

import pytest

from tanat.criterion.mixin.time.settings import TimeCriterion
from tanat.criterion.base.exception import InvalidCriterionError


class TestTimeCriterion:
    """
    Test TimeCriterion applied to single trajectory.
    """

    @pytest.fixture
    def single_trajectory(self, trajectory_pool):
        """
        Return a single trajectory from the pool for testing purposes.
        """
        return trajectory_pool[3].copy()

    @pytest.mark.parametrize(
        "sequence_name",
        ["event", "interval"],
    )
    def test_time_criterion_filter_single_trajectory(
        self, single_trajectory, sequence_name, snapshot
    ):
        """
        Test filtering a single trajectory using TimeCriterion with `inplace=False`.
        """
        time_criterion = TimeCriterion(start_before="2023-04-30")

        filtered_trajectory = single_trajectory.filter(
            criterion=time_criterion,
            sequence_name=sequence_name,
            inplace=False,
        )

        filtered_sequence_data = filtered_trajectory[sequence_name].sequence_data
        snapshot.assert_match(filtered_sequence_data.to_csv())

    @pytest.mark.parametrize(
        "sequence_name",
        ["event", "interval"],
    )
    def test_time_criterion_filter_single_trajectory_inplace(
        self, single_trajectory, sequence_name, snapshot
    ):
        """
        Test filtering a single trajectory using TimeCriterion with `inplace=True`.
        """
        time_criterion = TimeCriterion(start_before="2023-04-30")

        result = single_trajectory.filter(
            criterion=time_criterion,
            sequence_name=sequence_name,
            inplace=True,
        )

        assert result is None

        modified_sequence_data = single_trajectory[sequence_name].sequence_data
        snapshot.assert_match(modified_sequence_data.to_csv())

    @pytest.mark.parametrize(
        "sequence_name",
        ["event", "interval"],
    )
    def test_time_criterion_filter_consistency_between_inplace_and_copy(
        self, single_trajectory, sequence_name
    ):
        """
        Ensure consistent filtering results between inplace and non-inplace TimeCriterion filtering.
        """
        time_criterion = TimeCriterion(start_before="2023-04-30")

        # Non-inplace
        filtered_trajectory = single_trajectory.filter(
            criterion=time_criterion,
            sequence_name=sequence_name,
            inplace=False,
        )
        non_inplace_result = filtered_trajectory[sequence_name].sequence_data

        # Inplace
        trajectory_copy = single_trajectory.copy()
        trajectory_copy.filter(
            criterion=time_criterion,
            sequence_name=sequence_name,
            inplace=True,
        )
        inplace_result = trajectory_copy[sequence_name].sequence_data

        assert non_inplace_result.equals(inplace_result)

    def test_time_criterion_filter_state_sequence_raises(self, single_trajectory):
        """
        Test that applying TimeCriterion to the 'state' sequence raises NotImplementedError.
        """
        time_criterion = TimeCriterion(start_before="2023-04-30")

        with pytest.raises(NotImplementedError):
            single_trajectory.filter(
                criterion=time_criterion,
                sequence_name="state",
                inplace=False,
            )

        trajectory_copy = single_trajectory.copy()
        with pytest.raises(NotImplementedError):
            trajectory_copy.filter(
                criterion=time_criterion,
                sequence_name="state",
                inplace=True,
            )

    @pytest.mark.parametrize(
        "sequence_name",
        ["event", "interval"],
    )
    def test_time_criterion_dict_equivalence(self, single_trajectory, sequence_name):
        """
        Validate that using a dict-based time criterion yields
        the same result as using a TimeCriterion object.
        """
        dict_criterion = {"start_before": "2023-04-30"}

        filtered_from_dict = single_trajectory.filter(
            criterion=dict_criterion,
            criterion_type="time",
            sequence_name=sequence_name,
            inplace=False,
        )

        time_criterion_obj = TimeCriterion(start_before="2023-04-30")
        filtered_from_obj = single_trajectory.filter(
            criterion=time_criterion_obj,
            sequence_name=sequence_name,
            inplace=False,
        )

        assert filtered_from_dict[sequence_name].sequence_data.equals(
            filtered_from_obj[sequence_name].sequence_data
        )

    def test_time_criterion_filter_preserves_other_sequences(self, single_trajectory):
        """
        Ensure that applying TimeCriterion to one sequence does not alter unrelated sequences.
        """
        time_criterion = TimeCriterion(start_before="2023-04-30")

        filtered_trajectory = single_trajectory.filter(
            criterion=time_criterion,
            sequence_name="event",
            inplace=False,
        )

        for sequence_name in single_trajectory.sequences:
            if sequence_name != "event":
                assert filtered_trajectory[sequence_name].sequence_data.equals(
                    single_trajectory[sequence_name].sequence_data
                )

    @pytest.mark.parametrize(
        "sequence_name",
        ["event", "interval"],
    )
    def test_time_criterion_filter_with_no_matching_elements_returns_empty(
        self, single_trajectory, sequence_name
    ):
        """
        Test that applying TimeCriterion with no matches returns an empty sequence.

        Uses an unrealistic date far in the future to ensure no records match.
        """
        time_criterion = TimeCriterion(start_after="2100-12-12")

        filtered_trajectory = single_trajectory.filter(
            criterion=time_criterion,
            sequence_name=sequence_name,
            inplace=False,
        )

        assert filtered_trajectory.sequences.get(sequence_name) is None

    def test_match_method_raises_error(self, single_trajectory):
        """
        Test match method raises an error.
        Match method is only applicable for 'trajectory' compatible criterion.
        """
        criterion = TimeCriterion(start_before="2023-04-30")

        with pytest.raises(InvalidCriterionError):
            single_trajectory.match(criterion=criterion)

        ## -- from dict
        with pytest.raises(InvalidCriterionError):
            single_trajectory.match(
                criterion={"start_before": "2023-04-30"},
                criterion_type="time",
            )
