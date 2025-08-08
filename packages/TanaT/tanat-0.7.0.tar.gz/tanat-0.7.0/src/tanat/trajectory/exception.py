#!/usr/bin/env python3
"""
Base class for trajectory exceptions.
"""

from ..exception import TanatException


class TrajectoryException(TanatException):
    """Base class for trajectory exceptions."""


class TrajectoryNotFoundError(TrajectoryException):
    """Exception raised when a trajectory ID is not found."""
