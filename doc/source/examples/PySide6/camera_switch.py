from PySide6.QtCore import Signal, Slot, QSize
from PySide6.QtWidgets import QToolBar, QComboBox, QToolButton
from PySide6.QtGui import QIcon
from civiq6 import VimbaDevices, VimbaCameraDevice
from camera_stream import CameraWindow


class CameraToolBar(QToolBar):
    deviceActivated = Signal(VimbaCameraDevice)
    cameraActiveChangeRequested = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._deviceComboBox = QComboBox()
        self._cameraButton = QToolButton()
        self._cameraActive = False

        self._deviceComboBox.setPlaceholderText("Select camera")
        self._deviceComboBox.activated.connect(self._onDeviceActivation)

        self._cameraButton.setToolTip("Click to toggle camera")
        cameraButtonIcon = QIcon()
        cameraButtonIcon.addFile("../camera.svg", QSize(24, 24))
        self._cameraButton.setIcon(cameraButtonIcon)
        self._cameraButton.clicked.connect(self._onCameraButtonClick)

        self.addWidget(self._deviceComboBox)
        self.addWidget(self._cameraButton)

        self.loadDevices()

    def _onDeviceActivation(self, index: int):
        device = self._deviceComboBox.itemData(index)
        self.deviceActivated.emit(device)

    @Slot(VimbaCameraDevice)
    def setCameraDevice(self, device: VimbaCameraDevice):
        self._deviceComboBox.setCurrentIndex(self._deviceComboBox.findData(device))

    def _onCameraButtonClick(self):
        self.cameraActiveChangeRequested.emit(not self._cameraActive)

    @Slot(bool)
    def setCameraActive(self, cameraActive: bool):
        if cameraActive:
            self._cameraButton.setCheckable(True)
            self._cameraButton.setChecked(True)
        else:
            self._cameraButton.setChecked(False)
            self._cameraButton.setCheckable(False)
        self._cameraActive = cameraActive

    def loadDevices(self):
        self._deviceComboBox.clear()
        for device in VimbaDevices.videoInputs():
            name = device.description()
            self._deviceComboBox.addItem(name, userData=device)


class CameraSwitchWindow(CameraWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._toolBar = CameraToolBar()
        self._vimbaDevices = VimbaDevices()
        self._vimbaDevices.videoInputsChanged.connect(self._onVideoInputsChange)
        self._toolBar.deviceActivated.connect(self._camera.setCameraDevice)
        self._camera.cameraDeviceChanged.connect(self._onCameraDeviceChange)
        self._toolBar.cameraActiveChangeRequested.connect(self._camera.setActive)
        self._camera.activeChanged.connect(self._toolBar.setCameraActive)

        self.addToolBar(self._toolBar)

        self._toolBar.setCameraDevice(self._camera.cameraDevice())

    def _onVideoInputsChange(self):
        self._toolBar.loadDevices()
        self._toolBar.setCameraDevice(self._camera.cameraDevice())

    def _onCameraDeviceChange(self):
        self._toolBar.setCameraDevice(self._camera.cameraDevice())


if __name__ == "__main__":
    import vimba  # type: ignore[import]
    from PySide6.QtWidgets import QApplication
    import sys

    VIMBA_INST = vimba.Vimba.get_instance()
    VIMBA_INST.enable_log(vimba.LOG_CONFIG_INFO_CONSOLE_ONLY)

    app = QApplication(sys.argv)
    window = CameraSwitchWindow()
    window.show()
    app.exec()
    app.quit()
