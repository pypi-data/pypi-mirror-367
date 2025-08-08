#!/usr/bin/env python3
"""
Query-based date resolution utilities and settings.
"""

import logging
import dataclasses
from typing import Optional

from .anchor import resolve_date_from_anchor, DateAnchor

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class QueryDateResolverSettings:
    """
    Configuration for query-based date resolution.

    Attributes:
        query (str): Query string to select relevant rows from sequence data.
            Can refer to any valid field (e.g. "event == 'hospitalization'").
        anchor (DateAnchor, optional): Reference point within periods for time calculation.
            Auto-resolved by sequence type if not specified:
            - EventSequence: 'start' (events are points in time)
            - StateSequence: 'start' (beginning of state periods)
            - IntervalSequence: uses sequence settings anchor
            Override with explicit anchor for custom resolution strategy.
        use_first (bool): If True, uses first matching row; otherwise last.
    """

    query: str
    use_first: bool = True
    anchor: Optional[DateAnchor] = None


def get_date_from_query(sequence_data, query, temporal_columns, anchor, use_first=True):
    """
    Retrieve date from dataframe using query and anchoring strategy.

    Args:
        sequence_data: Dataframe containing sequence data
        query: Query to apply to the dataframe
        temporal_columns: List of temporal columns
        anchor: Date anchoring strategy (START, END, MIDDLE)
        use_first: If True, uses first row of result, otherwise last

    Returns:
        Unique date or dictionary of dates by sequence
    """
    df_filtered = sequence_data.query(query, inplace=False)
    all_seq_ids = sequence_data.index.unique()
    is_pool = all_seq_ids.nunique() > 1

    if not is_pool:
        if df_filtered.empty:
            LOGGER.warning("Query returned empty DataFrame. Returning None.")
            return None
        return resolve_date_from_anchor(
            df_filtered, temporal_columns, anchor, use_first
        )

    # Handle pool case - return dict of dates by sequence
    result = {}
    for seq_id in all_seq_ids:
        if seq_id in df_filtered.index:
            seq_data = df_filtered.loc[[seq_id]]
            result[seq_id] = resolve_date_from_anchor(
                seq_data, temporal_columns, anchor, use_first
            )
        else:
            result[seq_id] = None
            LOGGER.warning("No sequence found with id %s", seq_id)

    return result
