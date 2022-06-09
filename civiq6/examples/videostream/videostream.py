"""
Basic video streaming example.
"""

from PySide6.QtCore import Slot, QThread, QEventLoop, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QMainWindow, QLabel
from civiq6 import VimbaRunner, VimbaCamera, VimbaCaptureSession, ArraySink


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
        self._array_sink = ArraySink()
        self._label = QLabel()

        self.captureSession().setCamera(self.camera())
        self.captureSession().setArraySink(self.arraySink())
        self.arraySink().imageChanged.connect(self.setImageToLabel)

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

    def arraySink(self) -> ArraySink:
        return self._array_sink

    def label(self) -> QLabel:
        return self._label

    @Slot(QImage)
    def setImageToLabel(self, image: QImage):
        self.label().setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        self.vimbaRunner().stopVimba()
        self.vimbaThread().quit()
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
