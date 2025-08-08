"""
Longest Common Prefix
==================

Compute the longest common prefix (LCP) between two sequences.
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
    LCPSequenceMetric,
    LCPSequenceMetricSettings,
)

# %% [markdown]
# ## Data Setup
#
# Let's create a simple sequence data to demonstrate the LCP metric.

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
# ### Longest Common Prefix (LCP)
#
# Focuses on similarity at the beginning of sequences.

# %%
# Create LCP metric
settings = LCPSequenceMetricSettings()
lcp_metric = LCPSequenceMetric(settings=settings)

# -- Settings overview
lcp_metric.view_settings()

# %%
# Access two simple sequences
seq_0 = simple_pool["seq-0"]
seq_1 = simple_pool["seq-1"]

# Compute LCP distance
lcp_metric(seq_0, seq_1)

# %%
# Compute LCP distance directly on sequence pool
lcp_metric.collect_as_matrix(simple_pool)

# %% [markdown]
# Before computing the metric, you can customize its behavior using `update_settings()` or `kwargs`.

# %%
# Preconfigure the behavior using update_settings
lcp_metric.update_settings(
    as_dist=True,
    norm=False,
)

lcp_metric.collect_as_matrix(simple_pool)

# %%
# Modify behavior directly from kwargs
lcp_metric.collect_as_matrix(
    simple_pool,
    as_dist=True,
    norm=False,
)
