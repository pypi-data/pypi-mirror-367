#!/usr/bin/env python3
"""
Factory configuration.
"""

from typing import Optional, Union

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.exportable.decorator import exportable
from pypassist.dataclass.decorators.viewer.decorator import viewer
from pypassist.fallback.typing import Dict
from pypassist.utils.typing import ParamDict

from .settings import TrajectoryPoolFactorySettings
from .factory import TrajectoryPoolRunnerFactory
from ...sequence.config import SequencePoolConfig


@viewer
@exportable(stem_file="factory")
@dataclass
class TrajectoryPoolRunnerFactoryConfig(TrajectoryPoolFactorySettings):
    """
    TrajectoryPool runner factory configuration.

    This class extends TrajectoryPoolFactorySettings with a modified type for seqpools_kwargs
    to support ParamDict (Dict[str, Any]) objects that can be converted to SequencePool objects.

    Attributes:
        id_column: The name of the column representing the ID.
        static_features: The names of the columns representing the static features.
        intersection: If True, uses the intersection of IDs across SequencePools.
        id_values: Optional list of specific IDs to include in the TrajectoryPool.
        static_data_loader: Optional name of a loader for static data.
        seqpools_kwargs: Optional dictionary of keyword arguments to pass to the SequencePool
                        factory. Supports both string references and ParamDict configurations.
    """

    # Override definition with a different type
    seqpools_kwargs: Optional[Dict[str, Union[str, ParamDict]]] = None

    def get_factory(self, workenv):
        """
        Get the TrajectoryPool factory.

        Args:
            workenv: The working environment instance.

        Returns:
            TrajectoryPoolRunnerFactory: The configured TrajectoryPool factory.
        """
        # pylint: disable=no-member
        settings_dict = self.serialize()

        if self.seqpools_kwargs is not None:
            settings_dict["seqpools_kwargs"] = self._resolve_seqpools_kwargs(workenv)

        # pylint: disable=no-member
        return TrajectoryPoolRunnerFactory(settings=settings_dict, workenv=workenv)

    def _resolve_seqpools_kwargs(self, workenv):
        """
        Resolve the sequence pool kwargs into actual SequencePool objects.

        This method handles two types of inputs:
        1. Dictionary configurations that are converted to SequencePoolConfig objects
        2. String references to existing SequencePool objects in the workenv

        Args:
            workenv: The working environment instance.

        Returns:
            Dict[str, SequencePool]: The resolved dictionary of sequence pools.

        Raises:
            ValueError: If a string reference cannot be resolved to an existing SequencePool.
        """
        if not self.seqpools_kwargs:
            return {}

        resolved_seqpools_kwargs = {}

        for seqpool_name, seqpool_kwargs in self.seqpools_kwargs.items():
            if isinstance(seqpool_kwargs, dict):
                # Convert dictionary to SequencePoolConfig and get SequencePool
                resolved_seqpools_kwargs[seqpool_name] = SequencePoolConfig(
                    **seqpool_kwargs
                ).get_sequence_pool(workenv=workenv)
            elif isinstance(seqpool_kwargs, str):
                # Get existing SequencePool by name
                resolved_pool = workenv.sequence_pools.get(seqpool_kwargs, None)

                if resolved_pool is None:
                    available_seqpools = list(workenv.sequence_pools.keys())
                    raise ValueError(
                        f"Invalid SequencePool reference: {seqpool_kwargs!r} not found "
                        f"in working environment. Available: {available_seqpools}"
                    )

                resolved_seqpools_kwargs[seqpool_name] = resolved_pool

        return resolved_seqpools_kwargs
