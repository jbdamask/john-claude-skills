#!/bin/bash
# Setup venv for memory-checkpoint skill

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/.venv"

if [ -d "$VENV_DIR" ]; then
    echo "Venv already exists at $VENV_DIR"
    exit 0
fi

echo "Creating venv at $VENV_DIR..."
python3 -m venv "$VENV_DIR"

echo "Installing fastembed..."
"$VENV_DIR/bin/pip" install fastembed

echo "Setup complete!"
