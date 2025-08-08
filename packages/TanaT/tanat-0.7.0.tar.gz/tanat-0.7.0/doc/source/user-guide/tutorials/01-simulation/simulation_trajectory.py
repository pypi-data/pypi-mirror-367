# %% [markdown]
# # Trajectory Simulation
#
# This notebook demonstrates how to simulate synthetic trajectories using *TanaT*. Trajectories combine multiple sequence types (events, states, intervals) to represent complex patient journeys. We'll explore how to create realistic multi-dimensional temporal data into comprehensive trajectories.
#
# These simulation tools are essential for:
# - Testing sequence analysis algorithms
# - Generating synthetic data for research
# - Understanding the impact of sequence characteristics on analysis outcomes
# - Creating controlled experiments with known ground truth

# %% [markdown]
# ### Required imports

# %%
from datetime import datetime
import numpy as np
import pandas as pd

# Simulation imports
from tanat.dataset.simulation.sequence import (
    generate_event_sequences,
    generate_state_sequences,
    generate_interval_sequences,
)

# Sequence pools
from tanat.sequence import (
    EventSequencePool,
    StateSequencePool,
    IntervalSequencePool,
)

# Trajectory pool
from tanat.trajectory import TrajectoryPool

# %% [markdown]
# ## 1. Creating Multi-Sequence Trajectories
#
# Trajectories represent complete patient journeys by combining different types of sequences. Let's simulate a healthcare scenario with medical visits, health states, and medication treatments.

# %%
# Global settings
N_SEQ = 150
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

# %% [markdown]
# ### Generate Individual Sequence Types
#
# First, we'll create the component sequences that will form our trajectories.

# %%
# Generate event sequences (medical visits)
event_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "GENERAL_PRACTITIONER",
        "SPECIALIST",
        "EMERGENCY",
        "LABORATORY",
        "RADIOLOGIST",
    ],
    missing_data=0.1,
    entity_feature="visit_type",
    seed=SEED,
)

# Generate state sequences (health conditions)
state_data = generate_state_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "HEALTHY",
        "ACUTE_ILLNESS",
        "TREATMENT",
        "RECOVERY",
        "CHRONIC_MONITORING",
    ],
    missing_data=0.05,
    entity_feature="health_state",
    seed=SEED,
)

# Generate interval sequences (medication treatments)
interval_data = generate_interval_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "ANTIBIOTIC",
        "PAIN_RELIEVER",
        "ANTI_INFLAMMATORY",
        "ANTIHYPERTENSIVE",
    ],
    missing_data=0.15,
    entity_feature="medication",
    seed=SEED,
)

print(f"Generated data for {N_SEQ} patients:")
print(f"- Events: {len(event_data)} records")
print(f"- States: {len(state_data)} records")
print(f"- Intervals: {len(interval_data)} records")

# %% [markdown]
# ### Create Sequence Pools
#
# Transform the raw data into *TanaT* sequence pools with appropriate settings.

# %%
# Create sequence pools
event_pool = EventSequencePool(
    event_data,
    {
        "id_column": "id",
        "time_column": "date",
        "entity_features": ["visit_type"],
    },
)

state_pool = StateSequencePool(
    state_data,
    {
        "id_column": "id",
        "start_column": "start_date",
        "default_end_value": datetime.now(),
        "entity_features": ["health_state"],
    },
)

interval_pool = IntervalSequencePool(
    interval_data,
    {
        "id_column": "id",
        "start_column": "start_date",
        "end_column": "end_date",
        "entity_features": ["medication"],
    },
)

# %% [markdown]
# ### Generate Static Patient Data
#
# Create demographic and clinical characteristics that will be shared across all sequences for each patient.


# %%
def generate_patient_demographics(n_patients, seed=42):
    """Generate realistic patient demographic data."""
    np.random.seed(seed)

    demographics = []
    for i in range(n_patients):
        patient_id = f"seq-{i}"
        demographics.append(
            {
                "id": patient_id,
                "age_group": np.random.choice(
                    ["18-30", "31-50", "51-70", "70+"], p=[0.2, 0.3, 0.3, 0.2]
                ),
                "gender": np.random.choice(["M", "F"], p=[0.48, 0.52]),
                "insurance_type": np.random.choice(
                    ["PUBLIC", "PRIVATE", "MIXED"], p=[0.6, 0.3, 0.1]
                ),
                "chronic_condition": np.random.choice([True, False], p=[0.35, 0.65]),
                "risk_score": np.random.uniform(0, 10),
            }
        )

    return pd.DataFrame(demographics)


static_data = generate_patient_demographics(N_SEQ, seed=SEED)
print("Patient demographics:")
static_data.head()

# %% [markdown]
# ## 2. Building the Trajectory Pool
#
# Combine the sequence pools and static data into a comprehensive trajectory pool.

# %%
# Create trajectory pool
trajectory_pool = TrajectoryPool.init_empty()

# Add sequence pools with descriptive names
trajectory_pool.add_sequence_pool(event_pool, "medical_visits")
trajectory_pool.add_sequence_pool(state_pool, "health_states")
trajectory_pool.add_sequence_pool(interval_pool, "medications")

# Add static features
trajectory_pool.add_static_features(
    static_data,
    id_column="id",
    static_features=[
        "age_group",
        "gender",
        "insurance_type",
        "chronic_condition",
        "risk_score",
    ],
)

# Configure trajectory pool settings
trajectory_pool.update_settings(
    intersection=False,  # Use union of IDs across SequencePools
)

trajectory_pool

# %% [markdown]
# ### Examine Individual Trajectories
#
# Let's look at a complete patient trajectory.

# %%
# Examine a specific patient trajectory
patient_id = "seq-5"
patient_trajectory = trajectory_pool[patient_id]
patient_trajectory
