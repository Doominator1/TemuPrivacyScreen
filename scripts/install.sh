#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "error: '$PYTHON_BIN' not found on PATH." >&2
    echo "Install Python 3.10+ (Xcode Command Line Tools or python.org) and re-run." >&2
    exit 1
fi

PYTHON_VERSION="$("$PYTHON_BIN" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
echo "==> Using $PYTHON_BIN (Python $PYTHON_VERSION)"

echo "==> Creating virtual environment at $VENV_DIR"
"$PYTHON_BIN" -m venv "$VENV_DIR"

VENV_PY="$VENV_DIR/bin/python3"

echo "==> Upgrading pip/setuptools/wheel inside the venv"
"$VENV_PY" -m pip install --upgrade pip setuptools wheel

echo "==> Installing TemuPrivacyScreen and its dependencies into the venv"
"$VENV_PY" -m pip install -e "$ROOT_DIR"

echo "==> Pre-downloading on-device models into the venv (one-time, verified by SHA-256)"
"$VENV_PY" "$SCRIPT_DIR/warm_models.py"

echo "==> Install complete."
echo "Everything (interpreter, packages, and models) now lives under: $VENV_DIR"
echo "Run scripts/run.sh to start TemuPrivacyScreen."
