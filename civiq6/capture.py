"""
Capturing with Vimba
====================

:mod:`civiq6.capture` provides interface to acquire the frames from
:class:`VimbaCamera` and to save them.

"""

import cv2  # type: ignore[import]
import dataclasses
import enum
import numpy as np
import numpy.typing as npt
import os
import qimage2ndarray  # type: ignore[import]
from typing import Optional, List
import vimba  # type: ignore[import]
from .camera import VimbaCamera
from .qt_compat import QtCore, QtGui


__all__ = [
    "VimbaCaptureSession",
    "ArraySink",
    "VimbaImageCapture",
    "VideoCaptureFormat",
    "VimbaVideoRecorder",
]


# Monkeypatch qimage2ndarray until new version (> 1.9.0)
# https://github.com/hmeine/qimage2ndarray/issues/29
for name, qimage_format in qimage2ndarray.qimageview_python.FORMATS.items():
    if name in dir(QtGui.QImage.Format):
        qimage_format.code = getattr(QtGui.QImage, name)


VIMBA_LOGGER = vimba.Log.get_instance()


class VimbaCaptureSession(QtCore.QObject):
    """
    Class to acquire the frames from :class:`VimbaCamera`.

    This is the central class that manages capturing of the video from camera.

    You can connect a camera to :class:`VimbaCaptureSession` using
    :meth:`setCamera`. Video frames can be acquired by setting :class:`ArraySink`
    using :meth:`setArraySink`.

    You can capture still images by setting a :class:`VimbaImageCapture` object
    on the capture session, and record video using a :class:`VimbaVideoRecorder`.

    """

    cameraChanged = QtCore.Signal()
    imageCaptureChanged = QtCore.Signal()
    recorderChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._camera = None
        self._arraySink = None
        self._imageCapture = None
        self._recorder = None

    def camera(self) -> Optional[VimbaCamera]:
        """
        The camera used to capture video.

        Set the camera with :meth:`setCamera` to record video or to take images.
        """
        return self._camera

    def arraySink(self) -> Optional["ArraySink"]:
        """
        Object to receive the video frame as numpy array and emit as `QImage`.

        Set the array sink with :meth:`setArraySink` to acquire the frames.
        """
        return self._arraySink

    def imageCapture(self) -> Optional["VimbaImageCapture"]:
        """
        Object to capture still images.

        Set the image capture with :meth:`setImageCapture` to capture images.
        """
        return self._imageCapture

    def recorder(self) -> Optional["VimbaVideoRecorder"]:
        """
        The recorder object used to capture video.

        Set the recorder with :meth:`setRecorder` to capture video.
        """
        return self._recorder

    def setCamera(self, camera: Optional[VimbaCamera]):
        """Set the new camera and emit :attr:`cameraChanged` signal."""
        old_camera = self.camera()
        if old_camera is not None:
            old_camera._removeCaptureSession()
        self._camera = camera
        if camera is not None:
            camera._setCaptureSession(self)
        self.cameraChanged.emit()

    def setArraySink(self, sink: Optional["ArraySink"]):
        """Set the new array sink."""
        self._arraySink = sink

    def setImageCapture(self, imageCapture: Optional["VimbaImageCapture"]):
        """
        Set the new image capture and emit :attr:`imageCaptureChanged` signal.
        """
        old_cap = self.imageCapture()
        if old_cap is not None:
            old_cap._captureSession = None
        self._imageCapture = imageCapture
        if imageCapture is not None:
            imageCapture._captureSession = self
        self.imageCaptureChanged.emit()

    def setRecorder(self, recorder: Optional["VimbaVideoRecorder"]):
        """Set the new recorder and emit :attr:`recorderChanged` signal."""
        old_rec = self.recorder()
        if old_rec is not None:
            old_rec._captureSession = None
        self._recorder = recorder
        if recorder is not None:
            recorder._captureSession = self
        self.recorderChanged.emit()

    def _setArray(self, array: npt.NDArray[np.uint8]):
        """Internal method used by :class:`VimbaCamera` to pass frame array."""
        sink = self.arraySink()
        if sink is not None:
            sink.setArray(array)
        imageCapture = self.imageCapture()
        if imageCapture is not None:
            imageCapture._setArray(array)
        recorder = self.recorder()
        if recorder is not None:
            recorder._setArray(array)


class ArraySink(QtCore.QObject):
    """
    Object to receive the array from :class:`VimbaCaptureSession` and emit as
    `QImage` to :attr:`imagechanged` signal.

    Notes
    =====

    For unknown reason, passing the numpy array through signal-slot greatly
    reduces the thread performance. Therefore it is converted to `QImage` first
    and then emitted.

    """

    imageChanged = QtCore.Signal(QtGui.QImage)
    videoSizeChanged = QtCore.Signal(QtCore.QSize)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._array = np.empty((0, 0, 0))
        self._arraySize = QtCore.QSize(-1, -1)

    def array(self) -> npt.NDArray[np.uint8]:
        """Returns the current array."""
        return self._array

    def arraySize(self) -> QtCore.QSize:
        """Returns the current array size."""
        return self._arraySize

    def setArray(self, array: npt.NDArray[np.uint8]):
        """
        Set :meth:`array` with new array and emit :attr:`imageChanged`. If the
        new array size is different from the size of previously passed array,
        :class:`videoSizeChanged` is emitted.

        This method is called directly by :class:`VimbaCaptureSession`, and runs
        in the same thread with the capture session.
        """
        self._array = array
        if array.size == 0:
            img = QtGui.QImage()
        else:
            img = qimage2ndarray.array2qimage(array)
        self.imageChanged.emit(img)

        oldsize = self.arraySize()
        h, w = array.shape[:2]
        newsize = QtCore.QSize(w, h)
        if oldsize != newsize:
            self._arraySize = newsize
            self.videoSizeChanged.emit(newsize)


class VimbaImageCapture(QtCore.QObject):
    """
    Class to capture still images from the camera.

    This class is a high level images recording class, intended to be used with
    :class:`VimbaCaptureSession`.

    .. code:: python

       camera = VimbaCamera()
       captureSession = VimbaCaptureSession()
       imageCapture = VimbaImageCapture()
       captureSession.setCamera(camera)
       captureSession.setImageCapture(imageCapture)
       camera.start()
       imageCapture.capture()

    """

    fileFormatChanged = QtCore.Signal()
    imageSaved = QtCore.Signal(int, str)

    class FileFormat(enum.IntEnum):
        """Enumerates the image file formats."""

        JPEG = 1
        PNG = 2

    @classmethod
    def supportedFormats(cls) -> List[FileFormat]:
        """Returns the list of supported image file formats."""
        return list(cls.FileFormat)

    @classmethod
    def fileFormatDescription(cls, f: FileFormat) -> str:
        if f == cls.FileFormat.JPEG:
            ret = "JPEG"
        elif f == cls.FileFormat.PNG:
            ret = "PNG"
        else:
            raise TypeError(f"{f} is not valid file format.")
        return ret

    @classmethod
    def fileFormatName(cls, f: FileFormat) -> str:
        if f == cls.FileFormat.JPEG:
            ret = "JPEG"
        elif f == cls.FileFormat.PNG:
            ret = "PNG"
        else:
            raise TypeError(f"{f} is not valid file format.")
        return ret

    @classmethod
    def fileFormatExtension(cls, f: FileFormat) -> str:
        if f == cls.FileFormat.JPEG:
            ret = "jpg"
        elif f == cls.FileFormat.PNG:
            ret = "png"
        else:
            raise TypeError(f"{f} is not valid file format.")
        return ret

    def __init__(self, parent=None):
        super().__init__(parent)
        self._captureSession = None
        self._fileFormat = self.FileFormat.JPEG
        self._id = 0

        self._image = None
        self._capturing = False

    def captureSession(self) -> Optional[VimbaCaptureSession]:
        """
        Returns the capture session that provides the video frames, or `None` if
        not connected to a capture session.

        Use :meth:`VimbaCaptureSession.setImageCapture` to connect the image
        capture to a session.
        """
        return self._captureSession

    def fileFormat(self) -> FileFormat:
        """Image file format that still images will be saved as."""
        return self._fileFormat

    def setFileFormat(self, fileFormat: FileFormat):
        """Set :meth:`fileFormat` and emit :attr:`fileFormatChanged` signal."""
        self._fileFormat = fileFormat
        self.fileFormatChanged.emit()

    @QtCore.Slot(str)
    def captureToFile(self, location: str = "") -> int:
        """
        Capture the image, save it to file, and return id of the captured image.

        *location* is the path to the file without extension. File format and
        extension are determined by :meth:`fileFormat`.

        Captured image id and path are emitted by :attr:`imageSaved` signal.
        """
        if self.captureSession() is None or self._image is None:
            return -1
        self._capturing = True

        path = f"{location}{os.extsep}{self.fileFormatExtension(self.fileFormat())}"
        ret = self._id
        cv2.imwrite(path, self._image)
        self._id += 1
        self.imageSaved.emit(ret, path)
        VIMBA_LOGGER.info("Captured %s" % path)

        self._image = None
        self._capturing = False
        return ret

    def _setArray(self, array: npt.NDArray[np.uint8]):
        """Internal method for :class:`VimbaCaptureSession` to provide frames."""
        if not self._capturing:
            self._image = array


@dataclasses.dataclass(frozen=True)
class VideoCaptureFormat:
    """Wraps video container extension and codec FourCC data."""

    extension: str = ""
    fourcc: str = ""


class VimbaVideoRecorder(QtCore.QObject):
    class RecorderState(enum.IntEnum):
        StoppedState = 1
        RecordingState = 2
        PausedState = 3

    StoppedState = RecorderState.StoppedState
    RecordingState = RecorderState.RecordingState
    PausedState = RecorderState.PausedState

    actualLocationChanged = QtCore.Signal()
    mediaFormatChanged = QtCore.Signal()
    videoFrameRateChanged = QtCore.Signal()
    videoResolutionChanged = QtCore.Signal()
    recorderStateChanged = QtCore.Signal(RecorderState)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._captureSession = None
        self._outputLocation = QtCore.QUrl()
        self._actualLocation = QtCore.QUrl()
        self._mediaFormat = VideoCaptureFormat("mp4", "mp4v")
        self._frameRate = 0.0
        self._resolution = QtCore.QSize()
        self._recorderState = self.StoppedState

        self._writer = None
        self._lock = QtCore.QMutex()

    def captureSession(self) -> Optional[VimbaCaptureSession]:
        """Object which provides frames to be recorded."""
        return self._captureSession

    def outputLocation(self) -> QtCore.QUrl:
        """Destination location to record the video."""
        return self._outputLocation

    def actualLocation(self) -> QtCore.QUrl:
        """
        Actual location of the last recorded video.

        The actual location is set after recording starts.
        """
        return self._actualLocation

    def mediaFormat(self) -> VideoCaptureFormat:
        return self._mediaFormat

    def videoFrameRate(self) -> float:
        """
        Returns the video frame rate.

        Non-positive value indicates that the recorder should use the frame rate
        of the camera device.
        """
        return self._frameRate

    def videoResolution(self) -> QtCore.QSize:
        """
        Returns the video resolution.

        Empty ``QSize`` indicates that the recorder should use the resolution
        of the camera device.
        """
        return self._resolution

    def recorderState(self) -> RecorderState:
        """
        Current state of the media recorder.

        This value changes synchronously during :meth:`record`, :meth:`pause` or
        :meth:`stop` calls.
        """
        return self._recorderState

    def setOutputLocation(self, location: QtCore.QUrl):
        """
        Set :meth:`outputLocation`.

        The location should not include video format.
        """
        self._outputLocation = location

    def setMediaFormat(self, f: VideoCaptureFormat):
        self._mediaFormat = f
        self.mediaFormatChanged.emit()

    def setVideoFrameRate(self, frameRate: float):
        self._frameRate = frameRate
        self.videoFrameRateChanged.emit()

    def setVideoResolution(self, width: int, height: int):
        self._resolution = QtCore.QSize(width, height)
        self.videoResolutionChanged.emit()

    @QtCore.Slot()
    def record(self):
        """
        Start recording.

        While the recorder state is changed immediately to
        :attr:`RecorderState.RecordingState`, recording may start asynchronously.
        """
        if self.recorderState() == self.StoppedState:
            session = self.captureSession()
            if session is None:
                return
            camera = self.captureSession().camera()
            if camera is None:
                return

            mediaFormat = self.mediaFormat()
            ext = mediaFormat.extension
            path = f"{self.outputLocation().toLocalFile()}{os.extsep}{ext}"
            fourcc = cv2.VideoWriter_fourcc(*mediaFormat.fourcc)

            fps = self.videoFrameRate()
            if fps <= 0:
                fps = camera.cameraDevice().frameRate()
                if fps <= 0:
                    return

            size = self.videoResolution().toTuple()
            if any(i <= 0 for i in size):
                size = camera.cameraDevice().resolution().toTuple()
                if any(i <= 0 for i in size):
                    return

            pixelFormat = camera.cameraDevice().pixelFormat()
            if pixelFormat is None:
                return
            elif pixelFormat in [
                vimba.PixelFormat.Mono8,
                vimba.PixelFormat.Mono10,
                vimba.PixelFormat.Mono10p,
                vimba.PixelFormat.Mono12,
                vimba.PixelFormat.Mono12Packed,
                vimba.PixelFormat.Mono12p,
                vimba.PixelFormat.Mono14,
                vimba.PixelFormat.Mono16,
            ]:
                isColor = False
            else:
                isColor = True

            self._lock.lock()
            self._writer = cv2.VideoWriter(path, fourcc, fps, size, isColor)
            self._recorderState = self.RecordingState
            self._lock.unlock()

            self._actualLocation = QtCore.QUrl.fromLocalFile(path)
            self.actualLocationChanged.emit()
            self.recorderStateChanged.emit(self.recorderState())
            VIMBA_LOGGER.info(
                f"Started recording {self.actualLocation().toLocalFile()}"
            )
        elif self.recorderState() == self.PausedState:
            self._recorderState = self.RecordingState
            self.recorderStateChanged.emit(self.recorderState())
            VIMBA_LOGGER.info(
                f"Resumed recording {self.actualLocation().toLocalFile()}"
            )

    @QtCore.Slot()
    def pause(self):
        """
        Pause recording.

        The recorder state is changed to :attr:`RecorderState.PausedState`.
        """
        if self.recorderState() == self.RecordingState:
            self._recorderState = self.PausedState
            self.recorderStateChanged.emit(self.recorderState())
            VIMBA_LOGGER.info(f"Paused recording {self.actualLocation().toLocalFile()}")

    @QtCore.Slot()
    def stop(self):
        """
        Stop recording and save the video.

        The recorder state is changed to :attr:`RecorderState.StoppedState`.
        """
        if self.recorderState() != self.StoppedState:
            self._lock.lock()
            self._recorderState = self.StoppedState
            self._writer.release()
            self._writer = None
            self._lock.unlock()
            self.recorderStateChanged.emit(self.recorderState())
            VIMBA_LOGGER.info(
                f"Finished recording {self.actualLocation().toLocalFile()}"
            )

    def _setArray(self, array: npt.NDArray[np.uint8]):
        """Internal method for :class:`VimbaCaptureSession` to provide frames."""
        self._lock.lock()
        if self.recorderState() is self.RecordingState:
            self._writer.write(array)
        self._lock.unlock()
