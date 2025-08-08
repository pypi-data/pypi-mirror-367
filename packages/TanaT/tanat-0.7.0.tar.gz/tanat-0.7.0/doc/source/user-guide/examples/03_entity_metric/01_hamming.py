"""
Hamming metric
==================

Compute the distance between two entities.
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

# Entity metrics
from tanat.metric.entity import (
    HammingEntityMetric,
    HammingEntityMetricSettings,
)

# %% [markdown]
# ## Data Setup
#
# Let's create a simple sequence data to demonstrate different metric capabilities.

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
# ## Hamming Entity Metric
#
# Entity metrics compare individual elements within sequences. They form the foundation for sequence-level comparisons.
# By default, the Hamming metric returns 0 for identical elements and 1 for different elements.

# %%
# Create Hamming entity metric with default settings
settings = HammingEntityMetricSettings()
hamming_metric = HammingEntityMetric(settings=settings)
# -- Settings overview
hamming_metric.view_settings()


# %%
# Access first entity from seq-0
entity_a = simple_pool["seq-0"][0]
# Access first entity from seq-1
entity_b = simple_pool["seq-1"][0]
# Compute distance between two entities
print(f"Distance between: {entity_a.value} and {entity_b.value}")
hamming_metric(entity_a, entity_b)


# %% [markdown]
# Before computing the metric, you can customize its behavior using `update_settings()` or `kwargs`.
# In the case of the Hamming metric, providing a cost_dict allows you to control the cost associated with specific comparisons between entity values.

# %%
# Preconfigure the cost dictionary using update_settings
hamming_metric.update_settings(
    cost={
        ("A", "B"): 0,
        ("B", "C"): 1,
        ("C", "D"): 2,
        ("A", "C"): 3,
        ("A", "D"): 4,
        ("B", "D"): 5,
    },
    default_value=-2,  # Fallback cost for any unspecified comparison
)

hamming_metric(entity_a, entity_b)

# %%
# Provide the cost dictionary directly as kwargs
hamming_metric(
    entity_a,
    entity_b,
    cost={
        ("A", "B"): 0,
        ("B", "C"): 1,
        ("C", "D"): 2,
        ("A", "C"): 3,
        ("A", "D"): 4,
        ("B", "D"): 5,
    },
    default_value=10,  # Fallback cost for any unspecified comparison
)
