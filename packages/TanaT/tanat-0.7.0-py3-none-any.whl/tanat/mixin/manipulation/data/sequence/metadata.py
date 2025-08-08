#!/usr/bin/env python3
"""
Metadata mixin.
"""

import dataclasses

from .....sequence.metadata.metadata import Metadata
from .....time.granularity import Granularity


class MetadataMixin:
    """
    Mixin for metadata.
    """

    def __init__(self, metadata=None):
        if metadata is not None:
            self._check_metadata(metadata)
        self._metadata = metadata

    @property
    def metadata(self):
        """
        The metadata.
        """
        if self._metadata is None:
            return Metadata()
        return self._metadata

    @property
    def granularity(self):
        """
        The granularity of the sequences in the pool.
        """
        if self.metadata is None:
            return None
        return self.metadata.granularity

    @granularity.setter
    def granularity(self, value):
        """Set the granularity."""
        self._metadata = dataclasses.replace(
            self.metadata, granularity=Granularity.from_str(value)
        )

    def _check_metadata(self, metadata):
        """
        Check the input metadata.
        """
        if isinstance(metadata, dict):
            metadata = Metadata(**metadata)
        if not isinstance(metadata, Metadata):
            raise ValueError("Metadata must be an instance of Metadata.")
