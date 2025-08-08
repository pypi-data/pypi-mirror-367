#!/usr/bin/env python3
"""
State sequence class.
"""

from ...base.sequence import Sequence
from .entity import StateEntity
from .settings import StateSequenceSettings


class StateSequence(Sequence, register_name="state"):
    """
    State sequence.
    """

    SETTINGS_DATACLASS = StateSequenceSettings

    def _get_entity(self, data):
        return StateEntity(data, self._settings)

    def filter(self, criterion, criterion_type=None, inplace=False, **kwargs):
        """
        Filter entities based on the given criterion.

        This method is inherited from the parent class but is **not compatible**
        with this subclass.
        It raises an exception because filtering at the entity level is not
        supported for state sequences.
        Consider using interval sequences instead.

        Args:
            criterion_settings (Union[Criterion, dict]):
                Criterion, either as a `Criterion` object or a dictionary,
                applicable at the entity level.

            criterion_type (str, optional):
                Type of criterion to apply (e.g., "query" or "pattern").
                Required if `criterion_settings` is a dictionary.

            inplace (bool, optional):
                If `True`, modifies the object in place. Defaults to `False`.

            **kwargs:
                Additional arguments to override criterion attributes.

        Raises:
            NotImplementedError:
                Raised because entity-level filtering is not supported for state sequences.
        """
        raise NotImplementedError(
            "Entity level filtering is not supported for state sequences. "
            "Consider using interval sequence instead."
        )
