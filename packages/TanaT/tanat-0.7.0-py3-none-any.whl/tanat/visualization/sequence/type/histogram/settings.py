#!/usr/bin/env python3
"""
Histogram visualization settings.
"""

from typing import Optional

from pydantic.dataclasses import dataclass, Field
from pypassist.dataclass.decorators.viewer import viewer

from .....time.granularity import Granularity
from ....style.base import BaseVizSettings
from ....style.legend import LegendSettings
from .enum import HistoBarOrder, HistoShowAs, HistoOrientation


@viewer
@dataclass
class HistoMarkerSettings:
    """
    Histogram bar visual configuration.

    Controls the appearance of histogram bars including transparency
    and border styling for optimal visual presentation.

    Attributes:
        alpha (float): Transparency of histogram bars (0-1).
            0 = fully transparent, 1 = fully opaque. Default is 0.7.
            Useful for showing overlapping patterns or subtle styling.
        edge_color (str, optional): Color of bar borders/edges.
            If None, uses the same color as bar fill. Specify color
            name, hex code, or 'black'/'white' for distinct borders.
    """

    alpha: float = 0.7
    edge_color: Optional[str] = None


@viewer
@dataclass
class HistoAesthetics:
    """
    Aesthetics configuration for histogram visualizations.

    Controls how sequence data is aggregated, displayed, and organized
    in histogram format for frequency and duration analysis.

    Attributes:
        show_as (HistoShowAs): Data aggregation method for bars.
            - OCCURRENCE: Raw occurrence counts per category
            - FREQUENCY: Relative frequencies or rates
            - TIME_SPENT: Duration spent in states/intervals
            Default is FREQUENCY.
        granularity (Granularity, optional): Time resolution for duration
            calculations when show_as=TIME_SPENT. If None, uses sequence's
            natural granularity.
        bar_order (HistoBarOrder): Sorting method for histogram bars.
            - ALPHABETIC: Sort by category name alphabetically
            - ASCENDING: Sort by value (low to high)
            - DESCENDING: Sort by value (high to low)
            Default is ALPHABETIC.
        orientation (HistoOrientation): Bar display orientation.
            - VERTICAL: Traditional vertical bars (categories on x-axis)
            - HORIZONTAL: Horizontal bars (categories on y-axis)
            Default is VERTICAL.
    """

    show_as: HistoShowAs = HistoShowAs.FREQUENCY
    granularity: Optional[Granularity] = None
    bar_order: HistoBarOrder = HistoBarOrder.ALPHABETIC
    orientation: HistoOrientation = HistoOrientation.VERTICAL


@viewer
@dataclass
class HistoSequenceVizSettings(BaseVizSettings):
    """
    Complete configuration for histogram visualizations.

    Combines aesthetic settings, marker properties, and base visualization
    settings to create comprehensive histogram configurations. Specialized
    for frequency analysis and duration comparisons.

    Attributes:
        aesthetics (HistoAesthetics): Histogram calculation and display
            configuration including aggregation method, ordering, and
            orientation.
        marker (HistoMarkerSettings): Visual properties for histogram bars
            including transparency and border styling.
        legend (LegendSettings): Legend configuration. Hidden by default
            since histograms often don't need legends for single-category
            analysis.
        title (str): Plot title
        colors (Union[str, Dict, List[str]]): Color configuration (palette/mapping/list)
        x_axis (XAxisSettings): X-axis settings (labels, limits, formatting)
        y_axis (YAxisSettings): Y-axis settings (labels, limits, formatting)

    Note: title, colors, x_axis, y_axis, and legend are inherited from BaseVizSettings

    Examples:
        >>> # Basic frequency histogram
        >>> settings = HistoSequenceVizSettings()

        >>> # Time spent histogram with custom styling
        >>> settings = HistoSequenceVizSettings(
        ...     aesthetics=HistoAesthetics(
        ...         show_as="time_spent",
        ...         bar_order="descending",
        ...         orientation="horizontal"
        ...     ),
        ...     marker=HistoMarkerSettings(alpha=0.9, edge_color="black")
        ... )

        >>> # Occurrence histogram with visible legend
        >>> settings = HistoSequenceVizSettings(
        ...     aesthetics=HistoAesthetics(show_as="occurrence"),
        ...     legend=LegendSettings(show=True, title="Categories")
        ... )
    """

    aesthetics: HistoAesthetics = Field(default_factory=HistoAesthetics)
    marker: HistoMarkerSettings = Field(default_factory=HistoMarkerSettings)
    ## -- overrides default from BaseVizSettings -- ##
    legend: LegendSettings = Field(default_factory=lambda: LegendSettings(show=False))
