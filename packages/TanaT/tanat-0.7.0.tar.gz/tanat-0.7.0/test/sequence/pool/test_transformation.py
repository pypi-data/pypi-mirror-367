#!/usr/bin/env python3
"""
Test sequence transformations on sequence pool.
"""

import pytest

from tanat.mixin.manipulation.data.sequence.transform.exceptions import (
    TransformationError,
)


class TestTransformationMethod:
    """
    Tests for the transformation methods used on sequence pools.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_to_relative_time_tzero_default(self, sequence_pools, pool_type, snapshot):
        """
        Transform a sequence pool to relative time with default T zero.
        """
        pool = sequence_pools[pool_type]
        # T zero is defaulted to the first position in the sequence
        transform_df = pool.to_relative_time(granularity="day")

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_to_relative_rank_tzero_default(self, sequence_pools, pool_type, snapshot):
        """
        Transform a sequence pool to relative rank with default T zero.
        """
        pool = sequence_pools[pool_type]
        # T zero is defaulted to the first position in the sequence
        transform_df = pool.to_relative_rank()

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_to_relative_time_tzero_modified(self, sequence_pools, pool_type, snapshot):
        """
        Transform a sequence pool to relative time with modified T zero.
        """
        pool = sequence_pools[pool_type]
        # T zero is modified to be the third position in the sequence
        pool.zero_from_position(3)
        transform_df = pool.to_relative_time(granularity="day")

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_to_relative_rank_tzero_modified(self, sequence_pools, pool_type, snapshot):
        """
        Transform a sequence pool to relative rank with modified T zero.
        """
        pool = sequence_pools[pool_type]
        # T zero is modified to be the third position in the sequence
        pool.zero_from_position(3)
        transform_df = pool.to_relative_rank()

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_to_relative_time_granularity_modified(
        self, sequence_pools, pool_type, snapshot
    ):
        """
        Transform a sequence pool to relative time with modified granularity.
        """
        pool = sequence_pools[pool_type]
        # T zero is defaulted to the first position in the sequence
        transform_df = pool.to_relative_time(granularity="hour")

        snapshot.assert_match(transform_df.to_csv())

    def test_zero_from_position_out_of_bounds_raises(self, sequence_pools):
        """
        Setting zero_from_position with an out-of-bounds index should raise
        TransformationError on transformation.
        """
        pool = sequence_pools["event"]
        pool.zero_from_position(2000)

        with pytest.raises(TransformationError):
            pool.to_relative_time(granularity="day")

        ## Same for relative rank
        with pytest.raises(TransformationError):
            pool.to_relative_rank()

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    @pytest.mark.parametrize("by_id", [False, True])
    def test_to_occurrence(self, sequence_pools, pool_type, by_id, snapshot):
        """
        Test the to_occurrence transformation on sequence pools with by_id True/False.
        """
        pool = sequence_pools[pool_type]
        transform_df = pool.to_occurrence(by_id=by_id, drop_na=True)

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    @pytest.mark.parametrize("by_id", [False, True])
    def test_to_occurrence_frequency(self, sequence_pools, pool_type, by_id, snapshot):
        """
        Test the to_occurrence_frequency transformation on sequence pools with by_id True/False.
        """
        pool = sequence_pools[pool_type]
        transform_df = pool.to_occurrence_frequency(by_id=by_id, drop_na=True)

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    @pytest.mark.parametrize("by_id", [False, True])
    def test_to_time_spent(self, sequence_pools, pool_type, by_id, snapshot):
        """
        Test the to_time_spent transformation on sequence pools with by_id True/False.
        """
        pool = sequence_pools[pool_type]
        transform_df = pool.to_time_spent(by_id=by_id, granularity="day", drop_na=True)

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize(
        "pool_type,entity_features",
        [
            ("event", ["provider", "FAKE_FEATURES"]),  # FAKE_FEATURES should be skipped
            ("state", ["health_state"]),
            ("interval", ["medication", "administration_route"]),
        ],
    )
    @pytest.mark.parametrize("by_id", [False, True])
    def test_to_time_spent_with_entity_features(
        self, sequence_pools, pool_type, entity_features, by_id, snapshot
    ):
        """
        Test the to_time_spent transformation with entity features and by_id True/False.
        """
        pool = sequence_pools[pool_type]
        transform_df = pool.to_time_spent(
            by_id=by_id,
            granularity="day",
            drop_na=True,
            entity_features=entity_features,
        )

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    @pytest.mark.parametrize("by_id", [False, True])
    def test_to_time_proportion(self, sequence_pools, pool_type, by_id, snapshot):
        """
        Test the to time proportion transformation on sequence pools with by_id True/False.
        """
        pool = sequence_pools[pool_type]
        transform_df = pool.to_time_spent(
            by_id=by_id, granularity="day", proportion=True, drop_na=True
        )

        snapshot.assert_match(transform_df.to_csv())
