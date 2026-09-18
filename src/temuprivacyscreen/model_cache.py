from __future__ import annotations

import os
import sys
from pathlib import Path

_CACHE_ENV_VAR = "UNIFACE_CACHE_DIR"
_CACHE_SUBDIR = "uniface-models"


def venv_model_cache_dir() -> Path:
    return Path(sys.prefix) / _CACHE_SUBDIR


def configure_model_cache() -> Path:
    cache_dir = venv_model_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ[_CACHE_ENV_VAR] = str(cache_dir)
    return cache_dir
