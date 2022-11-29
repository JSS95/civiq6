"""
Video processing example with multithreaded Gaussian blurring.
"""

import cv2
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, QThread, QEventLoop, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QMainWindow, QLabel
from qimage2ndarray import rgb_view, array2qimage
from civiq6 import VimbaRunner, VimbaCamera, VimbaCaptureSession, ArraySink


class BlurringProcessor(QObject):
    """Object to perform Gaussian blurring on the image."""

    imageChanged = Signal(QImage)

    @Slot(QImage)
    def setImage(self, image: QImage):
        array = rgb_view(image)
        ret = cv2.GaussianBlur(array, (0, 0), 25)
        image = array2qimage(ret)
        self.imageChanged.emit(image)


class ArrayProcessingSink(ArraySink):
    """Array sink to emit array only when ready."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ready = True

    def setArray(self, array: np.ndarray):
        if self.ready:
            self.ready = False
            super().setArray(array)

    def setReady(self):
        self.ready = True


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # start vimba
        self._vimbaThread = QThread()
        self._vimbaRunner = VimbaRunner()
        self._waitVimba = QEventLoop(self)
        self._vimbaRunner.moveToThread(self._vimbaThread)
        self._vimbaThread.started.connect(self._vimbaRunner.runVimba)
        self._vimbaRunner.vimbaReady.connect(self._waitVimba.quit)
        self._vimbaThread.start()
        self._waitVimba.exec()

        self._camera = VimbaCamera()
        self._captureSession = VimbaCaptureSession()
        self._arraySink = ArrayProcessingSink()
        self._processorThread = QThread()
        self._imageProcessor = BlurringProcessor()
        self._label = QLabel()

        self._captureSession.setCamera(self._camera)
        self._captureSession.setArraySink(self._arraySink)
        self._arraySink.imageChanged.connect(self._imageProcessor.setImage)
        self._imageProcessor.imageChanged.connect(self.setImageToLabel)

        self._imageProcessor.moveToThread(self._processorThread)
        self._processorThread.start()

        self._label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self._label)

        # start camera
        self._camera.start()

    @Slot(QImage)
    def setImageToLabel(self, image: QImage):
        self._label.setPixmap(QPixmap.fromImage(image))
        self._arraySink.setReady()

    def closeEvent(self, event):
        self._vimbaRunner.stopVimba()
        self._vimbaThread.quit()
        self._vimbaThread.wait()
        self._processorThread.quit()
        self._processorThread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    import vimba
    from PySide6.QtWidgets import QApplication
    import sys

    VIMBA_INST = vimba.Vimba.get_instance()
    VIMBA_INST.enable_log(vimba.LOG_CONFIG_INFO_CONSOLE_ONLY)

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
    app.quit()
