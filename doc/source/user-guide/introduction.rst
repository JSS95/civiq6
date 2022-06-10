============
Introduction
============

.. currentmodule:: civiq6

CIViQ6 (pronounced as "civic") is a Python package for camera integration of `VimbaPython <https://github.com/alliedvision/VimbaPython>`_ and Qt6.

CIViQ6 is designed to be used with either `PySide6 <https://pypi.org/project/PySide6/>`_ or `PyQt6 <https://pypi.org/project/PyQt6/>`_.
However, PyQt6 is not available until the dependent package, `qimage2ndarray <https://pypi.org/project/qimage2ndarray/>`_, supports it.

How to use
==========

CIViQ6 must be imported **after** the Qt package is imported.

.. code:: python

   import PySide6
   import civiq6 as cvq

Before accessing the camera API, :class:`VimbaRunner` must be run to start the Vimba instance.
After then, user can acquire and save the frames from the camera in a similar way to Qt6.

For more information, see :ref:`Reference <reference>` and :ref:`Examples <examples>` pages.
