# %% [markdown]
# # Data Wrangling for Sequences
#
# This notebook demonstrates essential data wrangling techniques for sequence data in *TanaT*. We'll explore filtering, querying, pattern matching, and temporal alignment operations that are crucial for preparing sequence data for analysis.
#
# These techniques are essential for:
# - Preparing data for machine learning models
# - Extracting patient cohorts for clinical studies
# - Cleaning and validating temporal datasets
# - Creating analysis-ready sequence collections

# %% [markdown]
# ### Required imports

# %%
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Simulation imports
from tanat.dataset.simulation.sequence import (
    generate_event_sequences,
    generate_interval_sequences,
    generate_state_sequences,
)

# Sequence pools
from tanat.sequence import (
    EventSequencePool,
    StateSequencePool,
    IntervalSequencePool,
)

# Criterion for filtering
from tanat.criterion import (
    QueryCriterion,
    PatternCriterion,
    TimeCriterion,
    LengthCriterion,
    StaticCriterion,
)

# Visualization
from tanat.visualization.sequence import SequenceVisualizer

# %% [markdown]
# ## 1. Data Setup
#
# We'll create a comprehensive healthcare dataset with three types of sequences: event sequences (discrete healthcare visits), state sequences (health conditions over time), and interval sequences (medication periods). This multi-modal approach reflects real-world healthcare data complexity.

# %% [markdown]
# ### Dataset Configuration
#
# Define the parameters for our simulated healthcare dataset.

# %%
# Dataset parameters
N_SEQ = 150  # Number of patient sequences
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]  # Variable sequence lengths
SEED = 42  # For reproducible results

# %% [markdown]
# ### Event Sequences: Healthcare Visits
#
# Generate sequences representing different types of healthcare visits with temporal ordering.

# %%
# Healthcare visit types reflecting real clinical workflows
event_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "GENERAL_PRACTITIONER",
        "SPECIALIST",
        "NURSE",
        "RADIOLOGIST",
        "LABORATORY",
        "EMERGENCY",
        "PHARMACY",
    ],
    missing_data=0.15,  # 15% missing data to simulate real-world conditions
    entity_feature="visit_type",
    seed=SEED,
)

print(f"Generated {len(event_data)} event records across {N_SEQ} patients")

# %% [markdown]
# ### State Sequences: Health Conditions
#
# Generate sequences representing patient health states that persist over time periods.

# %%
# Health states following typical disease progression patterns
state_data = generate_state_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "HEALTHY",
        "SICK",
        "TREATMENT",
        "CONVALESCENCE",
        "CHRONIC_MONITORING",
        "REMISSION",
    ],
    missing_data=0.1,  # Lower missing rate for health states
    entity_feature="health_state",
    seed=SEED,
)

# Report generated state sequences
state_data.describe(include="all")

# %% [markdown]
# ### Interval Sequences: Medication Periods
#
# Generate sequences representing medication prescriptions with start and end dates.

# %%
# Common medication categories with defined treatment periods
interval_data = generate_interval_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "ANTIBIOTIC",
        "PAIN_RELIEVER",
        "CORTICOSTEROID",
        "ANTICOAGULANT",
        "ANTIHYPERTENSIVE",
        "INSULIN",
    ],
    missing_data=0.2,  # Higher missing rate for medication data
    entity_feature="medication",
    seed=SEED,
)

# Report generated interval sequences
interval_data.describe(include="all")

# %% [markdown]
# ### Summary of Generated Data
#
# Overview of the three sequence types we'll use for data wrangling demonstrations.

# %%
print("Dataset summary:")
print(f"- Event sequences: {len(event_data)} records")
print(f"- State sequences: {len(state_data)} records")
print(f"- Interval sequences: {len(interval_data)} records")
print(f"- Total patients: {N_SEQ}")

# %% [markdown]
# ### Patient Demographics and Clinical Data
#
# Generate static patient characteristics that will enable demographic and clinical filtering demonstrations.


# %%
def generate_patient_data(num_patients, seed=42):
    """
    Generate realistic patient demographic and clinical data.
    """
    np.random.seed(seed)

    patients = []
    for i in range(num_patients):
        patient_id = f"seq-{i}"
        patients.append(
            {
                "id": patient_id,
                "gender": np.random.choice(["M", "F"], p=[0.48, 0.52]),
                "age": np.random.randint(18, 85),
                "insurance": np.random.choice(
                    ["PUBLIC", "PRIVATE", "MIXED"], p=[0.6, 0.25, 0.15]
                ),
                "chronic_condition": np.random.choice([True, False], p=[0.4, 0.6]),
                "risk_level": np.random.choice(
                    ["LOW", "MEDIUM", "HIGH"], p=[0.5, 0.3, 0.2]
                ),
                "comorbidity_count": np.random.poisson(1.2),
            }
        )

    return pd.DataFrame(patients)


# %% [markdown]
# ### Generate and Examine Patient Data
#
# Create the static patient dataset and explore its characteristics.

# %%
# Generate patient demographics
static_data = generate_patient_data(N_SEQ, seed=SEED)

print("Patient demographics generated:")
static_data.head()

# %%
# Examine demographic distributions
static_data.describe(include="all")

# %% [markdown]
# ### Sequence Pool Configuration
#
# Sequence pools are the core data structures in TanaT that combine temporal sequence data with static patient characteristics. Each pool type handles different temporal patterns:
# - **Event pools**: Discrete time points (healthcare visits)
# - **State pools**: Persistent conditions over time periods
# - **Interval pools**: Activities with defined start and end times

# %% [markdown]
# ### Event Sequence Pool Setup
#
# Configure the event pool to handle healthcare visit sequences with patient demographics.

# %%
# Define shared static features for all sequence types
static_features = [
    "gender",
    "age",
    "insurance",
    "chronic_condition",
    "risk_level",
    "comorbidity_count",
]

# Event sequence configuration
event_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["visit_type"],
    "static_features": static_features,
}

event_pool = EventSequencePool(
    event_data,
    event_settings,
    static_data=static_data,
)

print(f"Event pool created: {len(event_pool)} sequences")

# %% [markdown]
# ### State Sequence Pool Setup
#
# Configure the state pool to handle health condition sequences with temporal persistence.

# %%
# State sequence configuration
state_settings = {
    "id_column": "id",
    "start_column": "start_date",
    "default_end_value": datetime.now(),  # Avoid warnings for open-ended states
    "entity_features": ["health_state"],
    "static_features": static_features,
}

state_pool = StateSequencePool(
    state_data,
    state_settings,
    static_data=static_data,
)

print(f"State pool created: {len(state_pool)} sequences")

# %% [markdown]
# ### Interval Sequence Pool Setup
#
# Configure the interval pool to handle medication periods with defined durations.

# %%
# Interval sequence configuration
interval_settings = {
    "id_column": "id",
    "start_column": "start_date",
    "end_column": "end_date",
    "entity_features": ["medication"],
    "static_features": static_features,
}

interval_pool = IntervalSequencePool(
    interval_data, interval_settings, static_data=static_data
)

print(f"Interval pool created: {len(interval_pool)} sequences")

# %% [markdown]
# ### Sequence Pool Summary
#
# All sequence pools are now ready for data wrangling operations.

# %%
print("All sequence pools initialized:")
print(f"- Event sequences: {len(event_pool)} patients")
print(f"- State sequences: {len(state_pool)} patients")
print(f"- Interval sequences: {len(interval_pool)} patients")
print(f"\nEach pool integrates {len(static_features)} static patient features")

# %% [markdown]
# ### Initial Data Distribution Visualization
#
# Examine the distribution of event types, health states, and medications in our dataset before applying any filtering operations.

# %%
# Visualize event type distribution
color_map_event = {
    "GENERAL_PRACTITIONER": "#c8a2d8",
    "SPECIALIST": "#f8b3ba",
    "EMERGENCY": "#f9d79c",
    "LABORATORY": "#85c1b3",
    "RADIOLOGIST": "#a9c9f0",
    "NURSE": "#d4a574",
    "PHARMACY": "#92d1a3",
}
# fmt: off
SequenceVisualizer.histogram(
    show_as="occurrence",
    bar_order="descending"
) \
    .title("Healthcare Visit Distribution - All Patients") \
    .colors(color_map_event) \
    .legend(show=True, title="Visit Types", loc="upper right") \
    .x_axis(label="Visit Types") \
    .y_axis(label="Frequency") \
    .draw(event_pool)
# fmt: on

# %%
# Visualize health state distribution
color_map_state = {
    "HEALTHY": "#28a745",
    "SICK": "#dc3545",
    "TREATMENT": "#007bff",
    "REMISSION": "#6f42c1",
    "CHRONIC_MONITORING": "#fd7e14",
    "CONVALESCENCE": "#20c997",
}
# fmt: off
SequenceVisualizer.histogram(
    show_as="occurrence",
    bar_order="descending"
) \
    .title("Health State Distribution - All Patients") \
    .colors("Set1") \
    .legend(show=True, title="Health States", loc="upper right") \
    .x_axis(label="Health States") \
    .y_axis(label="Frequency") \
    .draw(state_pool)
# fmt: on

# %% [markdown]
# ## 2. Basic Filtering with Query Criterion
#
# Query criterion provide pandas-style filtering capabilities for sequence data. They enable precise selection of entities or sequences based on attribute values, supporting both simple conditions and complex logical expressions.

# %% [markdown]
# ### Understanding Filtering Levels
#
# TanaT supports three filtering levels:
# - **Entity-level**: Filters individual records within sequences
# - **Sequence-level**: Filters entire sequences based on whether they contain matching entities
# - **Trajectory-level**: Not shown here. See [Trajectory data wrangling](./data_wrangling_trajectory.ipynb).

# %% [markdown]
# ### Entity-Level Filtering
#
# Extract specific types of entities across all sequences. This preserves the sequence structure but only includes matching entities.

# %%
# Create criterion for emergency visits
emergency_criterion = QueryCriterion(query="visit_type == 'EMERGENCY'")

# Apply entity-level filtering
emergency_entities = event_pool.filter(emergency_criterion, level="entity")

# %%
# Visualize the impact of filtering on event pool
# fmt: off
SequenceVisualizer.histogram(
    show_as="occurrence",
    bar_order="descending"
) \
    .title("Emergency Visit Entities Only") \
    .colors(color_map_event) \
    .legend(show=True, title="Visit Types", loc="upper right") \
    .x_axis(label="Visit Types") \
    .y_axis(label="Frequency") \
    .draw(emergency_entities)
# fmt: on

# %%
# Examine the filtered emergency visit data
emergency_entities

# %% [markdown]
# ### Sequence-Level Filtering
#
# Select entire sequences that contain at least one entity matching the criterion. This maintains complete sequence context.

# %%
# Filter for sequences containing emergency visits
sequences_with_emergency = event_pool.filter(
    emergency_criterion,
    level="sequence",
)

# Examine the results
sequences_with_emergency

# %%
# Visualize the impact of emergency visit filtering
# fmt: off
SequenceVisualizer.histogram(
    show_as="occurrence",
    bar_order="descending"
) \
    .title("Visit Distribution in Emergency-Containing Sequences") \
    .colors(color_map_event) \
    .legend(show=True, title="Visit Types", loc="upper right") \
    .x_axis(label="Visit Types") \
    .y_axis(label="Frequency") \
    .draw(sequences_with_emergency)
# fmt: on


# %% [markdown]
# ### Multi-Condition Query Filtering
#
# Use complex pandas query expressions to filter on multiple conditions simultaneously.

# %%
# Filter for specialist or radiologist visits using 'in' operator
specialist_criterion = QueryCriterion(
    query="visit_type in ['SPECIALIST', 'RADIOLOGIST']"
)
specialist_sequences = event_pool.filter(specialist_criterion, level="sequence")

# Examine the results
specialist_sequences


# %% [markdown]
# ## 3. Pattern-Based Filtering
#
# Pattern criterion enable sophisticated sequence pattern matching beyond simple value filtering. They support single value matching, sequential patterns, and regular expressions for complex data extraction scenarios.

# %% [markdown]
# ### Single Value Pattern Matching
#
# Identify sequences containing specific entity values. This is useful for finding all sequences with particular events or states.

# %%
# Find sequences containing treatment state
treatment_pattern = PatternCriterion(
    pattern={"health_state": "TREATMENT"},
    contains=True,  # Check if pattern exists anywhere in sequence
)
treatment_sequences = state_pool.filter(treatment_pattern, level="sequence")

# Examine treatment sequences
treatment_sequences

# %%
# Examine health state distribution in treatment sequences
# fmt: off
SequenceVisualizer.histogram(
    show_as="frequency",
    bar_order="descending"
) \
    .title("Health State Distribution in Treatment Sequences") \
    .colors(color_map_state) \
    .legend(show=True, title="Health States", loc="upper right") \
    .x_axis(label="Health States") \
    .y_axis(label="Frequency") \
    .draw(treatment_sequences)
# fmt: on

# %% [markdown]
# ### Sequential Pattern Matching
#
# Find sequences containing specific ordered patterns. This identifies disease progression patterns or care pathways.

# %%
# Find sequences with SICK followed by TREATMENT progression
sick_to_treatment = PatternCriterion(
    pattern={"health_state": ["SICK", "TREATMENT"]},
    # Pattern can occur anywhere in sequence
    contains=True,
)
recovery_sequences = state_pool.filter(sick_to_treatment, level="sequence")

# Examine recovery sequence characteristics
recovery_sequences

# %%
# Examine a specific recovery sequence example
example_id = list(recovery_sequences.unique_ids)[0]
example_sequence = recovery_sequences[example_id]
example_sequence

# %%
# Visualize recovery patterns with timeline
# fmt: off
SequenceVisualizer.timeline(
    stacking_mode="flat",
    relative_time=True,
    granularity="day"
) \
    .title("Recovery Progression Patterns (SICK → TREATMENT)") \
    .colors(color_map_state) \
    .marker(spacing=0.8, alpha=0.8) \
    .legend(show=True, title="Health States", loc="upper right") \
    .x_axis(label="Days from Start") \
    .draw(recovery_sequences)
# fmt: on

# %% [markdown]
# ### Regular Expression Pattern Matching
#
# Use regex patterns for flexible string matching in entity attributes. This enables complex pattern matching on text data.

# %%
# Find sequences with specialist visits (starting with 'S') followed by laboratory
regex_pattern = PatternCriterion(
    pattern={"visit_type": ["regex:^S", "LABORATORY"]},
    # Sequential pattern with regex
    contains=True,
)
specialist_lab_sequences = event_pool.filter(regex_pattern, level="sequence")

# Examine the results
specialist_lab_sequences

# %% [markdown]
# ## 4. Static Data Operations
#
# Static criterion enable filtering based on patient demographics and clinical characteristics that remain constant throughout the observation period. This is essential for cohort selection and demographic analysis.

# %% [markdown]
# ### Multi-Condition Static Filtering
#
# Filter patients based on multiple demographic and clinical criteria simultaneously.

# %%
# Define criterion for elderly patients with chronic conditions
elderly_chronic_criterion = StaticCriterion(
    query="age > 65 and chronic_condition == True"
)

print("Filtering for elderly patients (>65) with chronic conditions...")

# %%
# Apply filtering across all sequence types
elderly_chronic_events = event_pool.filter(elderly_chronic_criterion)
elderly_chronic_states = state_pool.filter(elderly_chronic_criterion)
elderly_chronic_intervals = interval_pool.filter(elderly_chronic_criterion)

print("Static filtering results:")
print(f"Event sequences: {len(elderly_chronic_events)} patients")
print(f"State sequences: {len(elderly_chronic_states)} patients")
print(f"Interval sequences: {len(elderly_chronic_intervals)} patients")

# %%
# Examine patient characteristics in filtered cohort
print("Characteristics of elderly chronic patients:")
cohort_data = elderly_chronic_events.static_data
cohort_data.describe(include="all")

# %% [markdown]
# ### Risk Stratification Filtering
#
# Identify patient cohorts based on clinical risk levels for targeted analysis.

# %%
# Filter for high-risk patients
high_risk_criterion = StaticCriterion(query="risk_level == 'HIGH'")
high_risk_sequences = event_pool.filter(high_risk_criterion)

print("Risk-based filtering results:")
print(f"High-risk patients: {len(high_risk_sequences)}")
print(f"Percentage of total: {len(high_risk_sequences)/len(event_pool)*100:.1f}%")

# %%
# Compare risk levels with other characteristics
risk_analysis = high_risk_sequences.static_data
print("High-risk patient characteristics:")
print(f"Mean age: {risk_analysis['age'].mean():.1f} years")
print(f"Chronic condition rate: {risk_analysis['chronic_condition'].mean()*100:.1f}%")
print(f"Mean comorbidities: {risk_analysis['comorbidity_count'].mean():.1f}")

## -- Overview of high-risk sequences -- ##
high_risk_sequences

# %% [markdown]
# ## 5. Time Window Filtering
#
# Time criterion enable filtering based on temporal characteristics, allowing precise selection of entities or sequences within specific time windows. This is crucial for longitudinal studies and time-bounded analyses.

# %% [markdown]
# ### Entity-Level Time Filtering
#
# Filter individual entities (events, states, intervals) that fall within specified time boundaries.

# %%
# Define recent time window (last 3 months)
recent_start = datetime.now() - timedelta(days=90)
recent_end = datetime.now()

recent_time_criterion = TimeCriterion(
    start_after=recent_start,
    end_before=recent_end,
    # Entity must be entirely within time range
    duration_within=True,
)

print(f"Filtering for entities between: [{recent_start.date()}, {recent_end.date()}]")

# %%
# Apply time filtering to interval sequences (medication periods)
recent_intervals = interval_pool.filter(
    recent_time_criterion,
    level="entity",
)

print("Recent medication intervals:")
print(f"Entities in time window: {len(recent_intervals.sequence_data)}")
print(f"Original entities: {len(interval_pool.sequence_data)}")
print(f"Sequences affected: {len(recent_intervals)}")

# %%
# Examine recent medication data
recent_intervals.sequence_data.head()

# %%
# Visualize medication duration distribution in recent intervals
# fmt: off
SequenceVisualizer.histogram(
    show_as="time_spent",
    bar_order="descending",
    orientation="horizontal"
) \
    .title("Recent Medication Duration Analysis") \
    .colors("Spectral") \
    .legend(show=True, title="Medications", loc="lower right") \
    .x_axis(label="Total Duration") \
    .y_axis(label="Medication Types") \
    .draw(recent_intervals)
# fmt: on

# %% [markdown]
# ### Sequence-Level Time Filtering
#
# Filter entire sequences that fall within specified time boundaries, maintaining complete sequence context.

# %%
# Define historical time window (1 year ago to 3 months ago)
historical_start = datetime.now() - timedelta(days=365)
historical_end = datetime.now() - timedelta(days=90)

historical_time_criterion = TimeCriterion(
    start_after=historical_start,
    end_before=historical_end,
    sequence_within=True,  # Entire sequence must be within time range
)


# %%
# Apply sequence-level time filtering
historical_events = event_pool.filter(historical_time_criterion, level="sequence")

## Report results
historical_events

# %% [markdown]
# ## 6. Length-Based Filtering
#
# Length criterion enable filtering sequences based on the number of entities they contain. This is useful for ensuring sufficient data for analysis or identifying outlier sequences.

# %% [markdown]
# ### Filtering for Extended Sequences
#
# Identify sequences with sufficient data points for robust analysis.

# %%
# Filter for sequences with more than 8 entities
long_sequences_criterion = LengthCriterion(gt=8)
long_event_sequences = event_pool.filter(long_sequences_criterion)

## Report results
print("\nLong event sequences overview:")
long_event_sequences

# %% [markdown]
# ### Filtering for Concise Sequences
#
# Identify sequences with limited data points, which may require different analytical approaches.

# %%
# Filter for sequences with 5 or fewer entities
short_sequences_criterion = LengthCriterion(le=5)
short_event_sequences = event_pool.filter(short_sequences_criterion)

print("Short sequence filtering:")
print(f"Sequences with ≤5 entities: {len(short_event_sequences)}")
print(f"Percentage of total: {len(short_event_sequences)/len(event_pool)*100:.1f}%")

## Report results
short_event_sequences


# %% [markdown]
# ## 7. Handling Missing Data
#
# Missing data is common in healthcare sequences due to incomplete recording, system limitations, or patient non-adherence. TanaT provides tools to identify, analyze, and handle missing values appropriately.

# %% [markdown]
# ### Detecting Missing Data Patterns
#
# First, identify the presence and extent of missing data in the dataset.

# %%
# Check vocabulary to see if missing values (None) are present
print("Dataset vocabulary analysis:")
print(f"Event vocabulary: {event_pool.vocabulary}")
print(f"Missing values present: {None in event_pool.vocabulary}")

# %% [markdown]
# ### Entity-Level Missing Data Analysis
#
# Identify individual entities with missing attribute values.

# %%
# Find entities with missing visit types
missing_visits_criterion = QueryCriterion(query="visit_type.isna()")
missing_visit_entities = event_pool.filter(missing_visits_criterion, level="entity")

# Report missing visit entities
missing_visit_entities

# %% [markdown]
# ### Sequence-Level Missing Data Analysis
#
# Identify sequences that contain any missing values, which may need special handling.

# %%
# Find sequences containing missing values
sequences_with_missing = event_pool.filter(missing_visits_criterion, level="sequence")

# Report sequences with missing values
sequences_with_missing.unique_ids

# %% [markdown]
# ### Data Cleaning: Removing Missing Values
#
# Create clean datasets by filtering out entities with missing values.

# %%
# Create clean dataset by removing entities with missing values
clean_data_criterion = QueryCriterion(query="visit_type.notna()")
clean_event_pool = event_pool.filter(clean_data_criterion, level="entity")

print("Data cleaning results:")
print(f"Original entities: {len(event_pool.sequence_data)}")
print(f"Clean entities: {len(clean_event_pool.sequence_data)}")
print(
    f"Entities removed: {len(event_pool.sequence_data) - len(clean_event_pool.sequence_data)}"
)

# %%
# Verify data cleaning effectiveness
print("Data quality verification:")
print(f"Vocabulary before cleaning: {event_pool.vocabulary}")
print(f"Vocabulary after cleaning: {clean_event_pool.vocabulary}")
print(f"Missing values eliminated: {None not in clean_event_pool.vocabulary}")

# %% [markdown]
# ## 8. Reference Date Management
#
# Reference dates (T0) enable temporal alignment of sequences by establishing a common starting point. This is essential for comparative analysis and cohort studies where events need to be aligned relative to a specific milestone.

# %% [markdown]
# ### Event-Based Reference Dating
#
# Set reference dates based on the occurrence of specific events in each sequence.

# %%
# Set T0 based on first emergency visit occurrence
emergency_t0_pool = event_pool.copy()
emergency_t0_pool.zero_from_query(
    query="visit_type == 'EMERGENCY'",
    # Use first occurrence if multiple emergency visits
    use_first=True,
)

# %%
# Examine reference dates
pd.DataFrame.from_dict(
    emergency_t0_pool.t_zero,
    orient="index",
    columns=["T0 Date"],
)


# %% [markdown]
# ### Temporal Transformation: Relative Time
#
# Convert absolute timestamps to relative time from the reference date for temporal analysis.

# %%
# Transform to relative time (days from emergency visit)
emergency_t0_pool.to_relative_time(
    granularity="day",
    drop_na=True,  # Remove entities without valid T0
)

# %%
# Visualize temporal alignment impact
# fmt: off
SequenceVisualizer.timeline(
    relative_time=True,
    stacking_mode="flat",
    granularity="day"
) \
    .title("Healthcare Visits Aligned to Emergency Visit (T0)") \
    .colors(color_map_event) \
    .marker(size=10, alpha=0.9) \
    .legend(show=True, title="Visit Types", loc="upper right") \
    .x_axis(label="Days from Emergency Visit") \
    .set_theme("dark_background") \
    .draw(emergency_t0_pool)
# fmt: on

# %% [markdown]
# ### Position-Based Reference Dating
#
# Alternative approach: set reference dates based on sequence position rather than event content.

# %%
# Set T0 based on the third event in each sequence
position_t0_pool = event_pool.copy()
# 0-indexed: position 2 = 3rd event
position_t0_pool.zero_from_position(position=2)


# %%
# Examine position-based reference dates
pd.DataFrame.from_dict(
    position_t0_pool.t_zero,
    orient="index",
    columns=["T0 Date"],
)


# %% [markdown]
# ### Temporal Transformation: Relative Rank
#
# Convert to ordinal positions relative to the reference point.

# %%
# Transform to relative rank (ordinal positions from T0)
position_t0_pool.to_relative_rank()

# %% [markdown]
# ## 9. Advanced Sequence Filtering
#
# Advanced filtering combines multiple criterion to create sophisticated patient cohorts. TanaT supports both set-based operations (intersection, union) and sequential filtering approaches for complex data extraction scenarios.

# %% [markdown]
# ### Set-Based Cohort Selection
#
# Use the `which()` method to identify patient IDs meeting specific criterion, then combine using set operations.

# %%
# Step 1: Identify high-risk patients
high_risk_ids = event_pool.which(StaticCriterion(query="risk_level == 'HIGH'"))
print(f"Step 1 - High-risk patients: {len(high_risk_ids)}")

# %%
# Step 2: Identify elderly patients
elderly_ids = event_pool.which(StaticCriterion(query="age > 50"))
print(f"Step 2 - Elderly patients (>50): {len(elderly_ids)}")

# %%
# Step 3: Identify patients with emergency visits
emergency_ids = event_pool.which(QueryCriterion(query="visit_type == 'EMERGENCY'"))
print(f"Step 3 - Patients with emergency visits: {len(emergency_ids)}")

# %%
# Step 4: Find intersection of all three criteria
intersection_ids = high_risk_ids.intersection(elderly_ids).intersection(emergency_ids)

print(f"Step 4 - Final cohort intersection: {len(intersection_ids)}")
print(
    f"Selection rate: {len(intersection_ids)/len(event_pool)*100:.1f}% of total patients"
)

# %%
# Create filtered sequence pool from intersection
intersection_pool = event_pool.subset(intersection_ids)

## Report results
intersection_pool

# %% [markdown]
# ### Sequential Filtering Approach
#
# Alternative method: apply filters sequentially using the `filter()` method for the same result.

# %%
# Sequential filtering approach
# Filter 1: High-risk patients
high_risk_pool = event_pool.filter(StaticCriterion(query="risk_level == 'HIGH'"))
# Report high-risk pool
high_risk_pool


# %%
# Filter 2: Among high-risk, select elderly patients
elderly_high_risk_pool = high_risk_pool.filter(StaticCriterion(query="age > 50"))
print(f"After elderly filter: {len(elderly_high_risk_pool)} patients")

# %%
# Filter 3: Among elderly high-risk, find those with emergency visits
final_cohort_pool = elderly_high_risk_pool.filter(
    QueryCriterion(query="visit_type == 'EMERGENCY'"), level="sequence"
)
print(f"Final cohort: {len(final_cohort_pool)} patients")

# %%
# Verify both approaches yield identical results
print("Verification of filtering approaches:")
print(f"Set-based approach: {len(intersection_pool)} patients")
print(f"Sequential approach: {len(final_cohort_pool)} patients")
print(f"Results identical: {len(intersection_pool) == len(final_cohort_pool)}")

## Report final cohort
final_cohort_pool
