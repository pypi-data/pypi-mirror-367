"""
Linear Pairwise Sequence Metric
==================

C the linear pairwise distance between two sequences.
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
    LinearPairwiseSequenceMetric,
    LinearPairwiseSequenceMetricSettings,
)

# %% [markdown]
# ## Data Setup
#
# Let's create a simple sequence data to demonstrate the linear pairwise metric.

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
# ### Linear Pairwise Metric
#
# Compares sequences element-by-element using an underlying entity metric (default: Hamming with default settings).

# %%
# Init linear metric with default settings
settings = LinearPairwiseSequenceMetricSettings()
linear_metric = LinearPairwiseSequenceMetric(settings=settings)

# -- Settings overview
linear_metric.view_settings()


# %%
# Access two simple sequences
seq_0 = simple_pool["seq-0"]
seq_1 = simple_pool["seq-1"]

# Compute linear pairwise distance
linear_metric(seq_0, seq_1)

# %%
# Compute linear pairwise directly on sequence pool
linear_metric.collect_as_matrix(simple_pool)

# %% [markdown]
# Before computing the metric, you can customize its behavior using `update_settings()` or `kwargs`.

# %%
# Preconfigure the aggregation function using update_settings
linear_metric.update_settings(
    agg_fun="sum",  # Use sum aggregation instead of default mean
)

linear_metric.collect_as_matrix(simple_pool)

# %%
# Provide the aggregation function directly as kwargs
linear_metric.collect_as_matrix(
    simple_pool,
    agg_fun="sum",  # Use sum aggregation instead of default mean
)
