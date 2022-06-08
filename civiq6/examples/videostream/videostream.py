"""
Video streaming example with multithreaded Gaussian blurring process.
"""

from PySide6.QtCore import QThread, QEventLoop
from PySide6.QtWidgets import QMainWindow
from civiq6 import VimbaRunner


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

    def vimbaThread(self) -> QThread:
        return self._vimbaThread

    def vimbaRunner(self) -> VimbaRunner:
        return self._vimbaRunner

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
