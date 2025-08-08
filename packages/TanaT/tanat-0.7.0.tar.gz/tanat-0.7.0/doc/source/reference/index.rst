Reference
=========

This section contains the complete technical documentation for TanaT, including the full API reference and glossary of terms.

.. toctree::
   :maxdepth: 2

   api/index
   glossary

API Documentation
-----------------

The :doc:`api/index` contains the complete API reference for all TanaT classes, functions, and modules. 
This is automatically generated from the source code docstrings and provides detailed information about:

* Class hierarchies and inheritance
* Method signatures and parameters
* Return types and exceptions
* Usage examples and notes

Glossary
--------

The :doc:`glossary` defines key terms and concepts used throughout TanaT. 
This is particularly helpful for understanding the specialized terminology related to temporal sequence analysis.

Quick Reference
---------------

**Core Data Structures**

* **Entity**: Basic temporal data unit with features and temporal extent
* **Sequence**: Collection of entities of the same type for one individual
* **Trajectory**: Multiple sequences for one individual, possibly with static features
* **Pool**: Collection of sequences or trajectories across multiple individuals

**Sequence Types**

* **Event Sequence**: Point-in-time events
* **Interval Sequence**: Events with duration, can overlap
* **State Sequence**: Continuous states, non-overlapping intervals

**Key Modules**

* ``tanat.sequence``: Sequence data structures and pools
* ``tanat.trajectory``: Trajectory data structures and pools
* ``tanat.metric``: Distance metrics for sequences and trajectories
* ``tanat.clustering``: Clustering algorithms for temporal data
* ``tanat.visualization``: Visualization tools for temporal sequences
