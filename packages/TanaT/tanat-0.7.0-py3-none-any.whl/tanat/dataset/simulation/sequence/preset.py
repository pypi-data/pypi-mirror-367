#!/usr/bin/env python3
"""
Preset Simulation Functions
"""

from tseqmock.generator.base.profile import Profile
from tseqmock.method.base import GenMethod
from tseqmock.core import TSeqMocker


def generate_event_sequences(
    n_seq,
    seq_size,
    vocabulary=None,
    missing_data=None,
    entity_feature="event",
    seed=None,
):
    """
    Generate event sequences

    Args:
        n_seq: Number of sequences.
        seq_size: Sequence size.
        vocabulary (list, optional): Custom vocabulary for state generation. Defaults to None.
        missing_data (float, optional): Proportion of missing data. Defaults to None.
        entity_feature (str, optional): Name of the entity feature. Defaults to "event".
        seed (int, optional): Random seed. Defaults to None.

    Returns:
        Sequence pool.
    """
    mocker = TSeqMocker("event", seed=seed)
    gen = GenMethod.init("random")
    if vocabulary is not None:
        gen.update_settings(vocabulary=vocabulary)

    missing_config = None
    if missing_data is not None:
        missing_config = {entity_feature: missing_data}

    profile = Profile(
        n_seq=n_seq,
        sequence_size=seq_size,
        entity_features={entity_feature: gen},
        missing_data=missing_config,
        profile_id="",
    )
    return mocker(profiles=[profile])


def generate_state_sequences(
    n_seq,
    seq_size,
    vocabulary=None,
    missing_data=None,
    entity_feature="state",
    seed=None,
):
    """
    Generate synthetic state sequences.

    Args:
        n_seq (int): Number of sequences.
        seq_size (int or list): Sequence size(s).
        vocabulary (list, optional): Custom vocabulary for state generation. Defaults to None.
        missing_data (float, optional): Proportion of missing data. Defaults to None.
        entity_feature (str, optional): Name of the entity feature. Defaults to "state".

    Returns:
        SequencePool: Simulated sequence pool.
    """
    mocker = TSeqMocker("state", seed=seed)
    gen = GenMethod.init("random")
    if vocabulary is not None:
        gen.update_settings(vocabulary=vocabulary)

    missing_config = None
    if missing_data is not None:
        missing_config = {entity_feature: missing_data}

    profile = Profile(
        n_seq=n_seq,
        sequence_size=seq_size,
        entity_features={entity_feature: gen},
        missing_data=missing_config,
        profile_id="",
    )
    return mocker(profiles=[profile])


def generate_interval_sequences(
    n_seq,
    seq_size,
    vocabulary=None,
    missing_data=None,
    entity_feature="activity",
    seed=None,
):
    """
    Generate interval sequences.

    Args:
        n_seq (int): Number of sequences.
        seq_size (int or list): Sequence size(s).
        vocabulary (list, optional): Custom vocabulary for state generation. Defaults to None.
        missing_data (float, optional): Proportion of missing data. Defaults to None.
        entity_feature (str, optional): Name of the entity feature. Defaults to "activity".

    Returns:
        Sequence pool.
    """
    mocker = TSeqMocker("interval", seed=seed)
    gen = GenMethod.init("random")
    if vocabulary is not None:
        gen.update_settings(vocabulary=vocabulary)

    missing_config = None
    if missing_data is not None:
        missing_config = {entity_feature: missing_data}

    profile = Profile(
        n_seq=n_seq,
        sequence_size=seq_size,
        entity_features={entity_feature: gen},
        missing_data=missing_config,
        profile_id="",
    )
    return mocker(profiles=[profile])
