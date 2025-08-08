#!/usr/bin/env python3
"""
Query criterion mixin.
"""

import logging

from .settings import QueryCriterion


LOGGER = logging.getLogger(__name__)


class QueryCriterionApplierMixin:
    """
    Mixin for applying pandas-style query filtering to data.
    """

    SETTINGS_DATACLASS = QueryCriterion

    def _apply_query(self, sequence_or_pool, inplace=False):
        """
        Apply the query to the given data.

        Args:
            sequence_or_pool (Union[SequencePool, Sequence]):
                The sequence or sequence pool to filter.
            inplace (bool, optional):
                - True: Modify the original DataFrame
                - False: Return a new filtered DataFrame
                Defaults to False.

        Returns:
            pandas.DataFrame: The filtered data or None if inplace.
        """
        return sequence_or_pool.sequence_data.query(
            self.settings.query, inplace=inplace
        )
