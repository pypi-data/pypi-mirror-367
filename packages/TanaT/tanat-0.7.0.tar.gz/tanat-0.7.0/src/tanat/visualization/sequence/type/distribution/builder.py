#!/usr/bin/env python3
"""
Distribution visualization builder.
"""

from ....utils.color_manager import ColorManager
from ...base.builder import BaseSequenceVizBuilder
from .settings import DistributionSequenceVizSettings
from .enum import DistributionMode


class DistributionVizBuilder(BaseSequenceVizBuilder, register_name="distribution"):
    """
    Builder for distribution sequence visualizations.

    Creates distribution plots showing how states are distributed
    across time periods. Supports stacked and unstacked visualizations with
    different calculation modes (percentage, proportion, count).

    Note: Only supports for states sequences.
    """

    SETTINGS_DATACLASS = DistributionSequenceVizSettings

    # Configuration des noms de colonnes standardisées
    COLUMN_NAMES = {
        "time": "__TIME__",
        "annotation": "__ANNOTATION__",
        "value": "__VALUE__",
        "color": "__COLOR__",
    }

    def __init__(self, settings=None):
        if settings is None:
            settings = DistributionSequenceVizSettings()
        BaseSequenceVizBuilder.__init__(self, settings)

    def _prepare_data(self, sequence_or_pool, drop_na=True, entity_features=None):
        """
        Prepare sequence data for distribution visualization.
        """
        # 1. Get temporal bins data using the new method
        granularity = self.settings.aesthetics.granularity
        mode_enum = self.settings.aesthetics.mode
        time_relative = self.settings.aesthetics.time_relative

        # Convert DistributionMode to string expected by to_distribution
        mode_mapping = {
            DistributionMode.PERCENTAGE: "percentage",
            DistributionMode.COUNT: "count",
            DistributionMode.PROPORTION: "proportion",
        }
        mode = mode_mapping.get(mode_enum, "percentage")

        # Use the new to_distribution method
        data = sequence_or_pool.to_distribution(
            granularity=granularity,
            mode=mode,
            time_relative=time_relative,
            drop_na=drop_na,
            entity_features=entity_features,
        )  # 2. Standardize column names to match visualization expectations
        data_copy = data.rename(
            columns={
                "time_period": self.COLUMN_NAMES["time"],
                "annotation": self.COLUMN_NAMES["annotation"],
                sequence_or_pool.transformer_settings.distribution_column: self.COLUMN_NAMES[
                    "value"
                ],
            }
        )

        # 3. Add colors column
        data_copy = self._add_colors_column(data_copy)

        return data_copy

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
        Render distribution visualization.
        """
        time_col = self.COLUMN_NAMES["time"]
        annotation_col = self.COLUMN_NAMES["annotation"]
        value_col = self.COLUMN_NAMES["value"]
        color_col = self.COLUMN_NAMES["color"]

        # Pivot data for plotting
        pivot_data = data.pivot(
            index=time_col, columns=annotation_col, values=value_col
        )
        pivot_data = pivot_data.fillna(0)

        # Get colors for each category
        categories = pivot_data.columns
        colors_series = data.groupby(annotation_col)[color_col].first()
        colors = [colors_series.get(cat) for cat in categories]

        # Choose visualization mode based on stacked setting
        if self.settings.aesthetics.stacked:
            # Mode cumulé (comme TraMineR)
            ax.stackplot(
                pivot_data.index,
                *[pivot_data[col] for col in categories],
                labels=categories,
                colors=colors,
                alpha=self.settings.marker.alpha,
            )
        else:
            # Mode à plat avec alpha pour voir les superpositions
            for i, col in enumerate(categories):
                ax.fill_between(
                    pivot_data.index,
                    0,
                    pivot_data[col],
                    label=col,
                    color=colors[i],
                    alpha=self.settings.marker.alpha
                    * 0.7,  # Plus transparent pour le mode flat
                )

        # Configure legend
        self._configure_legend(ax)

        # Apply base styling
        self.apply_styling(ax)
