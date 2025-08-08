#!/usr/bin/env python3
"""
Sequence pool mocking class
"""

from tseqmock.core import TSeqMocker

from ....sequence.base.pool import SequencePool


class SequencePoolMocker(TSeqMocker):
    """
    Sequence pool mocking class
    """

    def __call__(self, **kwargs):
        """
        Generate sequence pool

        Args:
            kwargs: Optional overrides for specific settings.

        Returns:
            SequencePool instance.
        """
        return self.generate(**kwargs)

    def generate(self, **kwargs):
        """
        Generate sequence pool

        Args:
            kwargs: Optional overrides for specific settings.

        Returns:
            SequencePool instance.
        """
        data = super().__call__(**kwargs)  ## -- execute TSeqMock
        summary = self.summary
        stype = self.stype
        settings = self._prepare_sequence_pool_settings()
        return SequencePool.init(stype, data, settings, static_data=summary)

    def _prepare_sequence_pool_settings(self):
        """
        Prepare settings for sequence pool initialization.
        """
        settings = self.settings
        column_mapping = settings.output_columns.serialize(format_type="json")
        data_columns = [
            column
            for column in self.data.columns
            if column not in column_mapping.values()
        ]
        static_features = [
            column
            for column in self.summary.columns
            if column not in column_mapping.values()
        ]
        column_mapping.update(
            {
                "entity_features": data_columns,
                "static_features": static_features,
            }
        )
        return column_mapping
