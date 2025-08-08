#!/usr/bin/env python3
"""
Test position zeroing of sequence.
"""

import pytest


@pytest.fixture
def position_value():
    """
    Fixture for position value.
    """
    return 2


class TestPositionZeroingSequence:
    """
    Test position zeroing of sequence.
    """

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_zeroing_sequence_pool_from_position(
        self, sequence_pools, seq_type, position_value, snapshot
    ):
        """
        Test position zeroing of sequence pool.
        """
        pool = sequence_pools[seq_type]
        pool.zero_from_position(position_value)
        snapshot.assert_match(pool.t_zero)

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_zeroing_single_sequence_from_position(
        self, sequence_pools, seq_type, position_value, snapshot
    ):
        """
        Test position zeroing of single sequence.
        """
        single_sequence = sequence_pools[seq_type][3]
        single_sequence.zero_from_position(position_value)
        snapshot.assert_match(single_sequence.t_zero)
