#!/bin/bash

set -x
set -e

BASEDIR="` dirname $( dirname $( realpath $0 ) ) `"
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/einsicht.desktop"

if [ ! -f "$DESKTOP_FILE" ]; then
    $BASEDIR/bin/install.sh
fi

MIMETYPES=$(grep -Po '^MimeType=\K.*' "$DESKTOP_FILE" | tr ';' ' ')

for MIMETYPE in $MIMETYPES; do
    xdg-mime default "$DESKTOP_FILE" "$MIMETYPE"
done

update-desktop-database "$HOME/.local/share/applications"

