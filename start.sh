#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

"$SCRIPT_DIR/lovr-x86_64.AppImage" "$SCRIPT_DIR/front" &

if [[ "$*" == *"--dev"* ]]; then
    /usr/bin/env python3 "$SCRIPT_DIR/back/main.py"
else
    /usr/bin/env python3 "$SCRIPT_DIR/back/dpg_gui_start.py"
fi
