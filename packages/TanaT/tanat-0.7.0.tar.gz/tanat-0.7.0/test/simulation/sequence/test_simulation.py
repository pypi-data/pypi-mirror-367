#!/usr/bin/env python3
"""
Tests for sequence simulation.
"""

import pytest

import pandas as pd
from tanat.dataset.simulation.sequence import SequencePoolMocker, Profile
from tanat.sequence.base.pool import SequencePool


class TestSequenceSimulation:
    """
    Tests for sequence simulation.
    """

    @pytest.mark.parametrize("seq_type", ["state", "event", "interval"])
    def test_simulated_sequence_pool_structure(self, seq_type):
        """Test that the simulated sequence pool has the expected structure."""
        mocker = SequencePoolMocker(seq_type, seed=42)
        mocker.add_profile(Profile())

        pool = mocker()

        # Minimal checks
        assert isinstance(pool, SequencePool)
        assert isinstance(pool.static_data, pd.DataFrame)
        assert isinstance(pool.sequence_data, pd.DataFrame)
