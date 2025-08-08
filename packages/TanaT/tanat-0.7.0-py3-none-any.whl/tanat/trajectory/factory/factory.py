#!/usr/bin/env python3
"""
Factory to generate a TrajectoryPool within a runner process.
"""

from pypassist.runner.workenv.mixin.processor import ProcessorMixin
from pypassist.mixin.settings import SettingsMixin

from .settings import TrajectoryPoolFactorySettings
from ..pool import TrajectoryPool


class TrajectoryPoolRunnerFactory(SettingsMixin, ProcessorMixin):
    """
    TrajectoryPool factory.
    """

    SETTINGS_DATACLASS = TrajectoryPoolFactorySettings

    def __init__(self, settings, *, workenv):
        SettingsMixin.__init__(self, settings)
        ProcessorMixin.__init__(self)
        self._workenv = workenv

    # pylint: disable=arguments-differ
    def process(self, *, export, output_dir, exist_ok, **seqpool_kwargs):
        """
        Create a TrajectoryPool from workflow inputs.

        Args:
            export: Whether to export the trajectory pool.
            output_dir: Directory to export to.
            exist_ok: Whether to overwrite existing files.
            **seqpool_kwargs: Sequence pools to include in the trajectory pool.

        Returns:
            TrajectoryPool: The created trajectory pool

        Raises:
            ValueError: If no valid SequencePools are specified
            KeyError: If a referenced loader is not found
        """
        input_settings = self.settings

        static_data = self._resolve_static_loader(self._workenv)

        # Create settings for TrajectoryPool
        pool_settings = {
            "id_column": input_settings.id_column,
            "static_features": input_settings.static_features,
            "intersection": input_settings.intersection,
            "id_values": input_settings.id_values,
        }

        trajpool = TrajectoryPool.init_from_seqpools(
            static_data=static_data,
            settings=pool_settings,
            **input_settings.safe_seqpools_kwargs(),
            **seqpool_kwargs,
        )
        if export:
            trajpool.export_static_data(
                filepath=output_dir / "static_data.csv",
                exist_ok=exist_ok,
                makedirs=True,
                index=False,
            )
        return trajpool

    def _resolve_static_loader(self, workenv):
        """
        Retrieve and instantiate a loader using the settings and working env.

        Args:
            workenv: The working environment containing loaders

        Returns:
            The resolved static data loader or None

        Raises:
            KeyError: If the referenced loader is not found
        """
        if workenv is None or not self.settings.static_data_loader:
            return None

        data_loader = self.settings.static_data_loader

        if isinstance(data_loader, str):
            if data_loader not in workenv.loaders:
                raise KeyError(
                    f"Loader '{data_loader}' not found in working env. "
                    f"Available: {list(workenv.loaders.keys())}."
                )
            return workenv.loaders[data_loader]

        return None
