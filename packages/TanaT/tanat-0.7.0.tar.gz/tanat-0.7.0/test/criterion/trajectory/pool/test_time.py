#!/usr/bin/env python3
"""
Test time criterion applied to trajectory pools.
"""

import pytest

from tanat.criterion.mixin.time.settings import TimeCriterion
from tanat.criterion.base.exception import (
    InvalidCriterionError,
)


class TestTimeCriterion:
    """
    Test time criterion applied to trajectory pools.
    """

    @pytest.mark.parametrize(
        "sequence_name,start_after,end_before",
        [
            ("event", "2023-04-01", "2023-05-01"),
            ("state", "2023-04-01", "2023-04-15"),
            ("interval", "2023-04-01", "2023-04-30"),
        ],
    )
    def test_filter_trajectories_on_sequence_level(
        self,
        trajectory_pool,
        sequence_name,
        start_after,
        end_before,
        snapshot,
    ):
        """
        Trajectory pool: Time criterion applied to sequence level (inplace=False).
        """
        time_criterion = TimeCriterion(
            start_after=start_after,
            end_before=end_before,
        )
        filtered_pool = trajectory_pool.filter(
            criterion=time_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        snapshot.assert_match(sorted(filtered_pool.unique_ids))
        assert filtered_pool.settings.intersection is True

    @pytest.mark.parametrize(
        "sequence_name,start_after,end_before",
        [
            ("event", "2023-04-01", "2023-05-01"),
            ("interval", "2023-04-01", "2023-04-30"),
        ],
    )
    def test_filter_trajectories_on_entity_level(
        self,
        trajectory_pool,
        sequence_name,
        start_after,
        end_before,
        snapshot,
    ):
        """
        Test filtering trajectories on entity level.
        """
        time_criterion = TimeCriterion(
            start_after=start_after,
            end_before=end_before,
        )
        filtered_pool = trajectory_pool.filter(
            criterion=time_criterion,
            level="entity",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )

        snapshot.assert_match(sorted(filtered_pool.unique_ids))
        assert filtered_pool.settings.intersection is True

    def test_filter_entity_level_raises_error_on_state(self, trajectory_pool):
        """
        Test filtering entity level raises error on state.
        """
        criterion = TimeCriterion(start_after="2023-04-01", end_before="2023-05-01")
        with pytest.raises(NotImplementedError):
            trajectory_pool.filter(
                criterion=criterion,
                level="entity",
                sequence_name="state",
                inplace=False,
                intersection=True,
            )

    @pytest.mark.parametrize(
        "sequence_name,start_after,end_before",
        [
            ("event", "2023-04-01", "2023-05-01"),
            ("state", "2023-04-01", "2023-04-15"),
            ("interval", "2023-04-01", "2023-04-30"),
        ],
    )
    def test_filter_trajectories_on_sequence_level_inplace(
        self,
        trajectory_pool,
        sequence_name,
        start_after,
        end_before,
        snapshot,
    ):
        """
        Trajectory pool: Time criterion applied to sequence level (inplace=True).
        """
        time_criterion = TimeCriterion(
            start_after=start_after,
            end_before=end_before,
        )

        ## -- filtering on copy
        trajectory_pool_copy = trajectory_pool.copy()
        filtered_pool = trajectory_pool_copy.filter(
            criterion=time_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )

        ## -- inplace should return None
        assert filtered_pool is None
        snapshot.assert_match(sorted(trajectory_pool_copy.unique_ids))

    @pytest.mark.parametrize(
        "sequence_name,start_after,end_before",
        [
            ("event", "2050-01-01", "2050-01-02"),
            ("state", "2050-01-01", "2050-01-02"),
            ("interval", "2050-01-01", "2050-01-02"),
        ],
    )
    def test_filter_no_matching_time_criterion(
        self, trajectory_pool, sequence_name, start_after, end_before
    ):
        """
        Test filtering with time criterion that doesn't match any data.
        Should return an empty trajectory pool.
        """
        ## -- time criterion with future dates
        time_criterion = TimeCriterion(start_after=start_after, end_before=end_before)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=time_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )

        assert filtered_pool.unique_ids == set()

    @pytest.mark.parametrize(
        "sequence_name,start_after,end_before",
        [
            ("event", "2050-01-01", "2050-01-02"),
            ("state", "2050-01-01", "2050-01-02"),
            ("interval", "2050-01-01", "2050-01-02"),
        ],
    )
    def test_filter_no_matching_time_criterion_inplace(
        self, trajectory_pool, sequence_name, start_after, end_before
    ):
        """
        Test filtering with time criterion that doesn't match any data (inplace=True).
        Should result in an empty trajectory pool.
        """
        ## -- time criterion with future dates
        time_criterion = TimeCriterion(start_after=start_after, end_before=end_before)

        # Inplace filtering
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=time_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )

        # Test empty result
        assert traj_pool_copy.unique_ids == set()

    @pytest.mark.parametrize(
        "sequence_name,start_after,end_before",
        [
            ("event", "2023-04-01", "2023-05-01"),
            ("state", "2023-04-01", "2023-04-15"),
            ("interval", "2023-04-01", "2023-04-30"),
            ("event", "2023-04-01", "2023-05-01"),
            ("state", "2023-04-01", "2023-04-15"),
            ("interval", "2023-04-01", "2023-04-30"),
        ],
    )
    def test_time_filtering_via_dict_criterion(
        self, trajectory_pool, sequence_name, start_after, end_before
    ):
        """
        Verify consistency of filtering using criterion defined in a dictionary.
        """
        # Dictionary criterion
        dict_criterion = {
            "start_after": start_after,
            "end_before": end_before,
        }

        # Non-inplace filtering with dict criterion
        filtered_pool = trajectory_pool.filter(
            criterion=dict_criterion,
            criterion_type="time",
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        non_inplace_result = sorted(filtered_pool.unique_ids)

        # Inplace filtering with dict criterion
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=dict_criterion,
            criterion_type="time",
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )
        inplace_result = sorted(traj_pool_copy.unique_ids)

        # Test consistency
        assert non_inplace_result == inplace_result

    @pytest.mark.parametrize(
        "sequence_name,start_after,end_before",
        [
            ("event", "2023-04-01", "2023-05-01"),
            ("state", "2023-04-01", "2023-04-15"),
            ("interval", "2023-04-01", "2023-04-30"),
            ("event", "2023-04-01", "2023-05-01"),
            ("state", "2023-04-01", "2023-04-15"),
            ("interval", "2023-04-01", "2023-04-30"),
        ],
    )
    def test_intersection_false(
        self,
        trajectory_pool,
        sequence_name,
        start_after,
        end_before,
        snapshot,
    ):
        """
        Test that setting intersection=False does not affect the length of the filtered
        trajectory pool, but does affect the length of the inner sequence pool.
        """
        time_criterion = TimeCriterion(
            start_after=start_after,
            end_before=end_before,
        )
        filtered_pool = trajectory_pool.filter(
            criterion=time_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=False,
        )

        assert len(filtered_pool) == len(trajectory_pool)
        assert filtered_pool.settings.intersection is False
        filtered_sequence_ids = sorted(
            filtered_pool.sequence_pools[sequence_name].unique_ids
        )
        snapshot.assert_match(filtered_sequence_ids)

    @pytest.mark.parametrize(
        "sequence_name,start_after,end_before",
        [
            ("event", "2023-04-01", "2023-05-01"),
            ("state", "2023-04-01", "2023-04-15"),
            ("interval", "2023-04-01", "2023-04-30"),
        ],
    )
    def test_which_time_criterion(
        self, trajectory_pool, sequence_name, start_after, end_before, snapshot
    ):
        """
        Test which method for time criterion on trajectory pools.
        """
        time_criterion = TimeCriterion(start_after=start_after, end_before=end_before)

        matching_ids = trajectory_pool.sequence_pools[sequence_name].which(
            time_criterion
        )
        assert isinstance(matching_ids, set)
        snapshot.assert_match(sorted(matching_ids))

    def test_which_method_raises_error(self, trajectory_pool):
        """
        Which method should raise an error for time criterion because this criterion is not
        applicable at 'trajectory' level.
        """

        criterion_kwargs = {"start_after": "2023-04-01", "end_before": "2023-05-01"}
        criterion = TimeCriterion(**criterion_kwargs)

        with pytest.raises(InvalidCriterionError):
            trajectory_pool.which(criterion)

        ## -- from dict
        with pytest.raises(InvalidCriterionError):
            trajectory_pool.which(criterion_kwargs, criterion_type="time")
