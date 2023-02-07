Selecting the camera and turning on/off
=======================================

This example extends the class defined in :ref:`examples-streaming` example to implement selecting the camera and starting/stopping it.

Before running the example, make sure your scripts are placed in the following directory structure:

| examples
| ├── scripts
| │⠀⠀⠀├── :ref:`examples-switch`
| │⠀⠀⠀└── :ref:`camera_stream.py <examples-streaming>`
| └── :download:`camera.svg`

Running **camera_switch.py** opens a camera streaming window with a toolbar that allows you to manipulate the camera.

.. _examples-switch:

camera_switch.py
-----------------

.. tabs::

   .. tab:: PySide6

      :download:`camera_switch.py <./PySide6/camera_switch.py>`

      .. include:: ./PySide6/camera_switch.py
         :code: python

   .. tab:: PyQt6

      :download:`camera_switch.py <./PyQt6/camera_switch.py>`

      .. include:: ./PyQt6/camera_switch.py
         :code: python
