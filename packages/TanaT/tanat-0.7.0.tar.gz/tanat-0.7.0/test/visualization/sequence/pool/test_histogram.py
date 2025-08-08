#!/usr/bin/env python3
"""Tests for HistoSequenceViz visualizer."""

import pytest
import matplotlib
from tanat.visualization.sequence.core import SequenceVisualizer
from tanat.visualization.utils.result import VisualizationResult


class TestHistoSequenceViz:
    """Tests for HistoSequenceViz visualization."""

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_histo_draw(self, sequence_pools, pool_type):
        """Test that the figure generated for different types of sequence pools is correct."""
        pool = sequence_pools[pool_type]
        viz = SequenceVisualizer.histogram()
        viz_res = viz.draw(pool)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()

    @pytest.mark.parametrize(
        "pool_type,show_as",
        [("event", "occurrence"), ("state", "time_spent"), ("interval", "frequency")],
    )
    def test_histo_show_as_modes(self, sequence_pools, pool_type, show_as):
        """Test different visualization modes."""
        pool = sequence_pools[pool_type]
        viz = SequenceVisualizer.histogram(show_as=show_as)
        viz_res = viz.draw(pool)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()

    @pytest.mark.parametrize("bar_order", ["ascending", "descending", "alphabetic"])
    def test_histo_bar_order(self, sequence_pools, bar_order):
        """Test that different bar ordering methods work correctly."""
        state_pool = sequence_pools["state"]
        viz = SequenceVisualizer.histogram(bar_order=bar_order)
        viz_res = viz.draw(state_pool)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()

    @pytest.mark.parametrize(
        "theme_style", ["dark_background", "seaborn-v0_8-whitegrid"]
    )
    def test_histo_theme_variations(self, sequence_pools, theme_style):
        """Test that different themes are correctly applied."""
        state_pool = sequence_pools["state"]
        viz = SequenceVisualizer.histogram()
        viz.set_theme(builtin_style=theme_style)
        viz_res = viz.draw(state_pool)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()

    @pytest.mark.parametrize("granularity", ["day", "hour"])
    def test_histo_time_spent_granularity(self, sequence_pools, granularity):
        """Test time_spent mode visualization with different granularities."""
        state_pool = sequence_pools["state"]
        state_pool.granularity = granularity
        viz = SequenceVisualizer.histogram(
            show_as="time_spent", granularity=granularity
        )
        viz_res = viz.draw(state_pool)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        viz_res.close()
