#!/usr/bin/env python3
"""
Sequence visualization core class.
"""

import logging
import copy

from .base.builder import BaseSequenceVizBuilder
from ..utils.theme_manager import ThemeManager
from ..utils.result import VisualizationResult
from ...sequence.base.sequence import Sequence
from ...sequence.base.pool import SequencePool

LOGGER = logging.getLogger(__name__)


class SequenceVisualizer:
    """
    Main entry point for sequence visualization.

    Provides a unified, chainable API for creating different types of sequence 
    visualizations including timelines, histograms, and distributions. 
    Follows a fluent interface pattern for configuration.

    The visualizer supports three main visualization types:
    - Timeline: Shows sequences over time with temporal alignment
    - Histogram: Displays frequency/duration distributions 
    - Distribution: Shows state distributions across time periods

    Examples:
        >>> # Create timeline with custom configuration
        >>> SequenceVisualizer.timeline(relative_time=True) \\
        ...     .colors('Set1') \\
        ...     .legend(show=True, title='Events') \\
        ...     .draw(sequence_pool) \\
        ...     .show()

        >>> # Create histogram with occurrence counts
        >>> SequenceVisualizer.histogram(show_as='occurrence') \\
        ...     .title('Event Frequencies') \\
        ...     .draw(sequence_pool) \\
        ...     .show()

        >>> # Create stacked distribution plot
        >>> SequenceVisualizer.distribution(stacked=True) \\
        ...     .marker(alpha=0.8) \\
        ...     .draw(state_pool) \\
        ...     .show()
    """

    def __init__(self, viz_type, settings=None, theme=None):
        """
        Initialize the sequence visualizer.

        Creates a visualizer instance for a specific visualization type
        with optional custom settings and theme configuration.

        Args:
            viz_type (str): Visualization type ('timeline', 'histogram',
                'distribution').
            settings (dict, optional): Visualization-specific settings
                to override defaults.
            theme (str, optional): Built-in matplotlib theme name
                (e.g., 'dark_background') or path to .mplstyle file.

        Examples:
            >>> # Basic timeline visualizer
            >>> viz = SequenceVisualizer('timeline')

            >>> # Timeline with custom settings and dark theme
            >>> settings = {'aesthetics': {'relative_time': True}}
            >>> viz = SequenceVisualizer('timeline', settings,
            ...                          'dark_background')
        """
        self.viz_type = viz_type
        self._builder = BaseSequenceVizBuilder.init(viz_type, settings)
        self.theme_manager = ThemeManager(theme) if theme else None
        self._original_settings = self._copy_settings()

    def _copy_settings(self):
        """
        Create a copy of the current settings.

        Returns:
            A copy of the current settings object.
        """
        return copy.deepcopy(self.settings)

    @property
    def settings(self):
        """
        Get current visualization settings.

        Returns:
            Settings object with current configuration values for the
            visualization type (timeline/histogram/distribution).
        """
        return self._builder.settings

    def update_settings(self, settings=None, **kwargs):
        """
        Update settings by delegating to the builder.

        Args:
            settings: New settings object to update from
            **kwargs: Individual settings to update using dot notation
        """
        self._builder.update_settings(settings=settings, **kwargs)
        self._original_settings = self._copy_settings()

    def _tmp_update_settings(self, settings=None, **kwargs):
        """
        Temporary method to update settings without affecting original settings.

        Args:
            settings: New settings object to update from
            **kwargs: Individual settings to update using dot notation
        """
        self._builder.update_settings(settings=settings, **kwargs)

    def view_settings(self, format_type="yaml", **kwargs):
        """
        Display current visualization settings.

        Shows all configuration options for the current visualization type
        in a formatted, human-readable way.

        Args:
            format_type (str): Display format ('yaml', 'json', 'dict').
            **kwargs: Additional formatting options.

        Returns:
            Formatted settings display (depends on format_type).

        Examples:
            >>> # View settings in YAML format (default)
            >>> viz.view_settings()

            >>> # View settings as JSON
            >>> viz.view_settings('json')
        """
        return self._builder.view_settings(format_type=format_type, **kwargs)

    def draw(self, sequence_or_pool, drop_na=True, entity_features=None, **kwargs):
        """
        Create visualization from sequence data.

        Main method to generate the visualization. Prepares data, applies
        theme settings, and renders the plot based on current configuration.

        Args:
            sequence_or_pool (Sequence or SequencePool): Data to visualize.
            drop_na (bool): Whether to exclude rows with missing values.
            entity_features (list, optional): Specific entity features to
                include. If None, uses all available features.
            **kwargs: Additional settings overrides for this draw operation.

        Returns:
            VisualizationResult: Object with figure, axis, and display methods.

        Examples:
            >>> # Basic visualization
            >>> result = viz.draw(sequence_pool)
            >>> result.show()

            >>> # Exclude missing data and select specific features
            >>> result = viz.draw(sequence_pool, drop_na=True,
            ...                   entity_features=['state', 'activity'])

            >>> # Override settings for this draw only
            >>> result = viz.draw(sequence_pool, stacking_mode='flat')
        """
        self._validate_sequence(sequence_or_pool)

        # Apply theme if set
        if self.theme_manager:
            self.theme_manager.apply()

        # Prepare data with explicit parameters
        data = self._builder.prepare_data(
            sequence_or_pool, drop_na=drop_na, entity_features=entity_features, **kwargs
        )

        # Create figure
        fig, ax = self._builder.create_figure()

        # render visualization
        self._builder.render(ax, data, **kwargs)

        result = VisualizationResult(fig, ax, self.theme_manager)

        # Reset builder to original settings after rendering
        # This allows reusing the same visualizer instance without side effects
        self._reset_builder_settings()

        return result

    def _reset_builder_settings(self):
        """Reset builder to original settings."""
        self._builder.update_settings(settings=self._original_settings)

    def prepare_data(
        self, sequence_or_pool, drop_na=True, entity_features=None, **kwargs
    ):
        """
        Prepare sequence data for visualization without rendering.

        Args:
            sequence_or_pool: Sequence or SequencePool to prepare
            drop_na: Whether to drop rows with missing values
            entity_features: Specific entity features to include
            **kwargs: Additional keyword arguments for settings overrides

        """
        return self._builder.prepare_data(
            sequence_or_pool, drop_na=drop_na, entity_features=entity_features, **kwargs
        )

    def set_theme(self, theme=None, builtin_style=None):
        """
        Configure visualization theme.

        Sets matplotlib style theme for the visualization. Can use built-in
        matplotlib styles or custom theme configurations.

        Args:
            theme (dict, optional): Custom theme settings with style
                properties (colors, fonts, etc.).
            builtin_style (str, optional): Built-in matplotlib style name
                (e.g., 'seaborn', 'ggplot', 'dark_background').

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Use built-in dark theme
            >>> viz.set_theme(builtin_style='dark_background')

            >>> # Use seaborn style
            >>> viz.set_theme(builtin_style='seaborn')

            >>> # Custom theme (chainable)
            >>> viz.set_theme(builtin_style='ggplot').draw(data).show()
        """
        if self.theme_manager is None:
            self.theme_manager = ThemeManager()

        if builtin_style:
            self.theme_manager.set_builtin_style(builtin_style)
        elif theme:
            self.theme_manager.set_theme(theme)

        return self

    def _validate_sequence(self, sequence_or_pool):
        """Validate the input sequence."""
        if not isinstance(sequence_or_pool, (Sequence, SequencePool)):
            raise ValueError(
                f"Invalid sequence type: expected Sequence or SequencePool, "
                f"got {type(sequence_or_pool).__name__}"
            )

    @classmethod
    def timeline(
        cls,
        stacking_mode="by_category",
        relative_time=False,
        granularity=None,
    ):
        """
        Create timeline visualizer.

        Timeline visualizations show sequences over time with temporal
        alignment. Useful for showing event occurrences, state durations,
        and interval relationships across time.

        Args:
            stacking_mode (str): How to stack multiple sequences:
                - 'by_category': Stack by entity categories
                - 'flat': All sequences on separate rows
                - 'automatic': Choose based on data
            relative_time (bool): Whether to use relative time scale.
                If True, aligns sequences to a common starting point.
            granularity (str, optional): Time granularity ('day', 'hour',
                'week', etc.). If None, uses data's natural granularity.

        Returns:
            SequenceVisualizer: Configured timeline visualizer.

        Examples:
            >>> # Basic timeline with category stacking
            >>> SequenceVisualizer.timeline()

            >>> # Flat timeline with relative time
            >>> SequenceVisualizer.timeline(stacking_mode='flat',
            ...                             relative_time=True)

            >>> # Daily granularity timeline
            >>> SequenceVisualizer.timeline(granularity='day')
        """
        settings = {
            "aesthetics": {
                "relative_time": relative_time,
                "granularity": granularity,
                "stacking_mode": stacking_mode,
            }
        }
        return cls("timeline", settings)

    @classmethod
    def histogram(
        cls,
        show_as="frequency",
        bar_order="alphabetic",
        orientation="vertical",
        granularity=None,
    ):
        """
        Create histogram visualizer.

        Histogram visualizations show frequency or duration distributions
        for sequence elements. Useful for analyzing occurrence patterns,
        time spent in states, or event frequencies.

        Args:
            show_as (str): What to display:
                - 'frequency'/'occurrence': Count occurrences
                - 'time_spent': Duration in states/intervals
            bar_order (str): How to order bars:
                - 'alphabetic': Sort by entity names
                - 'ascending': Sort by values (low to high)
                - 'descending': Sort by values (high to low)
            orientation (str): Bar orientation ('vertical' or 'horizontal').
            granularity (str, optional): Time granularity for time_spent mode.

        Returns:
            SequenceVisualizer: Configured histogram visualizer.

        Examples:
            >>> # Basic occurrence histogram
            >>> SequenceVisualizer.histogram()

            >>> # Time spent histogram, descending order
            >>> SequenceVisualizer.histogram(show_as='time_spent',
            ...                               bar_order='descending')

            >>> # Horizontal histogram
            >>> SequenceVisualizer.histogram(orientation='horizontal')
        """
        settings = {
            "aesthetics": {
                "show_as": show_as,
                "bar_order": bar_order,
                "orientation": orientation,
                "granularity": granularity,
            }
        }
        return cls("histogram", settings)

    @classmethod
    def distribution(
        cls,
        distribution_type="percentage",
        relative_time=False,
        stacked=True,
        granularity=None,
    ):
        """
        Create distribution visualizer.

        Distribution visualizations show how states or events are distributed
        across time periods. Useful for temporal pattern analysis and
        comparing proportions over time.

        Args:
            distribution_type (str): Distribution calculation:
                - 'percentage': Values as percentages (0-100)
                - 'proportion': Values as proportions (0-1)
                - 'count': Raw counts
            relative_time (bool): Whether to use relative time scale.
            stacked (bool): Whether to stack distributions. If False,
                shows separate lines/areas for each category.
            granularity (str, optional): Time period granularity
                ('day', 'week', 'month', etc.).

        Returns:
            SequenceVisualizer: Configured distribution visualizer.

        Examples:
            >>> # Basic stacked percentage distribution
            >>> SequenceVisualizer.distribution()

            >>> # Count distribution with relative time
            >>> SequenceVisualizer.distribution(distribution_type='count',
            ...                                  relative_time=True)

            >>> # Unstacked weekly proportions
            >>> SequenceVisualizer.distribution(distribution_type='proportion',
            ...                                  stacked=False,
            ...                                  granularity='week')
        """
        settings = {
            "aesthetics": {
                "mode": distribution_type,
                "granularity": granularity,
                "stacked": stacked,
                "relative_time": relative_time,
            }
        }
        return cls("distribution", settings)

    # Pipe-like interface for chaining operations
    def legend(self, show=True, title=None, loc="upper center", bbox_to_anchor=None):
        """
        Configure legend settings.

        Controls legend display, positioning, and appearance for the
        visualization. Chainable method for fluent interface.

        Args:
            show (bool): Whether to display the legend.
            title (str, optional): Legend title text. If None, no title.
            loc (str): Legend location ('upper center', 'upper right', 
                'lower left', etc.).
            bbox_to_anchor (tuple, optional): Precise legend positioning
                as (x, y) coordinates.

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Basic legend with title
            >>> viz.legend(show=True, title='States')

            >>> # Legend in upper right corner
            >>> viz.legend(loc='upper right')

            >>> # Custom positioned legend (chainable)
            >>> viz.legend(title='Events', loc='upper left') \\
            ...    .draw(data).show()
        """
        legend_settings = {"show": show, "loc": loc}

        if title is not None:
            legend_settings["title"] = title

        if bbox_to_anchor is not None:
            legend_settings["bbox_to_anchor"] = bbox_to_anchor

        self._tmp_update_settings(legend=legend_settings)
        return self

    def legend_off(self):
        """
        Hide the legend.

        Convenience method to disable legend display. Equivalent to
        legend(show=False).

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Hide legend (chainable)
            >>> viz.legend_off().draw(data).show()
        """
        return self.legend(show=False)

    # ===== AXIS METHODS =====
    def x_axis(
        self,
        show=None,
        label=None,
        limits=None,
        rotation=None,
        ha=None,
        va=None,
        autofmt_xdate=None,
    ):
        """
        Configure x-axis in one method.

        Comprehensive x-axis configuration including visibility, labeling,
        limits, and label formatting. Chainable method for fluent interface.

        Args:
            show (bool, optional): True/False to show/hide x-axis.
            label (str, optional): X-axis label text.
            limits (list, optional): X-axis limits as [min, max].
            rotation (float, optional): Label rotation angle in degrees.
            ha (str, optional): Horizontal alignment ('left', 'center', 'right').
            va (str, optional): Vertical alignment ('top', 'center', 'bottom').
            autofmt_xdate (bool, optional): Auto-format x-axis date labels.

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Basic x-axis with label
            >>> viz.x_axis(show=True, label='Time (days)')

            >>> # Rotated labels with limits
            >>> viz.x_axis(label='Date', rotation=45, limits=['2023-01-01', 
            ...                                               '2023-12-31'])

            >>> # Chainable configuration
            >>> viz.x_axis(label='Relative Time').title('Timeline') \\
            ...    .draw(data).show()
        """
        current_axis = self.settings.x_axis
        axis_settings = current_axis.__dict__

        if show is not None:
            axis_settings["show"] = show
        if label is not None:
            axis_settings["xlabel"] = label
        if limits is not None:
            axis_settings["xlim"] = limits
        if rotation is not None:
            axis_settings["xlabel_rotation"] = rotation
        if ha is not None:
            axis_settings["xlabel_ha"] = ha
        if va is not None:
            axis_settings["xlabel_va"] = va
        if autofmt_xdate is not None:
            axis_settings["autofmt_xdate"] = autofmt_xdate

        self._tmp_update_settings(x_axis=axis_settings)
        return self

    def y_axis(
        self,
        show=None,
        label=None,
        limits=None,
        rotation=None,
        ha=None,
        va=None,
    ):
        """
        Configure y-axis in one method.

        Comprehensive y-axis configuration including visibility, labeling,
        limits, and label formatting. Chainable method for fluent interface.

        Args:
            show (bool, optional): True/False to show/hide y-axis.
            label (str, optional): Y-axis label text.
            limits (list, optional): Y-axis limits as [min, max].
            rotation (float, optional): Label rotation angle in degrees.
            ha (str, optional): Horizontal alignment ('left', 'center', 'right').
            va (str, optional): Vertical alignment ('top', 'center', 'bottom').

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Basic y-axis with label
            >>> viz.y_axis(show=True, label='Sequence ID')

            >>> # Y-axis with custom limits
            >>> viz.y_axis(label='Count', limits=[0, 100])

            >>> # Chainable y-axis configuration
            >>> viz.y_axis(label='Sequences', show=True) \\
            ...    .x_axis(label='Time') \\
            ...    .draw(data).show()
        """
        current_axis = self.settings.y_axis
        axis_settings = current_axis.__dict__

        if show is not None:
            axis_settings["show"] = show
        if label is not None:
            axis_settings["ylabel"] = label
        if limits is not None:
            axis_settings["ylim"] = limits
        if rotation is not None:
            axis_settings["ylabel_rotation"] = rotation
        if ha is not None:
            axis_settings["ylabel_ha"] = ha
        if va is not None:
            axis_settings["ylabel_va"] = va

        self._tmp_update_settings(y_axis=axis_settings)
        return self

    def xlim(self, min_val=None, max_val=None):
        """
        Quick x-axis limits setter.

        Convenience method to set x-axis limits without full x_axis() call.

        Args:
            min_val (float, optional): Minimum x-axis value.
            max_val (float, optional): Maximum x-axis value.

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Set x-axis limits
            >>> viz.xlim(0, 365)

            >>> # Set only maximum (chainable)
            >>> viz.xlim(max_val=100).draw(data).show()
        """
        return self.x_axis(limits=[min_val, max_val])

    def ylim(self, min_val=None, max_val=None):
        """
        Quick y-axis limits setter.

        Convenience method to set y-axis limits without full y_axis() call.

        Args:
            min_val (float, optional): Minimum y-axis value.
            max_val (float, optional): Maximum y-axis value.

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Set y-axis limits
            >>> viz.ylim(0, 50)

            >>> # Set only minimum (chainable)
            >>> viz.ylim(min_val=0).draw(data).show()
        """
        return self.y_axis(limits=[min_val, max_val])

    # ===== LABS METHODS =====
    def title(self, title):
        """
        Set plot title.

        Args:
            title (str): Main title text for the visualization.

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Set title
            >>> viz.title('Event Timeline Analysis')

            >>> # Chainable title setting
            >>> viz.title('State Distribution').legend(title='States') \\
            ...    .draw(data).show()
        """
        self._tmp_update_settings(title=title)
        return self

    def xlabel(self, label):
        """
        Quick x-axis label setter.

        Convenience method to set x-axis label and make it visible.

        Args:
            label (str): X-axis label text.

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Set x-axis label
            >>> viz.xlabel('Time (days)')

            >>> # Chainable label setting
            >>> viz.xlabel('Date').ylabel('Count').draw(data).show()
        """
        return self.x_axis(label=label, show=True)

    def ylabel(self, label):
        """
        Quick y-axis label setter.

        Convenience method to set y-axis label and make it visible.

        Args:
            label (str): Y-axis label text.

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Set y-axis label
            >>> viz.ylabel('Sequence Count')

            >>> # Chainable label setting
            >>> viz.ylabel('Frequency').xlabel('States').draw(data).show()
        """
        return self.y_axis(label=label, show=True)

    def colors(self, colors):
        """
        Set color palette for the visualization.

        Configure colors used for different categories/elements in the
        visualization. Supports various color specification formats.

        Args:
            colors (str, dict, or list): Color configuration:
                - str: Matplotlib colormap name (e.g., 'Set1', 'tab10')
                - dict: Mapping from category names to colors 
                  {'A': 'red', 'B': 'blue'}
                - list: List of colors ['red', 'blue', 'green']

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Use matplotlib colormap
            >>> viz.colors('Set1')

            >>> # Custom color mapping
            >>> viz.colors({'Active': 'green', 'Inactive': 'red'})

            >>> # List of colors (chainable)
            >>> viz.colors(['#FF5733', '#33FF57', '#3357FF']) \\
            ...    .draw(data).show()
        """
        self._tmp_update_settings(colors=colors)
        return self

    # ===== MARKER METHODS =====
    def marker(
        self,
        size=None,
        spacing=None,
        alpha=None,
        edge_color=None,
        shape=None,
    ):
        """
        Configure marker settings.

        Controls visual properties of markers used in timeline and other
        visualizations. Chainable method for fluent interface.

        Args:
            size (float, optional): Marker size (default varies by type).
            spacing (float, optional): Distance between markers.
            alpha (float, optional): Marker transparency (0-1, where 
                0=transparent, 1=opaque).
            edge_color (str, optional): Marker border color. If None,
                uses the fill color.
            shape (str, optional): Marker shape (e.g., '*', 'o', 's', '^').

        Returns:
            self: Chainable method for fluent interface.

        Examples:
            >>> # Basic marker configuration
            >>> viz.marker(size=5, alpha=0.8)

            >>> # Timeline markers with custom shape
            >>> viz.marker(shape='*', spacing=1.5, alpha=0.7)

            >>> # Chainable marker settings
            >>> viz.marker(size=3, alpha=0.9).colors('Set1') \\
            ...    .draw(data).show()
        """
        marker_settings = self.settings.marker.__dict__

        if size is not None:
            marker_settings["size"] = size
        if spacing is not None:
            marker_settings["spacing"] = spacing
        if alpha is not None:
            marker_settings["alpha"] = alpha
        if edge_color is not None:
            marker_settings["edge_color"] = edge_color
        if shape is not None:
            marker_settings["shape"] = shape

        self._tmp_update_settings(marker=marker_settings)
        return self
