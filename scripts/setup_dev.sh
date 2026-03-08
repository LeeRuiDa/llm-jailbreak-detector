#!/usr/bin/env bash
set -euo pipefail

VENV_PATH="${1:-.venv}"
PYTHON_BIN="${PYTHON_BIN:-python}"

if [ ! -d "$VENV_PATH" ]; then
  "$PYTHON_BIN" -m venv "$VENV_PATH"
fi

VENV_PYTHON="$VENV_PATH/bin/python"

"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -e '.[lora,eval,dev]'

printf 'Environment ready. Activate with: source %s/bin/activate\n' "$VENV_PATH"
