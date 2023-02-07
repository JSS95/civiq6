Setting camera features
=======================

This example extends the class defined in :ref:`examples-streaming` example to implement controlling the video FPS.

Before running the example, make sure your scripts are placed in the following directory structure:

| scripts
| ├── :ref:`examples-camerafeature`
| └── :ref:`camera_stream.py <examples-streaming>`

Running **camera_feature.py** opens a camera streaming window where you can modify the acquisition frame rate of the camera device.

.. note::
    This example is tested with Mako U-130B device.
    If your camera device has incompatible features this example may not work.

.. _examples-camerafeature:

camera_feature.py
-----------------

.. tabs::

   .. tab:: PySide6

      :download:`camera_feature.py <./PySide6/camera_feature.py>`

      .. include:: ./PySide6/camera_feature.py
         :code: python

   .. tab:: PyQt6

      :download:`camera_feature.py <./PyQt6/camera_feature.py>`

      .. include:: ./PyQt6/camera_feature.py
         :code: python
