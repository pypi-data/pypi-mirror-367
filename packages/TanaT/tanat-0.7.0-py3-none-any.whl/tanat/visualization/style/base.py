#!/usr/bin/env python3
"""
Base visualization settings classes.
"""

from typing import Optional, Union

from pydantic.dataclasses import dataclass, Field
from pypassist.fallback.typing import List, Dict

from .axis import XAxisSettings, YAxisSettings
from .legend import LegendSettings


@dataclass
class BaseVizSettings:
    """
    Common visualization settings for all sequence visualizations.

    Provides foundational configuration options shared across timeline,
    histogram, and distribution visualizations. Serves as base class
    for specialized visualization settings.

    Attributes:
        title (str, optional): Main title displayed at the top of the plot.
            If None, no title is shown.
        colors (str, dict, or list): Color configuration for visualization:
            - str: Matplotlib colormap/palette name ('Set1', 'tab10', 'viridis')
            - dict: Direct category-to-color mapping {'A': 'red', 'B': 'blue'}
            - list: List of colors to cycle through ['red', 'blue', 'green']
            Default is 'tab10' (matplotlib's standard 10-color palette).
        x_axis (XAxisSettings): X-axis configuration including labels,
            limits, rotation, and formatting options.
        y_axis (YAxisSettings): Y-axis configuration including labels,
            limits, and display options.
        legend (LegendSettings): Legend configuration including position,
            title, and visibility settings.
    """

    title: Optional[str] = None
    colors: Union[str, Dict, List[str]] = "tab10"
    x_axis: XAxisSettings = Field(default_factory=XAxisSettings)
    y_axis: YAxisSettings = Field(default_factory=YAxisSettings)
    legend: LegendSettings = Field(default_factory=LegendSettings)
