"""
Edit Distance
==================

Compute the edit distance between two sequences.
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
    EditSequenceMetric,
    EditSequenceMetricSettings,
)

# %% [markdown]
# ## Data Setup
#
# Let's create a simple sequence data to demonstrate the Edit metric.

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
# ### Edit Distance
#
# Measures the minimum number of operations needed to transform one sequence into another.

# %%
# Create edit distance metric
settings = EditSequenceMetricSettings()
edit_metric = EditSequenceMetric(settings=settings)

# Settings overview
edit_metric.view_settings()

# %%
# Access two simple sequences
seq_0 = simple_pool["seq-0"]
seq_1 = simple_pool["seq-1"]

# Compute edit distance
edit_metric(seq_0, seq_1)

# %%
# Compute Edit distance directly on sequence pool
edit_metric.collect_as_matrix(simple_pool)

# %% [markdown]
#
# Before computing the metric, you can customize its behavior using `update_settings()` or `kwargs`.

# %%
# Preconfigure the deletion cost using update_settings
edit_metric.update_settings(
    deletion_cost=2.0,  # Double the deletion cost
)

edit_metric.collect_as_matrix(simple_pool)

# %%
# Modify behavior directly from kwargs
edit_metric.collect_as_matrix(
    simple_pool,
    deletion_cost=2.0,  # Double the deletion cost
)
