#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ "$*" == *"--controlpaneltest"* ]]; then

    cd $SCRIPT_DIR/back
    /usr/bin/env "$SCRIPT_DIR/back/gui/release/control_panel_start.py" mainless

else

    "$SCRIPT_DIR/lovr-monadolay.AppImage" "$SCRIPT_DIR/front" &

    if [[ "$*" == *"--dev"* ]]; then
        cd $SCRIPT_DIR/back
        /usr/bin/env "$SCRIPT_DIR/back/gui/release/control_panel_start.py"
    else
        cd $SCRIPT_DIR/back
        /usr/bin/env "$SCRIPT_DIR/back/gui/testing/dpg_gui_start.py"
    fi

fi