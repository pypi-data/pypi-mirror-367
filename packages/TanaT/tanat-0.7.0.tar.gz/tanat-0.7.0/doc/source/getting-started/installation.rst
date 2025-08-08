Installation
---------------

Using PyPI 
~~~~~~~~~~~

Using ``pip`` should also work fine:

.. code-block:: bash

    python -m pip install tanat


Using latest github-hosted version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to get *TanaT*'s latest version, you can refer to the official repository hosted at the Inria gitlab:

.. code-block:: bash

    python -m pip -e install https://gitlab.inria.fr/tanat/core/tanat


Dependencies
~~~~~~~~~~~~~

*TanaT* relies on several foundational libraries from the scientific Python ecosystem, including:

- ``pandas`` for tabular data handling
- ``numpy`` and ``scipy`` for numerical and scientific computing
- ``matplotlib`` for basic visualization
- ``scikit-learn`` for machine learning utilities

In addition, *TanaT* makes use of:

- ``scikit-survival`` for survival analysis
- ``sqlalchemy`` for SQL-based data access
- ``tqdm`` for progress tracking in processing pipelines
- ``PyYAML`` for configuration handling
- ``pypassist``, ``tseqmock``, and ``tanat_cli_preset`` as internal or companion tools for simulation, CLI, and mocking
