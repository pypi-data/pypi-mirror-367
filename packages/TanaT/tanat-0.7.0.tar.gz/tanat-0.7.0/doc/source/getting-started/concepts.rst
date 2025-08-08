.. _concepts_ref:

Key Concepts

*TanaT* is a highly flexible framework that allows to manipulate different types timed sequences.

In this section, we introduce the different core notions we basically introduced in *TanaT*. 
We invite the user to browse this part of the documentation to understand the general philosophy of the library.


Entities, sequences and trajectories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The *TanaT* library distinguishes three different types of data structure to represent temporal data : entities (events), sequences and trajectories.

The basic data structure of the temporal data structure that are represented are the *entities*.
An entity is a description of something that occurred for one individual and it has a temporal extend.

* The description of the entity nature can be seen as a vector of features (qualitative or qualitative). 
  There is at least one feature to describe an entity. 
  In the most simple case, we represent the nature of the entity by a letter in a vocabulary, i.e., a qualitative feature. 
* The temporal extent of an entity is defined by either a single date or a start and end date (a time period).

The *sequence* is the first temporal data structure. It is a collection of entities. 
A sequence specifies the nature and the type of temporal extend of the entities it contains. 
This means that all the entities of a sequence share the same type of temporal extend (ponctual, intervals or state) and 
also the same descriptive features. 


.. note::
    The figure below illustrates the notion of *sequence* in which there are 4 instant entities. 
    The entity types are represented by a letter: `A`, `B`, `C` or `D`. All entities have only one qualitative feature. 
    There are represented on a time line to represent their temporal extends.

    It is worth noting that the sequence holds two entities with the same feature value (`A`). 
    It is also possible to have two different entities at the same time. 
    The only formal impossibility it to have two entities with equals features at the same date. 

    .. mermaid::

        gantt
            dateFormat  YYYY-MM-DD
            axisFormat %d
            title       Illustration of a sequence

            Event A (1st) : milestone, A1, 2023-11-01, 0d
            Event A (2nd) : milestone, A2, 2023-11-08, 0d
            Event B      : milestone, B1, 2023-11-08, 0d
            Event C      : milestone, C1, 2023-11-23, 0d


The third important data structure to represent temporal data is called a *trajectory*. 
It models a multiple sequence for a unique individual. In this case, all the sequences may 
have different characteristics from each others.
The trajectory can be used to represent complex temporal sequences, in which there are different types of entities.
For instance, for representing a journey, you may be interested in representing the weather along time (state sequence), 
the city you visisted (interval sequences) and, in the same representation, also the visit you made.

.. note::
    In the illustration below, we represent a trajectory, with three different types of sequences. 
    Two of them are event sequences, while the second in an interval sequence.
    The feature sets for each type of sequences are distinct.

    .. mermaid::

        gantt
            dateFormat  YYYY-MM-DD
            axisFormat %d
            title       Illustration of a Trajectory

            section Type 1 sequence
            Event A : milestone, A1, 2023-11-01, 0d
            Event A : milestone, A2, 2023-11-08, 0d
            Event B : milestone, B1, 2023-11-20, 0d

            section Type 2 sequence
            Interval I : I1, 2023-11-15, 2023-11-18

            section Type 3 sequence
            Event U : milestone, U1, 2023-11-09, 0d
            Event V : milestone, V1, 2023-11-13, 0d

For complex modelling of an individual, a Trajectory also enables to describe *static features* (i.e. feature that are not associated to a temporal extend).
In the context of modeling care pathways, static features could be the birthdate, the gender, some conditions, etc.
Like the description of an entity, the static features of an individual are represented by feature/value couples.


Different types of temporal extends
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Let us now detailed the three different types of sequences that are currently modeled in *TanaT*, namely: the *event sequences*, the *interval sequences* and the *state sequences*.
These types are illustrated below.

* **Event Sequence**: the entities are ponctuals (for instance, a medical visit). 
* **Interval sequence**: the entities occur during an certain amount of time (for, instance an hospitalisation during a week).  
  The entities can overlaps and holes in the timeline are allowed. The intervals can be degenerated (same begin and end). 
* **State sequence**: the entities have intervals as temporal extends. In this case, the entites are states.  
  Contrary to the interval sequence, there is a unique state at each time instant. 
  This means that the intervals of a state sequence must be contiguous: when an interval ends, another starts. 
  Another constraint is that two successive intervals must have different state descriptions (different feature values).

.. mermaid::

    gantt
        dateFormat  YYYY-MM-DD
        axisFormat %d
        title       Illustration of the different sequences types

        section Event sequence
        Event A : milestone, A1, 2023-11-01, 0d
        Event A : milestone, A2, 2023-11-08, 0d
        Event B : milestone, B1, 2023-11-20, 0d

        section Interval sequence
        Interval K : K1, 2023-11-04, 2023-11-09
        Interval J : J1, 2023-11-12, 2023-11-17
        Interval I : I1, 2023-11-15, 2023-11-19

        section State sequence
        State U : U1, 2023-11-01, 2023-11-08
        State V : V1, 2023-11-08, 2023-11-12
        State W : W1, 2023-11-12, 2023-11-18
        State X : X1, 2023-11-18, 2023-11-22

Pools
~~~~~~~

In *TanaT*, the collection of objects (trajectoires or sequences) are called *pools*. 
In a pool, each object is the data of one individual and all individuals are described by the exact same features (same types of sequences; with same types of temporal extend and features; and same static feature). 
A pool can be seens as a dataframe considering that it describes a collection of individuals, but it defines the features (columns) that are shared by all individual descriptions. 

A *pool* is the data structure that has to be used when dealing with a collection of sequences or trajectories.

Settings
~~~~~~~~~~

The notion of *setting* is very important in *TanaT* to supplement the description of the semantics of the temporal data or the metrics.
The setting is a companion instance of an object of interest that embed its setting. 
This mechanism is used to prevent from having functions or constructors with complex and variable parameters across the classes. 
It replaces the use of multiple parameters by the definition of unique parameter that is an instance of a setting. 
This makes the library more powerful and extensible.

From the implementation point of view, each *TanaT* class will have its own specific setting class which describes the settings. 
For instance, the class :py:class:`EventSequenceSettings` is the companion class for the specification of :py:class:`EventSequence`. 
The following example illustrates the use of the setting object for event sequence to instantiate a pool of event sequences in this case.

.. code-block:: python

    seq_settings = EventSequenceSettings(
        id_column="id",
        time_column="date",
        entity_features=["event"],
    )

    seqpool = EventSequencePool(data=my_data, settings=seq_settings)


A setting is associated to each sequence/trajectory and contains the description of the objet characteristics. 
A setting objet is held by the pool to be *shared by all the sequences/trajectories* of the pool.

Most objects in TanaT — including metrics, clustering algorithms, and others — have their own dedicated settings classes.

.. |br| raw:: html

      <br>
