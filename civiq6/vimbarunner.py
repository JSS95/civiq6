"""
Vimba instance
==============

:mod:`civiq6.vimbarunner` provides a class to start the Vimba instance.

"""

from typing import List, TYPE_CHECKING
import vimba  # type: ignore[import]
from .qt_compat import QtCore

if TYPE_CHECKING:
    from .camera import VimbaCamera


__all__ = [
    "VimbaRunner",
]


VIMBA_INST = vimba.Vimba.get_instance()


class VimbaRunner(QtCore.QObject):
    """
    Class to run the Vimba instance.

    :class:`VimbaRunner` manages the camera change event by running the Vimba
    instance in event loop. Once Vimba instance is successfully run,
    :attr:`vimbaReady` signal is emitted.

    To access the cameras, this instance must be run first. Typical way to use is
    to move the instance to dedicated thread.

    This example runs :class:`VimbaRunner` in dedicated thread:

    .. code:: python

       vimbaThread = QThread()
       vimbaRunner = VimbaRunner()
       vimbaRunner.moveToThread(vimbaThread)
       vimbaThread.started.connect(vimbaRunner.runVimba)
       vimbaThread.start()

    :class:`VimbaRunner` is a singleton object.

    """

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
        """
        Run the vimba instance.

        This method registers :meth:`cameraChangeHandler` to the camera change
        handler of Vimba instance, and loades all connected cameras to
        :class:`VimbaDevices`.

        When Vimba is successfully run, :attr:`vimbaReady` signal is emitted and
        event loop is executed. If event loop is finished or Vimba fails to run,
        camera change handler is unregistered.

        To finish the event loop, run :meth:`stopVimba`.

        """
        with VIMBA_INST:
            try:
                VIMBA_INST.register_camera_change_handler(self.cameraChangeHandler)
                self.updateCameras()
                self.vimbaReady.emit()
                self._eventLoop.exec()
            finally:
                VIMBA_INST.unregister_camera_change_handler(self.cameraChangeHandler)

    def stopVimba(self):
        """
        Stop all running cameras and quits the Vimba instance event loop.
        """
        while self._runningCameras:
            cam = self._runningCameras.pop()
            cam.stop()
        self._eventLoop.quit()

    def cameraChangeHandler(self, camera: vimba.Camera, event: vimba.CameraEvent):
        """Run :meth:`updateCameras`."""
        self.updateCameras()

    def updateCameras(self):
        """Update all cameras to :class:`VimbaDevices`."""
        cams = VIMBA_INST.get_all_cameras()
        VimbaDevices().setVideoInputs([VimbaCameraDevice.fromCamera(c) for c in cams])


from .devices import VimbaDevices, VimbaCameraDevice  # noqa: E402
