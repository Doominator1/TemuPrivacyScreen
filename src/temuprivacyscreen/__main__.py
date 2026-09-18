from __future__ import annotations

import sys

from .model_cache import configure_model_cache

configure_model_cache()

from .app import run
from .config import parse_args
from .logging_setup import configure_logging


def main() -> None:
    config = parse_args()
    configure_logging(console_level=config.console_level)
    sys.exit(run(config))


if __name__ == "__main__":
    main()
