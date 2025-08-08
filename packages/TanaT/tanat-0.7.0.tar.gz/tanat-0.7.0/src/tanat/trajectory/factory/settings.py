#!/usr/bin/env python3
"""
Settings for TrajectoryPoolRunnerFactory
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.fallback.typing import Dict

from ..settings.pool import TrajectoryPoolSettings
from ...sequence.base.pool import SequencePool


@dataclass
class TrajectoryPoolFactorySettings(TrajectoryPoolSettings):
    """
    Settings for TrajectoryPoolRunnerFactory.

    Attributes:
        id_column: The name of the column representing the ID.
        static_features: The names of the columns representing the static features.
        intersection: If True, uses the intersection of IDs across SequencePools.
        id_values: Optional list of specific IDs to include in the TrajectoryPool.
        static_data_loader: Optional name of a loader for static data.
        seqpools_kwargs: Optional dictionary of keyword arguments specifying
            SequencePool configurations.
    """

    static_data_loader: Optional[str] = None
    seqpools_kwargs: Optional[Dict[str, SequencePool]] = None

    def safe_seqpools_kwargs(self):
        """
        Safely access seqpools_kwargs.

        Returns:
            Dict[str, SequencePool]: The sequence pools kwargs.
            or an empty dict if seqpools_kwargs is None
        """
        if self.seqpools_kwargs is None:
            return {}
        return self.seqpools_kwargs
