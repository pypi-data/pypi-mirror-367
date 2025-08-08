#!/usr/bin/env python3
"""
Survival Tree Model.
"""

from sksurv.tree import SurvivalTree

from ...base.model import SurvivalModel
from .settings import TreeSurvivalSettings


class TreeSurvivalModel(SurvivalModel, register_name="tree"):
    """
    Survival Tree Model.
    """

    SETTINGS_DATACLASS = TreeSurvivalSettings

    def __init__(self, settings=None):
        if settings is None:
            settings = TreeSurvivalSettings()
        SurvivalModel.__init__(self, settings)

    def _init_model(self):
        """
        Initializes the survival model with the current settings.
        """
        return SurvivalTree(
            splitter=self.settings.splitter,
            max_depth=self.settings.max_depth,
            min_samples_split=self.settings.min_samples_split,
            min_samples_leaf=self.settings.min_samples_leaf,
            min_weight_fraction_leaf=self.settings.min_weight_fraction_leaf,
            max_features=self.settings.max_features,
            random_state=self.settings.random_state,
            max_leaf_nodes=self.settings.max_leaf_nodes,
            low_memory=self.settings.low_memory,
        )

    def fit(self, data_x, y):
        """
        Fit the survival model to the provided data.

        Args:
            data_x (array-like): Features.
            y (structured array): Target, containing the event indicator as first field,
                and time of event or censoring as second field.

        Returns:
            self: The fitted model instance.
        """
        data_x = self._prepare_and_encode_data2fit(data_x)
        self.model.fit(data_x, y)
