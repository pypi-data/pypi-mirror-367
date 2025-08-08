#!/usr/bin/env python3
"""
Test query  zeroing of sequence.
"""
import pytest


class TestQueryZeroingSequence:
    """
    Test query zeroing of sequence.
    """

    @pytest.mark.parametrize(
        "seq_type,query_value",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_zeroing_sequence_pool_from_query(
        self, sequence_pools, seq_type, query_value, snapshot
    ):
        """
        Test query zeroing of sequence pool.
        """
        pool = sequence_pools[seq_type]
        pool.zero_from_query(query_value)
        snapshot.assert_match(pool.t_zero)

    @pytest.mark.parametrize(
        "seq_type,query_value",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_zeroing_single_sequence_from_query(
        self, sequence_pools, seq_type, query_value, snapshot
    ):
        """
        Test query zeroing of single sequence.
        """
        single_sequence = sequence_pools[seq_type][3]
        single_sequence.zero_from_query(query_value)
        snapshot.assert_match(single_sequence.t_zero)
