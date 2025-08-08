#!/usr/bin/env python3
"""
Test length criterion applied to sequence pools.
"""

import pytest

from tanat.criterion.sequence.type.length.settings import LengthCriterion
from tanat.criterion.sequence.type.length.exception import (
    ContradictoryLengthCriterionError,
)
from tanat.criterion.base.exception import InvalidCriterionError


class TestLengthCriterion:
    """
    Test length criterion applied to sequence pools.
    """

    @pytest.mark.parametrize(
        "pool_type,min_length",
        [
            ("event", 10),
            ("state", 3),
            ("interval", 4),
        ],
    )
    def test_filter_by_length_gt(self, sequence_pools, pool_type, min_length, snapshot):
        """
        Test filtering sequences longer than a threshold for all pool types (inplace=False).
        """
        pool = sequence_pools[pool_type]
        original_data = pool.sequence_data.copy()

        # Create length criterion for sequences with more than min_length entities
        length_criterion = LengthCriterion(gt=min_length)

        # Filter long sequences
        filtered_pool = pool.filter(length_criterion, inplace=False)

        # Check original data is unchanged
        assert pool.sequence_data.equals(original_data)
        assert filtered_pool is not pool

        # Check length of each sequence
        for seq_id in filtered_pool.unique_ids:
            sequence = filtered_pool.get_sequences()[seq_id]
            assert len(sequence.sequence_data) > min_length

        snapshot.assert_match(filtered_pool.sequence_data.to_csv())
        snapshot.assert_match(filtered_pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,min_length",
        [
            ("event", 10),
            ("state", 3),
            ("interval", 4),
        ],
    )
    def test_filter_by_length_gt_inplace(
        self, sequence_pools, pool_type, min_length, snapshot
    ):
        """
        Test filtering sequences longer than a threshold for all pool types (inplace=True).
        """
        pool = sequence_pools[pool_type].copy()

        # Create length criterion for sequences with more than min_length entities
        length_criterion = LengthCriterion(gt=min_length)

        # Filter long sequences inplace
        result = pool.filter(length_criterion, inplace=True)

        assert result is None

        # Check length of each sequence
        for seq_id in pool.unique_ids:
            sequence = pool.get_sequences()[seq_id]
            assert len(sequence.sequence_data) > min_length

        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,min_length,max_length",
        [
            ("event", 7, 12),
            ("state", 2, 4),
            ("interval", 3, 6),
        ],
    )
    def test_filter_by_length_range(
        self, sequence_pools, pool_type, min_length, max_length, snapshot
    ):
        """
        Test filtering sequences with length in a range for all pool types (inplace=False).
        """
        pool = sequence_pools[pool_type]
        original_data = pool.sequence_data.copy()

        # Create length criterion for sequences with length in range
        length_criterion = LengthCriterion(ge=min_length, le=max_length)

        # Filter sequences
        filtered_pool = pool.filter(length_criterion, inplace=False)

        # Check original data is unchanged
        assert pool.sequence_data.equals(original_data)
        assert filtered_pool is not pool

        # Check length of each sequence
        for seq_id in filtered_pool.unique_ids:
            sequence = filtered_pool.get_sequences()[seq_id]
            length = len(sequence.sequence_data)
            assert min_length <= length <= max_length

        snapshot.assert_match(filtered_pool.sequence_data.to_csv())
        snapshot.assert_match(filtered_pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,min_length,max_length",
        [
            ("event", 7, 12),
            ("state", 2, 4),
            ("interval", 3, 6),
        ],
    )
    def test_filter_by_length_range_inplace(
        self, sequence_pools, pool_type, min_length, max_length, snapshot
    ):
        """
        Test filtering sequences with length in a range for all pool types (inplace=True).
        """
        pool = sequence_pools[pool_type].copy()

        # Create length criterion for sequences with length in range
        length_criterion = LengthCriterion(ge=min_length, le=max_length)

        # Filter sequences inplace
        result = pool.filter(length_criterion, inplace=True)

        assert result is None

        # Check length of each sequence
        for seq_id in pool.unique_ids:
            sequence = pool.get_sequences()[seq_id]
            length = len(sequence.sequence_data)
            assert min_length <= length <= max_length

        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,max_length",
        [
            ("event", 8),
            ("state", 3),
            ("interval", 4),
        ],
    )
    def test_filter_by_length_lt(self, sequence_pools, pool_type, max_length, snapshot):
        """
        Test filtering sequences shorter than a threshold for all pool types (inplace=False).
        """
        pool = sequence_pools[pool_type]
        original_data = pool.sequence_data.copy()

        # Create length criterion for sequences with less than max_length entities
        length_criterion = LengthCriterion(lt=max_length)

        # Filter short sequences
        filtered_pool = pool.filter(length_criterion, inplace=False)

        # Check original data is unchanged
        assert pool.sequence_data.equals(original_data)
        assert filtered_pool is not pool

        # Check length of each sequence
        for seq_id in filtered_pool.unique_ids:
            sequence = filtered_pool.get_sequences()[seq_id]
            assert len(sequence.sequence_data) < max_length

        snapshot.assert_match(filtered_pool.sequence_data.to_csv())
        snapshot.assert_match(filtered_pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "bad_criterion",
        [
            ({"gt": 5, "lt": 3}),  # contradictory range
            ({"ge": 10, "le": 5}),
            ({"gt": 7, "lt": 5}),
        ],
    )
    def test_contradictory_length_criterion(self, bad_criterion):
        """
        Test behavior with contradictory length criterion conditions.
        """
        # Create invalid length criterion
        with pytest.raises(ContradictoryLengthCriterionError):
            _ = LengthCriterion(**bad_criterion)

    @pytest.mark.parametrize(
        "pool_type,length_value",
        [
            ("event", 100),  # very high value
            ("state", 50),  # very high value
            ("interval", 80),  # very high value
        ],
    )
    def test_filter_no_matching_length_criterion(
        self, sequence_pools, pool_type, length_value
    ):
        """
        Test filtering with length criterion that doesn't match any data.
        Should return an empty dataframe.
        """
        pool = sequence_pools[pool_type]

        # Create length criterion for sequences longer than any in the pool
        length_criterion = LengthCriterion(gt=length_value)

        # Apply filter
        filtered_pool = pool.filter(length_criterion, inplace=False)

        # Result should be an empty dataframe
        assert filtered_pool.sequence_data.empty

        # Test with inplace=True
        pool_copy = pool.copy()
        result = pool_copy.filter(length_criterion, inplace=True)
        assert result is None
        assert pool_copy.sequence_data.empty
        assert pool_copy.static_data.empty

    @pytest.mark.parametrize(
        "pool_type",
        [
            ("event"),
            ("state"),
            ("interval"),
        ],
    )
    def test_filter_invalid_level(self, sequence_pools, pool_type):
        """
        Test filtering with length criterion at entity level, which should raise an error.
        """
        pool = sequence_pools[pool_type]
        length_criterion = LengthCriterion(gt=5)

        with pytest.raises(InvalidCriterionError):
            pool.filter(length_criterion, level="entity", inplace=False)

    @pytest.mark.parametrize(
        "pool_type,min_length",
        [
            ("event", 10),
            ("state", 3),
            ("interval", 4),
        ],
    )
    def test_which_length_criterion(
        self, sequence_pools, pool_type, min_length, snapshot
    ):
        """Test which method for length criterion"""
        pool = sequence_pools[pool_type]
        pattern_criterion = LengthCriterion(gt=min_length)
        matching_ids = pool.which(pattern_criterion)
        assert isinstance(matching_ids, set)
        snapshot.assert_match(sorted(matching_ids))

    @pytest.mark.parametrize(
        "pool_type,min_length",
        [
            ("event", 10),
            ("state", 3),
            ("interval", 4),
        ],
    )
    def test_filter_by_length_gt_consistency(
        self, sequence_pools, pool_type, min_length
    ):
        """
        Check filter by length gt with inplace=True and inplace=False produce the same results.
        """
        original_pool = sequence_pools[pool_type]
        length_criterion = LengthCriterion(gt=min_length)

        # Non-inplace filtering
        filtered_pool_non_inplace = original_pool.filter(
            length_criterion, inplace=False
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        # Inplace filtering
        pool_copy = original_pool.copy()
        pool_copy.filter(length_criterion, inplace=True)
        inplace_result = pool_copy.sequence_data

        ## which
        matching_ids = list(original_pool.which(length_criterion))

        # Test consistency
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids

    @pytest.mark.parametrize(
        "pool_type,min_length,max_length",
        [
            ("event", 7, 12),
            ("state", 2, 4),
            ("interval", 3, 6),
        ],
    )
    def test_filter_by_length_range_consistency(
        self, sequence_pools, pool_type, min_length, max_length
    ):
        """
        Check filter by length range with inplace=True and inplace=False produce the same results.
        """
        original_pool = sequence_pools[pool_type]
        length_criterion = LengthCriterion(ge=min_length, le=max_length)

        # Non-inplace filtering
        filtered_pool_non_inplace = original_pool.filter(
            length_criterion, inplace=False
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        # Inplace filtering
        pool_copy = original_pool.copy()
        pool_copy.filter(length_criterion, inplace=True)
        inplace_result = pool_copy.sequence_data

        ## which
        matching_ids = list(original_pool.which(length_criterion))

        # Test consistency
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids

    @pytest.mark.parametrize(
        "pool_type,min_length,max_length",
        [
            ("event", 7, 12),
            ("state", 2, 4),
            ("interval", 3, 6),
        ],
    )
    def test_pattern_sequence_filtering_via_dict_criterion(
        self, sequence_pools, pool_type, min_length, max_length
    ):
        """
        Verify consistency of sequence filtering using criterion defined in a dictionary.
        """
        original_pool = sequence_pools[pool_type]
        length_criterion = {"ge": min_length, "le": max_length}

        # Non-inplace filtering
        filtered_pool_non_inplace = original_pool.filter(
            length_criterion, criterion_type="length", level="sequence", inplace=False
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        # Inplace filtering
        pool_copy = original_pool.copy()
        pool_copy.filter(
            length_criterion, criterion_type="length", level="sequence", inplace=True
        )
        inplace_result = pool_copy.sequence_data

        ## which
        matching_ids = list(
            original_pool.which(length_criterion, criterion_type="length")
        )

        # Test consistency
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids
