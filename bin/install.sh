#!/bin/bash

set -e
set -x

BASEDIR="` dirname $( dirname $( realpath $0 ) ) `"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR/128x128/apps"
mkdir -p "$ICON_DIR/512x512/apps"

ln -sf "$BASEDIR/bin/1s.sh" "$BIN_DIR/1s"
ln -sf "$BASEDIR/resources/einsicht.desktop" "$DESKTOP_DIR/einsicht.desktop"
ln -sf "$BASEDIR/resources/einsicht-logo-v1.128.png" "$ICON_DIR/128x128/apps/einsicht.png"
ln -sf "$BASEDIR/resources/einsicht-logo-v1.512.png" "$ICON_DIR/512x512/apps/einsicht.png"

chmod +x "$BIN_DIR/1s"

update-desktop-database "$HOME/.local/share/applications"

(
    ENV_BIN="$BASEDIR/env/bin"
    PYTHON="$ENV_BIN/python3"
    PIP="$ENV_BIN/pip3"
    
    source "$ENV_BIN/activate"
    
    $PYTHON $PIP install systemd systemd-python
)


