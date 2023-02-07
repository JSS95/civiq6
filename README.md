# CIViQ6 - Camera Integration for Vimba and Qt6

[![PyPI version](https://badge.fury.io/py/CIViQ6.svg)](https://badge.fury.io/py/CIViQ6)
[![Python Version](https://img.shields.io/pypi/pyversions/civiq6)](https://pypi.org/project/civiq6/)
[![Build Status](https://github.com/JSS95/civiq6/actions/workflows/ci.yml/badge.svg)](https://github.com/JSS95/civiq6/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/civiq6/badge/?version=latest)](https://civiq6.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/github/license/JSS95/civiq6)](https://github.com/JSS95/civiq6/blob/master/LICENSE)

CIViQ6 is a Python package which integrates [VimbaPython](https://github.com/alliedvision/VimbaPython) and Qt6 multimedia scheme.

The following Qt bindings are supported:
- [PySide6](https://pypi.org/project/PySide6/)
- [PyQt6](https://pypi.org/project/PyQt6/)

This package is tested using Vimba 6.0, VimbaPython 1.2.1, and Mako U-130B camera device connected to the device with Window 11.

# How to use

`VimbaRunner` must be run first in `QThread` to start Vimba instance.

After Vimba is started, you can access the vimba camera APIs and acquire frames.

CIViQ6 is designed to be similar to Qt6's QtMultimedia framework:

|       Qt class       |  CIViQ6 counterpart  |
| -------------------- | -------------------- |
|     QMediaDevices    |      VimbaDevices    |
|     QCameraDevice    |   VimbaCameraDevice  |
|       QCamera        |      VimbaCamera     |
| QMediaCaptureSession |  VimbaCaptureSession |

For more information, refer to the documentation and examples.

# Examples

Use cases with multithreading are provided in [examples](https://github.com/JSS95/civiq6/tree/master/civiq6/examples) directory.
They can be found in documentation as well.

# Installation

Before you install, be careful for other Qt-dependent packages installed in your environment.
For example, non-headless `OpenCV-Python` modifies the Qt dependency thus can make other Qt bindings unavailable.

To install CIViQ6, you first need to install [VimbaPython](https://github.com/alliedvision/VimbaPython) package which is not distributed by PyPI.
Go to its repository and follow the instructions.

After VimbaPython is installed, `civiq6` can be installed using `pip`.

```
$ pip install civiq6
```

# Documentation

CIViQ6 is documented with [Sphinx](https://pypi.org/project/Sphinx/).
Documentation can be found on Read the Docs:

> https://civiq6.readthedocs.io/

If you want to build the document yourself, clone the source code and install with `[doc]` option.
This option installs the additional packages to build the document and to run the examples.

Go to `doc` directory and build the document.

```
$ pip install civiq6[doc]
$ cd doc
$ make html
```

Document will be generated in `build/html` directory. Open `index.html` to see the central page.
