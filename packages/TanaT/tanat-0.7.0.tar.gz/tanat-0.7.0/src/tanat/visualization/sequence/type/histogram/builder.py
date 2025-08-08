#!/usr/bin/env python3
"""
Histogram visualization builder.
"""

import numpy as np

from ....utils.color_manager import ColorManager
from ...base.builder import BaseSequenceVizBuilder
from .settings import HistoSequenceVizSettings
from .enum import HistoShowAs, HistoBarOrder, HistoOrientation


class HistogramVizBuilder(BaseSequenceVizBuilder, register_name="histogram"):
    """
    Builder for histogram sequence visualizations.

    Creates histogram plots showing frequency distributions or time spent
    analysis for sequence elements. Supports different display modes,
    bar ordering, and orientations for comprehensive sequence analysis.
    """

    SETTINGS_DATACLASS = HistoSequenceVizSettings

    # Configuration des noms de colonnes standardisées
    COLUMN_NAMES = {
        "annotation": "__ANNOTATION__",
        "value": "__VALUE__",
        "color": "__COLOR__",
    }

    def __init__(self, settings=None):
        if settings is None:
            settings = HistoSequenceVizSettings()
        BaseSequenceVizBuilder.__init__(self, settings)

    def _prepare_data(self, sequence_or_pool, drop_na=True, entity_features=None):
        """
        Prepare sequence data for histogram visualization.
        """
        # 1. Get base data according to aesthetics
        show_as = self.settings.aesthetics.show_as

        if show_as == HistoShowAs.FREQUENCY:
            data = sequence_or_pool.to_occurrence_frequency(
                drop_na=drop_na, entity_features=entity_features
            )
        elif show_as == HistoShowAs.TIME_SPENT:
            granularity = self.settings.aesthetics.granularity
            if granularity is None:
                granularity = sequence_or_pool.granularity
            data = sequence_or_pool.to_time_spent(
                granularity=granularity,
                drop_na=drop_na,
                entity_features=entity_features,
            )
        else:  # OCCURRENCE
            data = sequence_or_pool.to_occurrence(
                drop_na=drop_na, entity_features=entity_features
            )

        # 2. Create annotation column
        data_copy = self._create_annotation_column(
            data, sequence_or_pool, entity_features
        )

        # 3. Aggregate data for histogram
        data_copy = self._aggregate_histogram_data(data_copy)

        # 4. Sort data according to settings
        data_copy = self._sort_data(data_copy)

        # 5. Add colors column
        data_copy = self._add_colors_column(data_copy)

        return data_copy

    def _create_annotation_column(self, data_copy, sequence_or_pool, entity_features):
        """
        Create annotation column from entity features.

        Logic:
        - If entity_features is None: use all entity_features from sequence_or_pool.settings
        - If entity_features provided: use those specific features
        """
        annotation_col = self.COLUMN_NAMES["annotation"]

        # ensure valid entity features
        entity_features = sequence_or_pool.settings.validate_and_filter_entity_features(
            entity_features
        )

        if len(entity_features) == 1:
            # Single feature: rename to annotation column
            data_copy.rename(columns={entity_features[0]: annotation_col}, inplace=True)
        else:
            # Multiple features: combine into tuple
            data_copy[annotation_col] = (
                data_copy[entity_features].astype(str).agg(",".join, axis=1)
            )
        return data_copy

    def _aggregate_histogram_data(self, data):
        """Aggregate data for histogram rendering."""
        annotation_col = self.COLUMN_NAMES["annotation"]
        value_col = self.COLUMN_NAMES["value"]

        # Find the value column from known patterns
        value_cols = [
            "__FREQUENCY__",
            "__TIME_SPENT__",
            "__OCCURRENCE__",
        ]

        source_value_col = None
        for col in value_cols:
            if col in data.columns:
                source_value_col = col
                break

        grouped = data.groupby(annotation_col)[source_value_col].sum().reset_index()
        grouped.columns = [annotation_col, value_col]

        return grouped

    def _sort_data(self, data):
        """Sort data according to bar_order setting."""
        annotation_col = self.COLUMN_NAMES["annotation"]
        value_col = self.COLUMN_NAMES["value"]

        if self.settings.aesthetics.bar_order == HistoBarOrder.ALPHABETIC:
            return data.sort_values(annotation_col)
        if self.settings.aesthetics.bar_order == HistoBarOrder.ASCENDING:
            return data.sort_values(value_col)
        if self.settings.aesthetics.bar_order == HistoBarOrder.DESCENDING:
            return data.sort_values(value_col, ascending=False)

        return data

    def _add_colors_column(self, data):
        """Add colors column based on annotations and settings."""
        annotation_col = self.COLUMN_NAMES["annotation"]
        color_col = self.COLUMN_NAMES["color"]

        # Get colors config from settings
        colors_config = getattr(self.settings, "colors", None)

        # Get colors using the color manager
        colors = ColorManager.get_colors(data[annotation_col], colors_config)
        data[color_col] = colors

        return data

    def _render(self, ax, data):
        """
        Render histogram visualization.
        """
        if data.empty:
            ax.text(
                0.5,
                0.5,
                "No data to display",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
            )
            return

        annotation_col = self.COLUMN_NAMES["annotation"]
        value_col = self.COLUMN_NAMES["value"]
        color_col = self.COLUMN_NAMES["color"]

        # Get data for plotting
        annotations = data[annotation_col]
        values = data[value_col]
        colors = data[color_col] if color_col in data.columns else None

        # Render based on orientation
        if self.settings.aesthetics.orientation == HistoOrientation.VERTICAL:
            _ = ax.bar(
                annotations,
                values,
                alpha=self.settings.marker.alpha,
                color=colors,
                label=annotations,  # Add labels for legend
            )

        else:  # HORIZONTAL
            _ = ax.barh(
                annotations,
                values,
                alpha=self.settings.marker.alpha,
                color=colors,
                label=annotations,  # Add labels for legend
            )

        # Configure legend
        self._configure_legend(ax)

        # Apply base styling
        self.apply_styling(ax)
