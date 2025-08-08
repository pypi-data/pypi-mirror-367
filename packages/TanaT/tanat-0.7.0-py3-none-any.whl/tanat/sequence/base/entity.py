#!/usr/bin/env python3
"""
Entity base class.
"""

from abc import ABC, abstractmethod

from pypassist.mixin.settings import SettingsMixin


class Entity(ABC, SettingsMixin):
    """
    Entity class.
    """

    def __init__(self, data, settings):
        self._data = data
        SettingsMixin.__init__(self, settings)

    @property
    def value(self):
        """
        Return the value of the entity.
        """
        features = self._settings.entity_features
        data_row = self._data[features]
        if len(features) > 1:
            # -- multiple features, tuple
            return tuple(data_row)

        return data_row.item()

    @property
    def extent(self):
        """
        Return the extent of the entity.
        """
        return self._get_temporal_extent()

    @abstractmethod
    def _get_temporal_extent(self):
        """
        Returns the extent of the entity.
        """

    def __getitem__(self, feature_name):
        if feature_name not in self._settings.get_valid_columns():
            raise ValueError(f"Invalid feature name: {feature_name}")

        return self._data[feature_name]


## -- Temporal extent


class TemporalExtent(ABC):
    """
    Representation of a temporal extent of a temporal entity
    """

    @abstractmethod
    def __repr__(self):
        """
        Return a string representation of the temporal extent.
        """


class InstantExtent(TemporalExtent):
    """
    Representation of an instant in time.
    """

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return str(self.date)


class PeriodExtent(TemporalExtent):
    """
    Representation of an period in time.
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def duration(self, granularity):
        """
        Duration of the period
        """
        raise NotImplementedError

    def __repr__(self):
        return f"[{self.start}, {self.end}]"
