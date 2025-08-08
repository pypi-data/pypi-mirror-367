#!/usr/bin/env python3
"""
Distribution visualization settings.
"""

from typing import Optional

from pydantic.dataclasses import dataclass, Field
from pypassist.dataclass.decorators.viewer import viewer

from ....style.base import BaseVizSettings
from .....time.granularity import Granularity
from .enum import DistributionMode


@viewer
@dataclass
class DistributionMarkerSettings:
    """
    Distribution marker visual configuration.

    Controls the visual appearance of distribution plots including
    transparency and styling for area charts or line plots.

    Attributes:
        alpha (float): Transparency of distribution plot areas/lines (0-1).
            0 = fully transparent, 1 = fully opaque. Default is 0.7.
            Lower values allow overlapping distributions to be visible.

    Examples:
        >>> # Semi-transparent distribution for layering
        >>> marker = DistributionMarkerSettings(alpha=0.5)

        >>> # Fully opaque distribution
        >>> marker = DistributionMarkerSettings(alpha=1.0)
    """

    alpha: float = 0.7


@viewer
@dataclass
class DistributionAesthetics:
    """
    Aesthetics configuration for distribution visualizations.

    Controls how temporal distributions are calculated, displayed, and
    organized across time periods for pattern analysis.

    Attributes:
        mode (DistributionMode): Distribution calculation method.
            - PERCENTAGE: Values as percentages (0-100%)
            - COUNT: Raw counts per time period
            - PROPORTION: Decimal proportions (0-1)
            Default is PERCENTAGE.
        stacked (bool): Whether to stack distributions vertically.
            If True, creates stacked area chart showing cumulative patterns.
            If False, displays separate lines/areas for each category.
            Default is True.
        granularity (Granularity, optional): Time resolution for binning.
            Controls how time periods are defined (day, week, month, etc.).
            If None, uses sequence's natural granularity.
        time_relative (bool): Whether to use relative time scale.
            If True, aligns all sequences to common starting point.
            If False, uses absolute timestamps. Default is False.

    Examples:
        >>> # Stacked percentage distribution with daily bins
        >>> aesthetics = DistributionAesthetics(
        ...     mode=DistributionMode.PERCENTAGE,
        ...     stacked=True,
        ...     granularity=Granularity.DAY
        ... )

        >>> # Unstacked count distribution with relative time
        >>> aesthetics = DistributionAesthetics(
        ...     mode=DistributionMode.COUNT,
        ...     stacked=False,
        ...     time_relative=True
        ... )
    """

    mode: DistributionMode = DistributionMode.PERCENTAGE
    stacked: bool = True
    granularity: Optional[Granularity] = None
    time_relative: bool = False


@viewer
@dataclass
class DistributionSequenceVizSettings(BaseVizSettings):
    """
    Complete configuration for distribution visualizations.

    Combines aesthetic settings, marker properties, and base visualization
    settings to create comprehensive distribution plot configurations.

    Attributes:
        aesthetics (DistributionAesthetics): Distribution calculation and
            display configuration including mode, stacking, and time settings.
        marker (DistributionMarkerSettings): Visual properties for
            distribution areas/lines including transparency.
        title (str): Plot title
        colors (Union[str, Dict, List[str]]): Color configuration (palette/mapping/list)
        x_axis (AxisSettings): X-axis settings (labels, limits, formatting)
        y_axis (AxisSettings): Y-axis settings (labels, limits, formatting)
        legend (LegendSettings): Legend configuration (position, title, visibility)

    Note: title, colors, x_axis, y_axis, and legend are inherited from BaseVizSettings.

    Examples:
        >>> # Basic distribution settings
        >>> settings = DistributionSequenceVizSettings()

        >>> # Custom percentage distribution with transparency
        >>> settings = DistributionSequenceVizSettings(
        ...     aesthetics=DistributionAesthetics(
        ...         mode="percentage",
        ...         stacked=True
        ...     ),
        ...     marker=DistributionMarkerSettings(alpha=0.8)
        ... )

        >>> # Count distribution with relative time
        >>> settings = DistributionSequenceVizSettings(
        ...     aesthetics=DistributionAesthetics(
        ...         mode="count",
        ...         time_relative=True,
        ...         stacked=False
        ...     )
        ... )
    """

    aesthetics: DistributionAesthetics = Field(default_factory=DistributionAesthetics)
    marker: DistributionMarkerSettings = Field(
        default_factory=DistributionMarkerSettings
    )
