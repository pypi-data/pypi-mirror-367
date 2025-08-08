#!/usr/bin/env python3
"""
Timeline visualization settings.
"""

from typing import Optional

from pydantic.dataclasses import dataclass, Field
from pypassist.dataclass.decorators.viewer import viewer

from ....style.base import BaseVizSettings
from ....style.axis import YAxisSettings
from .enum import TimelineStackingMode


@viewer
@dataclass
class TimelineMarkerSettings:
    """
    Timeline marker visual configuration.

    Controls appearance of markers representing events, state transitions,
    and interval boundaries in timeline visualizations.

    Attributes:
        size (float): Marker size. Larger values create more prominent
            markers. Default is 2.
        spacing (float): Vertical distance between markers in same category.
            Controls visual density. Default is 2.2.
        alpha (float): Marker transparency (0-1). 0=transparent, 1=opaque.
            Default is 0.7 for subtle visibility.
        edge_color (Optional[str]): Marker border color. If None, uses
            marker fill color. Specify color name or hex code.
        shape (str): Marker shape symbol. Options include:
            - '*': Star (default, good for events)
            - 'o': Circle (clean, universal)
            - 's': Square (structured appearance)
            - '^': Triangle (directional emphasis)
    """

    size: float = 2
    spacing: float = 2.2
    alpha: float = 0.7
    edge_color: Optional[str] = None
    shape: str = "*"


@viewer
@dataclass
class TimelineAesthetics:
    """
    Aesthetics configuration for timeline visualizations.

    Controls temporal display, sequence organization, and time scaling
    for optimal timeline presentation and pattern analysis.

    Attributes:
        stacking_mode (TimelineStackingMode): Method for organizing
            multiple sequences vertically:
            - BY_CATEGORY: Group sequences by annotation/category
            - FLAT: Each sequence gets its own horizontal row
            - AUTOMATIC: System chooses optimal stacking
            Default is BY_CATEGORY.
        relative_time (bool): Whether to use relative time scaling.
            If True, aligns sequences to common starting point for pattern
            comparison. If False, uses absolute timestamps. Default False.
        granularity (Optional[str]): Time granularity for temporal
            resolution ('day', 'hour', 'week', 'month', etc.).
            If None, uses sequence's natural granularity.
    """

    stacking_mode: TimelineStackingMode = TimelineStackingMode.BY_CATEGORY
    relative_time: bool = False
    granularity: Optional[str] = None


@viewer
@dataclass
class TimelineSequenceVizSettings(BaseVizSettings):
    """
    Complete configuration for timeline visualizations.

    Combines aesthetic settings, marker properties, and base visualization
    settings to create comprehensive timeline configurations. Specialized
    for temporal sequence analysis and pattern visualization.

    Attributes:
        aesthetics (TimelineAesthetics): Timeline display configuration
            including stacking mode, time scaling, and granularity.
        marker (TimelineMarkerSettings): Visual properties for timeline
            markers including size, spacing, transparency, and shape.
        y_axis (YAxisSettings): Y-axis configuration. Hidden by default
            since timeline y-axis typically shows sequence IDs or categories
            rather than meaningful numeric values.
        title (str): Plot title
        colors (Union[str, Dict, List[str]]): Color configuration (palette/mapping/list)
        x_axis (XAxisSettings): X-axis settings (labels, limits, date formatting)
        legend (LegendSettings): Legend configuration (position, title, visibility)

    Note: title, colors, x_axis, and legend are inherited from BaseVizSettings.

    Examples:
        >>> # Basic timeline with default settings
        >>> settings = TimelineSequenceVizSettings()

        >>> # Relative time timeline with custom markers
        >>> settings = TimelineSequenceVizSettings(
        ...     aesthetics=TimelineAesthetics(
        ...         stacking_mode="flat",
        ...         relative_time=True,
        ...         granularity='day'
        ...     ),
        ...     marker=TimelineMarkerSettings(
        ...         size=3, spacing=1.5, shape='o'
        ...     )
        ... )

        >>> # Timeline with visible y-axis and custom title
        >>> settings = TimelineSequenceVizSettings(
        ...     title='Sequence Timeline Analysis',
        ...     y_axis=YAxisSettings(show=True, ylabel='Sequences'),
        ...     aesthetics=TimelineAesthetics(
        ...         stacking_mode="by_category"
        ...     )
        ... )
    """

    aesthetics: TimelineAesthetics = Field(default_factory=TimelineAesthetics)
    marker: TimelineMarkerSettings = Field(default_factory=TimelineMarkerSettings)

    # -- overrides defaults from BaseVizSettings --
    y_axis: YAxisSettings = Field(default_factory=lambda: YAxisSettings(show=False))
