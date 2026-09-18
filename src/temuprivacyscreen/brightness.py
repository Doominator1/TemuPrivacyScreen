from __future__ import annotations

import ctypes
from ctypes.util import find_library

from .logging_setup import get_logger

logger = get_logger(__name__)

_CORE_GRAPHICS_PATH = "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
_DISPLAY_SERVICES_PATH = (
    "/System/Library/PrivateFrameworks/DisplayServices.framework/DisplayServices"
)
_CORE_DISPLAY_PATH = "/System/Library/Frameworks/CoreDisplay.framework/CoreDisplay"

CGDirectDisplayID = ctypes.c_uint32


class BrightnessUnavailableError(RuntimeError):
    pass


class _Bindings:
    def __init__(self) -> None:
        core_graphics_path = find_library("CoreGraphics") or _CORE_GRAPHICS_PATH
        self._core_graphics = ctypes.CDLL(core_graphics_path)
        self._core_graphics.CGMainDisplayID.restype = CGDirectDisplayID
        self._core_graphics.CGMainDisplayID.argtypes = []

        self._display_services = self._try_load(_DISPLAY_SERVICES_PATH)
        self._core_display = self._try_load(_CORE_DISPLAY_PATH)

        self._ds_get = self._bind(
            self._display_services,
            "DisplayServicesGetBrightness",
            [CGDirectDisplayID, ctypes.POINTER(ctypes.c_float)],
            ctypes.c_int,
        )
        self._ds_set = self._bind(
            self._display_services,
            "DisplayServicesSetBrightness",
            [CGDirectDisplayID, ctypes.c_float],
            ctypes.c_int,
        )
        self._ds_can_change = self._bind(
            self._display_services,
            "DisplayServicesCanChangeBrightness",
            [CGDirectDisplayID],
            ctypes.c_bool,
        )
        self._ds_changed = self._bind(
            self._display_services,
            "DisplayServicesBrightnessChanged",
            [CGDirectDisplayID, ctypes.c_double],
            None,
        )

        self._cd_get = self._bind(
            self._core_display,
            "CoreDisplay_Display_GetUserBrightness",
            [CGDirectDisplayID],
            ctypes.c_double,
        )
        self._cd_set = self._bind(
            self._core_display,
            "CoreDisplay_Display_SetUserBrightness",
            [CGDirectDisplayID, ctypes.c_double],
            None,
        )

        if self._ds_set is None and self._cd_set is None:
            raise BrightnessUnavailableError(
                "Neither DisplayServices nor CoreDisplay exposed a brightness-set "
                "symbol on this system. This macOS version may have removed both "
                "private brightness APIs."
            )

    @staticmethod
    def _try_load(path: str) -> ctypes.CDLL | None:
        try:
            return ctypes.CDLL(path)
        except OSError:
            logger.warning("Could not load framework at %s", path)
            return None

    @staticmethod
    def _bind(
        lib: ctypes.CDLL | None,
        symbol: str,
        argtypes: list,
        restype,
    ):
        if lib is None:
            return None
        try:
            func = getattr(lib, symbol)
        except AttributeError:
            logger.debug("Symbol %s not present in %s", symbol, lib)
            return None
        func.argtypes = argtypes
        func.restype = restype
        return func

    def main_display_id(self) -> int:
        return int(self._core_graphics.CGMainDisplayID())

    def get_brightness(self, display_id: int) -> float:
        if self._ds_get is not None:
            value = ctypes.c_float(0.0)
            status = self._ds_get(display_id, ctypes.byref(value))
            if status == 0:
                return float(value.value)
            logger.debug("DisplayServicesGetBrightness returned status=%d", status)

        if self._cd_get is not None:
            return float(self._cd_get(display_id))

        raise BrightnessUnavailableError("Unable to read brightness from any known API.")

    def set_brightness(self, display_id: int, value: float) -> None:
        value = max(0.0, min(1.0, value))

        if self._ds_set is not None:
            status = self._ds_set(display_id, ctypes.c_float(value))
            if status == 0:
                return
            logger.debug("DisplayServicesSetBrightness returned status=%d", status)

        if self._cd_set is not None:
            if self._ds_can_change is not None and not self._ds_can_change(display_id):
                raise BrightnessUnavailableError(
                    f"Display {display_id:#x} does not support brightness changes."
                )
            self._cd_set(display_id, value)
            if self._ds_changed is not None:
                self._ds_changed(display_id, value)
            return

        raise BrightnessUnavailableError("Unable to set brightness through any known API.")


_bindings: _Bindings | None = None


def _get_bindings() -> _Bindings:
    global _bindings
    if _bindings is None:
        _bindings = _Bindings()
    return _bindings


def main_display_id() -> int:
    return _get_bindings().main_display_id()


def get_brightness(display_id: int) -> float:
    return _get_bindings().get_brightness(display_id)


def set_brightness(display_id: int, value: float) -> None:
    _get_bindings().set_brightness(display_id, value)


class BrightnessGuard:
    """Owns the dim/restore lifecycle for one display.

    Tracks the last known "real" brightness so a restore always returns to the
    value the user had set, even if dim() is called more than once in a row.
    """

    def __init__(self, display_id: int) -> None:
        self._display_id = display_id
        self._saved_brightness: float | None = None
        self._dimmed = False

    @property
    def dimmed(self) -> bool:
        return self._dimmed

    def dim(self, target: float) -> None:
        if not self._dimmed:
            self._saved_brightness = get_brightness(self._display_id)
            logger.debug("Saved current brightness=%.4f before dimming", self._saved_brightness)
        set_brightness(self._display_id, target)
        self._dimmed = True
        logger.info("Screen dimmed to %.4f", target)

    def restore(self) -> None:
        if self._saved_brightness is None:
            logger.warning("Restore requested with no saved brightness; leaving as-is.")
            self._dimmed = False
            return
        set_brightness(self._display_id, self._saved_brightness)
        logger.info("Screen brightness restored to %.4f", self._saved_brightness)
        self._dimmed = False
