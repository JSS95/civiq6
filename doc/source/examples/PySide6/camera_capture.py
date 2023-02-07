from PySide6.QtCore import Signal, Slot, QSize
from PySide6.QtWidgets import QToolBar, QLineEdit, QToolButton, QStyle
from PySide6.QtGui import QIcon
from videorecorder import VideoRecorder
from camera_stream import CameraWindow


class CaptureToolBar(QToolBar):
    captureRequested = Signal(str)
    recordPathChanged = Signal(str)
    recordRequested = Signal(VideoRecorder.RecorderState)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._capturePathLineEdit = QLineEdit()
        self._captureButton = QToolButton()
        self._recordPathLineEdit = QLineEdit()
        self._recordButton = QToolButton()
        self._recorderState = VideoRecorder.RecorderState.StoppedState

        self._capturePathLineEdit.setPlaceholderText("Image capture path")
        self._captureButton.setToolTip("Click to capture image")
        captureActionIcon = QIcon()
        captureActionIcon.addFile("../capture.svg", QSize(24, 24))
        self._captureButton.setIcon(captureActionIcon)

        self._recordPathLineEdit.setPlaceholderText("Video record path")
        self._recordButton.setToolTip("Click to toggle video recording")
        recordActionIcon = QIcon()
        recordActionIcon.addFile("../record.svg", QSize(24, 24))
        self._recordButton.setIcon(recordActionIcon)

        self.addWidget(self._capturePathLineEdit)
        self.addWidget(self._captureButton)
        self.addSeparator()
        self.addWidget(self._recordPathLineEdit)
        self.addWidget(self._recordButton)

        self._captureButton.clicked.connect(self._onCaptureButtonClick)
        self._recordPathLineEdit.editingFinished.connect(self._onRecordPathEdit)
        self._recordButton.clicked.connect(self._onRecordActionClick)

    def _onCaptureButtonClick(self):
        path = self._capturePathLineEdit.text()
        self.captureRequested.emit(path)

    def _onRecordPathEdit(self):
        path = self._recordPathLineEdit.text()
        self.recordPathChanged.emit(path)

    def _onRecordActionClick(self):
        if self._recorderState == VideoRecorder.RecorderState.StoppedState:
            state = VideoRecorder.RecorderState.RecordingState
        else:
            state = VideoRecorder.RecorderState.StoppedState
        self._recorderState = state
        self.recordRequested.emit(state)

    @Slot(VideoRecorder.RecorderState)
    def setRecorderState(self, state: VideoRecorder.RecorderState):
        if state == VideoRecorder.RecorderState.RecordingState:
            self._recordButton.setChecked(True)
            self._recordButton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
            )
        elif state == VideoRecorder.RecorderState.StoppedState:
            self._recordButton.setChecked(False)
            icon = QIcon()
            icon.addFile("../record.svg", QSize(24, 24))
            self._recordButton.setIcon(icon)


class CameraCaptureWindow(CameraWindow):
    def initUI(self):
        super().initUI()

        self._toolBar = CaptureToolBar()
        self.addToolBar(self._toolBar)


if __name__ == "__main__":
    import vimba  # type: ignore[import]
    from PySide6.QtWidgets import QApplication
    import sys

    VIMBA_INST = vimba.Vimba.get_instance()
    VIMBA_INST.enable_log(vimba.LOG_CONFIG_INFO_CONSOLE_ONLY)

    app = QApplication(sys.argv)
    window = CameraCaptureWindow()
    window.show()
    app.exec()
    app.quit()
