#!/usr/bin/env python3
"""
Sequence pool configuration.
"""

from typing import Optional, Union

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import registry
from pypassist.dataclass.decorators.exportable.decorator import exportable
from pypassist.utils.typing import ParamDict

from .metadata.metadata import Metadata
from ..loader.config import LoaderConfig
from .base.pool import SequencePool
from .settings.base import BaseSequenceSettings


@registry(base_cls=SequencePool, register_name_attr="stype")
@exportable(strategy="registry")
@dataclass
class SequencePoolConfig:
    """
    Sequence pool configuration.

    Attributes:
        stype: Type of sequence to use, resolved via type registry.
        data_loader: String identifier of a loader to retrieve from working env or Loader.
        settings: Sequence-specific settings dataclass or settings dictionary.
                  This will be automatically converted into the correct dataclass
                  by the registry decorator.
        metadata: Optional metadata associated with the sequence pool.

    Note:
        - `stype` determines which sequence type to use, resolved via the registry.
        - `settings` is initially a `Dict[str, Any]`, but it will be converted
          dynamically into a settings dataclass corresponding to `stype`.
        - The conversion is handled inside the `@registry` decorator.

    Example:
        ```yaml
        stype: "event"
        data_loader: "csv"
        settings:
            id_column: "id"
            time_column: "timestamp"
            entity_features: ["data1", "data2"]
        ```
    """

    data_loader: Union[str, ParamDict]
    stype: str
    settings: Union[ParamDict, BaseSequenceSettings]
    static_data_loader: Optional[Union[str, ParamDict]] = None
    metadata: Optional[Metadata] = None

    @staticmethod
    def _resolve_loader(loader, workenv):
        """
        Retrieve and instantiate a loader.
        """
        if loader is None:
            return None

        if isinstance(loader, str):
            if loader not in workenv.loaders:
                available_loaders = list(workenv.loaders.keys())
                raise KeyError(
                    f"Loader '{loader}' not found in working env. "
                    f"Available loaders : {available_loaders}"
                )
            return workenv.loaders[loader]

        if isinstance(loader, dict):
            loader = LoaderConfig(**loader)

        if isinstance(loader, LoaderConfig):
            return loader.get_loader(workenv)

        raise ValueError(
            f"Invalid argument for loader: {loader!r}. "
            "Must be a string reference to a Loader in workeing env or a LoaderConfig instance."
        )

    def get_sequence_pool(self, workenv):
        """
        Retrieve and instantiate a sequence pool using the configuration and working env.
        """
        seq_type = self.stype
        seqpool_cls = SequencePool.get_registered(seq_type)
        data_loader = self._resolve_loader(self.data_loader, workenv)
        static_loader = self._resolve_loader(self.static_data_loader, workenv)
        return seqpool_cls(
            data=data_loader,
            settings=self.settings,
            metadata=self.metadata,
            static_data=static_loader,
        )
