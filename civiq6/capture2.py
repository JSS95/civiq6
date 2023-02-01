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


def vimbaFrame2VideoFrame(frame: vimba.Frame) -> QtMultimedia.QVideoFrame:
    pixelFormat = COMPATIBLE_FORMATS.get(
        frame.get_pixel_format(),
        QtMultimedia.QVideoFrameFormat.PixelFormat.Format_Invalid,
    )
    w, h = frame.get_width(), frame.get_height()
    frameFormat = QtMultimedia.QVideoFrameFormat(QtCore.QSize(w, h), pixelFormat)
    videoFrame = QtMultimedia.QVideoFrame(frameFormat)

    if pixelFormat != QtMultimedia.QVideoFrameFormat.PixelFormat.Format_Invalid:
        videoFrame.map(QtMultimedia.QVideoFrame.MapMode.WriteOnly)
        get_frame_data(videoFrame)[:] = bytes(frame.get_buffer())
        videoFrame.unmap()  # save the modified memory
    return videoFrame


class VideoOutputProtocol(Protocol):
    # TODO: remove this protocol and just use hasattr(qobj, "videoSink")
    def videoSink(self) -> Optional[QtMultimedia.QVideoSink]:
        ...


class VimbaCaptureSession2(QtCore.QObject):
    cameraChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._camera = None
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
        videoFrame = vimbaFrame2VideoFrame(frame)
        videoSink = self._videoSink
        if videoSink is not None:
            videoSink.setVideoFrame(videoFrame)

    def videoSink(self) -> Optional[QtMultimedia.QVideoSink]:
        return self._videoSink

    def videoOutput(self) -> Optional[VideoOutputProtocol]:
        return self._videoOutput

    def setVideoSink(self, videoSink: Optional[QtMultimedia.QVideoSink]):
        self._videoSink = videoSink

    def setVideoOutput(self, videoOutput: Optional[VideoOutputProtocol]):
        self._videoOutput = videoOutput
        if videoOutput is None:
            self._videoSink = None
        else:
            self._videoSink = videoOutput.videoSink()
