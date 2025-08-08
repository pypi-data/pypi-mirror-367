#! /usr/bin/env python3
"""
Criterion level enum.
"""

import importlib
import enum
import logging

from pypassist.enum.enum_str import EnumStrMixin

LOGGER = logging.getLogger(__name__)


class CriterionLevel(EnumStrMixin, enum.Enum):
    """
    Criterion level compatibility.

    Determines whether a criterion will be applied on a sequence or an entity level.
    Level are ordered as: Entity < Sequence < Trajectory
    """

    ENTITY = enum.auto()
    SEQUENCE = enum.auto()
    TRAJECTORY = enum.auto()

    @classmethod
    def get_applier_info(cls, level):
        """
        Get import information for a level.

        Args:
            level: CriterionLevel instance

        Returns:
            tuple: (module_path, class_name)
        """
        mapping = {
            cls.ENTITY: (
                "tanat.criterion.entity.base.applier",
                "EntityCriterionApplier",
            ),
            cls.SEQUENCE: (
                "tanat.criterion.sequence.base.applier",
                "SequenceCriterionApplier",
            ),
            cls.TRAJECTORY: (
                "tanat.criterion.trajectory.base.applier",
                "TrajectoryCriterionApplier",
            ),
        }

        if level not in mapping:
            raise ValueError(f"Unsupported criterion level: {level}")

        return mapping[level]

    def get_registry_cls(self):
        """
        Get the criterion registry base class for the specified level.
        """
        try:
            module_path, class_name = self.__class__.get_applier_info(self)
            # Import the module
            module = importlib.import_module(module_path)
            # Get the class
            criterion_class = getattr(module, class_name)
            return criterion_class

        except (ImportError, AttributeError) as e:
            LOGGER.error("Failed to resolve criterion class for level %s: %s", self, e)
            raise ValueError(
                f"Failed to resolve criterion class for level {self}: {e}"
            ) from e

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value

        raise NotImplementedError(
            f"'<=' not supported between instances of '{type(self).__name__}' "
            f"and '{type(other).__name__}'"
        )
