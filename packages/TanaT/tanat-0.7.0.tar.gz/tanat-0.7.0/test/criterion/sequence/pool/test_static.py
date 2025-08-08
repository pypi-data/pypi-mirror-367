#!/usr/bin/env python3
"""
Test static criterion applied to sequence pools.
"""

import pytest

from tanat.criterion.mixin.static.settings import StaticCriterion
from tanat.criterion.base.exception import InvalidCriterionError


class TestStaticCriterion:
    """
    Test static criterion applied to sequence pools.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_filter_by_age(self, sequence_pools, pool_type, snapshot):
        """
        Test filtering by age for all pool types (inplace=False).
        """
        pool = sequence_pools[pool_type]
        original_data = pool.static_data.copy()
        static_criterion = StaticCriterion(query="age > 65")
        filtered_pool = pool.filter(static_criterion, inplace=False)

        assert pool.static_data.equals(original_data)
        assert filtered_pool is not pool
        snapshot.assert_match(filtered_pool.sequence_data.to_csv())
        snapshot.assert_match(filtered_pool.static_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_filter_by_age_inplace(self, sequence_pools, pool_type, snapshot):
        """
        Test filtering by age for all pool types (inplace=True).
        """
        pool = sequence_pools[pool_type].copy()
        static_criterion = StaticCriterion(query="age > 65")
        result = pool.filter(static_criterion, inplace=True)

        assert result is None
        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.static_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_filter_by_multiple_static_criterion(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Test filtering by multiple static criterion for all pool types (inplace=False).
        """
        pool = sequence_pools[pool_type]
        static_criterion = StaticCriterion(
            query="age > 60 and chronic_condition == True and insurance == 'PRIVATE'"
        )
        filtered_pool = pool.filter(static_criterion, inplace=False)

        ## -- test
        snapshot.assert_match(filtered_pool.sequence_data.to_csv())
        snapshot.assert_match(filtered_pool.static_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_filter_by_multiple_static_criterion_inplace(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Test filtering by multiple static criterion for all pool types (inplace=True).
        """
        pool = sequence_pools[pool_type].copy()
        static_criterion = StaticCriterion(
            query="age > 60 and chronic_condition == True and insurance == 'PRIVATE'"
        )
        result = pool.filter(static_criterion, inplace=True)

        assert result is None
        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.static_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_filter_with_no_matching_criterion_inplace(self, sequence_pools, pool_type):
        """
        Test filtering with criterion that match no data and verify an empty dataframe is returned (inplace=True).
        """
        pool = sequence_pools[pool_type].copy()
        static_criterion = StaticCriterion(query="gender == 'FAKE_GENDER'")

        # Apply filter with inplace=True
        result = pool.filter(static_criterion, inplace=True)

        assert result is None
        assert pool.sequence_data.empty
        assert pool.static_data.empty

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_filter_with_no_matching_criterion_non_inplace(
        self, sequence_pools, pool_type
    ):
        """
        Test filtering with criterion that match no data and verify an empty dataframe is returned (inplace=False).
        """
        pool = sequence_pools[pool_type]
        original_sequence_data = pool.sequence_data.copy()
        original_static_data = pool.static_data.copy()
        static_criterion = StaticCriterion(query="gender == 'FAKE_GENDER'")

        filtered_pool = pool.filter(static_criterion, inplace=False)

        # Verify a new pool object was returned
        assert filtered_pool is not pool
        assert filtered_pool.sequence_data.empty
        assert filtered_pool.static_data.empty

        # Verify the original pool remains unchanged
        assert not pool.sequence_data.empty
        assert not pool.static_data.empty
        assert pool.sequence_data.equals(original_sequence_data)
        assert pool.static_data.equals(original_static_data)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_filter_invalid_level(self, sequence_pools, pool_type):
        """
        Test filtering with static criterion at entity level, which should raise an error.
        """
        pool = sequence_pools[pool_type]
        length_criterion = StaticCriterion(query="age > 65")

        with pytest.raises(InvalidCriterionError):
            pool.filter(length_criterion, level="entity", inplace=False)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_which_query_criterion(self, sequence_pools, pool_type, snapshot):
        """Test which method for query criterion"""
        pool = sequence_pools[pool_type]
        query_criterion = StaticCriterion(query="age > 65")
        matching_ids = pool.which(query_criterion)

        assert isinstance(matching_ids, set)
        snapshot.assert_match(sorted(matching_ids))

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_filter_by_multiple_static_criterion_consistency(
        self, sequence_pools, pool_type
    ):
        """
        Check consistency between inplace and non-inplace filtering with multiple criterion.
        """
        original_pool = sequence_pools[pool_type]
        static_criterion = StaticCriterion(
            query="age > 60 and chronic_condition == True and insurance == 'PRIVATE'"
        )

        # Non-inplace filtering
        filtered_pool = original_pool.filter(static_criterion, inplace=False)
        non_inplace_result = filtered_pool.static_data

        # Inplace filtering
        pool_copy = original_pool.copy()
        pool_copy.filter(static_criterion, inplace=True)
        inplace_result = pool_copy.static_data

        ## which
        matching_ids = sorted(original_pool.which(static_criterion))

        # Test
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_filter_by_age_consistency(self, sequence_pools, pool_type):
        """
        Check consistency between inplace and non-inplace filtering by age.
        """
        original_pool = sequence_pools[pool_type]
        static_criterion = StaticCriterion(query="age > 65")

        # Non-inplace filtering
        filtered_pool = original_pool.filter(static_criterion, inplace=False)
        non_inplace_result = filtered_pool.static_data

        # Inplace filtering
        pool_copy = original_pool.copy()
        pool_copy.filter(static_criterion, inplace=True)
        inplace_result = pool_copy.static_data

        ## which
        matching_ids = sorted(original_pool.which(static_criterion))

        # Test results consistency
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_static_sequence_filtering_via_dict_criterion(
        self, sequence_pools, pool_type
    ):
        """
        Verify consistency of sequence filtering using criterion defined in a dictionary.
        """
        original_pool = sequence_pools[pool_type]
        static_criterion = {"query": "age > 65"}

        # Non-inplace filtering
        filtered_pool = original_pool.filter(
            static_criterion, criterion_type="static", level="sequence", inplace=False
        )
        non_inplace_result = filtered_pool.static_data

        # Inplace filtering
        pool_copy = original_pool.copy()
        pool_copy.filter(
            static_criterion, criterion_type="static", level="sequence", inplace=True
        )
        inplace_result = pool_copy.static_data

        ## which
        matching_ids = sorted(
            original_pool.which(static_criterion, criterion_type="static")
        )

        # Test results consistency
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids
