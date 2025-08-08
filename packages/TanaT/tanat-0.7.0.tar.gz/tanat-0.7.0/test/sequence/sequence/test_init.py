#!/usr/bin/env python3
"""
Test initialization of unique sequence.
"""

import pytest

import pandas as pd

from tanat.sequence.base.sequence import Sequence


class TestInitSequence:
    """
    Test initialization of sequence.
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
    def test_init_unique_sequence(self, single_id_data, seq_type, settings):
        """
        Test initialization of unique sequence.
        """
        sequence_data = single_id_data[seq_type]
        static_data = single_id_data["static_data"]

        uniq_seq = Sequence.init(
            seq_type,
            id_value=1,
            sequence_data=sequence_data,
            settings=settings,
            static_data=static_data,
        )

        assert isinstance(uniq_seq, Sequence)
        assert isinstance(uniq_seq.sequence_data, pd.DataFrame)
        assert isinstance(uniq_seq.static_data, pd.DataFrame)

    @pytest.mark.parametrize("anchor", ["start", "middle", "end"])
    def test_anchoring_interval(self, single_id_data, anchor, snapshot):
        """
        Test anchoring behavior for interval sequence types.
        For id_value = 1, it does not modify entity order.
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
        sequence_data = single_id_data["interval"]

        uniq_seq = Sequence.init(
            "interval",
            id_value=1,
            sequence_data=sequence_data,
            settings=settings,
        )
        snapshot.assert_match(uniq_seq.sequence_data.to_csv())
