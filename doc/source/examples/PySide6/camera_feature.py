from PySide6.QtCore import Slot
from PySide6.QtWidgets import QToolBar, QDoubleSpinBox
import vimba  # type: ignore[import]
from civiq6 import VimbaCamera
from camera_stream import CameraWindow
from typing import Any


VIMBA_LOGGER = vimba.Log.get_instance()


def setFeatureValue(cam: VimbaCamera, featName: str, featVal: Any):
    cam.getFeatureByName(featName).set(featVal)
    temp = "Set \"%s\" feature of camera \"%s\" to \"%s\""
    VIMBA_LOGGER.info(
        temp % (featName, str(cam.cameraDevice().id(), "utf-8"), str(featVal))
    )


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

    @Slot()
    def _onFPSEditingFinish(self):
        fps = self._fpsSpinBox.value()
        cam = self._camera
        if cam.isAvailable():
            setFeatureValue(cam, "AcquisitionFrameRate", fps)

    @Slot(bool)
    def _onCameraActiveChange(self, active: bool):
        if active:
            cam = self._camera
            if cam.isAvailable():
                setFeatureValue(cam, "AcquisitionFrameRateMode", "Basic")
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
    from PySide6.QtWidgets import QApplication
    import sys

    VIMBA_INST = vimba.Vimba.get_instance()
    VIMBA_INST.enable_log(vimba.LOG_CONFIG_INFO_CONSOLE_ONLY)

    app = QApplication(sys.argv)
    window = CameraFPSWindow()
    window.camera().start()
    window.show()
    app.exec()
    app.quit()
