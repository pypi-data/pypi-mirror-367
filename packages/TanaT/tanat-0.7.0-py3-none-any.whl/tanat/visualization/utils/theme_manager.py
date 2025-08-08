#!/usr/bin/env python3
"""
Theme manager for sequence visualization.
"""

import logging

import matplotlib.pyplot as plt

LOGGER = logging.getLogger(__name__)


class ThemeManager:
    """
    Manages themes and styling for visualizations.
    """

    def __init__(self, theme=None):
        """
        Initialize theme manager.

        Args:
            theme: Built-in matplotlib theme name or path to .mplstyle file
        """
        self.theme = theme
        self._original_rcparams = None

    def apply(self):
        """Apply the current theme and save original state."""
        if self.theme:
            # Save current rcParams before applying theme
            self._original_rcparams = plt.rcParams.copy()
            plt.style.use(self.theme)
            LOGGER.debug("Applied theme: %s", self.theme)

    def set_theme(self, theme):
        """Set a new theme."""
        self.theme = theme

    def set_builtin_style(self, style_name):
        """Set a built-in matplotlib style."""
        self.theme = style_name

    def reset(self):
        """Reset to original matplotlib state."""
        if self._original_rcparams is not None:
            plt.rcParams.update(self._original_rcparams)
            LOGGER.debug("Reset to original matplotlib settings")
        else:
            plt.style.use("default")
            LOGGER.debug("Reset to default matplotlib style")
