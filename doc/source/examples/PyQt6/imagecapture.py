import imageio
import vimba  # type: ignore[import]
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QMutex
from civiq6 import VimbaCaptureSession
from typing import Optional


VIMBA_LOGGER = vimba.Log.get_instance()


class ImageCapture(QObject):
    imageSaved = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._captureSession = None
        self._id = 0

        self._image = None
        self._lock = QMutex()

    def captureSession(self) -> Optional[VimbaCaptureSession]:
        return self._captureSession

    def _setCaptureSession(self, captureSession: Optional[VimbaCaptureSession]):
        self._captureSession = captureSession

    @pyqtSlot(str)
    def captureToFile(self, path: str = "") -> int:
        if self.captureSession() is None or self._image is None:
            return -1

        self._lock.lock()

        try:
            imageio.imwrite(path, self._image)
            self._image = None
        finally:
            self._lock.unlock()

        ret_id = self._id
        self._id += 1
        VIMBA_LOGGER.info("Captured %s" % path)
        self.imageSaved.emit(ret_id, path)

        return ret_id

    def _setFrame(self, frame: vimba.Frame):
        obtained = self._lock.tryLock()
        if obtained:
            try:
                self._image = frame.as_opencv_image().copy()
            finally:
                self._lock.unlock()
