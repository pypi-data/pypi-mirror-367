"""
Dynamic Time Warping
==================

Compute the dynamic time warping (DTW) distance between two sequences.
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

# Sequence Metrics
from tanat.metric.sequence import (
    DTWSequenceMetric,
    DTWSequenceMetricSettings,
)

# %% [markdown]
# ## Data Setup
#
# Let's create a simple sequence data to demonstrate the DTW metric.

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
# ### Dynamic Time Warping (DTW)
#
# DTW allows flexible alignment between sequences of different lengths.

# %%
# Create DTW metric
settings = DTWSequenceMetricSettings()
dtw_metric = DTWSequenceMetric(settings=settings)

# -- Settings overview
dtw_metric.view_settings()

# %%
# Access two simple sequences
seq_0 = simple_pool["seq-0"]
seq_1 = simple_pool["seq-1"]

# Compute DTW distance
dtw_metric(seq_0, seq_1)

# %%
# Compute DTW directly on sequence pool
dtw_metric.collect_as_matrix(simple_pool)

# %% [markdown]
# Before computing the metric, you can customize its behavior using `update_settings()` or `kwargs`.

# %%
# Preconfigure the the behavior of the metric
dtw_metric.update_settings(
    sc_param=2,  # band constraint = 2
)

dtw_metric.collect_as_matrix(simple_pool)

# %%
# Modify the behavior directly from kwargs
dtw_metric.collect_as_matrix(
    simple_pool,
    sc_param=2,  # band constraint = 2
)
