from __future__ import annotations

import math

import cv2
import numpy as np
from uniface.types import Face, GazeResult

from .gaze_logic import ScreenState

_WINDOW_NAME = "TemuPrivacyScreen Preview"
_VISIBLE_COLOR = (80, 220, 80)
_HIDDEN_COLOR = (60, 60, 230)


class PreviewWindow:
    def __init__(self) -> None:
        cv2.namedWindow(_WINDOW_NAME, cv2.WINDOW_NORMAL)

    def show(
        self,
        frame: np.ndarray,
        face: Face | None,
        gaze: GazeResult | None,
        state: ScreenState,
    ) -> bool:
        annotated = frame.copy()
        color = _HIDDEN_COLOR if state is ScreenState.HIDDEN else _VISIBLE_COLOR

        if face is not None:
            x1, y1, x2, y2 = (int(v) for v in face.bbox[:4])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                annotated,
                f"{face.confidence:.2f}",
                (x1, max(0, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
                cv2.LINE_AA,
            )

            if gaze is not None:
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                length = max(40, (x2 - x1))
                dx = int(-length * math.sin(gaze.yaw))
                dy = int(-length * math.sin(gaze.pitch))
                cv2.arrowedLine(annotated, (cx, cy), (cx + dx, cy + dy), color, 2, tipLength=0.3)

        cv2.imshow(_WINDOW_NAME, annotated)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            return False
        if cv2.getWindowProperty(_WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            return False
        return True

    def close(self) -> None:
        cv2.destroyWindow(_WINDOW_NAME)
