#!/usr/bin/env python3
"""
Legend settings class for visualization configuration.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer


@viewer
@dataclass
class LegendSettings:
    """
    Legend configuration for visualizations.

    Controls legend display, positioning, and appearance to help identify
    different categories, states, or elements in the visualization.

    Attributes:
        loc (str): Legend location within the plot area.
            Common options: 'upper center', 'upper right', 'upper left',
            'lower center', 'lower right', 'lower left', 'center left',
            'center right', 'center'. Default is 'upper center'.
        show (bool): Whether to display the legend. Default is True.
        bbox_to_anchor (tuple, optional): Custom legend positioning
            outside the plot area as (x, y) coordinates. Useful for
            placing legend outside plot boundaries. If None, uses loc.
        title (str, optional): Title text displayed above legend entries.
            If None, no title is shown.
    """

    loc: str = "upper center"
    show: bool = True
    bbox_to_anchor: Optional[tuple] = None
    title: Optional[str] = None
