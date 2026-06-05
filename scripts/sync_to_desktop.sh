#!/bin/bash
# Copy project into Desktop/FloSpace when workspace path is broken (FloSpace was a file).
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-$HOME/Desktop/FloSpace}"

if [ -f "$DEST" ]; then
  rm "$DEST"
fi
mkdir -p "$DEST"
rsync -a --exclude .venv --exclude node_modules --exclude __pycache__ "$SRC/" "$DEST/"
echo "Synced to $DEST"
