"""
Video streaming and processing.
"""

import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, QThread, QEventLoop, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QMainWindow, QLabel
from qimage2ndarray import array2qimage
from civiq6 import VimbaRunner, VimbaCamera, VimbaCaptureSession, ArraySink


class ArrayProcessor(QObject):
    imageChanged = Signal(QImage)

    @Slot(np.ndarray)
    def setArray(self, array: np.ndarray):
        self.imageChanged.emit(array2qimage(array))

    @Slot(QImage)
    def setImage(self, image: QImage):
        self.imageChanged.emit(image)


class ArrayProcessingSink(ArraySink):
    """Array sink to emit array only when the processor is ready."""

    imageChanged = Signal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ready = True

    def setArray(self, array: np.ndarray):
        if self.ready:
            # self.ready = False
            super().setArray(array)
            self.imageChanged.emit(array2qimage(array))

    def setReady(self):
        self.ready = True


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # start vimba
        self._vimbaThread = QThread()
        self._vimbaRunner = VimbaRunner()
        self._waitVimba = QEventLoop(self)
        self.vimbaRunner().moveToThread(self.vimbaThread())
        self.vimbaThread().started.connect(self.vimbaRunner().runVimba)
        self.vimbaRunner().vimbaReady.connect(self._waitVimba.quit)
        self.vimbaThread().start()
        self._waitVimba.exec()

        self._camera = VimbaCamera()
        self._capture_session = VimbaCaptureSession()
        self._array_sink = ArrayProcessingSink()
        self._processorThread = QThread()
        self._array_processor = ArrayProcessor()
        self._label = QLabel()

        self.captureSession().setCamera(self.camera())
        self.captureSession().setArraySink(self.arraySink())
        self.arraySink().arrayChanged.connect(self.arrayProcessor().setArray)
        self.arrayProcessor().imageChanged.connect(self.setImageToLabel)

        self.arrayProcessor().moveToThread(self.processorThread())
        self.processorThread().start()

        self.label().setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label())

        # start camera
        self.camera().start()

    def vimbaThread(self) -> QThread:
        return self._vimbaThread

    def vimbaRunner(self) -> VimbaRunner:
        return self._vimbaRunner

    def camera(self) -> VimbaCamera:
        return self._camera

    def captureSession(self) -> VimbaCaptureSession:
        return self._capture_session

    def arraySink(self) -> ArrayProcessingSink:
        return self._array_sink

    def processorThread(self) -> QThread:
        return self._processorThread

    def arrayProcessor(self) -> ArrayProcessor:
        return self._array_processor

    def label(self) -> QLabel:
        return self._label

    @Slot(QImage)
    def setImageToLabel(self, image: QImage):
        self.label().setPixmap(QPixmap.fromImage(image))
        self.arraySink().setReady()

    def closeEvent(self, event):
        self.processorThread().quit()
        self.vimbaRunner().stopVimba()
        self.vimbaThread().quit()
        self.processorThread().wait()
        self.vimbaThread().wait()
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
