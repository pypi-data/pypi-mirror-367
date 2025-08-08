#!/usr/bin/env python3
"""
Test query zeroing of trajectory.
"""

import pytest


class TestQueryZeroingTrajectory:
    """
    Test query zeroing of trajectory.
    """

    @pytest.mark.parametrize(
        "seq_name,query_value",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_zeroing_trajectory_pool_from_query(
        self, trajectory_pool, seq_name, query_value, snapshot
    ):
        """
        Test query zeroing of trajectory pool.
        """
        trajectory_pool.zero_from_query(query_value, sequence_name=seq_name)
        snapshot.assert_match(trajectory_pool.t_zero)

    @pytest.mark.parametrize(
        "seq_name,query_value",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_zeroing_single_trajectory_from_query(
        self, trajectory_pool, seq_name, query_value, snapshot
    ):
        """
        Test query zeroing of single trajectory.
        """
        single_trajectory = trajectory_pool[3]
        single_trajectory.zero_from_query(query_value, sequence_name=seq_name)
        snapshot.assert_match(single_trajectory.t_zero)
