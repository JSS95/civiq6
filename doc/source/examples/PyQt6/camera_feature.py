from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QToolBar, QDoubleSpinBox
from camera_stream import CameraWindow


class CameraFPSWindow(CameraWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._fpsSpinBox = QDoubleSpinBox()
        self._toolBar = QToolBar()
        self._fpsSpinBox.editingFinished.connect(self._onFPSEditingFinish)

        self._camera.activeChanged.connect(self._onCameraActiveChange)

        self._fpsSpinBox.setPrefix("FPS: ")
        self._toolBar.addWidget(self._fpsSpinBox)
        self.addToolBar(self._toolBar)

    @pyqtSlot()
    def _onFPSEditingFinish(self):
        fps = self._fpsSpinBox.value()
        cam = self._camera
        if cam.isAvailable():
            cam.getFeatureByName("AcquisitionFrameRate").set(fps)

    @pyqtSlot(bool)
    def _onCameraActiveChange(self, active: bool):
        if active:
            cam = self._camera
            if cam.isAvailable():
                cam.getFeatureByName("AcquisitionFrameRateMode").set("Basic")
                fpsFeature = cam.getFeatureByName("AcquisitionFrameRate")
                minFPS, maxFPS = fpsFeature.get_range()
                self._fpsSpinBox.setMinimum(minFPS)
                self._fpsSpinBox.setMaximum(maxFPS)
                self._fpsSpinBox.setValue(fpsFeature.get())
        else:
                self._fpsSpinBox.setMinimum(0.0)
                self._fpsSpinBox.setMaximum(0.0)
                self._fpsSpinBox.setValue(0.0)

    def closeEvent(self, event):
        self._fpsSpinBox.clearFocus()
        super().closeEvent(event)


if __name__ == "__main__":
    import vimba  # type: ignore[import]
    from PyQt6.QtWidgets import QApplication
    import sys

    VIMBA_INST = vimba.Vimba.get_instance()
    VIMBA_INST.enable_log(vimba.LOG_CONFIG_INFO_CONSOLE_ONLY)

    app = QApplication(sys.argv)
    window = CameraFPSWindow()
    window.camera().start()
    window.show()
    app.exec()
    app.quit()
