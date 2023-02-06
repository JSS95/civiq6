from PySide6.QtCore import Slot
from PySide6.QtWidgets import QToolBar, QDoubleSpinBox
from videostream import CameraWindow


class CameraFeatureWindow(CameraWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._fpsSpinBox.editingFinished.connect(self._onEditingFinish)

        cam = self._camera
        if cam.isAvailable():
            cam.getFeatureByName("AcquisitionFrameRateMode").set("Basic")
            fpsFeature = cam.getFeatureByName("AcquisitionFrameRate")
            minFPS, maxFPS = fpsFeature.get_range()
            self._fpsSpinBox.setMinimum(minFPS)
            self._fpsSpinBox.setMaximum(maxFPS)
            self._fpsSpinBox.setValue(fpsFeature.get())

    def initUI(self):
        super().initUI()

        self._fpsSpinBox = QDoubleSpinBox()
        self._fpsSpinBox.setPrefix("FPS: ")

        self._toolBar = QToolBar()
        self._toolBar.addWidget(self._fpsSpinBox)
        self.addToolBar(self._toolBar)

    @Slot()
    def _onEditingFinish(self):
        fps = self._fpsSpinBox.value()
        cam = self._camera
        if cam.isAvailable():
            cam.getFeatureByName("AcquisitionFrameRate").set(fps)

    def closeEvent(self, event):
        self._fpsSpinBox.clearFocus()
        super().closeEvent(event)


if __name__ == "__main__":
    import vimba  # type: ignore[import]
    from PySide6.QtWidgets import QApplication
    import sys

    VIMBA_INST = vimba.Vimba.get_instance()
    VIMBA_INST.enable_log(vimba.LOG_CONFIG_INFO_CONSOLE_ONLY)

    app = QApplication(sys.argv)
    window = CameraFeatureWindow()
    window.show()
    app.exec()
    app.quit()
