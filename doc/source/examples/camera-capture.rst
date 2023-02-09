.. _examples-capturing:

Capturing and recording
=======================

This example extends the class defined in :ref:`examples-streaming` example to implement image capturing and video recording.

Before running the example, make sure your scripts are placed in the following directory structure:

| examples
| ├── scripts
| │⠀⠀⠀├── :ref:`examples-cameracapture`
| │⠀⠀⠀├── :ref:`examples-imagecapture`
| │⠀⠀⠀├── :ref:`examples-videorecorder`
| │⠀⠀⠀└── :ref:`camera_stream.py <examples-streaming>`
| ├── :download:`capture.svg`
| └── :download:`record.svg`

Running **camera_capture.py** opens a camera streaming window where you can capture or record the frames.

.. _examples-imagecapture:

imagecapture.py
---------------

.. tabs::

   .. tab:: PySide6

      :download:`imagecapture.py <./PySide6/imagecapture.py>`

      .. include:: ./PySide6/imagecapture.py
         :code: python

   .. tab:: PyQt6

      :download:`imagecapture.py <./PyQt6/imagecapture.py>`

      .. include:: ./PyQt6/imagecapture.py
         :code: python

.. _examples-videorecorder:

videorecorder.py
----------------

.. tabs::

   .. tab:: PySide6

      :download:`videorecorder.py <./PySide6/videorecorder.py>`

      .. include:: ./PySide6/videorecorder.py
         :code: python

   .. tab:: PyQt6

      :download:`videorecorder.py <./PyQt6/videorecorder.py>`

      .. include:: ./PyQt6/videorecorder.py
         :code: python

.. _examples-cameracapture:

camera_capture.py
-----------------

.. tabs::

   .. tab:: PySide6

      :download:`camera_capture.py <./PySide6/camera_capture.py>`

      .. include:: ./PySide6/camera_capture.py
         :code: python

   .. tab:: PyQt6

      :download:`camera_capture.py <./PyQt6/camera_capture.py>`

      .. include:: ./PyQt6/camera_capture.py
         :code: python
