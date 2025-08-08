Contributing
------------

First of all, thank you for considering contributing to *TanaT*.
It is still an experimental toolkit, but it received a warn welcome from various communities that 
are interested in its functionalities.


Contributions are managed through GitLab Issues and Pull Requests.

We are welcoming contributions in the following forms:

- **Bug reports**: when filing an issue to report a bug, please use the search tool to ensure the bug hasn't been reported yet;
- **New feature suggestions**: if you think *TanaT* should include a new algorithm, please open an issue to ask for it (of course, you should always check that the feature has not been asked for yet :). Think about linking to a pdf version of the paper that first proposed the method when suggesting a new algorithm.
- **Bug fixes and new feature implementations**: if you feel you can fix a reported bug/implement a suggested feature yourself, do not hesitate to:

  1. fork the project;
  2. implement your bug fix;
  3. submit a pull request referencing the ID of the issue in which the bug was reported / the feature was suggested;

If you would like to contribute by implementing a new feature reported in the Issues, maybe starting with `Issues that are attached the "good first issue" label <https://github.com/tslearn-team/tslearn/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22>`_ would be a good idea.

When submitting code, please think about code quality, adding proper docstrings including doctests with high code coverage.

More details on Pull requests
=============================

The preferred workflow for contributing to *TanaT* is to fork the
`main repository <https://gitlab.inria.fr/tanat/core/tanat>`_ on
GitLab, clone, and develop on a branch. Steps:

1. Fork the `project repository <https://gitlab.inria.fr/tanat/core/tanat>`_
   by clicking on the 'Fork' button near the top right of the page. This creates
   a copy of the code under your GitHub user account. For more details on
   how to fork a repository see `this guide <https://help.github.com/articles/fork-a-repo/>`_.

2. Clone your fork of the *TanaT* repo to your local disk::

      $ git clone git@github.com:YourLogin/tanat.git
      $ cd tanat

3. Create a ``my-feature`` branch to hold your development changes.
   Always use a ``my-feature`` branch. It's good practice to never work on the ``master`` branch::

     $ git checkout -b my-feature

4. Develop the feature on your feature branch. To record your changes in git,
   add changed files using ``git add`` and then ``git commit`` files::

     $ git add modified_files
     $ git commit

5. Push the changes with::

    $ git push -u origin my-feature

6. Follow `these instructions <https://help.github.com/articles/creating-a-pull-request-from-a-fork>`_
   to create a pull request from your fork. This will send an email to the committers.

(If any of the above seems like magic to you, please look up the
`Git documentation <https://git-scm.com/documentation>`_ on the web, or ask a friend or another contributor for help.)

