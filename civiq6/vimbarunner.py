"""
Vimba instance
==============

"""

from typing import List, TYPE_CHECKING
import vimba  # type: ignore[import]
from .dynqt6 import QtCore

if TYPE_CHECKING:
    from .camera import VimbaCamera


__all__ = [
    "VimbaRunner",
]


VIMBA_INST = vimba.Vimba.get_instance()


class VimbaRunner(QtCore.QObject):

    vimbaReady = QtCore.Signal()

    def __new__(cls, parent=None):
        if not hasattr(cls, "_inst"):
            cls._inst = super().__new__(cls, parent)
            cls._initialized = False
        return cls._inst

    def __init__(self, parent=None):
        if not self._initialized:
            super().__init__(parent)
            self._initialized = True
            self._runningCameras: List["VimbaCamera"] = []
            self._eventLoop = QtCore.QEventLoop(self)

    @QtCore.Slot()
    def runVimba(self):
        with VIMBA_INST:
            try:
                VIMBA_INST.register_camera_change_handler(self.cameraChangeHandler)
                self.updateCameras()
                self.vimbaReady.emit()
                self._eventLoop.exec()
            finally:
                VIMBA_INST.unregister_camera_change_handler(self.cameraChangeHandler)

    def stopVimba(self):
        while self._runningCameras:
            cam = self._runningCameras.pop()
            cam.stop()
        self._eventLoop.quit()

    def cameraChangeHandler(self, camera: vimba.Camera, event: vimba.CameraEvent):
        self.updateCameras()

    def updateCameras(self):
        cams = VIMBA_INST.get_all_cameras()
        VimbaDevices().setVideoInputs([VimbaCameraDevice.fromCamera(c) for c in cams])


from .devices import VimbaDevices, VimbaCameraDevice  # noqa: E402
