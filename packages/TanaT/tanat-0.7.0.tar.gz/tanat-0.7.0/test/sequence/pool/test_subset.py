#!/usr/bin/env python3
"""
Test subsetting sequences by ids on sequence pool.
"""

import pytest


class TestSubsetMethod:
    """
    Tests for the `subset` method used to extract sequences by ID.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_subset_by_ids_non_inplace(self, sequence_pools, pool_type, snapshot):
        """
        Subset a sequence pool by specific IDs (inplace=False).
        """
        pool = sequence_pools[pool_type]
        subset_ids = list(pool.unique_ids)[:5]

        subset_pool = pool.subset(subset_ids, inplace=False)

        assert set(subset_pool.unique_ids) == set(subset_ids)
        assert len(subset_pool) == len(subset_ids)

        snapshot.assert_match(subset_pool.sequence_data.to_csv())
        snapshot.assert_match(subset_pool.static_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_subset_by_ids_inplace(self, sequence_pools, pool_type, snapshot):
        """
        Subset a sequence pool by specific IDs (inplace=True).
        """
        pool = sequence_pools[pool_type].copy()
        subset_ids = list(pool.unique_ids)[:5]

        result = pool.subset(subset_ids, inplace=True)

        assert result is None
        assert set(pool.unique_ids) == set(subset_ids)

        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.static_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_subset_with_no_match_non_inplace(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Subset a sequence pool with non-existent IDs (inplace=False).
        Should return an empty pool.
        """
        pool = sequence_pools[pool_type]
        non_existent_ids = [999, 1000, 1001]

        subset_pool = pool.subset(non_existent_ids, inplace=False)

        assert len(subset_pool) == 0
        assert len(subset_pool.unique_ids) == 0
        assert subset_pool.sequence_data.empty
        assert subset_pool.static_data.empty

        snapshot.assert_match(subset_pool.sequence_data.to_csv())
        snapshot.assert_match(subset_pool.static_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_subset_with_no_match_inplace(self, sequence_pools, pool_type, snapshot):
        """
        Subset a sequence pool with non-existent IDs (inplace=True).
        Should mutate the pool to be empty.
        """
        pool = sequence_pools[pool_type].copy()
        non_existent_ids = [999, 1000, 1001]

        result = pool.subset(non_existent_ids, inplace=True)

        assert result is None
        assert len(pool) == 0
        assert pool.sequence_data.empty
        assert pool.static_data.empty

        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.static_data.to_csv())
