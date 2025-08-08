#!/usr/bin/env python3
"""Tests for TimelineSequenceViz visualizer on a single sequence."""

import pytest
import matplotlib
from tanat.visualization.sequence.core import SequenceVisualizer
from tanat.visualization.utils.result import VisualizationResult


class TestTimelineSingleSequenceViz:
    """Tests for TimelineSequenceViz visualization on a single sequence."""

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_timeline_draw(self, sequence_pools, pool_type):
        """Test that the figure generated for different types of sequence is correct."""
        pool = sequence_pools[pool_type]
        sequence = pool[4]
        viz = SequenceVisualizer.timeline()
        viz_res = viz.draw(sequence)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()

    @pytest.mark.parametrize(
        "pool_type,stacking_mode",
        [("event", "FLAT"), ("state", "BY_CATEGORY"), ("interval", "FLAT")],
    )
    def test_timeline_stacking_modes(self, sequence_pools, pool_type, stacking_mode):
        """Test different stacking modes."""
        pool = sequence_pools[pool_type]
        sequence = pool[4]
        viz = SequenceVisualizer.timeline(stacking_mode=stacking_mode)
        viz_res = viz.draw(sequence)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()

    @pytest.mark.parametrize(
        "theme_style", ["dark_background", "seaborn-v0_8-whitegrid"]
    )
    def test_timeline_theme_variations(self, sequence_pools, theme_style):
        """Test that different themes are correctly applied."""
        state_pool = sequence_pools["state"]
        sequence = state_pool[4]
        viz = SequenceVisualizer.timeline()
        viz.set_theme(theme_style)
        viz_res = viz.draw(sequence)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_timeline_custom_settings(self, sequence_pools, pool_type):
        """Test with custom settings for TimelineSequenceViz."""
        pool = sequence_pools[pool_type]
        sequence = pool[4]
        viz = SequenceVisualizer.timeline()
        custom_settings = {
            "stacking_mode": "FLAT",
        }
        viz_res = viz.draw(sequence, aesthetics=custom_settings)
        assert isinstance(viz_res, VisualizationResult)
        fig = viz_res.fig
        assert isinstance(fig, matplotlib.figure.Figure)
        # close the figure
        viz_res.close()
