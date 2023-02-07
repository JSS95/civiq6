from PySide6.QtCore import QUrl, Signal, Slot, QSize
from PySide6.QtWidgets import QToolBar, QLineEdit, QToolButton, QStyle
from PySide6.QtGui import QIcon
from imagecapture import ImageCapture
from videorecorder import VideoRecorder
from camera_stream import CameraWindow


class CaptureToolBar(QToolBar):
    captureRequested = Signal(str)
    recordPathChanged = Signal(QUrl)
    recordStartRequested = Signal()
    recordStopRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._capturePathLineEdit = QLineEdit()
        self._captureButton = QToolButton()
        self._recordPathLineEdit = QLineEdit()
        self._recordButton = QToolButton()
        self._recordState = VideoRecorder.RecorderState.StoppedState

        self._capturePathLineEdit.setPlaceholderText("Image capture path")
        self._captureButton.setToolTip("Click to capture image")
        captureButtonIcon = QIcon()
        captureButtonIcon.addFile("../capture.svg", QSize(24, 24))
        self._captureButton.setIcon(captureButtonIcon)

        self._recordPathLineEdit.setPlaceholderText("Video record path")
        self._recordButton.setToolTip("Click to toggle video recording")
        recordButtonIcon = QIcon()
        recordButtonIcon.addFile("../record.svg", QSize(24, 24))
        self._recordButton.setIcon(recordButtonIcon)

        self.addWidget(self._capturePathLineEdit)
        self.addWidget(self._captureButton)
        self.addSeparator()
        self.addWidget(self._recordPathLineEdit)
        self.addWidget(self._recordButton)

        self._captureButton.clicked.connect(self._onCaptureButtonClick)
        self._recordPathLineEdit.textChanged.connect(self._onRecordPathEdit)
        self._recordButton.clicked.connect(self._onRecordButtonClick)

    def _onCaptureButtonClick(self):
        path = self._capturePathLineEdit.text()
        self.captureRequested.emit(path)

    def _onRecordPathEdit(self, path: str):
        self.recordPathChanged.emit(QUrl.fromLocalFile(path))

    def _onRecordButtonClick(self):
        if self._recordState == VideoRecorder.RecorderState.StoppedState:
            self.recordStartRequested.emit()
        else:
            self.recordStopRequested.emit()

    @Slot(VideoRecorder.RecorderState)
    def setRecorderState(self, state: VideoRecorder.RecorderState):
        if state == VideoRecorder.RecorderState.RecordingState:
            self._recordButton.setCheckable(True)
            self._recordButton.setChecked(True)
            self._recordButton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
            )
        elif state == VideoRecorder.RecorderState.StoppedState:
            self._recordButton.setChecked(False)
            self._recordButton.setCheckable(False)
            icon = QIcon()
            icon.addFile("../record.svg", QSize(24, 24))
            self._recordButton.setIcon(icon)
        self._recordState = state


class CameraCaptureWindow(CameraWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._imageCapture = ImageCapture()
        self._videoRecorder = VideoRecorder()
        self._captureSession.setImageCapture(self._imageCapture)
        self._captureSession.setRecorder(self._videoRecorder)

        self._toolBar = CaptureToolBar()
        self._toolBar.captureRequested.connect(self._imageCapture.captureToFile)
        self._toolBar.recordPathChanged.connect(self._videoRecorder.setOutputLocation)
        self._toolBar.recordStartRequested.connect(self._videoRecorder.record)
        self._toolBar.recordStopRequested.connect(self._videoRecorder.stop)
        self._videoRecorder.recorderStateChanged.connect(self._toolBar.setRecorderState)

        self.addToolBar(self._toolBar)


if __name__ == "__main__":
    import vimba  # type: ignore[import]
    from PySide6.QtWidgets import QApplication
    import sys

    VIMBA_INST = vimba.Vimba.get_instance()
    VIMBA_INST.enable_log(vimba.LOG_CONFIG_INFO_CONSOLE_ONLY)

    app = QApplication(sys.argv)
    window = CameraCaptureWindow()
    window.camera().start()
    window.show()
    app.exec()
    app.quit()
