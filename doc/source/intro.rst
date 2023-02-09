.. _intro:

============
Introduction
============

.. currentmodule:: civiq6

CIViQ6 is a Python package for camera integration of `VimbaPython <https://github.com/alliedvision/VimbaPython>`_ and Qt6.

CIViQ6 vs QtMultimedia
======================

CIViQ6 provides classes that are analogous to QtMultimedia classes.

.. list-table:: CIViQ6 vs QtMultimedia
   :header-rows: 1

   * - CIViQ6
     - QtMultimedia
   * - :class:`.VimbaRunner`
     - \-
   * - :class:`.VimbaDevices`
     - QMediaDevices
   * - :class:`.VimbaCameraDevice`
     - QCameraDevice
   * - :class:`.VimbaCamera`
     - QCamera
   * - :class:`.VimbaCaptureSession`
     - QMediaCaptureSession

These classes can be used similarly to their Qt counterparts and are compatible to other classes such as QVideoSink or QVideoWidget.

There are a few differences, however...

Running Vimba
-------------

:class:`.VimbaRunner` is a class unique to CIViQ6 without any Qt counterpart.
Before starting any camera, VimbaRunner must be run in separate thread to initiate the Vimba instance.

See :ref:`examples-streaming` page for example.

Capturing and recording
-----------------------

:class:`.VimbaCaptureSession` is **NOT** compatible to QtMultimedia's QImageCapture and QMediaRecorder classes.
You must instead define your own classes to capture the image and to record the video.

:ref:`examples-capturing` page provides example for defining your own capturer and recorder.

Camera properties
-----------------

:class:`.VimbaCamera` does not support various properties which are defined in QCamera, and is not compatible to QCameraFormat.
Instead, it uses the VimbaPython's camera feature design and provides access to it.

See the API reference and :ref:`examples-feature` page to see how the camera features can be controlled.

Supported Qt bindings
=====================

CIViQ6 is compatible with the following Qt binding packages:

- `PySide6 <https://pypi.org/project/PySide6/>`_
- `PyQt6 <https://pypi.org/project/PyQt6/>`_

When CIViQ6 is imported, available package is searched and selected in the order mentioned above.
To force a particular API, set environment variable ``CIVIQ_QT_API`` with package name. Letter case does not matter.
