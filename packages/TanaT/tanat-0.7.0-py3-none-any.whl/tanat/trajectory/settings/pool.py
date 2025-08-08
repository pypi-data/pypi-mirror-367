#!/usr/bin/env python3
"""
Settings for TrajectoryPool and its factory.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer

from .base import BaseTrajectorySettings


@viewer
@dataclass
class TrajectoryPoolSettings(BaseTrajectorySettings):
    """
    Settings for TrajectoryPool.

    Attributes:
        id_column: The name of the column representing the ID.
        static_features: The names of the columns representing the static features.
        intersection: If True, uses the intersection of IDs across SequencePools.
    """

    intersection: bool = False
