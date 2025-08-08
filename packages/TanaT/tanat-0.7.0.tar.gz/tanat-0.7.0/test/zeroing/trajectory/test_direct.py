#!/usr/bin/env python3
"""
Test direct zeroing of trajectory.
"""

import pytest

import datetime as dt


@pytest.fixture
def direct_value():
    return "2020-01-01"


class TestDirectZeroingTrajectory:
    """
    Test direct zeroing of trajectory.
    """

    def test_zeroing_trajectory_pool(self, trajectory_pool, direct_value):
        """
        Test direct zeroing of trajectory pool.
        """
        trajectory_pool.t_zero = direct_value
        assert trajectory_pool.t_zero == dt.datetime.strptime(direct_value, "%Y-%m-%d")

    def test_zeroing_single_trajectory(self, trajectory_pool, direct_value):
        """
        Test direct zeroing of single trajectory.
        """
        single_trajectory = trajectory_pool[3]
        single_trajectory.t_zero = direct_value
        assert single_trajectory.t_zero == dt.datetime.strptime(
            direct_value, "%Y-%m-%d"
        )
