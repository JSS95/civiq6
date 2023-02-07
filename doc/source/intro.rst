.. _intro:

============
Introduction
============

.. currentmodule:: civiq6

CIViQ6 is a Python package for camera integration of `VimbaPython <https://github.com/alliedvision/VimbaPython>`_ and Qt6.

Supported Qt bindings
=====================

CIViQ6 is compatible with the following Qt binding packages:

- `PySide6 <https://pypi.org/project/PySide6/>`_
- `PyQt6 <https://pypi.org/project/PyQt6/>`_

When CIViQ6 is imported, available package is searched and selected in the order mentioned above.
To force a particular API, set environment variable ``CIVIQ_QT_API`` with package name. Letter case does not matter.
