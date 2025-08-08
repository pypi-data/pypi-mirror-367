#!/usr/bin/env python3
"""
Test direct zeroing of sequence.
"""

import pytest

import datetime as dt


@pytest.fixture
def direct_value():
    return "2020-01-01"


class TestDirectZeroingSequence:
    """
    Test direct zeroing of sequence.
    """

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_zeroing_sequence_pool(self, sequence_pools, seq_type, direct_value):
        """
        Test direct zeroing of sequence pool.
        """
        pool = sequence_pools[seq_type]
        pool.t_zero = direct_value
        assert pool.t_zero == dt.datetime.strptime(direct_value, "%Y-%m-%d")

    @pytest.mark.parametrize("seq_type", ["event", "state", "interval"])
    def test_zeroing_single_sequence(self, sequence_pools, seq_type, direct_value):
        """
        Test direct zeroing of single sequence.
        """
        single_sequence = sequence_pools[seq_type][3]
        single_sequence.t_zero = direct_value

        assert single_sequence.t_zero == dt.datetime.strptime(direct_value, "%Y-%m-%d")
