#!/bin/bash
# One-time setup for variant-research skill.
# Creates a venv in the skill directory and installs dependencies.
# Subsequent runs detect the existing venv and exit immediately.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/.venv"
MARKER="$VENV_DIR/.setup_done"

# Skip if already set up
if [ -f "$MARKER" ]; then
    echo "Venv already configured at $VENV_DIR"
    exit 0
fi

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet requests jinja2

# Mark setup as complete
touch "$MARKER"
echo "Setup complete!"
