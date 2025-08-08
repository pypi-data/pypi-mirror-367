#!/usr/bin/env python3
"""
Color manager for handling colors.
"""

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


class ColorManager:
    """
    Color manager for handling various color configurations.

    Provides unified color handling for visualizations, supporting multiple
    input formats (dictionaries, lists, matplotlib palettes) and automatic
    color assignment to categories.
    """

    @staticmethod
    def get_colors(categories, colors_config, fallback_color="#808080"):
        """
        Get colors for categories based on configuration.

        Assigns colors to categories using various input formats. Handles
        direct mappings, color lists, and matplotlib palettes with automatic
        fallback for missing categories.

        Args:
            categories (array-like): Category names to assign colors to.
                Can be pandas Series, list, or numpy array.
            colors_config (dict, list, or str): Color configuration:
                - dict: Direct mapping {'category': 'color'}
                - list: Colors to cycle through ['red', 'blue', '#FF5733']
                - str: Matplotlib palette/colormap name ('Set1', 'tab10')
            fallback_color (str): Hex color for unmapped categories in
                dictionary mode. Default is gray (#808080).

        Returns:
            pd.Series: Series of hex colors indexed by input categories.
                Maintains original category order and handles duplicates.
        """
        unique_cats = pd.Series(categories).unique()

        if isinstance(colors_config, dict):
            # Direct mapping
            return pd.Series(categories).map(
                lambda x: colors_config.get(x, fallback_color)
            )

        if isinstance(colors_config, list):
            # Direct color list - cycle if needed
            palette = (colors_config * ((len(unique_cats) // len(colors_config)) + 1))[
                : len(unique_cats)
            ]

        else:  # str
            # Named matplotlib palette/colormap
            palette = ColorManager._get_matplotlib_colors(
                colors_config, len(unique_cats)
            )

        # Create mapping
        color_map = dict(zip(unique_cats, palette))
        return pd.Series(categories).map(color_map)

    @staticmethod
    def _get_matplotlib_colors(name, n_colors):
        """
        Extract colors from matplotlib colormap or palette.

        Handles both discrete palettes (like 'Set1', 'tab10') and continuous
        colormaps (like 'viridis', 'plasma') by sampling appropriate colors.

        Args:
            name (str): Matplotlib colormap/palette name (e.g., 'Set1',
                'viridis', 'tab10').
            n_colors (int): Number of colors needed.

        Returns:
            list: List of hex color strings.
        """
        # Try as colormap/palette
        # cmap = plt.cm.get_cmap(name)
        cmap = plt.colormaps[name]
        if hasattr(cmap, "colors"):
            # Discrete palette (like tab10) - cycle through colors if needed
            palette_colors = [mcolors.to_hex(c) for c in cmap.colors]
            colors = [palette_colors[i % len(palette_colors)] for i in range(n_colors)]
        else:
            # Continuous colormap
            colors = [
                mcolors.to_hex(cmap(i / max(1, n_colors - 1))) for i in range(n_colors)
            ]
        return colors
