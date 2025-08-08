#!/usr/bin/env python3
"""Tests for DistribStateSequenceViz visualizer on a single sequence."""

import pytest
import matplotlib
from tanat.visualization.sequence.core import SequenceVisualizer
from tanat.visualization.utils.result import VisualizationResult


class TestDistribStateSingleSequenceViz:
    """Tests for DistribStateSequenceViz visualization on a single sequence.."""

    def test_distrib_draw(self, sequence_pools):
        """Test that the figure generated for state sequence is correct."""
        state_pool = sequence_pools["state"]
        state_sequence = state_pool[4]
        viz = SequenceVisualizer.distribution(granularity="day")
        viz_res = viz.draw(state_sequence)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()

    @pytest.mark.parametrize(
        "theme_style", ["dark_background", "seaborn-v0_8-whitegrid"]
    )
    def test_distrib_theme_variations(self, sequence_pools, theme_style):
        """Test that different themes are correctly applied."""
        state_pool = sequence_pools["state"]
        state_sequence = state_pool[4]
        viz = SequenceVisualizer.distribution(granularity="day")
        viz.set_theme(theme_style)
        viz_res = viz.draw(state_sequence)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()

    @pytest.mark.parametrize(
        "granularity",
        ["DAY", "HOUR", "WEEK"],
    )
    def test_distrib_granularity(self, sequence_pools, granularity):
        """Test distribution visualization with explicit granularity settings."""
        state_pool = sequence_pools["state"]
        state_sequence = state_pool[4]
        viz = SequenceVisualizer.distribution(granularity=granularity)
        # Draw the visualization with the specified granularity
        viz_res = viz.draw(state_sequence)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()
