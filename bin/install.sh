#!/bin/bash

BASEDIR="` dirname $( dirname $( realpath $0 ) ) `"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor"
BIN_DIR="$HOME/.local/bin"

set -e
set -x

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