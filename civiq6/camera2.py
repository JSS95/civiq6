import vimba  # type: ignore[import]
from .devices import VimbaRunner, VimbaDevices, VimbaCameraDevice
from .qt_compat import QtCore
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .capture import VimbaCaptureSession


__all__ = [
    "VimbaCamera2",
]


VIMBA_LOGGER = vimba.Log.get_instance()


class VimbaCamera2(QtCore.QObject):
    activeChanged = QtCore.Signal(bool)
    cameraDeviceChanged = QtCore.Signal()

    def __init__(self, cameraDevice: Optional[VimbaCameraDevice] = None, parent=None):
        super().__init__(parent)
        if cameraDevice is None:
            cameraDevice = VimbaDevices.defaultVideoInput()
        self._cameraDevice = cameraDevice
        self._captureSession = None

        self._streamingThread = _StreamingThread(cameraDevice._Camera)
        self._waitCameraReady = QtCore.QEventLoop(self)
        self._streamingThread.ready.connect(self._waitCameraReady.quit)

    def cameraDevice(self) -> VimbaCameraDevice:
        return self._cameraDevice

    def captureSession(self) -> Optional["VimbaCaptureSession"]:
        return self._captureSession

    def isAvailable(self) -> bool:
        return not self._cameraDevice.isNull()

    def isActive(self) -> bool:
        if not self.isAvailable():
            return False
        camera = self._cameraDevice._Camera
        if camera is None:
            return False
        return camera.is_streaming()

    def setCameraDevice(self, device: VimbaCameraDevice):
        wasRunning = self.isActive()
        self.stop()
        self._streamingThread.ready.disconnect(self._waitCameraReady.quit)

        self._cameraDevice = device
        self._streamingThread = _StreamingThread(device._Camera)
        self._streamingThread.setCaptureSession(self.captureSession())
        self._streamingThread.ready.connect(self._waitCameraReady.quit)

        if wasRunning:
            self.start()
        self.cameraDeviceChanged.emit()

    @QtCore.Slot()
    def start(self):
        self.setActive(True)

    @QtCore.Slot()
    def stop(self):
        self.setActive(False)

    @QtCore.Slot(bool)
    def setActive(self, active: bool):
        if not self.isAvailable():
            return
        runner = VimbaRunner()
        if not self.isActive() and active:
            cam_id = self.cameraDevice().id().toStdString()
            VIMBA_LOGGER.info("Starting camera %s." % cam_id)
            self._streamingThread.start()
            self._waitCameraReady.exec()
            runner._runningCameras.append(self)
            self.activeChanged.emit(active)
        elif self.isActive() and not active:
            cam_id = self.cameraDevice().id().toStdString()
            VIMBA_LOGGER.info("Terminating camera %s." % cam_id)
            self._streamingThread.quit()
            self._streamingThread.wait()
            try:
                runner._runningCameras.remove(self)
            except ValueError:
                pass
            self.activeChanged.emit(active)

    def _setCaptureSession(self, session: "VimbaCaptureSession"):
        self._streamingThread.setCaptureSession(session)
        self._captureSession = session


class _StreamingThread(QtCore.QThread):
    ready = QtCore.Signal()

    def __init__(self, camera: Optional[vimba.Camera] = None, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.captureSession: Optional["VimbaCaptureSession"] = None

    def run(self):
        if self.camera is not None:
            with self.camera:
                cam_id = self.camera.get_id()
                try:
                    VIMBA_LOGGER.info("Camera %s started." % cam_id)
                    self.camera.start_streaming(self.grabFrame)
                    self.ready.emit()
                    self.exec()
                finally:
                    self.camera.stop_streaming()
                    VIMBA_LOGGER.info("Camera %s terminated." % cam_id)
        else:
            self.ready.emit()

    def grabFrame(self, camera: vimba.Camera, frame: vimba.Frame):
        if frame.get_status() == vimba.FrameStatus.Complete:
            array = frame.as_opencv_image().copy()
            session = self.captureSession
            if session is not None:
                session._setArray(array)
        camera.queue_frame(frame)

    def setCaptureSession(self, captureSession: Optional["VimbaCaptureSession"]):
        self.captureSession = captureSession
