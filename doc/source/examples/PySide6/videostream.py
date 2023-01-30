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
        self._vimbaRunner.moveToThread(self._vimbaThread)
        self._vimbaThread.started.connect(self._vimbaRunner.runVimba)
        self._vimbaRunner.vimbaReady.connect(self._waitVimba.quit)
        self._vimbaThread.start()
        self._waitVimba.exec()

        self._camera = VimbaCamera()
        self._captureSession = VimbaCaptureSession()
        self._arraySink = ArraySink()
        self._label = QLabel()

        self._captureSession.setCamera(self._camera)
        self._captureSession.setArraySink(self._arraySink)
        self._arraySink.imageChanged.connect(self.setImageToLabel)

        self._label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self._label)

        # start camera
        self._camera.start()

    @Slot(QImage)
    def setImageToLabel(self, image: QImage):
        self._label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        self._vimbaRunner.stopVimba()
        self._vimbaThread.quit()
        self._vimbaThread.wait()
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
