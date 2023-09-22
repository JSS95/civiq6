.. _installation:

============
Installation
============

This document explains how to install CIViQ6 package.

If you just want quick installation, first :ref:`install VimbaPython <install-vimba>`
Then, run the following command and forget about the rest of this document.

.. code-block:: bash

   $ pip install civiq

This will install ``civiq6`` package in your environment.

Developers are encouraged to :ref:`download the source <download-source>` and :ref:`install from the source <install-from-source>`.

Installing VimbaPython
======================

.. _install-vimba:

CIViQ is dependent to `VimbaPython <https://github.com/alliedvision/VimbaPython>`_ , which is not distributed by PyPI.
Go to its repository and follow the instructions to install the package.

Downloading the source (Optional)
=================================

.. _download-source:

You can download full source code of CIViQ6 project from its repository.

.. code-block:: bash

   $ git clone git@github.com:JSS95/civiq6.git

Installing
==========

The package can be installed by

.. code-block:: bash

   $ pip install [-e] <PyPI name/url/path>[dependency options]

.. rubric:: Install options

.. _install-options:

There are two noticeable install options for developers.

* Install with editable option (``-e``)
* Install with optional dependencies (``[...]``)

The editable option allows changes made to the source code to be immediately reflected in the installed package.
For more information, refer to `pip documentation <https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs>`_.

Optional dependencies can be specified by adding them into brackets right after the package url/path.
When specified, additional module are installed to help accessing extra features of the package.

Available specifications for CIViQ6 are:

* ``doc``: installs modules to build documentations and run examples.
* ``dev``: installs every additional dependency for developers.

With commas without trailing whitespaces, i.e. ``[A,B]``, you can pass multiple specifications.

Installing from repository
--------------------------

By passing the vcs url, ``pip`` command automatically clones the source code and installs the package.

.. code-block:: bash

   $ pip install git+ssh://git@github.com/JSS95/civiq6.git

If you want to pass install options, you need to specify the package name by ``#egg=``.
For example, the following code installs the package with every additional dependency.

.. code-block:: bash

   $ pip install git+ssh://git@github.com/JSS95/civiq6.git#egg=civiq6[full]

.. note::

   If you pass ``-e`` option, full source code of the project will be downloaded under ``src/`` directory in your current location.

Installing from source
----------------------

.. _install-from-source:

If you have already downloaded the source, you can install it by passing its path to ``pip install``.
For example, in the path where ``pyproject.toml`` is located, the following command installs the package in editable mode, with full dependencies for developers.

.. code-block:: bash

   $ pip install -e .[full]

Installing Qt binding
=====================

CIViQ6 needs Qt binding package installed in the environment, but it does not specify it as requirement.
Install any one of the supported Qt binding listed in :ref:`intro` before using CIViQ6.

