Quick Start Guide
=================

This guide will get you up and running with TanaT in just a few minutes. We'll walk through a simple example of analyzing temporal sequences.

Prerequisites
-------------

Make sure you have TanaT installed. If not, see the :doc:`installation` guide.

.. code-block:: bash

   pip install tanat

Basic Example: Analyzing Medical Visits
----------------------------------------

Let's start with a simple example analyzing a sequence of medical visits.

**Step 1: Import TanaT**

.. code-block:: python

   import pandas as pd
   from tanat.sequence import EventSequencePool, EventSequenceSettings

**Step 2: Prepare Your Data**

TanaT works with pandas DataFrames. Here's some sample data:

.. code-block:: python

   # Sample data: patient visits
   data = pd.DataFrame({
       'patient_id': ['P001', 'P001', 'P001', 'P002', 'P002'],
       'visit_date': ['2023-01-15', '2023-02-20', '2023-03-10', 
                      '2023-01-20', '2023-03-15'],
       'visit_type': ['GP', 'SPECIALIST', 'GP', 'GP', 'EMERGENCY']
   })
   
   # Convert dates
   data['visit_date'] = pd.to_datetime(data['visit_date'])

**Step 3: Create a Sequence Pool**

.. code-block:: python

   # Define settings for event sequences
   settings = EventSequenceSettings(
       id_column="patient_id",
       time_column="visit_date", 
       entity_features=["visit_type"]
   )
   
   # Create the sequence pool
   sequence_pool = EventSequencePool(data, settings)
   
   print(f"Created pool with {len(sequence_pool)} sequences")

**Step 4: Explore Your Sequences**

.. code-block:: python

   # Get basic statistics
   print(sequence_pool.statistics)
   
   # Access individual sequences
   patient_sequence = sequence_pool['P001']
   print(f"Patient P001 has {len(patient_sequence)} visits")

**Step 5: Visualize Sequences**

.. code-block:: python

   from tanat.visualization.sequence import SequenceVisualizer
   
   # Create visualization
   SequenceVisualizer.timeline(
         stacking_mode="flat",
         x_axis_label="Visit Date"
      ) \
      .title("Patient P001 Visit Timeline") \
      .draw(patient_sequence)

**Step 6: Analyze with Metrics**

.. code-block:: python

   from tanat.metric.sequence import DTWSequenceMetric
   from tanat.clustering import HierarchicalClusterer, HierarchicalClustererSettings
   
   # Define a metric for comparing sequences
   metric = DTWSequenceMetric()
   
   # Set up clustering
   cluster_settings = HierarchicalClustererSettings(
       metric=metric,
       n_clusters=2
   )
   
   clusterer = HierarchicalClusterer(cluster_settings)
   clusterer.fit(sequence_pool)
   
   print("Clustering completed!")
   print(clusterer.summarize())

What You've Learned
-------------------

In this quick start, you've learned how to:

1. **Load data** into TanaT using pandas DataFrames
2. **Create sequence pools** to organize your temporal data
3. **Explore sequences** with basic statistics and access methods
4. **Visualize sequences** using built-in visualization tools
5. **Apply analytics** like clustering with custom metrics

Next Steps
----------

Now that you have the basics down, here are some suggested next steps:

**Learn Core Concepts**
   Read :doc:`concepts` to understand TanaT's data model in depth

**Explore Examples**
   Browse the :doc:`../user-guide/examples/index` for more complex use cases

**Follow Tutorials**
   Work through detailed :doc:`../user-guide/tutorials/index` for specific domains

**Check the API**
   Consult the :doc:`../reference/api/index` for complete documentation

Common Patterns
---------------

**Working with Different Sequence Types**

.. code-block:: python

   # Event sequences (point-in-time events)
   from tanat.sequence import EventSequencePool, EventSequenceSettings
   
   # Interval sequences (events with duration)
   from tanat.sequence import IntervalSequencePool, IntervalSequenceSettings
   
   # State sequences (continuous states)
   from tanat.sequence import StateSequencePool, StateSequenceSettings

**Combining Multiple Sequence Types**

.. code-block:: python

   from tanat.trajectory import TrajectoryPool, TrajectoryPoolSettings
   
   # Combine different sequence types for the same individuals
   trajectory_pool = TrajectoryPool(
       sequence_pools={"visits": event_pool, "treatments": interval_pool},
       static_data=patient_demographics,
       settings=trajectory_settings
   )

**Custom Metrics and Analysis**

.. code-block:: python

   # Use different metrics for different analysis needs
   from tanat.metric.sequence import LinearPairwiseSequenceMetric
   from tanat.metric.entity import HammingEntityMetric
   
   # Combine entity and sequence metrics
   entity_metric = HammingEntityMetric()
   sequence_metric = LinearPairwiseSequenceMetric(entity_metric=entity_metric)

Troubleshooting
---------------

**Common Issues:**

- **Data format errors**: Ensure your DataFrame has the correct column names and data types
- **Date parsing**: Use ``pd.to_datetime()`` to convert date strings

**Getting Help:**

- Check the :doc:`../reference/glossary` for terminology
- Browse :doc:`../user-guide/examples/index` for similar use cases
- Consult the :doc:`../reference/api/index` for detailed parameter descriptions
- Report issues on our `GitLab repository <https://gitlab.inria.fr/tanat/core/tanat/-/issues>`_
