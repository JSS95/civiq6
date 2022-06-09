"""
Vimba camera interface
======================

"""

import copy
import queue
from typing import Optional, TYPE_CHECKING
import vimba  # type: ignore[import]
from .vimbarunner import VimbaRunner
from .devices import VimbaDevices, VimbaCameraDevice
from .dynqt6 import QtCore

if TYPE_CHECKING:
    from .capture import VimbaCaptureSession


__all__ = [
    "VimbaCamera",
    "FrameProducer",
    "FrameConsumer",
]


VIMBA_LOGGER = vimba.Log.get_instance()


class VimbaCamera(QtCore.QObject):

    activeChanged = QtCore.Signal(bool)

    def __init__(self, cameraDevice: Optional[VimbaCameraDevice] = None, parent=None):
        super().__init__(parent)
        if cameraDevice is None:
            cameraDevice = VimbaDevices.defaultVideoInput()
        self._cameraDevice = cameraDevice
        self._captureSession = None
        self._active = False

        self._frameQueue: queue.Queue = queue.Queue()
        self._frameProducer = FrameProducer(cameraDevice._Camera, self._frameQueue)
        self._waitProducerReady = QtCore.QEventLoop(self)
        self._frameConsumer = FrameConsumer(self._frameQueue)
        self._consumerThread = QtCore.QThread(self)
        self._frameConsumer.moveToThread(self._consumerThread)
        self._consumerThread.started.connect(  # type: ignore[attr-defined]
            self._frameConsumer.run
        )

        self._connectFrameProducer(self._frameProducer)

    def cameraDevice(self) -> VimbaCameraDevice:
        return self._cameraDevice

    def captureSession(self) -> Optional["VimbaCaptureSession"]:
        return self._captureSession

    def isAvailable(self) -> bool:
        return not self.cameraDevice().isNull()

    def isActive(self) -> bool:
        return self._active

    def setCameraDevice(self, device: Optional[VimbaCameraDevice] = None):
        was_running = self.isActive()
        self.stop()
        self._disconnectFrameProducer(self._frameProducer)
        if device is None:
            device = VimbaDevices.defaultVideoInput()
        self._cameraDevice = device
        self._frameProducer = FrameProducer(device._Camera, self._frameQueue)
        self._connectFrameProducer(self._frameProducer)
        if was_running:
            self.start()

    def _connectFrameProducer(self, producer: "FrameProducer"):
        producer.ready.connect(self._waitProducerReady.quit)

    def _disconnectFrameProducer(self, producer: "FrameProducer"):
        producer.ready.disconnect(self._waitProducerReady.quit)

    def _setCaptureSession(self, session: "VimbaCaptureSession"):
        self._frameConsumer.setCaptureSession(session)
        self._captureSession = session

    def _removeCaptureSession(self):
        self._frameConsumer.removeCaptureSession()
        self._captureSession = None

    @QtCore.Slot(bool)
    def setActive(self, active: bool):
        if not self.isAvailable():
            return
        runner = VimbaRunner()
        if not self.isActive() and active:
            cam_id = self.cameraDevice().id().toStdString()
            VIMBA_LOGGER.info("Starting camera %s." % cam_id)
            self._consumerThread.start()
            self._frameProducer.start()
            self._waitProducerReady.exec()
            runner._runningCameras.append(self)
            self._active = True
            self.activeChanged.emit(active)
        elif self.isActive() and not active:
            cam_id = self.cameraDevice().id().toStdString()
            VIMBA_LOGGER.info("Terminating camera %s." % cam_id)
            self._frameProducer.quit()
            self._frameProducer.wait()
            self._frameConsumer.stop()
            self._consumerThread.quit()
            self._consumerThread.wait()
            try:
                runner._runningCameras.remove(self)
            except ValueError:
                pass
            self._active = False
            self.activeChanged.emit(active)

    @QtCore.Slot()
    def start(self):
        self.setActive(True)

    @QtCore.Slot()
    def stop(self):
        self.setActive(False)


class FrameProducer(QtCore.QThread):

    ready = QtCore.Signal()

    def __init__(self, camera: Optional[vimba.Camera], queue: queue.Queue, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.queue = queue

    def run(self):
        if self.camera is not None:
            with self.camera:
                cam_id = self.camera.get_id()
                try:
                    VIMBA_LOGGER.info("Camera %s started." % cam_id)
                    self.camera.start_streaming(self.queue_frame)
                    self.ready.emit()
                    self.exec()
                finally:
                    self.camera.stop_streaming()
                    VIMBA_LOGGER.info("Camera %s terminated." % cam_id)
        else:
            self.ready.emit()

    def queue_frame(self, camera: vimba.Camera, frame: vimba.Frame):
        if frame.get_status() == vimba.FrameStatus.Complete:
            if not self.queue.full():
                try:
                    copied_frame = copy.deepcopy(frame)
                    self.queue.put_nowait(copied_frame)
                except queue.Full:
                    pass
        camera.queue_frame(frame)


class FrameConsumer(QtCore.QObject):
    def __init__(self, queue: queue.Queue, parent=None):
        super().__init__(parent)
        self.queue = queue
        self.alive = False
        self.captureSession = None

    @QtCore.Slot()
    def run(self):
        self.alive = True
        while self.alive:
            try:
                # must keep reference of the frame
                self.frame = self.queue.get_nowait()
                cv_img = self.frame.as_opencv_image().copy()
                session = self.captureSession
                if session is not None:
                    session.setArray(cv_img)
            except queue.Empty:
                pass

    def stop(self):
        self.alive = False

    def setCaptureSession(self, session: "VimbaCaptureSession"):
        self.captureSession = session  # type: ignore[assignment]

    def removeCaptureSession(self):
        self.captureSession = None
