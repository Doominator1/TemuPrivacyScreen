from __future__ import annotations

import math
from enum import Enum, auto

from uniface.types import GazeResult

from .config import Config
from .logging_setup import get_logger

logger = get_logger(__name__)


class ScreenState(Enum):
    VISIBLE = auto()
    HIDDEN = auto()


class Transition(Enum):
    NONE = auto()
    HIDE = auto()
    RESTORE = auto()


def is_within_enter_cone(gaze: GazeResult, config: Config) -> bool:
    yaw_deg = abs(math.degrees(gaze.yaw))
    pitch_deg = abs(math.degrees(gaze.pitch))
    return yaw_deg <= config.yaw_enter_deg and pitch_deg <= config.pitch_enter_deg


def is_within_exit_cone(gaze: GazeResult, config: Config) -> bool:
    yaw_deg = abs(math.degrees(gaze.yaw))
    pitch_deg = abs(math.degrees(gaze.pitch))
    return yaw_deg <= config.yaw_exit_deg and pitch_deg <= config.pitch_exit_deg


class GazeStateMachine:
    """Debounced state machine deciding whether the screen should be hidden.

    Uses two-sided hysteresis (a tighter cone to enter HIDDEN, a looser cone to
    leave it) plus consecutive-frame counters, so a single noisy frame near the
    threshold cannot flip the screen back and forth.
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._state = ScreenState.VISIBLE
        self._enter_streak = 0
        self._exit_streak = 0

    @property
    def state(self) -> ScreenState:
        return self._state

    def update(self, gaze: GazeResult | None) -> Transition:
        config = self._config

        if gaze is None:
            looking_for_enter = False
            looking_for_exit = not config.no_face_counts_as_exit
        else:
            looking_for_enter = is_within_enter_cone(gaze, config)
            looking_for_exit = is_within_exit_cone(gaze, config)

        if self._state is ScreenState.VISIBLE:
            self._exit_streak = 0
            if looking_for_enter:
                self._enter_streak += 1
            else:
                self._enter_streak = 0

            logger.debug(
                "state=VISIBLE gaze=%s enter_streak=%d/%d",
                gaze,
                self._enter_streak,
                config.enter_consecutive_frames,
            )

            if self._enter_streak >= config.enter_consecutive_frames:
                self._state = ScreenState.HIDDEN
                self._enter_streak = 0
                return Transition.HIDE
            return Transition.NONE

        # state is HIDDEN
        self._enter_streak = 0
        if looking_for_exit:
            self._exit_streak = 0
        else:
            self._exit_streak += 1

        logger.debug(
            "state=HIDDEN gaze=%s exit_streak=%d/%d",
            gaze,
            self._exit_streak,
            config.exit_consecutive_frames,
        )

        if self._exit_streak >= config.exit_consecutive_frames:
            self._state = ScreenState.VISIBLE
            self._exit_streak = 0
            return Transition.RESTORE
        return Transition.NONE
