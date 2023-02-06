import imageio
import vimba  # type: ignore[import]
from PySide6.QtCore import QObject, Signal, Slot
from civiq6 import VimbaCaptureSession
from typing import Optional


VIMBA_LOGGER = vimba.Log.get_instance()


class ImageCapture(QObject):
    imageSaved = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._captureSession = None
        self._id = 0

        self._image = None
        self._writing = False

    def captureSession(self) -> Optional[VimbaCaptureSession]:
        return self._captureSession

    def _setCaptureSession(self, captureSession: Optional[VimbaCaptureSession]):
        self._captureSession = captureSession

    @Slot()
    def captureToFile(self, path: str = "") -> int:
        if self.captureSession() is None or self._image is None:
            return -1
        self._writing = True

        imageio.imwrite(path, self._image)
        ret_id = self._id
        self._id += 1
        self._image = None
        self._writing = False

        VIMBA_LOGGER.info("Captured %s" % path)
        self.imageSaved.emit(ret_id, path)

        return ret_id

    def _setFrame(self, frame: vimba.Frame):
        if not self._writing:
            self._image = frame.as_opencv_image().copy()
