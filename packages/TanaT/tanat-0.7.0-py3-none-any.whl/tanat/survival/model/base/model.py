#!/usr/bin/env python3
"""
Base class for survival model.
"""

from abc import ABC, abstractmethod
import logging

from sksurv.preprocessing import OneHotEncoder
from pypassist.mixin.registrable import Registrable
from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.registrable.exceptions import UnregisteredTypeError

from .exception import UnregisteredSurvivalModelTypeError

LOGGER = logging.getLogger(__name__)


class SurvivalModel(
    ABC,
    Registrable,
    SettingsMixin,
):
    """
    Base class for Survival Model.
    """

    _REGISTER = {}
    SETTINGS_DATACLASS = None

    def __init__(self, settings):
        SettingsMixin.__init__(self, settings)
        self._is_fitted = False
        self._model = None

    @property
    def model(self):
        """
        Returns an instance of the model configured with the current settings.
        """
        if self._model is None:
            self._model = self._init_model()

        return self._model

    @abstractmethod
    def _init_model(self):
        """Initialize the model."""

    @abstractmethod
    def fit(self, data_x, y):
        """Fit the model to the provided data (sklearn style)."""

    def predict_survival_function(self, data_x, return_array=False):
        """Predict the survival function (sklearn style)."""
        data_x = self._prepare_and_encode_data2fit(data_x)
        return self.model.predict_survival_function(data_x, return_array=return_array)

    @classmethod
    def init(cls, model_type, settings=None):
        """
        Initialize the model for a specific type.

        Args:
            model_type:
                The model type.

            settings:
                The model settings.

        Returns:
            An instance of the model.
        """
        try:
            model = cls.get_registered(model_type)(settings)
        except UnregisteredTypeError as err:
            raise UnregisteredSurvivalModelTypeError(
                f"Unknown survival model type: '{model_type}'. "
                f"Available survival model types: {cls.list_registered()}"
            ) from err

        return model

    def _prepare_and_encode_data2fit(self, data_x):
        """
        Prepare the data for fitting.
        """
        list_cols = self.settings.static_features or data_x.columns
        data_x = self._ensure_categorical_cols(data_x.copy(), list_cols)
        data_x = OneHotEncoder().fit_transform(data_x)
        return data_x

    def _ensure_categorical_cols(self, data_x, list_cols):
        """
        Ensure that the specified columns are categorical.
        """
        for col in list_cols:
            data_x[col] = data_x[col].astype("category")
        return data_x[list_cols]
