from __future__ import annotations

import cv2
import numpy as np

from .config import Config
from .logging_setup import get_logger

logger = get_logger(__name__)


class Camera:
    def __init__(self, config: Config) -> None:
        self._config = config
        logger.debug("Opening camera index=%d via AVFoundation", config.camera_index)
        capture = cv2.VideoCapture(config.camera_index, cv2.CAP_AVFOUNDATION)
        if not capture.isOpened():
            raise RuntimeError(
                f"Could not open camera at index {config.camera_index}. "
                "Check System Settings > Privacy & Security > Camera for this terminal/app."
            )

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.frame_width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.frame_height)
        capture.set(cv2.CAP_PROP_FPS, config.target_fps)
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self._capture = capture
        logger.info(
            "Camera ready (%dx%d requested)",
            config.frame_width,
            config.frame_height,
        )

    def read(self) -> np.ndarray:
        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise RuntimeError("Camera read failed; the device may have been disconnected.")
        return frame

    def release(self) -> None:
        logger.debug("Releasing camera")
        self._capture.release()

    def __enter__(self) -> "Camera":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.release()
