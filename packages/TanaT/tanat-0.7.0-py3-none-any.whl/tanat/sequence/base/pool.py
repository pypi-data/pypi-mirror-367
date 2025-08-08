#!/usr/bin/env python3
"""
SequencePool base class.
"""

from abc import ABC, abstractmethod
import itertools
import logging

from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.registrable import Registrable, UnregisteredTypeError
from pypassist.runner.workenv.mixin.source import SourceMixin
from pypassist.utils.convert import ensure_list
from pydantic_core import core_schema

from ...criterion.base.enum import CriterionLevel
from ...criterion.utils import resolve_and_init_criterion
from ...mixin.manipulation.sequence import SequenceManipulationMixin
from ...mixin.summarizer.sequence import SequenceSummarizerMixin
from ..settings.utils import _create_child_settings
from .exception import (
    UnregisteredSequenceTypeError,
    SequenceNotFoundError,
)

LOGGER = logging.getLogger(__name__)


class SequencePool(
    ABC,
    Registrable,
    SettingsMixin,
    SequenceSummarizerMixin,
    SourceMixin,
    SequenceManipulationMixin,
    Cachable,
):
    """
    Base class for registrable SequencePool subclasses.
    """

    _REGISTER = {}
    _IS_POOL = True  ## A flag to differentiate between SequencePool and Sequence

    def __init__(self, sequence_data, settings, metadata=None, static_data=None):
        """
        Args:
            sequence_data:
                The input sequence data.

            settings:
                The sequence pool settings.

            metadata:
                The metadata for the input data.

            static_data:
                The static feature data.
        """
        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)
        SourceMixin.__init__(self)
        SequenceManipulationMixin.__init__(
            self,
            sequence_data=sequence_data,
            static_data=static_data,
            metadata=metadata,
        )

    @classmethod
    def init(cls, stype, sequence_data, settings, metadata=None, static_data=None):
        """
        Initialize the sequence pool for a specific type.

        Args:
            stype:
                The sequence type.

            sequence_data:
                The input sequence data.

            settings:
                The sequence pool settings.

            metadata:
                The metadata for the input data.

            static_data:
                The static feature data.

        Returns:
            An instance of the sequence pool.
        """
        try:
            seqpool = cls.get_registered(stype)(
                sequence_data, settings, metadata, static_data
            )
        except UnregisteredTypeError as err:
            raise UnregisteredSequenceTypeError(
                f"Unknown sequence type: '{stype}'. "
                f"Available sequence types: {cls.list_registered()}"
            ) from err

        return seqpool

    @Cachable.caching_property
    def sequence_data(self):
        """
        The sequence data.
        """
        return self._get_sequence_data()

    @property
    def unique_ids(self):
        """
        The set of unique IDs in the pool.
        """
        return set(self.sequence_data.index.get_level_values(self.settings.id_column))

    def _get_sequence(
        self, id_value, sequence_data, static_data=None, entity_features=None
    ):
        """
        Internal method for returning a subclass of Sequence containing the data
        associated with a specific ID.

        Args:
            id_value:
                The ID value this sequence.

            sequence_data:
                The sub-dataframe containing values for one particular ID.

            static_data:
                The static feature data.

            entity_features:
                Subset list of entity feature names to specify in settings.entity_features.
                If None, includes all features specified in `settings.entity_features`.

        Returns:
            An instance of a Sequence subclass.
        """
        settings = _create_child_settings(
            self.settings,
            entity_features=entity_features or self.settings.entity_features,
        )

        metadata_sequence = None
        if self.metadata is not None:
            metadata_sequence = self._copy_metadata(
                deep=False
            )  # Shallow copy is fine for individual sequence

        sequence = self._create_sequence_instance(
            id_value,
            sequence_data.loc[[id_value]],
            settings,
            metadata_sequence,
            static_data,
        )

        # Use common t_zero propagation
        self._propagate_t_zero(sequence, id_value)
        return sequence

    @abstractmethod
    def _create_sequence_instance(
        self, id_value, sequence_data, settings, metadata, static_data
    ):
        """
        Create sequence instance of the appropriate type.

        Args:
            id_value: The ID value for this sequence.
            sequence_data: The sequence data for this ID.
            settings: The sequence settings.
            metadata: The metadata for this sequence.
            static_data: The static data for this sequence.

        Returns:
            An instance of a Sequence subclass.
        """

    @Cachable.caching_method()
    def get_sequences(self, entity_features=None):
        """
        A dictionary mapping unique IDs to Sequence objects.

        Args:
            entity_features (list, optional):
                Subset list of feature names to include in the output.
                If None, includes all features specified in `settings.entity_features`.
        Returns:
            dict: A dictionary where the keys are unique IDs and the values are
                Sequence objects containing the corresponding data.
        """

        def get_sequence_data(subset_features=None):
            """
            Internal method for returning the sequence data, and data columns to consider.
            """
            sequence_data = self.sequence_data
            data_cols = None
            if subset_features is not None:
                if not isinstance(subset_features, list):
                    subset_features = list(subset_features)

                allowed_features = set(self.settings.subset_features)
                data_cols = [col for col in subset_features if col in allowed_features]
                ignored_features = set(subset_features) - allowed_features
                for feature in ignored_features:
                    LOGGER.warning(
                        "%s not in entity feature definition, will not be included",
                        feature,
                    )
                if data_cols:
                    full_column_set = data_cols + self.settings.temporal_columns()
                    sequence_data = sequence_data.loc[:, full_column_set]
            return sequence_data, data_cols

        sequence_data, data_cols = get_sequence_data(subset_features=entity_features)
        all_seq_ids = self.unique_ids
        sequences = {
            id_value: self._get_sequence(
                id_value, sequence_data, self.static_data, entity_features=data_cols
            )
            for id_value in all_seq_ids
        }
        return sequences

    def iter_pairs(self, entity_features=None):
        """
        Get all pairs of sequences in the sequence pool.

        Args:
            entity_features (list, optional):
                List of entity features names to include in the output.
                If None, includes all entity_features.
        Returns:
            An iterable of pairs of sequences.
        """
        set_unique_ids = self.unique_ids
        for id_a, id_b in itertools.product(set_unique_ids, repeat=2):
            yield (
                self._get_sequence(
                    id_a,
                    self.sequence_data,
                    self.static_data,
                    entity_features=entity_features,
                ),
                self._get_sequence(
                    id_b,
                    self.sequence_data,
                    self.static_data,
                    entity_features=entity_features,
                ),
            )

    # pylint: disable=arguments-differ
    def provide(
        self,
        *,
        export,
        output_dir,
        exist_ok,
    ):
        """
        Provide the sequence pool in a runner.
        """
        if export:
            self._export(output_dir, exist_ok=exist_ok, makedirs=True)
        return self

    def _export(self, output_dir, exist_ok, makedirs):
        """
        Export sequence pool settings, data and static data
        """
        # pylint: disable=no-member
        self.export_settings(
            output_dir=output_dir,
            format_type="yaml",
            exist_ok=exist_ok,
            makedirs=makedirs,
        )

        self.export_static_data(
            filepath=output_dir / "static_data.csv",
            exist_ok=exist_ok,
            makedirs=makedirs,
            index=False,
        )
        self.export_sequence_data(
            filepath=output_dir / "sequence_data.csv",
            exist_ok=exist_ok,
            makedirs=makedirs,
            index=False,
        )
        # TODO: Export metadata

    def subset(self, id_values, inplace=False):
        """
        Get a subset of the sequence pool based on a list of IDs.

        Args:
            id_values (list): A list of sequence IDs.
            inplace (bool, optional): If True, modifies the current sequence
                pool in place. Defaults to False.

        Returns:
            SequencePool: A new sequence pool containing only the specified
                sequences (or self if inplace=True).

        Examples:
            Create subset from specific IDs:

            >>> subset_pool = seqpool.subset(["seq-1", "seq-3", "seq-5"])
            >>> print(f"Subset contains {len(subset_pool)} sequences")

            Use with which() to filter then subset:

            >>> from tanat.criterion.mixin.static.settings import StaticCriterion
            >>> elderly_criterion = StaticCriterion(query="age > 60")
            >>> elderly_ids = seqpool.which(elderly_criterion)
            >>> elderly_subset = seqpool.subset(elderly_ids)
        """
        id_values = ensure_list(id_values)
        seq_data = self._subset_sequence_data(id_values)
        static_data = self._subset_static_data(id_values)

        if inplace:
            self._sequence_data = seq_data
            self._static_data = static_data
            self.clear_cache()
            return None

        # Use the new helper methods for clean copying
        metadata_copy = self._copy_metadata(deep=True)
        settings_copy = self._copy_settings(deep=True)

        return self.__class__(
            seq_data,
            settings_copy,
            metadata_copy,
            static_data,
        )

    def filter(
        self, criterion, level=None, inplace=False, criterion_type=None, **kwargs
    ):
        """
        Apply a filter to the sequence pool using the specified criterion.

        Args:
            criterion (Union[Criterion, dict]):
                Defines the criterion to apply, either as a dictionary or a
                Criterion object.
            level (str, optional):
                Specifies the level to apply the criterion, either "sequence"
                or "entity". Required if criterion is applicable at both levels
                or if criterion is a dictionary. Defaults to None.
            inplace (bool, optional):
                If set to True, modifies the current sequence pool in place.
                Defaults to False.
            criterion_type (str, optional):
                Indicates the type of criterion to apply, such as "query" or
                "pattern". Required if criterion is provided as a dictionary.
                Defaults to None.
            kwargs:
                Additional keyword arguments to override criterion attributes.

        Returns:
            SequencePool:
                Returns a new filtered sequence pool, or the modified pool if
                inplace is True.

        Examples:
            Filter sequences containing emergency events:

            >>> from tanat.criterion.mixin.pattern.settings import PatternCriterion
            >>> criterion = PatternCriterion(pattern={"event_type": "EMERGENCY"})
            >>> filtered_pool = seqpool.filter(criterion, level="sequence")

            Filter entities using pandas query:

            >>> from tanat.criterion.mixin.query.settings import QueryCriterion
            >>> criterion = QueryCriterion(query="event_type == 'EMERGENCY'")
            >>> filtered_pool = seqpool.filter(criterion, level="entity")

            Filter by static data (age > 50):

            >>> from tanat.criterion.mixin.static.settings import StaticCriterion
            >>> criterion = StaticCriterion(query="age > 50")
            >>> filtered_pool = seqpool.filter(criterion)
        """
        # -- validate, resolve, and initialize criterion
        criterion, _ = resolve_and_init_criterion(
            criterion, level, criterion_type, CriterionLevel.SEQUENCE
        )

        # Apply the filter
        return criterion.filter(self, inplace, **kwargs)

    def __len__(self):
        """
        Number of sequences in the pool
        """
        return len(self.unique_ids)

    def __getitem__(self, id_value):
        """
        Get the sequence for a specific ID.

        Args:
            id_value:
                The ID value.

        Returns:
            The sequence for the ID.
        """
        if id_value not in self.unique_ids:
            raise SequenceNotFoundError(
                f"Sequence ID `{id_value}` not found in `{self.__class__.__name__}`."
            )
        return self._get_sequence(id_value, self.sequence_data, self.static_data)

    def which(self, criterion, criterion_type=None, **kwargs):
        """
        Get the IDs of sequences that match the criterion.

        Args:
            criterion (Union[Criterion, dict]):
                Defines the criterion, either as a dictionary or a Criterion
                object to apply. The criterion must be applicable at the
                'sequence' level.
            criterion_type (str, optional):
                Indicates the type of criterion to apply, such as "query" or
                "pattern". Required if criterion is provided as a dictionary.
                Defaults to None.
            kwargs:
                Additional keyword arguments to override criterion attributes.

        Returns:
            set: A set of sequence IDs that match the criterion.

        Examples:
            Find sequences with emergency events:

            >>> from tanat.criterion.mixin.pattern.settings import PatternCriterion
            >>> criterion = PatternCriterion(pattern={"event_type": "EMERGENCY"})
            >>> emergency_ids = seqpool.which(criterion)
            >>> print(f"Found {len(emergency_ids)} emergency sequences")

            Find sequences by length:

            >>> from tanat.criterion.sequence.type.length.settings import LengthCriterion
            >>> criterion = LengthCriterion(gt=10)
            >>> long_seq_ids = seqpool.which(criterion)
        """
        seq_criterion, _ = resolve_and_init_criterion(
            criterion, "sequence", criterion_type, CriterionLevel.SEQUENCE
        )
        return seq_criterion.which(self, **kwargs)

    def __iter__(self):
        """Iterate over the sequence pool."""
        set_unique_ids = self.unique_ids
        for id_value in set_unique_ids:
            yield self._get_sequence(id_value, self.sequence_data, self.static_data)

    def __get_pydantic_core_schema__(self, handler):  # pylint: disable=unused-argument
        """Pydantic schema override."""
        return core_schema.any_schema()

    def __repr__(self):
        """Return a string representation of the sequence pool."""
        return self.summarize()
