"""
Soft Dynamic Time Warping
==================

Compute the soft dynamic time warping distance (soft DTW) between two sequences.
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
    SoftDTWSequenceMetric,
    SoftDTWSequenceMetricSettings,
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
# ### Soft Dynamic Time Warping
#
# A differentiable version of DTW that provides smoother distance calculations.

# %%
# Create Soft DTW metric
settings = SoftDTWSequenceMetricSettings()
soft_dtw_metric = SoftDTWSequenceMetric(settings=settings)

# -- Settings overview
soft_dtw_metric.view_settings()

# %%
# Access two simple sequences
seq_0 = simple_pool["seq-0"]
seq_1 = simple_pool["seq-1"]

# Compute edit distance
soft_dtw_metric(seq_0, seq_1)

# %%
# Compute soft DTW distance directly on sequence pool
soft_dtw_metric.collect_as_matrix(simple_pool)

# %% [markdown]
# Before computing the metric, you can customize its behavior using `update_settings()` or `kwargs`.

# %%
# Preconfigure gamma
soft_dtw_metric.update_settings(
    gamma=0.5,  # Reduce gamma
)

soft_dtw_metric.collect_as_matrix(simple_pool)

# %%
# Modify gamma directly from kwargs
soft_dtw_metric.collect_as_matrix(
    simple_pool,
    gamma=0.5,  # Reduce gamma
)
