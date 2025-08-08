#!/usr/bin/env python3
"""
Axis settings classes for visualization configuration.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer


@viewer
@dataclass
class XAxisSettings:
    """
    X-axis configuration for visualizations.

    Controls all aspects of x-axis display including labels, limits,
    rotation, and automatic date formatting for temporal visualizations.

    Attributes:
        xlabel_rotation (int): X-axis label rotation angle in degrees.
            Useful for long category names or dates. Default is 60.
        xlabel_va (str): Vertical alignment of x-axis labels.
            Options: 'top', 'center', 'bottom'. Default is 'top'.
        xlabel_ha (str): Horizontal alignment of x-axis labels.
            Options: 'left', 'center', 'right'. Default is 'right'.
        show (bool): Whether to display the x-axis. Default is True.
        xlim (tuple, optional): X-axis limits as (min, max).
            Use None for automatic scaling. Default is (None, None).
        xlabel (str, optional): Custom x-axis label text.
            If None, uses default or no label.
        autofmt_xdate (bool): Automatically format x-axis date labels
            for better readability in timeline visualizations. Default is True.
    """

    xlabel_rotation: int = 60
    xlabel_va: str = "top"
    xlabel_ha: str = "right"
    show: bool = True
    xlim: Optional[tuple] = None
    xlabel: Optional[str] = None
    autofmt_xdate: bool = True

    def __post_init__(self):
        if self.xlim is None:
            self.xlim = (None, None)


@viewer
@dataclass
class YAxisSettings:
    """
    Y-axis configuration for visualizations.

    Controls all aspects of y-axis display including labels, limits,
    and alignment. Commonly used for sequence counts, frequencies,
    or categorical displays in visualizations.

    Attributes:
        ylabel_rotation (int): Y-axis label rotation angle in degrees.
            Usually 0 for horizontal text. Default is 0.
        ylabel_va (str): Vertical alignment of y-axis labels.
            Options: 'top', 'center', 'bottom'. Default is 'top'.
        ylabel_ha (str): Horizontal alignment of y-axis labels.
            Options: 'left', 'center', 'right'. Default is 'right'.
        show (bool): Whether to display the y-axis. Default is True.
        ylim (tuple, optional): Y-axis limits as (min, max).
            Use None for automatic scaling. Default is (None, None).
        ylabel (str, optional): Custom y-axis label text.
            If None, uses default or no label.
    """

    ylabel_rotation: int = 0
    ylabel_va: str = "top"
    ylabel_ha: str = "right"
    show: bool = True
    ylim: Optional[tuple] = None
    ylabel: Optional[str] = None

    def __post_init__(self):
        if self.ylim is None:
            self.ylim = (None, None)
