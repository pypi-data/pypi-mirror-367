#!/usr/bin/env python3
"""
Visualization result class for chainable configuration.
"""


import logging

import matplotlib.pyplot as plt

LOGGER = logging.getLogger(__name__)


class VisualizationResult:
    """
    Result object for chainable visualization display and export.

    Provides methods to display, save, and further configure visualizations
    after they have been created. Supports method chaining and automatic
    theme cleanup.

    Attributes:
        fig: Matplotlib figure object.
        ax: Matplotlib axes object.
        theme_manager: Optional theme manager for cleanup.
    """

    def __init__(self, fig, ax, theme_manager=None):
        """
        Initialize visualization result.

        Args:
            fig: Matplotlib figure object.
            ax: Matplotlib axes object.
            theme_manager: Optional theme manager for cleanup.
        """
        self.fig = fig
        self.ax = ax
        self.theme_manager = theme_manager

    def show(self, tight_layout=True):
        """
        Display the visualization.

        Shows the matplotlib figure in the current environment (Jupyter,
        IDE, etc.). Automatically applies tight layout and cleans up themes.

        Args:
            tight_layout (bool): Whether to apply tight layout for better
                spacing. Recommended for most visualizations.

        Returns:
            self: Chainable method for fluent interface.
        """
        if tight_layout:
            plt.tight_layout()
        plt.show()

        # Reset theme after showing to prevent persistence
        if self.theme_manager:
            self.theme_manager.reset()

        return self

    def save(self, filepath, dpi=300, **kwargs):
        """
        Save the visualization to file.

        Exports the figure to various formats (PNG, PDF, SVG, etc.) based
        on file extension. High DPI default for publication quality.

        Args:
            filepath (str): Output file path. File format determined by
                extension (.png, .pdf, .svg, etc.).
            dpi (int): Resolution in dots per inch for raster formats.
                300 DPI recommended for publications.
            **kwargs: Additional matplotlib savefig arguments (bbox_inches,
                facecolor, edgecolor, etc.).

        Returns:
            self: Chainable method for fluent interface.
        """
        self.fig.savefig(filepath, dpi=dpi, **kwargs)

        # Reset theme after saving to prevent persistence
        if self.theme_manager:
            self.theme_manager.reset()

        return self

    def close(self):
        """
        Close the figure to free resources.

        Properly closes the matplotlib figure and frees memory. Important
        for preventing memory leaks in scripts that create many plots.

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Close after saving
            >>> result.save('plot.png').close()

            >>> # Close without displaying
            >>> result.close()
        """
        plt.close(self.fig)

        # Reset theme after closing to prevent persistence
        if self.theme_manager:
            self.theme_manager.reset()

        return self

    def grid(self, show=True, **kwargs):
        """
        Configure grid display.

        Adds or removes grid lines to improve plot readability. Chainable
        method for post-creation configuration.

        Args:
            show (bool): Whether to display grid lines.
            **kwargs: Additional matplotlib grid arguments:
                - alpha: Grid transparency (0-1)
                - linestyle: Grid line style ('-', '--', ':', etc.)
                - linewidth: Grid line width
                - color: Grid color

        Returns:
            self: Chainable method for fluent interface.
        """
        self.ax.grid(show, **kwargs)
        return self

    def __repr__(self):
        """
        Auto-display and close visualization in interactive environments.

        Automatically shows the plot and closes it to free resources.
        Perfect for Jupyter notebooks and interactive exploration.
        Logs the action for debugging purposes.
        """
        # Auto-display
        self.show(tight_layout=True)
        # Auto-cleanup
        self.close()
        LOGGER.debug(
            "VisualizationResults.__repr__: visualization displayed and closed automatically"
        )
        return ""
