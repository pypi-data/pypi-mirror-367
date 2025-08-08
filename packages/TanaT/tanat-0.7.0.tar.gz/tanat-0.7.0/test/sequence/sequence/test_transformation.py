#!/usr/bin/env python3
"""
Test sequence transformations on unique sequence.
"""

import pytest

from tanat.mixin.manipulation.data.sequence.transform.exceptions import (
    TransformationError,
)


class TestTransformationMethod:
    """
    Tests for the transformation methods used on unique sequences.
    """

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_to_relative_time_tzero_default(self, sequence_pools, seq_type, snapshot):
        """
        Transform a sequence to relative time with default T zero.
        """
        # Get a single sequence from the pool
        sequence = sequence_pools[seq_type][3]
        # T zero is defaulted to the first position in the sequence
        transform_df = sequence.to_relative_time(granularity="day")

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_to_relative_rank_tzero_default(self, sequence_pools, seq_type, snapshot):
        """
        Transform a sequence to relative rank with default T zero.
        """
        # Get a single sequence from the pool
        sequence = sequence_pools[seq_type][3]
        # T zero is defaulted to the first position in the sequence
        transform_df = sequence.to_relative_rank()

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_to_relative_time_tzero_modified(self, sequence_pools, seq_type, snapshot):
        """
        Transform a sequence to relative time with modified T zero.
        """
        # Get a single sequence from the pool
        sequence = sequence_pools[seq_type][3]
        # T zero is modified to be the second position in the sequence
        sequence.zero_from_position(2)
        transform_df = sequence.to_relative_time(granularity="day")

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_to_relative_rank_tzero_modified(self, sequence_pools, seq_type, snapshot):
        """
        Transform a sequence to relative rank with modified T zero.
        """
        # Get a single sequence from the pool
        sequence = sequence_pools[seq_type][3]
        # T zero is modified to be the second position in the sequence
        sequence.zero_from_position(2)
        transform_df = sequence.to_relative_rank()

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_to_relative_time_granularity_modified(
        self, sequence_pools, seq_type, snapshot
    ):
        """
        Transform a sequence to relative time with modified granularity.
        """
        # Get a single sequence from the pool
        sequence = sequence_pools[seq_type][3]
        # T zero is defaulted to the first position in the sequence
        transform_df = sequence.to_relative_time(granularity="hour")

        snapshot.assert_match(transform_df.to_csv())

    def test_zero_from_position_out_of_bounds_raises(self, sequence_pools):
        """
        Setting zero_from_position with an out-of-bounds index should raise
        TransformationError on transformation.
        """
        sequence = sequence_pools["event"][3]
        sequence.zero_from_position(2000)

        with pytest.raises(TransformationError):
            sequence.to_relative_time(granularity="day")

        ## Same for relative rank
        with pytest.raises(TransformationError):
            sequence.to_relative_rank()

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    @pytest.mark.parametrize("by_id", [False, True])
    def test_to_occurrence(self, sequence_pools, seq_type, by_id, snapshot):
        """
        Test the to_occurrence transformation on a single sequence with by_id True/False.
        """
        sequence = sequence_pools[seq_type][3]
        transform_df = sequence.to_occurrence(by_id=by_id, drop_na=True)

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    @pytest.mark.parametrize("by_id", [False, True])
    def test_to_occurrence_frequency(self, sequence_pools, seq_type, by_id, snapshot):
        """
        Test the to_occurrence_frequency transformation on a single sequence with by_id True/False.
        """
        sequence = sequence_pools[seq_type][3]
        transform_df = sequence.to_occurrence_frequency(by_id=by_id, drop_na=True)

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    @pytest.mark.parametrize("by_id", [False, True])
    def test_to_time_spent(self, sequence_pools, seq_type, by_id, snapshot):
        """
        Test the to_time_spent transformation on a single sequence with by_id True/False.
        """
        sequence = sequence_pools[seq_type][3]
        transform_df = sequence.to_time_spent(
            by_id=by_id, granularity="day", drop_na=True
        )

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize(
        "seq_type,entity_features",
        [
            ("event", ["provider", "FAKE_FEATURES"]),  # FAKE FEATURES should be skipped
            ("state", ["health_state"]),
            ("interval", ["medication", "administration_route"]),
        ],
    )
    @pytest.mark.parametrize("by_id", [False, True])
    def test_to_time_spent_with_entity_features(
        self, sequence_pools, seq_type, entity_features, by_id, snapshot
    ):
        """
        Test the to_time_spent transformation with entity features and by_id True/False on a single sequence.
        """
        sequence = sequence_pools[seq_type][3]
        transform_df = sequence.to_time_spent(
            by_id=by_id,
            granularity="day",
            drop_na=True,
            entity_features=entity_features,
        )

        snapshot.assert_match(transform_df.to_csv())

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    @pytest.mark.parametrize("by_id", [False, True])
    def test_to_time_proportion(self, sequence_pools, seq_type, by_id, snapshot):
        """
        Test the to_time_proportion transformation on a single sequence with by_id True/False.
        """
        sequence = sequence_pools[seq_type][3]
        transform_df = sequence.to_time_spent(
            by_id=by_id, granularity="day", proportion=True, drop_na=True
        )

        snapshot.assert_match(transform_df.to_csv())
