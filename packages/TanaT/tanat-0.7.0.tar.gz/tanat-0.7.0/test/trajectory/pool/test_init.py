#!/usr/bin/env python3
"""
Test initialization of trajectory pool.
"""

from tanat.trajectory.pool import TrajectoryPool


class TestInitTrajectoryPool:
    """
    Tests for TrajectoryPool initialization and sequence pool addition.
    """

    def test_initialize_empty_pool(self):
        """
        Test that `init_empty()` creates a TrajectoryPool with no sequence pools.
        """
        traj_pool = TrajectoryPool.init_empty()

        assert isinstance(traj_pool, TrajectoryPool)
        assert traj_pool.sequence_pools == {}

    def test_add_multiple_sequence_pools(self, sequence_pools):
        """
        Test that sequence pools can be added in a chained fashion using `add_sequence_pool()`.
        """
        traj_pool = TrajectoryPool.init_empty()

        traj_pool.add_sequence_pool(sequence_pools["event"], "event").add_sequence_pool(
            sequence_pools["interval"], "interval"
        ).add_sequence_pool(sequence_pools["state"], "state")

        assert isinstance(traj_pool, TrajectoryPool)
        assert sorted(list(traj_pool.sequence_pools.keys())) == [
            "event",
            "interval",
            "state",
        ]
