"""
Tree Survival Analysis
======================

This example shows how to apply a tree-based survival analysis model on temporal sequences using TanaT.
"""

# %% [markdown]
# ### Required Imports

# %%
import datetime
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Data simulation
from tanat.dataset.simulation.sequence import generate_event_sequences

# Sequence pool
from tanat.sequence import EventSequencePool

# Survival analysis
from tanat.survival import SurvivalAnalysis

# %% [markdown]
# ## 1. Data Setup
#
# We generate a set of synthetic event sequences and add static attributes (e.g., gender, age, smoking status) for each patient.

# %%
NUM_SEQUENCES = 100
SEQUENCE_LENGTHS = [4, 5, 6, 7, 8, 9, 10, 11, 12]
RANDOM_SEED = 42

# Generate synthetic event sequences
event_data = generate_event_sequences(
    n_seq=NUM_SEQUENCES,
    seq_size=SEQUENCE_LENGTHS,
    vocabulary=["A", "B", "C", "D"],
    missing_data=0.0,
    entity_feature="event",
    seed=RANDOM_SEED,
)

# Define sequence settings
sequence_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["event"],
}

event_pool = EventSequencePool(event_data, sequence_settings)

# %%
# Create static features (demographics)
patient_ids = list(event_pool.unique_ids)
static_data = pd.DataFrame(
    {
        "id": patient_ids,
        "gender": np.random.choice(["F", "M"], size=len(patient_ids)),
        "Age_Group": np.random.choice(
            ["40-49", "50-59", "60-69", "70-79"], size=len(patient_ids)
        ),
        "Smoker": np.random.choice([True, False], size=len(patient_ids)),
    }
)

# Add static features to the pool
event_pool.add_static_features(static_data)

# %% [markdown]
# ## 2. Tree-Based Survival Analysis
#
# We train a tree-based survival model using a specified event (e.g., `'A'`) as the failure condition.

# %%
# Initialize the model with tree-based backend
surv = SurvivalAnalysis("tree")
surv.view_settings()

# %%
# Define baseline time (T0) for survival computation
# 1 year ago
event_pool.t_zero = datetime.datetime.now() - datetime.timedelta(days=365)

# %%
# Split data into training and test sets
all_ids = list(event_pool.unique_ids)
train_ids = set(random.sample(all_ids, int(0.8 * len(all_ids))))
test_ids = set(all_ids) - train_ids

train_pool = event_pool.subset(train_ids)
test_pool = event_pool.subset(test_ids)

# %%
# Compute survival labels: time to first occurrence of event 'A'
surv_res = surv.get_survival_array(sequence_pool=train_pool, query="event == 'A'")
surv

# %%
# Train the model
fit_results = surv.fit(sequence_pool=train_pool, query="event == 'A'")

# %%
# Predict survival functions on new patients
survival_predictions = surv.predict_survival_function(sequence_or_pool=test_pool)

# %%
# Plot survival functions
plt.figure(figsize=(12, 8))
for i, sf in enumerate(survival_predictions):
    plt.step(sf.x, sf.y, where="post", label=f"Patient {i+1}")

plt.title("Predicted Survival Functions")
plt.xlabel("Time (days)")
plt.ylabel("Survival Probability")
plt.grid(True)
plt.legend(loc="best")
plt.show()
