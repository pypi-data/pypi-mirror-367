#!/usr/bin/env python3
"""
Input metadata.
"""

import logging
from typing import Optional
import copy

from pydantic.dataclasses import dataclass, Field
from pypassist.fallback.typing import Dict

from .enum import ColumnType
from ...time.granularity import Granularity

LOGGER = logging.getLogger(__name__)


@dataclass
class ColumnMetadata:
    """
    Column metadata.
    """

    ctype: ColumnType = ColumnType.INFERRED
    description: Optional[str] = None

    @classmethod
    def from_value(cls, value):
        """
        Initialize from a valid metadata file value.
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls(**value)
        if isinstance(value, str):
            return cls(ctype=value)
        raise ValueError("Either a dict or a string are required.")


@dataclass
class Metadata:
    """
    Metadata for Sequence and SequencePool data.

    Args:

        granularity:
            The granularity of the data.

        columns:
            A dict mapping column names to values that can be tranformed
            into ColumnMetadata via ColumnMetadata.from_value().

        default:
            A default ColumnMetadata to use for columns not found in
            "columns".
    """

    granularity: Granularity = Granularity.DAY
    columns: Dict[str, ColumnMetadata] = Field(default_factory=dict)
    default: ColumnMetadata = Field(default_factory=ColumnMetadata)

    def __post_init__(self):

        # Convert all column values using ColumnMetadata.from_value
        self.columns = {
            key: ColumnMetadata.from_value(value)
            for (key, value) in self.columns.items()
            if value
        }

    def get_column_type(self, name):
        """
        Get the type of a column given its name.

        Args:
            name:
                The column name.

        Returns:
            The column type as an instance of ColumnType.
        """
        return self.columns.get(name, self.default).ctype

    def copy(self):
        """
        Create a copy of the metadata.
        """
        return copy.deepcopy(self)
