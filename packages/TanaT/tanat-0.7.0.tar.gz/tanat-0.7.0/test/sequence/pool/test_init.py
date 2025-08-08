#!/usr/bin/env python3
"""
Test initialization of sequence pools.
"""

import pytest

import pandas as pd

from tanat.sequence.base.pool import SequencePool


class TestInitSequencePool:
    """
    Test initialization of sequence pools.
    """

    @pytest.mark.parametrize(
        "seq_type,settings",
        [
            ## -- event
            (
                "event",
                {
                    "id_column": "patient_id",
                    "time_column": "date",
                    "entity_features": ["event_type", "provider"],
                    "static_features": [
                        "gender",
                        "age",
                        "insurance",
                        "chronic_condition",
                    ],
                },
            ),
            ## -- state
            (
                "state",
                {
                    "id_column": "patient_id",
                    "entity_features": ["health_state", "condition"],
                    "start_column": "start_date",
                    "end_column": "end_date",
                    "static_features": [
                        "gender",
                        "age",
                        "insurance",
                        "chronic_condition",
                    ],
                },
            ),
            ## -- interval
            (
                "interval",
                {
                    "id_column": "patient_id",
                    "entity_features": [
                        "medication",
                        "administration_route",
                        "dosage",
                    ],
                    "start_column": "start_date",
                    "end_column": "end_date",
                    "static_features": [
                        "gender",
                        "age",
                        "insurance",
                        "chronic_condition",
                    ],
                },
            ),
        ],
    )
    def test_init_sequence_pool(self, pool_data, seq_type, settings):
        """
        Test initialization of sequence pools.
        """
        sequence_data = pool_data[seq_type]
        static_data = pool_data["static_data"]

        seqpool = SequencePool.init(
            seq_type, sequence_data, settings=settings, static_data=static_data
        )

        assert isinstance(seqpool, SequencePool)
        assert isinstance(seqpool.sequence_data, pd.DataFrame)
        assert isinstance(seqpool.static_data, pd.DataFrame)

    @pytest.mark.parametrize("anchor", ["start", "middle", "end"])
    def test_anchoring_interval(self, pool_data, anchor, snapshot):
        """
        Test anchoring behavior for interval sequence types.
        Should modify entity order.
        """
        settings = {
            "id_column": "patient_id",
            "entity_features": [
                "medication",
                "administration_route",
                "dosage",
            ],
            "start_column": "start_date",
            "end_column": "end_date",
            "anchor": anchor,
        }

        sequence_data = pool_data["interval"]

        seqpool = SequencePool.init("interval", sequence_data, settings=settings)
        snapshot.assert_match(seqpool.sequence_data.to_csv())
