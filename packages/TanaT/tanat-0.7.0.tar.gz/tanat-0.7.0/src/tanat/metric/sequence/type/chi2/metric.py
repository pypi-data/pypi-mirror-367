#!/usr/bin/env python3
"""
Chi2 distances.
"""

import logging
from datetime import timedelta

import numpy as np

from ...base.metric import SequenceMetric
from .....sequence.type.event.sequence import EventSequence
from .settings import Chi2MetricSettings


LOGGER = logging.getLogger(__name__)


class Chi2SequenceMetric(SequenceMetric, register_name="chi2"):
    """
    Chi2 Distance

    This metric uses only one (categorical) feature of entity to specify the state of
    the entity. The feature used as state is the first feature of a sequence or it has
    to be specified in the settings of the metrics (see Chi2MetricSettings).

    Letting $p_{j|x}$ be the proportion of time spent in state $j$ in sequence $x$,
    and $p_j$ the overall proportion of time spent in state $j$, the squared Chi-square
    distance reads as follows:
    $$
        chi(x, y) = \\sqrt{\\sum_{j=1}^{|\\Sigma|} \\frac{(p_{j|x} - p_{j|y})^2}{p_j}
    $$
    where $\\Sigma$ is the vocabulary.

    In the case of event sequences, we assume that the proportion of time spent is 1 for
    all events.

    Note
    ----
    Note that his first distribution-based measure is, by definition, sensitive to the time
    spent in the states. However, it is insensitive to the order and exact timing of the states.

    References
    ----------
    Studer, M. and G. Ritschard (2014). "A Comparative Review of Sequence Dissimilarity Measures".
    LIVES Working Papers, 33. NCCR LIVES, Switzerland, doi:10.12682/lives.2296-1658.2014.33

    Deville, J. C., & Saporta, G. (1983). Correspondence analysis,
    with an extension towards nominal time series. Journal of econometrics, 22(1-2),
    169-189.
    """

    SETTINGS_DATACLASS = Chi2MetricSettings

    def __init__(self, settings=None, workenv=None):
        if settings is None:
            settings = Chi2MetricSettings()

        super().__init__(settings, workenv=workenv)

    def __call__(self, seq_a, seq_b, **kwargs):
        """
        Calculate the metric for a specific pair of sequences.

        Args:
            seq_a (Sequence):
                First sequence.
            seq_b (Sequence):
                Second sequence.
            kwargs:
                Optional arguments to override specific settings.

        Returns:
            float: The metric value for the sequence pair.
        """
        self._validate_sequences(seq_a=seq_a, seq_b=seq_b)
        self.update_settings(None, **kwargs)

        if self._settings.feature_id is None:
            fid = seq_a._settings.entity_features[0]
        else:
            fid = self._settings.feature_id

        counts = {}
        chi2 = 0.0
        if isinstance(seq_a, EventSequence):
            for ent in seq_a.entities():
                val = ent[fid]
                if val in counts:
                    counts[val][0] += 1.0
                else:
                    counts[val] = [1.0, 0.0]
            for ent in seq_b.entities():
                val = ent[fid]
                if val in counts:
                    counts[val][1] += 1.0
                else:
                    counts[val] = [0.0, 1.0]
            for _, v in counts.items():
                chi2 += (v[0] - v[1]) ** 2 / (v[0] + v[1])
        else:  # states or intervals
            for ent in seq_a.entities():
                val = ent[fid]
                duration = ent.extent().duration
                if val in counts:
                    counts[val][0] += duration
                else:
                    counts[val] = [duration, timedelta()]
            for ent in seq_b.entities():
                val = ent[fid]
                duration = ent.extent().duration
                if val in counts:
                    counts[val][1] += duration
                else:
                    counts[val] = [timedelta(), duration]
            for _, v in counts.items():
                v0 = v[0].total_seconds() / 3600
                v1 = v[1].total_seconds() / 3600
                chi2 += (v0 - v1) ** 2 / (v0 + v1)
        return np.sqrt(chi2)
