#!/usr/bin/env python3
"""
Test position zeroing of trajectory.
"""

import pytest


@pytest.fixture
def position_value():
    """
    Fixture for position value.
    """
    return 2


class TestPositionZeroingTrajectory:
    """
    Test position zeroing of trajectory.
    """

    def test_zeroing_trajectory_pool_from_position(
        self, trajectory_pool, position_value, snapshot
    ):
        """
        Test position zeroing of trajectory pool.
        """
        trajectory_pool.zero_from_position(position_value)
        snapshot.assert_match(trajectory_pool.t_zero)

    def test_zeroing_single_trajectory_from_position(
        self, trajectory_pool, position_value, snapshot
    ):
        """
        Test position zeroing of single trajectory.
        """
        single_trajectory = trajectory_pool[3]
        single_trajectory.zero_from_position(position_value)
        snapshot.assert_match(single_trajectory.t_zero)
