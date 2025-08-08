Glossary
========

The glossary below defines common terms and API elements used throughout *TanaT*.

Core Concepts
-------------

**Entity**
    A description of something that happens for an individual during a certain timestamp. 
    An entity represents a single temporal event or state with associated features and temporal information.

**Individual**
    A unique subject or unit of observation in the dataset. Each individual can have multiple sequences 
    and trajectories associated with them over time.

**Sequence** or **Timed Sequence**
    A longitudinal representation of a collection of events that occurs to an individual along its lifespan.
    Sequences are ordered collections of entities of the same type for one individual.

**Trajectory**
    A collection of multiple sequences for one individual, possibly with additional static features.
    Trajectories provide a comprehensive view of an individual's temporal evolution across different dimensions.

**Pool**
    A collection of sequences or trajectories across multiple individuals. Pools enable batch processing
    and analysis of temporal data from multiple subjects.

**Static Feature**
    Time-invariant characteristics of an individual that remain constant throughout the observation period.
    Examples include demographic information, genetic markers, or baseline measurements.

Sequence Types
--------------

**Event Sequence**
    A sequence of point-in-time events where each entity represents something that happened at a specific moment.
    Events have no duration and are characterized by their timestamp and associated features.

**State Sequence**
    A sequence representing continuous states over time, where each entity has a duration and states 
    do not overlap. State sequences provide complete temporal coverage with non-overlapping intervals.

**Interval Sequence**
    A sequence of events with duration that can potentially overlap in time. Each entity represents
    an interval with start and end times, allowing for concurrent events.

Temporal Concepts
-----------------

**Interval**
    A period of time defined by start and end timestamps. Intervals can represent durations of states,
    events, or any temporal phenomena with extent.

**Timestamp**
    A specific point in time when an event occurs or a measurement is taken. Timestamps provide
    the temporal ordering for sequences.

**Temporal Extent**
    The time period covered by a sequence or trajectory, from the earliest to the latest timestamp.

**Granularity**
    The level of temporal precision used in the analysis, such as days, hours, or minutes.

Analysis Methods
----------------

**Clustering**
    A learning task focused on discovering groups consisting of instances with similar timed sequences 
    or trajectories. TanaT provides specialized clustering algorithms for temporal data.

**Distance Metric**
    A function that quantifies the similarity or dissimilarity between two sequences or trajectories.
    TanaT implements various metrics adapted for temporal sequence analysis.

**Criterion**
    Filtering or selection rules applied to sequences, trajectories, or entities based on temporal,
    pattern-based, or feature-based conditions.

**Aggregation**
    The process of combining multiple sequences or metrics into summary statistics or reduced representations.

Data Structures
---------------

**Pool Structure**
    The organizational framework for managing collections of sequences or trajectories, providing
    efficient access and manipulation of temporal data across multiple individuals.

**Metadata**
    Additional information about sequences and entity feature(s) that describes their properties,
    type, etc.

Workflow Components
-------------------

**Loader**
    Components responsible for reading and importing temporal data from various sources and formats
    into TanaT's internal data structures.

**Simulation**
    Tools for generating synthetic temporal sequences and trajectories for testing, validation,
    or augmentation purposes.

**Visualization**
    Methods and tools for creating graphical representations of temporal sequences, trajectories,
    and analysis results.

**Zeroing**
    The process of aligning temporal sequences to a common reference point (T0 or index date) or normalizing
    temporal coordinates for comparative analysis.

Advanced Concepts
-----------------

**Survival Analysis**
    Statistical methods for analyzing time-to-event data, including censoring and hazard modeling,
    integrated with TanaT's temporal sequence framework.

**Pattern Mining**
    The discovery of recurring temporal patterns, motifs, or subsequences within individual sequences
    or across multiple sequences in a pool.

**Temporal Alignment**
    The process of synchronizing sequences or trajectories to enable meaningful comparison and analysis
    across different individuals or time periods.

**Feature Engineering**
    The creation of derived features from temporal sequences, such as statistical summaries,
    pattern indicators, or temporal transformations.
