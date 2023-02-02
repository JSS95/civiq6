from PyQt6.QtCore import QThread, QEventLoop
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtMultimediaWidgets import QVideoWidget
from civiq6 import VimbaRunner, VimbaCamera2, VimbaCaptureSession


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

        self._camera = VimbaCamera2()
        self._captureSession = VimbaCaptureSession()
        self._videoWidget = QVideoWidget()
        self._captureSession.setCamera(self._camera)
        self._captureSession.setVideoOutput(self._videoWidget)

        self.setCentralWidget(self._videoWidget)

        # start camera
        self._camera.start()

    def closeEvent(self, event):
        self._vimbaRunner.stopVimba()
        self._vimbaThread.quit()
        self._vimbaThread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    import vimba  # type: ignore[import]
    from PyQt6.QtWidgets import QApplication
    import sys

    VIMBA_INST = vimba.Vimba.get_instance()
    VIMBA_INST.enable_log(vimba.LOG_CONFIG_INFO_CONSOLE_ONLY)

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
    app.quit()
