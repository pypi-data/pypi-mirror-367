#!/usr/bin/env python3
"""
Base class for sequence visualization builders.
"""

from abc import ABC, abstractmethod
import logging
import matplotlib.pyplot as plt

from pypassist.mixin.registrable import Registrable
from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.cachable import Cachable
from pypassist.mixin.registrable.exceptions import UnregisteredTypeError

from .exception import UnregisteredVisualizationTypeError

LOGGER = logging.getLogger(__name__)


class BaseSequenceVizBuilder(
    ABC,
    Registrable,
    SettingsMixin,
    Cachable,
):
    """
    Base class for sequence visualization builders.
    """

    _REGISTER = {}
    SETTINGS_DATACLASS = None

    def __init__(self, settings=None):
        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)

    def render(self, ax, data, **kwargs):
        """
        Render the visualization on the given axes.

        Args:
            ax: Matplotlib axes object
            data: Prepared sequence data
            **kwargs: Additional keyword arguments for rendering
        """
        with self.with_tmp_settings(**kwargs):
            self._render(ax, data)

    @abstractmethod
    def _render(self, ax, data):
        """
        Render the visualization on the given axes.

        Args:
            ax: Matplotlib axes object
            data: Prepared sequence data
        """

    @Cachable.caching_method()
    def prepare_data(
        self, sequence_or_pool, drop_na=True, entity_features=None, **kwargs
    ):
        """
        Prepare sequence data for visualization.

        Args:
            sequence_or_pool: Sequence or SequencePool object
            drop_na: Whether to drop rows with missing values
            entity_features: Specific entity features to include
            **kwargs: Additional keyword arguments for settings overrides

        Returns:
            Prepared DataFrame for visualization
        """
        with self.with_tmp_settings(**kwargs):
            return self._prepare_data(
                sequence_or_pool, drop_na=drop_na, entity_features=entity_features
            )

    @abstractmethod
    def _prepare_data(self, sequence_or_pool, drop_na=True, entity_features=None):
        """
        Internal method to prepare sequence data for visualization.

        Args:
            sequence_or_pool: Sequence or SequencePool object
            drop_na: Whether to drop rows with missing values
            entity_features: Specific entity features to include
        Returns:
            Prepared DataFrame for visualization
        """

    def create_figure(self):
        """
        Create matplotlib figure and axes using figure settings.
        """
        # Use default figsize if no figure settings available
        figsize = getattr(self.settings, "figsize", (10, 6))
        if hasattr(self.settings, "figure"):
            figsize = (self.settings.figure.width, self.settings.figure.height)
            dpi = getattr(self.settings.figure, "dpi", None)
        else:
            dpi = None

        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        return fig, ax

    def apply_styling(self, ax):
        """
        Apply styling using integrated style settings.
        """
        # Apply axis configurations
        self._configure_x_axis(ax)
        self._configure_y_axis(ax)
        self._configure_legend(ax)

        # Apply title if specified
        if self.settings.title:
            ax.set_title(self.settings.title)

    def _configure_legend(self, ax):
        """Configure legend using legend settings."""
        if not self.settings.legend.show:
            return None

        # Get handles and labels
        handles, labels = ax.get_legend_handles_labels()

        # Remove duplicates while preserving order
        by_label = dict(zip(labels, handles))
        unique_labels = list(by_label.keys())
        unique_handles = list(by_label.values())

        # Only create legend if we have labels
        if unique_labels:
            legend_kwargs = {
                "loc": self.settings.legend.loc,
            }

            # Add title if specified
            if self.settings.legend.title:
                legend_kwargs["title"] = self.settings.legend.title

            # Add bbox_to_anchor if specified (for positioning outside plot)
            if self.settings.legend.bbox_to_anchor:
                legend_kwargs["bbox_to_anchor"] = self.settings.legend.bbox_to_anchor

            ax.legend(unique_handles, unique_labels, **legend_kwargs)
        return None

    @classmethod
    def init(cls, viz_type, settings=None):
        """
        Initialize builder for a specific visualization type.

        Args:
            viz_type: The visualization type
            settings: The builder settings

        Returns:
            An instance of the builder
        """
        try:
            builder = cls.get_registered(viz_type)(settings)
        except UnregisteredTypeError as err:
            raise UnregisteredVisualizationTypeError(
                f"Unknown visualization type: '{viz_type}'. "
                f"Available types: {cls.list_registered()}"
            ) from err

        return builder

    def _configure_x_axis(self, ax):
        """Configure x-axis using x_axis settings."""
        x_axis = self.settings.x_axis

        # Show/hide axis
        if not x_axis.show:
            ax.xaxis.set_visible(False)
            return None

        # Set label
        if x_axis.xlabel:
            ax.set_xlabel(x_axis.xlabel)

        # Set limits
        if x_axis.xlim:
            xlim = x_axis.xlim
            if xlim[0] is not None or xlim[1] is not None:
                ax.set_xlim(xlim[0], xlim[1])

        # Configure label appearance
        if x_axis.xlabel_rotation is not None:
            rotation = x_axis.xlabel_rotation
            ha = getattr(x_axis, "xlabel_ha", "right" if rotation > 0 else "center")
            va = getattr(x_axis, "xlabel_va", "top")

            ax.tick_params(axis="x", labelrotation=rotation)
            for label in ax.get_xticklabels():
                label.set_horizontalalignment(ha)
                label.set_verticalalignment(va)
        return None

    def _configure_y_axis(self, ax):
        """Configure y-axis using y_axis settings."""
        y_axis = self.settings.y_axis

        # Show/hide axis
        if not y_axis.show:
            ax.yaxis.set_visible(False)
            return None

        # Set label
        if y_axis.ylabel:
            ax.set_ylabel(y_axis.ylabel)

        # Set limits
        if y_axis.ylim:
            ylim = y_axis.ylim
            if ylim[0] is not None or ylim[1] is not None:
                ax.set_ylim(ylim[0], ylim[1])

        # Configure label appearance
        if y_axis.ylabel_rotation is not None:
            rotation = y_axis.ylabel_rotation
            ha = getattr(y_axis, "ylabel_ha", "right")
            va = getattr(y_axis, "ylabel_va", "center" if rotation == 90 else "top")

            ax.tick_params(axis="y", labelrotation=rotation)
            for label in ax.get_yticklabels():
                label.set_horizontalalignment(ha)
                label.set_verticalalignment(va)
        return None
