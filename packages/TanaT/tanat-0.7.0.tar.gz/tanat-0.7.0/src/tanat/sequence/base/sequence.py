#!/usr/bin/env python3
"""
Sequence base class.
"""

from abc import ABC, abstractmethod

from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.registrable import Registrable, UnregisteredTypeError

from ...criterion.base.enum import CriterionLevel
from ...criterion.utils import resolve_and_init_criterion
from ...mixin.manipulation.sequence import SequenceManipulationMixin
from ...mixin.summarizer.sequence import SequenceSummarizerMixin
from .exception import UnregisteredSequenceTypeError


class Sequence(
    ABC,
    Registrable,
    SettingsMixin,
    SequenceSummarizerMixin,
    SequenceManipulationMixin,
    Cachable,
):
    """
    Base class for sequence objects.
    """

    _REGISTER = {}
    _IS_POOL = False  ## A flag to differentiate between SequencePool and Sequence

    def __init__(
        self, id_value, sequence_data, settings, metadata=None, static_data=None
    ):
        self.id_value = id_value
        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)
        SequenceManipulationMixin.__init__(
            self,
            sequence_data=sequence_data,
            static_data=static_data,
            metadata=metadata,
        )

    @classmethod
    def init(
        cls, stype, id_value, sequence_data, settings, metadata=None, static_data=None
    ):
        """
        Initialize the sequence for a specific type.

        Args:
            stype:
                The sequence type.

            id_value:
                The ID of the sequence.

            sequence_data:
                The input sequence data.

            settings:
                The sequence settings.

            metadata:
                The metadata for the input data.

            static_data:
                The static feature data.

        Returns:
            An instance of the sequence.
        """
        try:
            sequence_cls = cls.get_registered(stype)
            sequence = sequence_cls(
                id_value=id_value,
                sequence_data=sequence_data,
                settings=settings,
                metadata=metadata,
                static_data=static_data,
            )
        except UnregisteredTypeError as err:
            registered_sequence_types = cls.list_registered()
            raise UnregisteredSequenceTypeError(
                f"Unknown sequence type: '{stype}'. "
                f"Available sequence types: {registered_sequence_types}"
            ) from err

        return sequence

    @property
    def dim(self):
        """
        Returns the dimension of entity in the sequence,
        corresponding to the number of columns in `sequence_data`.
        """
        return self.sequence_data.shape[1]

    @property
    def dim_names(self):
        """
        Returns the dimension names of entity in the sequence,
        corresponding to the column names in `sequence_data`.
        """
        return list(self.sequence_data.columns)

    @Cachable.caching_method()
    def to_numpy(self, cols=None):
        """
        Returns the data as a NumPy array. If `cols` is specified, only the
        specified columns will be returned in the array.

        Args:
            cols (list):
                List of entity feature names to use.
                If None, all features specified in `settings.entity_features` will be used.

        Returns:
            numpy.array: sequence data
        """
        if cols is None:
            return self.sequence_data[self._settings.entity_features].to_numpy()

        cols = [x for x in self._settings.get_valid_columns() if x in set(cols)]
        return self.sequence_data[cols].to_numpy()

    def entities(self):
        """
        Yields entities generator.
        """
        for _, row in self.sequence_data.iterrows():
            yield self._get_entity(row)

    def match(self, criterion, criterion_type=None, **kwargs):
        """
        Determine if the sequence matches the criterion.

        Args:
            criterion (Union[Criterion, dict]):
                Defines the criterion, either as a dictionary or a Criterion
                object. The criterion must be applicable at the 'sequence' level.
            criterion_type (str, optional):
                Indicates the type of criterion to apply, such as "query" or
                "pattern". Required if criterion is provided as a dictionary.
                Defaults to None.
            kwargs:
                Additional keyword arguments to override criterion attributes.

        Returns:
            bool: True if the sequence matches the criterion, False otherwise

        Examples:
            Test if sequence contains emergency events:

            >>> from tanat.criterion.mixin.pattern.settings import PatternCriterion
            >>> criterion = PatternCriterion(pattern={"event_type": "EMERGENCY"})
            >>> has_emergency = sequence.match(criterion)
            >>> print(f"Has emergency: {has_emergency}")

            Test sequence length:

            >>> from tanat.criterion.sequence.type.length.settings import LengthCriterion
            >>> criterion = LengthCriterion(gt=5)
            >>> is_long = sequence.match(criterion)
        """
        criterion, _ = resolve_and_init_criterion(
            criterion, "sequence", criterion_type, CriterionLevel.SEQUENCE
        )
        return bool(criterion.match(self, **kwargs))

    def filter(self, criterion, criterion_type=None, inplace=False, **kwargs):
        """
        Filter entities that match the criterion.

        Args:
            criterion (Union[Criterion, dict]):
                Defines the criterion, either as a dictionary or a Criterion
                object. The criterion must be applicable at the 'entity' level.
            criterion_type (str, optional):
                Indicates the type of criterion to apply, such as "query" or
                "pattern". Required if criterion is provided as a dictionary.
                Defaults to None.
            inplace (bool, optional):
                If True, modifies the current sequence in place. Defaults to
                False.
            kwargs:
                Additional keyword arguments to override criterion attributes.

        Returns:
            Sequence: A filtered sequence or None if inplace.

        Examples:
            Filter entities without missing values:

            >>> from tanat.criterion.mixin.query.settings import QueryCriterion
            >>> criterion = QueryCriterion(query="event_type.notna()")
            >>> clean_seq = sequence.filter(criterion)
            >>> print(f"Original: {len(sequence)}, Filtered: {len(clean_seq)}")

            Filter entities using pattern matching:

            >>> from tanat.criterion.mixin.pattern.settings import PatternCriterion
            >>> criterion = PatternCriterion(pattern={"event_type": "EMERGENCY"})
            >>> emergency_entities = sequence.filter(criterion)
        """
        # -- validate, resolve, and initialize criterion
        criterion, _ = resolve_and_init_criterion(
            criterion, "entity", criterion_type, CriterionLevel.ENTITY
        )
        return criterion.filter(self, inplace, **kwargs)

    def __getitem__(self, index):
        """
        Return a sequence entity at a given order position.

        Args:
            index (int): index in the sequence
        """
        return self._get_entity(self._get_standardized_data().iloc[index])

    @abstractmethod
    def _get_entity(self, data):
        """
        Get an entity instance.
        """

    def __len__(self):
        """
        Returns the number of entity, corresponding to the number of rows in `sequence_data`.
        """
        return len(self.sequence_data)

    def __repr__(self):
        """Return a string representation of the sequence."""
        return self.summarize()
