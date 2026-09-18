from __future__ import annotations

import logging
import sys

_CONFIGURED = False


def configure_logging(console_level: str = "INFO") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    root = logging.getLogger("temuprivacyscreen")
    root.setLevel(logging.DEBUG)
    root.propagate = False

    console_formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
