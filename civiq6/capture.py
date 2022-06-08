import cv2  # type: ignore[import]
import dataclasses
import enum
import numpy as np
import numpy.typing as npt
import os
from typing import Optional, List
import vimba  # type: ignore[import]
from .camera import VimbaCamera
from .dynqt6 import QtCore


__all__ = [
    "VimbaCaptureSession",
    "ArraySink",
    "VimbaImageCapture",
    "VideoCaptureFormat",
    "VimbaVideoRecorder",
]


VIMBA_LOGGER = vimba.Log.get_instance()


class VimbaCaptureSession(QtCore.QObject):

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
        return self._camera

    def arraySink(self) -> Optional["ArraySink"]:
        return self._arraySink

    def imageCapture(self) -> Optional["VimbaImageCapture"]:
        return self._imageCapture

    def recorder(self) -> Optional["VimbaVideoRecorder"]:
        return self._recorder

    def setCamera(self, camera: Optional[VimbaCamera]):
        old_camera = self.camera()
        if old_camera is not None:
            old_camera._removeCaptureSession()
        self._camera = camera
        if camera is not None:
            camera._setCaptureSession(self)
        self.cameraChanged.emit()

    def setArraySink(self, sink: Optional["ArraySink"]):
        self._arraySink = sink

    def setImageCapture(self, imageCapture: Optional["VimbaImageCapture"]):
        old_cap = self.imageCapture()
        if old_cap is not None:
            old_cap._captureSession = None
        self._imageCapture = imageCapture
        if imageCapture is not None:
            imageCapture._captureSession = self
        self.imageCaptureChanged.emit()

    def setRecorder(self, recorder: Optional["VimbaVideoRecorder"]):
        old_rec = self.recorder()
        if old_rec is not None:
            old_rec._captureSession = None
        self._recorder = recorder
        if recorder is not None:
            recorder._captureSession = self
        self.recorderChanged.emit()

    def setArray(self, array: npt.NDArray[np.uint8]):
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

    arrayChanged = QtCore.Signal(np.ndarray)
    arraySizeChanged = QtCore.Signal(QtCore.QSize)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._array = np.empty((0, 0, 0))
        self._arraySize = QtCore.QSize(-1, -1)

    def array(self) -> npt.NDArray[np.uint8]:
        return self._array

    def arraySize(self) -> QtCore.QSize:
        return self._arraySize

    def setArray(self, array: npt.NDArray[np.uint8]):
        self._array = array
        self.arrayChanged.emit(array)

        oldsize = self.arraySize()
        h, w = array.shape[:2]
        newsize = QtCore.QSize(w, h)
        if oldsize != newsize:
            self._arraySize = newsize
            self.arraySizeChanged.emit(newsize)


class VimbaImageCapture(QtCore.QObject):

    fileFormatChanged = QtCore.Signal()
    imageSaved = QtCore.Signal(int, str)

    class FileFormat(enum.IntEnum):
        JPEG = 1
        PNG = 2

    @classmethod
    def supportedFormats(cls) -> List[FileFormat]:
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
        return self._captureSession

    def fileFormat(self) -> FileFormat:
        return self._fileFormat

    def setFileFormat(self, fileFormat: FileFormat):
        self._fileFormat = fileFormat
        self.fileFormatChanged.emit()

    @QtCore.Slot(str)
    def captureToFile(self, location: str = "") -> int:
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
        if not self._capturing:
            self._image = array


@dataclasses.dataclass(frozen=True)
class VideoCaptureFormat:
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
        self._frameRate = -1.0
        self._resolution = QtCore.QSize(-1, -1)
        self._recorderState = self.StoppedState

        self._writer = None

    def captureSession(self) -> Optional[VimbaCaptureSession]:
        return self._captureSession

    def outputLocation(self) -> QtCore.QUrl:
        return self._outputLocation

    def actualLocation(self) -> QtCore.QUrl:
        return self._actualLocation

    def mediaFormat(self) -> VideoCaptureFormat:
        return self._mediaFormat

    def videoFrameRate(self) -> float:
        return self._frameRate

    def videoResolution(self) -> QtCore.QSize:
        return self._resolution

    def recorderState(self) -> RecorderState:
        return self._recorderState

    def setOutputLocation(self, location: QtCore.QUrl):
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
            if fps < 0:
                fps = camera.cameraDevice().frameRate()
                if fps < 0:
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

            self._writer = cv2.VideoWriter(path, fourcc, fps, size, isColor)
            self._recorderState = self.RecordingState

            self._actualLocation = path
            self.actualLocationChanged.emit()
            self.recorderStateChanged.emit(self.recorderState())
            VIMBA_LOGGER.info(f"Started recording {self.actualLocation()}")
        elif self.recorderState() == self.PausedState:
            self._recorderState = self.RecordingState
            self.recorderStateChanged.emit(self.recorderState())
            VIMBA_LOGGER.info(f"Resumed recording {self.actualLocation()}")

    @QtCore.Slot()
    def pause(self):
        if self.recorderState() == self.RecordingState:
            self._recorderState = self.PausedState
            self.recorderStateChanged.emit(self.recorderState())
            VIMBA_LOGGER.info(f"Paused recording {self.actualLocation()}")

    @QtCore.Slot()
    def stop(self):
        if self.recorderState() != self.StoppedState:
            self._recorderState = self.StoppedState
            self._writer.release()
            self._writer = None
            self.recorderStateChanged.emit(self.recorderState())
            VIMBA_LOGGER.info(f"Finished recording {self.actualLocation()}")

    def _setArray(self, array: npt.NDArray[np.uint8]):
        if self.recorderState() is self.RecordingState:
            self._writer.write(array)
