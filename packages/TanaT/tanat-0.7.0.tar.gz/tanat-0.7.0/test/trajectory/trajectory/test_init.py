#!/usr/bin/env python3
"""
Test initialization of trajectory.
"""

from tanat.trajectory.trajectory import Trajectory


class TestInitTrajectory:
    """
    Tests for Trajectory initialization.
    """

    def test_initialize_trajectory(self, sequence_pools):
        """
        Test trajectory initialization.
        """
        traj = Trajectory(id_value=3, sequence_pools=sequence_pools)
        assert sorted(list(traj.sequences.keys())) == ["event", "interval", "state"]
