#!/usr/bin/env python
"""Column type enum."""

import enum

from pypassist.enum.enum_str import EnumStrMixin


# TODO
# Add duration, etc.
@enum.unique
class ColumnType(EnumStrMixin, enum.Enum):
    """
    Column type.
    """

    INFERRED = enum.auto()
    INT = enum.auto()
    FLOAT = enum.auto()
    STRING = enum.auto()
    BOOL = enum.auto()
    DATETIME = enum.auto()
