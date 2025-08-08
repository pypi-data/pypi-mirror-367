#!/usr/bin/env python3
"""
Unit tests for the `subset` method of a trajectory pool.
This method extracts sequences from a trajectory pool by a list of unique IDs.
"""

import pytest


class TestTrajectoryPoolSubset:
    """
    Test suite for the `subset` method applied to a trajectory pool.

    This suite tests both inplace and non-inplace behavior when subsetting
    by valid or invalid IDs.
    """

    @pytest.fixture
    def valid_subset_ids(self, trajectory_pool):
        """
        Fixture that returns a list of valid unique IDs from the trajectory pool.
        """
        return list(trajectory_pool.unique_ids)[:5]

    @pytest.fixture
    def invalid_subset_ids(self):
        """
        Fixture that returns a list of IDs not present in the trajectory pool.
        """
        return [999, 1000, 1001]

    def test_subset_by_valid_ids_non_inplace(
        self, trajectory_pool, valid_subset_ids, snapshot
    ):
        """
        Subset the trajectory pool by valid IDs with `inplace=False`.
        A new trajectory pool should be returned with only the selected sequences.
        """
        subset = trajectory_pool.subset(valid_subset_ids, inplace=False)

        assert set(subset.unique_ids) == set(valid_subset_ids)
        assert len(subset) == len(valid_subset_ids)

        snapshot.assert_match(subset.sequence_pools["event"].sequence_data.to_csv())
        snapshot.assert_match(subset.sequence_pools["state"].sequence_data.to_csv())
        snapshot.assert_match(subset.sequence_pools["interval"].sequence_data.to_csv())

    def test_subset_by_valid_ids_inplace(
        self, trajectory_pool, valid_subset_ids, snapshot
    ):
        """
        Subset the trajectory pool by valid IDs with `inplace=True`.
        The original trajectory pool should be mutated to contain only the selected sequences.
        """
        pool_copy = trajectory_pool.copy()
        result = pool_copy.subset(valid_subset_ids, inplace=True)

        assert result is None
        assert set(pool_copy.unique_ids) == set(valid_subset_ids)

        snapshot.assert_match(pool_copy.sequence_pools["event"].sequence_data.to_csv())
        snapshot.assert_match(pool_copy.sequence_pools["state"].sequence_data.to_csv())
        snapshot.assert_match(
            pool_copy.sequence_pools["interval"].sequence_data.to_csv()
        )

    def test_subset_with_invalid_ids_non_inplace(
        self, trajectory_pool, invalid_subset_ids
    ):
        """
        Subset the trajectory pool with non-existent IDs using `inplace=False`.
        Should return an empty trajectory pool.
        """
        subset = trajectory_pool.subset(invalid_subset_ids, inplace=False)

        assert len(subset) == 0
        assert len(subset.unique_ids) == 0
        for seqpool in subset.sequence_pools.values():
            assert seqpool.sequence_data.empty

    def test_subset_with_invalid_ids_inplace(self, trajectory_pool, invalid_subset_ids):
        """
        Subset the trajectory pool with non-existent IDs using `inplace=True`.
        The original trajectory pool should be mutated to be empty.
        """
        pool_copy = trajectory_pool.copy()
        result = pool_copy.subset(invalid_subset_ids, inplace=True)

        assert result is None
        assert len(pool_copy) == 0
        for seqpool in pool_copy.sequence_pools.values():
            assert seqpool.sequence_data.empty
