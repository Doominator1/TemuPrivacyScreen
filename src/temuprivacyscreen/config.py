from __future__ import annotations

import argparse
from dataclasses import dataclass

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

DETECTION_CONFIDENCE = 0.6

YAW_ENTER_DEG = 20.0
PITCH_ENTER_DEG = 18.0
YAW_EXIT_DEG = 28.0
PITCH_EXIT_DEG = 26.0

ENTER_CONSECUTIVE_FRAMES = 1
EXIT_CONSECUTIVE_FRAMES = 3
NO_FACE_COUNTS_AS_EXIT = True

DIM_BRIGHTNESS = 0.0

CONSOLE_LEVEL = "INFO"

TARGET_FPS = 60.0

PREVIEW = False


@dataclass(frozen=True, slots=True)
class Config:
    camera_index: int = CAMERA_INDEX
    frame_width: int = FRAME_WIDTH
    frame_height: int = FRAME_HEIGHT

    detection_confidence: float = DETECTION_CONFIDENCE

    yaw_enter_deg: float = YAW_ENTER_DEG
    pitch_enter_deg: float = PITCH_ENTER_DEG
    yaw_exit_deg: float = YAW_EXIT_DEG
    pitch_exit_deg: float = PITCH_EXIT_DEG

    enter_consecutive_frames: int = ENTER_CONSECUTIVE_FRAMES
    exit_consecutive_frames: int = EXIT_CONSECUTIVE_FRAMES
    no_face_counts_as_exit: bool = NO_FACE_COUNTS_AS_EXIT

    dim_brightness: float = DIM_BRIGHTNESS

    console_level: str = CONSOLE_LEVEL

    target_fps: float = TARGET_FPS

    preview: bool = PREVIEW


def parse_args(argv: list[str] | None = None) -> Config:
    defaults = Config()
    parser = argparse.ArgumentParser(
        prog="temuprivacyscreen",
        description="Detect when eyes are looking at this screen and dim it on-device.",
    )
    parser.add_argument("--camera-index", type=int, default=defaults.camera_index)
    parser.add_argument("--frame-width", type=int, default=defaults.frame_width)
    parser.add_argument("--frame-height", type=int, default=defaults.frame_height)
    parser.add_argument("--detection-confidence", type=float, default=defaults.detection_confidence)
    parser.add_argument("--yaw-enter-deg", type=float, default=defaults.yaw_enter_deg)
    parser.add_argument("--pitch-enter-deg", type=float, default=defaults.pitch_enter_deg)
    parser.add_argument("--yaw-exit-deg", type=float, default=defaults.yaw_exit_deg)
    parser.add_argument("--pitch-exit-deg", type=float, default=defaults.pitch_exit_deg)
    parser.add_argument("--enter-consecutive-frames", type=int, default=defaults.enter_consecutive_frames)
    parser.add_argument("--exit-consecutive-frames", type=int, default=defaults.exit_consecutive_frames)
    parser.add_argument("--dim-brightness", type=float, default=defaults.dim_brightness)
    parser.add_argument("--console-level", type=str, default=defaults.console_level)
    parser.add_argument("--target-fps", type=float, default=defaults.target_fps)
    parser.add_argument("--preview", action="store_true", default=defaults.preview)
    args = parser.parse_args(argv)

    return Config(
        camera_index=args.camera_index,
        frame_width=args.frame_width,
        frame_height=args.frame_height,
        detection_confidence=args.detection_confidence,
        yaw_enter_deg=args.yaw_enter_deg,
        pitch_enter_deg=args.pitch_enter_deg,
        yaw_exit_deg=args.yaw_exit_deg,
        pitch_exit_deg=args.pitch_exit_deg,
        enter_consecutive_frames=args.enter_consecutive_frames,
        exit_consecutive_frames=args.exit_consecutive_frames,
        dim_brightness=args.dim_brightness,
        console_level=args.console_level,
        target_fps=args.target_fps,
        preview=args.preview,
    )
