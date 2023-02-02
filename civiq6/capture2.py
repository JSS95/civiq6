import vimba  # type: ignore[import]
from .qt_compat import QtCore, QtMultimedia, get_frame_data
from .camera2 import VimbaCamera2
from typing import Optional, Protocol


__all__ = [
    "VimbaCaptureSession2",
]


COMPATIBLE_FORMATS = {
    vimba.PixelFormat.Mono8: QtMultimedia.QVideoFrameFormat.PixelFormat.Format_Y8,
    vimba.PixelFormat.Mono16: QtMultimedia.QVideoFrameFormat.PixelFormat.Format_Y16,
}


class VimbaCaptureSession2(QtCore.QObject):
    cameraChanged = QtCore.Signal()
    imageCaptureChanged = QtCore.Signal()
    videoOutputChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._camera = None
        self._imageCapture = None
        self._videoSink = None
        self._videoOutput = None

    def camera(self) -> Optional[VimbaCamera2]:
        return self._camera

    def setCamera(self, camera: Optional[VimbaCamera2]):
        old_camera = self.camera()
        if old_camera is not None:
            old_camera._setCaptureSession(None)
        self._camera = camera
        if camera is not None:
            camera._setCaptureSession(self)
        self.cameraChanged.emit()

    def _setFrame(self, frame: vimba.Frame):
        byte_data = bytes(frame.get_buffer())

        imageCapture = self._imageCapture
        if imageCapture is not None:
            imageCapture._setFrameBytes(byte_data)

        videoSink = self._videoSink
        if videoSink is not None:
            # convert vimba frame to QVideoFrame
            pixelFormat = COMPATIBLE_FORMATS.get(
                frame.get_pixel_format(),
                QtMultimedia.QVideoFrameFormat.PixelFormat.Format_Invalid,
            )
            w, h = frame.get_width(), frame.get_height()
            frameFormat = QtMultimedia.QVideoFrameFormat(
                QtCore.QSize(w, h),
                pixelFormat,
            )
            videoFrame = QtMultimedia.QVideoFrame(frameFormat)
            if pixelFormat != QtMultimedia.QVideoFrameFormat.PixelFormat.Format_Invalid:
                videoFrame.map(QtMultimedia.QVideoFrame.MapMode.WriteOnly)
                get_frame_data(videoFrame)[:] = byte_data
                videoFrame.unmap()  # save the modified memory
            # set constructed QVideoFrame to video sink
            videoSink.setVideoFrame(videoFrame)

    def imageCapture(self) -> Optional["ImageCaptureProtocol"]:
        return self._imageCapture

    def setImageCapture(self, imageCapture: Optional["ImageCaptureProtocol"]):
        old_capture = self._imageCapture
        if old_capture is not None:
            old_capture._setCaptureSession(None)
        self._imageCapture = imageCapture
        if imageCapture is not None:
            imageCapture._setCaptureSession(self)
        self.imageCaptureChanged.emit()

    def videoSink(self) -> Optional[QtMultimedia.QVideoSink]:
        return self._videoSink

    def videoOutput(self) -> Optional[QtCore.QObject]:
        return self._videoOutput

    def setVideoSink(self, videoSink: Optional[QtMultimedia.QVideoSink]):
        self._videoSink = videoSink

    def setVideoOutput(self, videoOutput: Optional[QtCore.QObject]):
        self._videoOutput = videoOutput
        if videoOutput is None:
            self._videoSink = None
        elif hasattr(videoOutput, "videoSink"):
            self._videoSink = videoOutput.videoSink()
        else:
            self._videoSink = None
        self.videoOutputChanged.emit()


class ImageCaptureProtocol(Protocol):
    def _setCaptureSession(self, captureSession: VimbaCaptureSession2):
        ...

    def _setFrameBytes(self, frameBytes: bytes):
        ...
