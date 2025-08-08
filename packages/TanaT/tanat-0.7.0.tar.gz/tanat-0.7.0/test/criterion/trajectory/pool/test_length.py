#!/usr/bin/env python3
"""
Test length criterion applied to trajectory pools.
"""

import pytest

from tanat.criterion.sequence.type.length.settings import LengthCriterion
from tanat.criterion.base.exception import InvalidCriterionError


class TestLengthCriterion:
    """
    Test length criterion applied to trajectory pools.
    """

    @pytest.mark.parametrize(
        "sequence_name,length_param",
        [
            ("event", {"gt": 10, "lt": 12}),
            ("state", {"le": 4, "ge": 3}),
            ("interval", {"ge": 3, "lt": 5}),
        ],
    )
    def test_filter_trajectories_on_sequence_level(
        self, trajectory_pool, sequence_name, length_param, snapshot
    ):
        """
        Trajectory pool: Length criterion applied to sequence level (inplace=False).
        """
        length_criterion = LengthCriterion(**length_param)
        filtered_pool = trajectory_pool.filter(
            criterion=length_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        snapshot.assert_match(sorted(filtered_pool.unique_ids))
        assert filtered_pool.settings.intersection is True

    @pytest.mark.parametrize(
        "sequence_name,length_param",
        [
            ("event", {"gt": 10, "lt": 12}),
            ("state", {"le": 4, "ge": 3}),
            ("interval", {"ge": 3, "lt": 5}),
        ],
    )
    def test_filter_trajectories_on_sequence_level_inplace(
        self, trajectory_pool, sequence_name, length_param, snapshot
    ):
        """
        Trajectory pool: Length criterion applied to sequence level (inplace=True).
        """
        ## -- length criterion
        length_criterion = LengthCriterion(**length_param)

        ## -- filtering on copy
        trajectory_pool_copy = trajectory_pool.copy()
        filtered_pool = trajectory_pool_copy.filter(
            criterion=length_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )

        ## -- inplace should return None
        assert filtered_pool is None
        snapshot.assert_match(sorted(trajectory_pool_copy.unique_ids))

    @pytest.mark.parametrize(
        "sequence_name,length_param",
        [
            ("event", {"gt": 10, "lt": 12}),
            ("state", {"le": 4, "ge": 3}),
            ("interval", {"ge": 3, "lt": 5}),
        ],
    )
    def test_filter_trajectories_on_sequence_level_consistency(
        self, trajectory_pool, sequence_name, length_param
    ):
        """
        Check filter sequence level with inplace=True and inplace=False produce the same results.
        """
        ## -- length criterion
        length_criterion = LengthCriterion(**length_param)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=length_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        non_inplace_result = sorted(filtered_pool.unique_ids)

        # Inplace filtering
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=length_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )
        inplace_result = sorted(traj_pool_copy.unique_ids)

        # Test consistency
        assert non_inplace_result == inplace_result

    @pytest.mark.parametrize(
        "sequence_name,length_param",
        [
            ("event", {"gt": 1000}),  # No sequence is this long
            ("state", {"lt": 0}),  # No sequence has negative length
            ("interval", {"ge": 999}),  # No sequence is this long
        ],
    )
    def test_filter_no_matching_length_criterion(
        self, trajectory_pool, sequence_name, length_param
    ):
        """
        Test filtering with length criterion that doesn't match any data.
        Should return an empty trajectory pool.
        """
        ## -- length criterion
        length_criterion = LengthCriterion(**length_param)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=length_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )

        assert filtered_pool.unique_ids == set()

    @pytest.mark.parametrize(
        "sequence_name,length_param",
        [
            ("event", {"gt": 1000}),  # No sequence is this long
            ("state", {"lt": 0}),  # No sequence has negative length
            ("interval", {"ge": 999}),  # No sequence is this long
        ],
    )
    def test_filter_no_matching_length_criterion_inplace(
        self, trajectory_pool, sequence_name, length_param
    ):
        """
        Test filtering with length criterion that doesn't match any data.
        Should return an empty trajectory pool.
        """
        ## -- length criterion
        length_criterion = LengthCriterion(**length_param)

        # Inplace filtering
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=length_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )

        # Test empty result
        assert traj_pool_copy.unique_ids == set()

    @pytest.mark.parametrize(
        "sequence_name,length_param",
        [
            ("event", {"gt": 10, "lt": 12}),
            ("state", {"le": 4, "ge": 3}),
            ("interval", {"ge": 3, "lt": 5}),
        ],
    )
    def test_length_filtering_via_dict_criterion(
        self, trajectory_pool, sequence_name, length_param
    ):
        """
        Verify consistency of filtering using criterion defined in a dictionary.
        """
        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=length_param,
            criterion_type="length",
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        non_inplace_result = sorted(filtered_pool.unique_ids)

        # Inplace filtering
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=length_param,
            criterion_type="length",
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )
        inplace_result = sorted(traj_pool_copy.unique_ids)

        # Test consistency
        assert non_inplace_result == inplace_result

    @pytest.mark.parametrize(
        "sequence_name,length_param",
        [
            ("event", {"gt": 10, "lt": 12}),
            ("state", {"le": 4, "ge": 3}),
            ("interval", {"ge": 3, "lt": 5}),
        ],
    )
    def test_intersection_false(
        self, trajectory_pool, sequence_name, length_param, snapshot
    ):
        """
        Test that setting intersection=False does not affect the length of the filtered
        trajectory pool, but does affect the length of the inner sequence pool.
        """
        filtered_pool = trajectory_pool.filter(
            criterion=length_param,
            criterion_type="length",
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

    def test_which_method_raises_error(self, trajectory_pool):
        """
        Which method should raise an error for length criterion because this criterion is not
        applicable at 'trajectory' level.
        """

        criterion_kwargs = {"gt": 10, "lt": 12}
        criterion = LengthCriterion(**criterion_kwargs)

        with pytest.raises(InvalidCriterionError):
            trajectory_pool.which(criterion)

        ## -- from dict
        with pytest.raises(InvalidCriterionError):
            trajectory_pool.which(criterion_kwargs, criterion_type="length")
