#!/usr/bin/env python3
"""
Base settings for trajectory objects.
"""

from typing import Optional
import dataclasses

from pydantic.dataclasses import dataclass

from ...sequence.settings.static_feature import StaticFeatureSettings


@dataclass
class BaseTrajectorySettings(StaticFeatureSettings):
    """
    Base settings for trajectory objects.

    Attributes:
        id_column: The name of the column representing the ID.
        static_features: The names of the columns representing the static features.
    """

    id_column: Optional[str] = None

    def reset_static_settings(self):
        """
        Reset static settings.

        Returns:
            A new instance with reset static settings.
        """
        return dataclasses.replace(self, id_column=None, static_features=None)
