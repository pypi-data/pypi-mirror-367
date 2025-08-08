# %% [markdown]
# # Sequence Simulation
#
# This notebook demonstrates how to simulate synthetic sequences using *TanaT*. We'll explore three types of sequences: event sequences (point-in-time occurrences), state sequences (persistent conditions), and interval sequences (activities with durations).

# %% [markdown]
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
import matplotlib.pyplot as plt
from sklearn.metrics import adjusted_rand_score

# Simulation imports
from tanat.dataset.simulation.sequence import (
    SequencePoolMocker,
    Profile,
    StateTimeDesign,
    EventTimeDesign,
    GenMethod,
    TimeStrategy,
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

# Clustering for evaluation
from tanat.clustering import (
    HierarchicalClustererSettings,
    HierarchicalClusterer,
)

# %% [markdown]
# ## 1. Basic Sequence Generation
#
# *TanaT* provides simple functions to generate synthetic sequences for testing and experimentation.

# %%
# Global settings
N_SEQ = 20
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

# %% [markdown]
# ### Event Sequences
#
# Event sequences represent point-in-time occurrences, such as medical visits or biomarker measurements.

# %%
# Generate event sequences representing medical visits
event_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "GENERAL_PRACTITIONER",
        "SPECIALIST",
        "RADIOLOGIST",
        "EMERGENCY",
    ],
    missing_data=0.1,
    entity_feature="event_type",
    seed=SEED,
)

print("Event sequence data:")
event_data.head(10)

# %% [markdown]
# ### State Sequences
#
# State sequences represent conditions that persist over time, such as health states or treatment phases.

# %%
# Generate state sequences representing health conditions
state_data = generate_state_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "HEALTHY",
        "TREATMENT",
        "CONVALESCENCE",
        "CHRONIC_MONITORING",
        "REMISSION",
    ],
    missing_data=0.1,
    entity_feature="health_state",
    seed=SEED,
)

print("State sequence data:")
state_data.head(10)

# %% [markdown]
# ### Interval Sequences
#
# Interval sequences represent activities with defined start and end times, such as medication treatments or procedures.

# %%
# Generate interval sequences representing medication treatments
interval_data = generate_interval_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "ANTIBIOTIC",
        "PAIN_RELIEVER",
        "CORTICOSTEROID",
        "ANTICOAGULANT",
        "ANTIHYPERTENSIVE",
    ],
    missing_data=0.1,
    entity_feature="medication",
    seed=SEED,
)

print("Interval sequence data:")
interval_data.head(10)

# %% [markdown]
# ## 2. Creating Sequence Pools
#
# Sequence pools organize and manage collections of sequences, providing methods for analysis and manipulation.

# %%
# Create sequence pools from the generated data
event_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["event_type"],
}

state_settings = {
    "id_column": "id",
    "start_column": "start_date",
    "entity_features": ["health_state"],
    "default_end_value": datetime.now(),
}

interval_settings = {
    "id_column": "id",
    "start_column": "start_date",
    "end_column": "end_date",
    "entity_features": ["medication"],
}

# Initialize sequence pools
event_pool = EventSequencePool(event_data, event_settings)
state_pool = StateSequencePool(state_data, state_settings)
interval_pool = IntervalSequencePool(interval_data, interval_settings)

print(f"Event pool: {len(event_pool)} sequences")
print(f"State pool: {len(state_pool)} sequences")
print(f"Interval pool: {len(interval_pool)} sequences")

# %% [markdown]
# ## 3. Advanced Simulation with SequencePoolMocker
#
# For more complex simulations, *TanaT* provides the SequencePoolMocker class, which allows creating distinct patient profiles with different sequence characteristics.

# %% [markdown]
# ### Simulating Patient Profiles
#
# We'll create two distinct patient groups with different health state patterns to demonstrate clustering capabilities.

# %%
# Create simulation engine for state sequences
mocker = SequencePoolMocker("state", seed=SEED)

# Group A: Acute illness and recovery pattern
states_A = ["HEALTHY", "SICK", "TREATMENT", "RECOVERY"]
gen_A = GenMethod.init("random")
gen_A.update_settings(vocabulary=states_A)

profile_A = Profile(
    n_seq=N_SEQ,
    sequence_size=SIZE_DISTRIBUTION,
    entity_features={"state": gen_A},
    profile_id="Acute_Recovery",
)

# Group B: Chronic relapsing condition pattern
states_B = ["SICK", "RELAPSE", "TREATMENT", "STABLE"]
gen_B = GenMethod.init("random")
gen_B.update_settings(vocabulary=states_B)

profile_B = Profile(
    n_seq=N_SEQ,
    sequence_size=SIZE_DISTRIBUTION,
    entity_features={"state": gen_B},
    profile_id="Chronic_Relapsing",
)

# Add profiles to simulator
mocker.add_profile(profile_A)
mocker.add_profile(profile_B)

# %% [markdown]
# ### Configuring Time Strategies
#
# Time strategies define how temporal aspects of sequences are generated.

# %%
# Configure time strategies
t0_strat = TimeStrategy.init("fixed")
t0_strat.update_settings(t0_date="2020-01-01")

sampling_strat = TimeStrategy.init("sequence_specific")
sampling_strat.update_settings(
    distribution="uniform", min_date="2020-01-01", max_date="2023-01-01"
)

mocker.set_time_design(
    StateTimeDesign(t0_strategy=t0_strat, sampling_strategy=sampling_strat)
)

# Generate the sequence pool
simulated_pool = mocker()
print(
    f"Generated pool with {len(simulated_pool)} sequences ({N_SEQ} profile A, {N_SEQ} profile B)"
)
# update default end value
simulated_pool.update_settings(default_end_value=datetime.now())
print(simulated_pool.statistics)

# %% [markdown]
# ## 4. Prepare a futur analysis using simulation
#
# Simulation can help evaluate the most suitable analysis techniques and guide experimental design before conducting real-world tests.

# %% [markdown]
# ### Impact of Sequence Length on Clustering
#
# Let's examine how sequence length affects the ability to distinguish between different profiles.


# %%
def compute_clustering_accuracy(pool):
    """Compute Adjusted Rand Index for clustering accuracy."""
    df = pool.static_data[["_PROFILE_ID_", "hclusters"]].copy()
    true_labels = (
        df["_PROFILE_ID_"].map({"Acute_Recovery": 0, "Chronic_Relapsing": 1}).values
    )
    pred_labels = df["hclusters"].values
    return adjusted_rand_score(true_labels, pred_labels)


# Test different sequence lengths
sequence_lengths = [3, 5, 8, 12, 16, 20]
accuracy_scores = []

for length in sequence_lengths:
    # Update profile settings
    profile_A.sequence_size = length
    profile_B.sequence_size = length

    # Generate new pool
    test_pool = mocker(profiles=[profile_A, profile_B])
    # update default end value to avoid warning
    test_pool.update_settings(default_end_value=datetime.now())

    # Cluster and evaluate
    clusterer = HierarchicalClusterer(
        HierarchicalClustererSettings(
            metric="dtw",
            n_clusters=2,
            cluster_column="hclusters",
        )
    )
    clusterer.fit(test_pool)

    accuracy = compute_clustering_accuracy(test_pool)
    accuracy_scores.append(accuracy)
    print(f"Length {length}: ARI = {accuracy:.3f}")

# %% [markdown]
# Let's visualize the clustering accuracy as a function of sequence length.

# %%
# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(sequence_lengths, accuracy_scores, marker="o", linewidth=2, markersize=8)
plt.title("Impact of Sequence Length on Clustering Accuracy", fontsize=14)
plt.xlabel("Sequence Length", fontsize=12)
plt.ylabel("Adjusted Rand Index", fontsize=12)
plt.ylim(-0.1, 1.05)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# %% [markdown]
# An upward trend in Adjusted Rand Index (ARI) is observed as the sequence length increases.
# ARI quantifies the similarity between clustering results and ground truth, correcting for random agreement.
# This suggests that longer sequences provide more information, making it easier to distinguish between the two simulated profiles.

# %% [markdown]
# ## 3. Biomarker Event Simulation
#
# Let's simulate biomarker measurements as event sequences with continuous values.

# %%
# Create biomarker simulation
biomarker_mocker = SequencePoolMocker("event", seed=42)

# Biomarker A: Normal range values
biomarker_a_gen = GenMethod.init("random")
biomarker_a_gen.update_settings(vocabulary=np.random.uniform(0, 1, 50))

# Biomarker B: Elevated values
biomarker_b_gen = GenMethod.init("random")
biomarker_b_gen.update_settings(vocabulary=np.random.uniform(2, 8, 50))

biomarker_profile = Profile(
    n_seq=N_SEQ,
    sequence_size=SIZE_DISTRIBUTION,
    entity_features={  # Multiple entity features
        "biomarker_a": biomarker_a_gen,
        "biomarker_b": biomarker_b_gen,
    },
    missing_data={"biomarker_a": 0.05, "biomarker_b": 0.05},
)

biomarker_mocker.add_profile(biomarker_profile)

# Configure sampling at specific intervals (baseline, 1 week, 1 month, 3 months)
time_strat = TimeStrategy.init("fixed")
time_strat.update_settings(
    t0_date="2023-01-01",
    sampling_steps=[7, 25, 62],  # Days between measurements
    granularity="day",
)

biomarker_mocker.set_time_design(
    EventTimeDesign(t0_strategy=time_strat, sampling_strategy=time_strat)
)

biomarker_pool = biomarker_mocker()

## -- Overview
print(biomarker_pool.statistics)

# %% [markdown]
# Let's access a single single sequence from the biomarker pool.


# %%
## access to single sequence
biomarker_sequence = biomarker_pool["seq-0-profile-0"]
print(biomarker_sequence.statistics)

# %% [markdown]
# Let's access the first entity value of the sequence, which corresponds to the first biomarker measurement.


# %%
# -- access to the first entity value (0 based)
biomarker_sequence[0].value
