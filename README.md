# CIViQ6

Python package for camera integration of [VimbaPython](https://github.com/alliedvision/VimbaPython) and Qt6.

CIViQ is designed to be used with either [PySide6](https://pypi.org/project/PySide6/) or [PyQt6](https://pypi.org/project/PyQt6/).
However, PyQt6 is not available until the dependent package, [qimage2ndarray](https://pypi.org/project/qimage2ndarray/), supports it.

This package is tested with Vimba 6.0, VimbaPython 1.2.1, and Mako U-130B camera device connected to Window 11.

# Installation

Before you install, be careful for other Qt-dependent packages installed in your environment.
For example, non-headless `OpenCV-Python` modifies the Qt dependency thus can make other Qt bindings unavailable.

To install CIViQ6, you first need to install VimbaPython package which is not distributed by PyPI.
Go to its repository and follow the instructions.

After VimbaPython is installed, `civiq6` can be installed using `pip`.

```
$ pip install civiq6
```

# How to use

`VimbaRunner` must be run first in `QThread` to start Vimba instance.

After Vimba is started, you can access the vimba camera APIs and acquire frames.

CIViQ is designed to be similar to Qt6's QtMultimedia framework:

|       Qt class       |  CIViQ counterpart  |
| -------------------- | ------------------- |
|     QMediaDevices    |     VimbaDevices    |
|     QCameraDevice    |  VimbaCameraDevice  |
|       QCamera        |     VimbaCamera     |
| QMediaCaptureSession | VimbaCaptureSession |
|      QVideoSink      |      ArraySink      |
|     QImageCapture    |  VimbaImageCapture  |
|    QMediaRecorder    |  VimbaVideoRecorder |

For more information, refer to the documentation and examples.

# Examples

Use cases with multithreading are provided in [examples](https://github.com/JSS95/civiq6/tree/master/civiq6/examples) directory.
They can be found in documentation as well.

# Documentation

Documentation can be found on Read the Docs:

> https://civiq6.readthedocs.io/

If you want to build the document yourself, clone the source code and install with `[doc]` option.
Go to `doc` directory and build.

```
$ pip install civiq6[doc]
$ cd doc
$ make html
```
