import enum
import imageio
import vimba  # type: ignore[import]
from PyQt6.QtCore import QObject, QUrl, pyqtSignal, pyqtSlot, QMutex
from civiq6 import VimbaCaptureSession
from typing import Optional


VIMBA_LOGGER = vimba.Log.get_instance()


class VideoRecorder(QObject):
    class RecorderState(enum.IntEnum):
        StoppedState = 1
        RecordingState = 2
        PausedState = 3

    recorderStateChanged = pyqtSignal(RecorderState)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._captureSession = None
        self._outputLocation = QUrl()
        self._recorderState = self.RecorderState.StoppedState
        self._writer = None
        self._lock = QMutex()

    def captureSession(self) -> Optional[VimbaCaptureSession]:
        return self._captureSession

    def _setCaptureSession(self, captureSession: Optional[VimbaCaptureSession]):
        self._captureSession = captureSession

    def outputLocation(self) -> QUrl:
        return self._outputLocation

    @pyqtSlot(QUrl)
    def setOutputLocation(self, outputLocation: QUrl):
        self._outputLocation = outputLocation

    def recorderState(self) -> RecorderState:
        return self._recorderState

    @pyqtSlot()
    def record(self):
        session = self._captureSession
        if session is None:
            return
        camera = session.camera()
        if camera is None:
            return
        if not camera.isAvailable():
            return

        if self._recorderState == self.RecorderState.StoppedState:
            path = self._outputLocation.toLocalFile()
            fps = camera.getFeatureByName("AcquisitionFrameRate").get()

            self._lock.lock()
            try:
                self._writer = imageio.get_writer(path, fps=fps)
            finally:
                self._lock.unlock()

            self._recorderState = self.RecorderState.RecordingState
            VIMBA_LOGGER.info(f"Started recording {path}")
            self.recorderStateChanged.emit(self._recorderState)

        elif self._recorderState == self.RecorderState.PausedState:
            self._recorderState = self.RecorderState.RecordingState

            VIMBA_LOGGER.info(f"Resumed recording {self._outputLocation.toLocalFile()}")
            self.recorderStateChanged.emit(self._recorderState)

    @pyqtSlot()
    def pause(self):
        if self._recorderState == self.RecorderState.RecordingState:
            self._recorderState = self.RecorderState.PausedState

            VIMBA_LOGGER.info(f"Paused recording {self._outputLocation.toLocalFile()}")
            self.recorderStateChanged.emit(self._recorderState)

    @pyqtSlot()
    def stop(self):
        if self._recorderState != self.RecorderState.StoppedState:
            self._lock.lock()
            try:
                self._writer.close()
                self._writer = None
            finally:
                self._lock.unlock()

            self._recorderState = self.RecorderState.StoppedState
            VIMBA_LOGGER.info(f"Stopped recording {self._outputLocation.toLocalFile()}")
            self.recorderStateChanged.emit(self._recorderState)

    def _setFrame(self, frame: vimba.Frame):
        if self._recorderState == self.RecorderState.RecordingState:
            obtained = self._lock.tryLock()
            if obtained:
                try:
                    self._writer.append_data(frame.as_opencv_image())
                finally:
                    self._lock.unlock()
