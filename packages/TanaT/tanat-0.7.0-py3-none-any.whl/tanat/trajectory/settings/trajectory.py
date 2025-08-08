#!/usr/bin/env python3
"""
Settings for Trajectory.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer

from .base import BaseTrajectorySettings


@viewer
@dataclass
class TrajectorySettings(BaseTrajectorySettings):
    """
    Settings for Trajectory.

    Attributes:
        id_column: The name of the column representing the ID of the trajectory.
        static_features: The names of the columns representing the static features.
    """

    # Add trajectory-specific settings here if needed
