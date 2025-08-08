"""
Create Custom Metric
==================

Create a custom sequence metric.
"""

# %% [markdown]
# ### Required imports

# %%
# Data simulation
from tanat.dataset.simulation.sequence import (
    generate_event_sequences,
)

# Sequence pools
from tanat.sequence import (
    EventSequencePool,
)


# %% [markdown]
# ## Data Setup
#
# Let's create a simple sequence data to demonstrate the soft DTW metric.

# %%
N_SEQ = 10
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

# Generate simple sequences for clear metric demonstration
simple_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["A", "B", "C", "D"],
    missing_data=0.0,
    entity_feature="event",
    seed=SEED,
)

simple_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["event"],
}

simple_pool = EventSequencePool(simple_data, simple_settings)
simple_pool

# %% [markdown]
# ### Custom Sequence Metric
#
# Define a custom sequence metric that simply calculates the length difference between two sequences.


# %%
# Create a custom sequence metric
from tanat.metric.sequence.base.metric import SequenceMetric
import dataclasses


@dataclasses.dataclass
class SimpleLengthSettings:
    """Settings for the length metric."""

    absolute: bool = True  # If True, returns absolute value of the difference


class SimpleLengthMetric(SequenceMetric, register_name="length"):
    """Metric that simply calculates the length difference between two sequences."""

    SETTINGS_DATACLASS = SimpleLengthSettings

    def __init__(self, settings=None):
        if settings is None:
            settings = SimpleLengthSettings()
        super().__init__(settings)

    def __call__(self, seq_a, seq_b, **kwargs):
        """Calculate the length difference between two sequences."""
        with self.with_tmp_settings(**kwargs):  # Temporarily override settings
            len_a = len(seq_a.sequence_data)
            len_b = len(seq_b.sequence_data)

            difference = len_a - len_b

            if self._settings.absolute:
                return abs(difference)

            return difference


# %%
# Access two simple sequences
seq_0 = simple_pool["seq-0"]
seq_1 = simple_pool["seq-1"]

# Test custom metric
custom_metric = SimpleLengthMetric()
custom_metric(seq_0, seq_1)

# %%
custom_metric.collect_as_matrix(simple_pool)
