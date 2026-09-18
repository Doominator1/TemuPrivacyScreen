from __future__ import annotations

import numpy as np
from uniface import MobileGaze, RetinaFace
from uniface.constants import GazeWeights, RetinaFaceWeights
from uniface.types import Face, GazeResult

from .config import Config
from .logging_setup import get_logger

logger = get_logger(__name__)


class Detector:
    def __init__(self, config: Config) -> None:
        logger.debug("Loading RetinaFace (mnet_025) face detector")
        self._face_detector = RetinaFace(
            model_name=RetinaFaceWeights.MNET_025,
            confidence_threshold=config.detection_confidence,
        )
        logger.debug("Loading MobileGaze (mobileone_s0) gaze estimator")
        self._gaze_estimator = MobileGaze(model_name=GazeWeights.MOBILEONE_S0)
        logger.info("Detector models loaded")

    def detect_primary_face(self, frame: np.ndarray) -> Face | None:
        faces = self._face_detector.detect(frame)
        if not faces:
            return None
        return max(faces, key=lambda face: face.confidence)

    def estimate_gaze(self, frame: np.ndarray, face: Face) -> GazeResult:
        height, width = frame.shape[:2]
        x1, y1, x2, y2 = face.bbox[:4]
        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(width, int(x2))
        y2 = min(height, int(y2))
        if x2 <= x1:
            x2 = min(width, x1 + 1)
        if y2 <= y1:
            y2 = min(height, y1 + 1)
        crop = frame[y1:y2, x1:x2]
        return self._gaze_estimator.estimate(crop)
