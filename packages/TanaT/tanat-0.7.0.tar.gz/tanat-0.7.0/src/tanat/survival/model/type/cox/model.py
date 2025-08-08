#!/usr/bin/env python3
"""
Coxnet survival model.
"""

from sksurv.linear_model import CoxnetSurvivalAnalysis

from ...base.model import SurvivalModel
from .settings import CoxnetSurvivalSettings


class CoxnetSurvivalModel(SurvivalModel, register_name="coxnet"):
    """
    Coxnet survival model.
    """

    SETTINGS_DATACLASS = CoxnetSurvivalSettings

    def __init__(self, settings=None):
        if settings is None:
            settings = CoxnetSurvivalSettings()
        SurvivalModel.__init__(self, settings)

    def _init_model(self):
        """
        Initializes the survival model with the current settings.
        """
        return CoxnetSurvivalAnalysis(
            n_alphas=self.settings.n_alphas,
            alphas=self.settings.alphas,
            alpha_min_ratio=self.settings.alpha_min_ratio,
            l1_ratio=self.settings.l1_ratio,
            penalty_factor=self.settings.penalty_factor,
            normalize=self.settings.normalize,
            tol=self.settings.tol,
            max_iter=self.settings.max_iter,
            verbose=self.settings.verbose,
            fit_baseline_model=True,
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
