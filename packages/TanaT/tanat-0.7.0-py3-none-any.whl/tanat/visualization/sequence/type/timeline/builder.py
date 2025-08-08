#!/usr/bin/env python3
"""
Timeline visualization builder.
"""

import pandas as pd

from ....utils.color_manager import ColorManager
from ...base.builder import BaseSequenceVizBuilder
from .settings import TimelineSequenceVizSettings
from .enum import TimelineStackingMode


class TimelineVizBuilder(BaseSequenceVizBuilder, register_name="timeline"):
    """
    Builder for timeline sequence visualizations.

    Creates timeline plots showing sequences over time with temporal alignment.
    Supports different stacking modes, relative/absolute time, and handles
    events, states, and intervals with appropriate visual representations.
    """

    SETTINGS_DATACLASS = TimelineSequenceVizSettings

    # Configuration des noms de colonnes standardisées
    COLUMN_NAMES = {
        "annotation": "__ANNOTATION__",
        "y_position": "__Y_POSITION__",
        "start_time": "__START_TIME__",
        "end_time": "__END_TIME__",
        "time_point": "__TIME_POINT__",
        "color": "__COLOR__",
    }

    def __init__(self, settings=None):
        if settings is None:
            settings = TimelineSequenceVizSettings()
        BaseSequenceVizBuilder.__init__(self, settings)

    def _prepare_data(self, sequence_or_pool, drop_na=True, entity_features=None):
        """
        Prepare sequence data for timeline visualization.
        """
        # 1. Get base data
        if self.settings.aesthetics.relative_time:
            granularity = self.settings.aesthetics.granularity
            if granularity is None:
                granularity = sequence_or_pool.granularity
            data_copy = sequence_or_pool.to_relative_time(
                granularity=granularity,
                drop_na=drop_na,
            ).copy()  # Copy to avoid modifying cached data
        else:
            # pylint:disable=protected-access
            data_copy = sequence_or_pool._get_standardized_data(
                drop_na=drop_na, entity_features=entity_features
            )  # return new copy at each call

        temporal_cols = sequence_or_pool.settings.temporal_columns(standardize=True)

        # 2. Create annotation column from entity features
        data_copy = self._create_annotation_column(
            data_copy, sequence_or_pool, entity_features
        )

        # 3. Standardize time columns
        data_copy = self._standardize_time_columns(data_copy, temporal_cols)

        # 4. Calculate y-positions
        data_copy = self._calculate_y_positions(data_copy)

        # 5. Add color column
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

    def _standardize_time_columns(self, data_copy, temporal_cols):
        """
        Standardize time columns using sequence configuration.

        Logic:
        - temporal_columns(standardize=True) returns 1 element (event) or
          2 elements (interval/states)
        - 1 element: event with single time point
        - 2 elements: interval with start and end times
        """
        if len(temporal_cols) == 1:
            # Event case: single time point
            time_col = temporal_cols[0]
            data_copy.rename(
                columns={time_col: self.COLUMN_NAMES["time_point"]}, inplace=True
            )

        elif len(temporal_cols) == 2:
            # Interval case: start and end times
            start_col, end_col = temporal_cols
            data_copy.rename(
                columns={
                    start_col: self.COLUMN_NAMES["start_time"],
                    end_col: self.COLUMN_NAMES["end_time"],
                },
                inplace=True,
            )

        return data_copy

    def _calculate_y_positions(self, data_copy):
        """Calculate y-positions based on stacking mode."""
        annotation_col = self.COLUMN_NAMES["annotation"]
        y_pos_col = self.COLUMN_NAMES["y_position"]

        if self.settings.aesthetics.stacking_mode == TimelineStackingMode.BY_CATEGORY:
            if annotation_col in data_copy.columns:
                categories = data_copy[annotation_col].unique()
                category_positions = {cat: i for i, cat in enumerate(categories)}
                data_copy[y_pos_col] = data_copy[annotation_col].map(category_positions)
            else:
                data_copy[y_pos_col] = 0

        elif self.settings.aesthetics.stacking_mode == TimelineStackingMode.FLAT:
            # Each sequence gets its own row
            unique_ids = data_copy.index.unique()
            id_positions = {id_val: i for i, id_val in enumerate(unique_ids)}
            data_copy[y_pos_col] = data_copy.index.map(id_positions)

        else:  # AUTOMATIC
            data_copy[y_pos_col] = self._calculate_automatic_positions(data_copy)

        return data_copy

    def _calculate_automatic_positions(self, data):
        """Calculate automatic y-positions to minimize overlaps."""
        annotation_col = self.COLUMN_NAMES["annotation"]
        y_positions = []
        seen_combinations = {}

        for idx, row in data.iterrows():
            combination = f"{idx}_{row.get(annotation_col)}"
            if combination not in seen_combinations:
                seen_combinations[combination] = len(seen_combinations)
            y_positions.append(seen_combinations[combination])

        return pd.Series(y_positions, index=data.index)

    def _add_colors_column(self, data_copy):
        """Add colors column based on annotations and settings."""
        annotation_col = self.COLUMN_NAMES["annotation"]
        color_col = self.COLUMN_NAMES["color"]

        # Get colors config from settings
        colors_config = self.settings.colors

        # Get colors using the simple color manager
        colors = ColorManager.get_colors(data_copy[annotation_col], colors_config)
        data_copy[color_col] = colors

        return data_copy

    def _render(self, ax, data):
        """
        Render timeline visualization.
        """
        annotation_col = self.COLUMN_NAMES["annotation"]

        # Group data by annotation for efficient rendering
        grouped = data.groupby(annotation_col, sort=False)

        for annotation, group in grouped:
            # Use first element for label, rest get None
            first_element = True

            for _, element in group.iterrows():
                label = annotation if first_element else None
                first_element = False

                if self._is_interval_element(element):
                    self._draw_interval(ax, element, label)
                else:
                    self._draw_point(ax, element, label)

        # Apply base styling
        self.apply_styling(ax)
        # Auto format dates if needed
        if self.settings.x_axis.autofmt_xdate:
            ax.figure.autofmt_xdate()

    def _is_interval_element(self, element):
        """Check if element represents an interval using standardized column names."""
        end_time_col = self.COLUMN_NAMES["end_time"]
        return (
            end_time_col in element.index
            and element[end_time_col] is not None
            and pd.notna(element[end_time_col])
        )

    def _draw_interval(self, ax, element, label=None):
        """Draw an interval element using standardized column names."""
        start_col = self.COLUMN_NAMES["start_time"]
        end_col = self.COLUMN_NAMES["end_time"]
        y_pos_col = self.COLUMN_NAMES["y_position"]
        color_col = self.COLUMN_NAMES["color"]

        # Get values using our standardized column names
        start_time = element.get(start_col)
        end_time = element.get(end_col)
        y_pos = element.get(y_pos_col)
        color = element.get(color_col)

        # Apply settings
        bar_height = self.settings.marker.spacing * 0.8
        alpha = self.settings.marker.alpha

        ax.barh(
            y_pos,
            width=end_time - start_time,
            left=start_time,
            height=bar_height,
            alpha=alpha,
            label=label,
            color=color,
        )

    def _draw_point(self, ax, element, label=None):
        """Draw a point element using standardized column names."""
        time_point_col = self.COLUMN_NAMES["time_point"]
        y_pos_col = self.COLUMN_NAMES["y_position"]
        color_col = self.COLUMN_NAMES["color"]

        # Get values using our standardized column names
        time_val = element.get(time_point_col)
        y_pos = element.get(y_pos_col)
        color = element.get(color_col)

        size = self.settings.marker.size * 20
        alpha = self.settings.marker.alpha
        marker = self.settings.marker.shape

        ax.scatter(
            time_val,
            y_pos,
            s=size,
            alpha=alpha,
            marker=marker,
            label=label,
            color=color,
        )
