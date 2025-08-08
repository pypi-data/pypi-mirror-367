"""
Coxnet Survival Analysis
========================

This example shows how to apply Coxnet-based survival analysis on temporal sequences using TanaT.
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
# We generate a set of event sequences and link them to static patient data (e.g., gender, age group, smoking status).

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
# Generate static features for each sequence (patient metadata)
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

# Attach static features to the event pool
event_pool.add_static_features(static_data)

# %% [markdown]
# ## 2. Coxnet Survival Analysis
#
# We’ll now train a Coxnet model to predict survival probabilities, using a specific event (e.g., `'A'`) as the endpoint.

# %%
# Initialize the survival analysis model
surv = SurvivalAnalysis("coxnet")
surv.view_settings()

# %%
# Define the starting point (T0) for all sequences
# 1 year ago
event_pool.t_zero = datetime.datetime.now() - datetime.timedelta(days=365)

# %%
# Split the data into training and testing sets
all_ids = list(event_pool.unique_ids)
train_ids = set(random.sample(all_ids, int(0.8 * len(all_ids))))
test_ids = set(all_ids) - train_ids

train_pool = event_pool.subset(train_ids)
test_pool = event_pool.subset(test_ids)

# %%
# Extract survival times for patients (e.g., time to first event 'A')
surv_res = surv.get_survival_array(
    sequence_pool=train_pool,
    query="event == 'A'",
)
surv

# %%
# Train the model using the training data
fit_results = surv.fit(sequence_pool=train_pool, query="event == 'A'")

# %%
# Predict survival functions for test patients
survival_predictions = surv.predict_survival_function(sequence_or_pool=test_pool)

# %%
# Plot predicted survival functions
plt.figure(figsize=(12, 8))
for i, sf in enumerate(survival_predictions):
    plt.step(sf.x, sf.y, where="post", label=f"Patient {i+1}")

plt.title("Predicted Survival Functions")
plt.xlabel("Time (days)")
plt.ylabel("Survival Probability")
plt.grid(True)
plt.legend(loc="best")
plt.show()
