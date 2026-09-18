#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
VENV_PY="$VENV_DIR/bin/python3"

if [ ! -x "$VENV_PY" ]; then
    echo "error: virtual environment not found at $VENV_DIR" >&2
    echo "Run scripts/install.sh first." >&2
    exit 1
fi

exec "$VENV_PY" -m temuprivacyscreen "$@"
