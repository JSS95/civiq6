"""
Vimba camera device
===================

"""

from typing import Optional, List
import vimba  # type: ignore[import]
from .dynqt6 import QtCore


__all__ = [
    "VimbaDevices",
    "VimbaCameraDevice",
]


class VimbaDevices(QtCore.QObject):
    videoInputsChanged = QtCore.Signal()

    def __new__(cls, parent=None):
        if not hasattr(cls, "_inst"):
            cls._inst = super().__new__(cls, parent)
            cls._initialized = False
        return cls._inst

    def __init__(self, parent=None):
        if not self._initialized:
            super().__init__(parent)
            self._initialized = True
            self._videoInputs = []

    @staticmethod
    def videoInputs() -> List["VimbaCameraDevice"]:
        return VimbaDevices()._videoInputs

    @staticmethod
    def defaultVideoInput() -> "VimbaCameraDevice":
        videoInputs = VimbaDevices.videoInputs()
        if not videoInputs:
            ret = VimbaCameraDevice()
        else:
            ret = videoInputs[0]
        return ret

    @QtCore.Slot(list)
    def setVideoInputs(self, videoInputs: List["VimbaCameraDevice"]):
        self._videoInputs = videoInputs
        self.videoInputsChanged.emit()


class VimbaCameraDevice(QtCore.QObject):
    @classmethod
    def fromCamera(cls, camera: vimba.Camera):
        obj = cls()
        obj._Camera = camera
        obj._id = camera.get_id()
        obj._desc = camera.get_name()
        return obj

    def __init__(self, other: Optional["VimbaCameraDevice"] = None):
        super().__init__()
        if other is None:
            self._Camera = None
            self._id = ""
            self._desc = ""
        else:
            self._Camera = other._Camera
            self._id = other._id
            self._desc = other._desc

    def __eq__(self, other):
        return type(self) == type(other) and self._Camera == other._Camera

    def __ne__(self, other):
        return type(self) != type(other) or self._Camera != other._Camera

    def id(self) -> QtCore.QByteArray:
        return QtCore.QByteArray(self._id)  # type: ignore[call-overload]

    def description(self) -> str:
        return self._desc

    def isNull(self) -> bool:
        return self._Camera is None

    def isDefault(self) -> bool:
        return self == VimbaDevices().defaultVideoInput()

    def frameRate(self) -> float:
        camera = self._Camera
        if camera is None:
            ret = -1
        else:
            with camera:
                ret = camera.get_feature_by_name("AcquisitionFrameRate").get()
        return ret

    def resolution(self) -> QtCore.QSize:
        camera = self._Camera
        if camera is None:
            w, h = -1, -1
        else:
            with camera:
                w = camera.get_feature_by_name("Width").get()
                h = camera.get_feature_by_name("Height").get()
        return QtCore.QSize(w, h)

    def pixelFormat(self) -> Optional[vimba.PixelFormat]:
        camera = self._Camera
        if camera is None:
            ret = None
        else:
            with camera:
                ret = camera.get_pixel_format()
        return ret
