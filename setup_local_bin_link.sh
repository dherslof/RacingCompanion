#!/bin/bash

# Description: This script installs Racing-Companion (creates a symlink) in ~/.local/bin, for easy access.
# Usage: Run this script from the repo root directory.

# Author: dherslof

# Fail fast
set -euo pipefail

RC_PATH="$(dirname "$(realpath "$0")")/racing-companion.py"
LINK_NAME="racing-companion"
LOCAL_BIN="$HOME/.local/bin"


# Checks
if [[ ! -x "$RC_PATH" ]]; then
    echo "Error: '$RC_PATH' does not exist or is not executable."
    exit 1
fi

if [[ ! -d "$LOCAL_BIN" ]]; then
    echo "Error: '$LOCAL_BIN' does not exist, unable to continue."
    exit 1
fi

LINK_PATH="$LOCAL_BIN/$LINK_NAME"
if [[ -L "$LINK_PATH" || -e "$LINK_PATH" ]]; then
    echo "Warning: '$LINK_PATH' already exists."
    # Defensive approach, just exit instead of removing and recreating
    exit 1
fi

# Create symlink
ln -s "$RC_PATH" "$LINK_PATH"
echo "Linked '$RC_PATH' → '$LINK_PATH'"

# PATH check
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo "Note: '$LOCAL_BIN' is not in your PATH."
    echo "You can add it with:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

exit 0