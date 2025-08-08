#!/usr/bin/env python3
"""
Test static criterion applied to trajectory pools.
"""

import pytest

from tanat.criterion.mixin.static.settings import StaticCriterion


class TestStaticCriterion:
    """
    Test static criterion applied to trajectory pools.
    """

    @pytest.mark.parametrize(
        "static_param",
        [
            {"query": "age > 50"},
            {"query": "gender == 'F'"},
            {"query": "insurance == 'PUBLIC'"},
            {"query": "chronic_condition == True"},
            {"query": "age > 30 and gender == 'M'"},
        ],
    )
    def test_filter_trajectories_on_trajectory_level(
        self, trajectory_pool, static_param, snapshot
    ):
        """
        Trajectory pool: Static criterion applied to trajectory level (inplace=False).
        """
        static_criterion = StaticCriterion(**static_param)
        filtered_pool = trajectory_pool.filter(
            criterion=static_criterion,
            level="trajectory",
            inplace=False,
            intersection=True,
        )
        snapshot.assert_match(sorted(filtered_pool.unique_ids))
        assert filtered_pool.settings.intersection is True

    @pytest.mark.parametrize(
        "static_param",
        [
            {"query": "age > 50"},
            {"query": "gender == 'F'"},
            {"query": "insurance == 'PUBLIC'"},
            {"query": "chronic_condition == True"},
            {"query": "age > 30 and gender == 'M'"},
        ],
    )
    def test_filter_trajectories_on_trajectory_level_inplace(
        self, trajectory_pool, static_param, snapshot
    ):
        """
        Trajectory pool: Static criterion applied to trajectory level (inplace=True).
        """
        # Static criterion
        static_criterion = StaticCriterion(**static_param)

        # Filtering on copy
        trajectory_pool_copy = trajectory_pool.copy()
        filtered_pool = trajectory_pool_copy.filter(
            criterion=static_criterion,
            level="trajectory",
            inplace=True,
            intersection=True,
        )

        # Inplace should return None
        assert filtered_pool is None
        snapshot.assert_match(sorted(trajectory_pool_copy.unique_ids))

    @pytest.mark.parametrize(
        "static_param",
        [
            {"query": "age > 50"},
            {"query": "gender == 'F'"},
            {"query": "insurance == 'PUBLIC'"},
            {"query": "chronic_condition == True"},
            {"query": "age > 30 and gender == 'M'"},
        ],
    )
    def test_filter_trajectories_on_trajectory_level_consistency(
        self, trajectory_pool, static_param
    ):
        """
        Check filter static level with inplace=True and inplace=False produce the same results.
        """
        # Static criterion
        static_criterion = StaticCriterion(**static_param)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=static_criterion,
            level="trajectory",
            inplace=False,
            intersection=True,
        )
        non_inplace_result = sorted(filtered_pool.unique_ids)

        # Inplace filtering
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=static_criterion,
            level="trajectory",
            inplace=True,
            intersection=True,
        )
        inplace_result = sorted(traj_pool_copy.unique_ids)

        # Test consistency
        assert non_inplace_result == inplace_result

    @pytest.mark.parametrize(
        "static_param",
        [
            {"query": "age > 200"},  # No patient is this old
            {"query": "gender == 'X'"},  # Invalid gender value
            {"query": "insurance == 'INVALID'"},  # Invalid insurance type
            {"query": "age < 0"},  # No patient has negative age
        ],
    )
    def test_filter_no_matching_static_criterion(self, trajectory_pool, static_param):
        """
        Test filtering with static criterion that doesn't match any data.
        Should return an empty trajectory pool.
        """
        # Static criterion
        static_criterion = StaticCriterion(**static_param)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=static_criterion,
            level="trajectory",
            inplace=False,
            intersection=True,
        )

        assert filtered_pool.unique_ids == set()

    @pytest.mark.parametrize(
        "static_param",
        [
            {"query": "age > 200"},  # No patient is this old
            {"query": "gender == 'X'"},  # Invalid gender value
            {"query": "insurance == 'INVALID'"},  # Invalid insurance type
            {"query": "age < 0"},  # No patient has negative age
        ],
    )
    def test_filter_no_matching_static_criterion_inplace(
        self, trajectory_pool, static_param
    ):
        """
        Test filtering with static criterion that doesn't match any data (inplace).
        Should return an empty trajectory pool.
        """
        # Static criterion
        static_criterion = StaticCriterion(**static_param)

        # Inplace filtering
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=static_criterion,
            level="trajectory",
            inplace=True,
            intersection=True,
        )

        # Test empty result
        assert traj_pool_copy.unique_ids == set()

    @pytest.mark.parametrize(
        "static_param",
        [
            {"query": "age > 50"},
            {"query": "gender == 'F'"},
            {"query": "insurance == 'PUBLIC'"},
            {"query": "chronic_condition == True"},
            {"query": "age > 30 and gender == 'M'"},
        ],
    )
    def test_static_filtering_via_dict_criterion(self, trajectory_pool, static_param):
        """
        Verify consistency of filtering using criterion defined in a dictionary.
        """
        # Non-inplace filtering with StaticCriterion object
        static_criterion = StaticCriterion(**static_param)
        filtered_pool_obj = trajectory_pool.filter(
            criterion=static_criterion,
            level="trajectory",
            inplace=False,
            intersection=True,
        )
        obj_result = sorted(filtered_pool_obj.unique_ids)

        # Non-inplace filtering with dict criterion
        filtered_pool_dict = trajectory_pool.filter(
            criterion=static_param,
            criterion_type="static",
            level="trajectory",
            inplace=False,
            intersection=True,
        )
        dict_result = sorted(filtered_pool_dict.unique_ids)

        # Test consistency
        assert obj_result == dict_result

    @pytest.mark.parametrize(
        "static_param",
        [
            {"query": "age > 50"},
            {"query": "gender == 'F'"},
            {"query": "insurance == 'PUBLIC'"},
            {"query": "chronic_condition == True"},
        ],
    )
    def test_intersection_false(self, trajectory_pool, static_param, snapshot):
        """
        Test that setting intersection=False affects trajectory filtering.
        With static criterion, intersection should not change the result
        since static filtering operates at trajectory level.
        """
        filtered_pool = trajectory_pool.filter(
            criterion=static_param,
            criterion_type="static",
            level="trajectory",
            inplace=False,
            intersection=False,
        )

        assert filtered_pool.settings.intersection is False
        snapshot.assert_match(sorted(filtered_pool.unique_ids))

    @pytest.mark.parametrize(
        "static_param",
        [
            {"query": "age > 50 and chronic_condition == True"},
            {"query": "gender == 'F' and insurance == 'PUBLIC'"},
            {"query": "age < 40 and gender == 'M'"},
        ],
    )
    def test_complex_static_queries(self, trajectory_pool, static_param, snapshot):
        """
        Test complex static queries with multiple conditions.
        """
        static_criterion = StaticCriterion(**static_param)
        filtered_pool = trajectory_pool.filter(
            criterion=static_criterion,
            level="trajectory",
            inplace=False,
            intersection=True,
        )
        snapshot.assert_match(sorted(filtered_pool.unique_ids))

    def test_static_criterion_with_which_method(self, trajectory_pool, snapshot):
        """
        Test using static criterion with the 'which' method to get IDs.
        """
        static_criterion = StaticCriterion(query="age > 50")

        # Get IDs using which method
        matching_ids = trajectory_pool.which(static_criterion)

        assert isinstance(matching_ids, set)
        snapshot.assert_match(sorted(matching_ids))

    def test_static_criterion_preserves_static_data(self, trajectory_pool, snapshot):
        """
        Test that static filtering preserves the static data structure.
        """
        static_criterion = StaticCriterion(query="age > 30")
        filtered_pool = trajectory_pool.filter(
            criterion=static_criterion,
            level="trajectory",
            inplace=False,
            intersection=True,
        )

        # Check that static data is preserved and filtered correctly
        assert filtered_pool.static_data is not None
        assert len(filtered_pool.static_data) == len(filtered_pool.unique_ids)
        snapshot.assert_match(filtered_pool.static_data.to_csv())
