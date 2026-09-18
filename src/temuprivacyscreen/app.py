from __future__ import annotations

import signal
import time
import types

from .brightness import BrightnessGuard, main_display_id
from .camera import Camera
from .config import Config
from .detector import Detector
from .gaze_logic import GazeStateMachine, Transition
from .logging_setup import get_logger
from .preview import PreviewWindow

logger = get_logger(__name__)


class _ShutdownRequested(Exception):
    pass


def _install_signal_handlers() -> None:
    def _handler(signum: int, frame: types.FrameType | None) -> None:
        raise _ShutdownRequested(f"received signal {signum}")

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)


def run(config: Config) -> int:
    logger.info("Starting TemuPrivacyScreen")
    logger.debug("Config: %s", config)

    _install_signal_handlers()

    display_id = main_display_id()
    logger.info("Controlling main display id=%#x", display_id)

    guard = BrightnessGuard(display_id)
    state_machine = GazeStateMachine(config)
    detector = Detector(config)

    min_frame_period = 1.0 / config.target_fps if config.target_fps > 0 else 0.0

    preview = PreviewWindow() if config.preview else None

    try:
        with Camera(config) as camera:
            logger.info("Entering capture loop (target_fps=%.1f)", config.target_fps)
            while True:
                loop_start = time.monotonic()

                frame = camera.read()
                face = detector.detect_primary_face(frame)
                gaze = detector.estimate_gaze(frame, face) if face is not None else None

                transition = state_machine.update(gaze)

                if transition is Transition.HIDE:
                    guard.dim(config.dim_brightness)
                elif transition is Transition.RESTORE:
                    guard.restore()

                if preview is not None:
                    if not preview.show(frame, face, gaze, state_machine.state):
                        raise _ShutdownRequested("preview window closed")

                elapsed = time.monotonic() - loop_start
                remaining = min_frame_period - elapsed
                if remaining > 0:
                    time.sleep(remaining)
                else:
                    logger.debug("Frame took %.1fms, exceeding target period", elapsed * 1000.0)

    except _ShutdownRequested as exc:
        logger.info("Shutting down: %s", exc)
    finally:
        if preview is not None:
            preview.close()
        if guard.dimmed:
            guard.restore()
        logger.info("TemuPrivacyScreen stopped")

    return 0
