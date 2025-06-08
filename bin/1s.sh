#!/bin/bash

set -e

BASEDIR="` dirname $( dirname $( realpath $0 ) ) `"

source "$BASEDIR/env/bin/activate"

PY_SCRIPT="$BASEDIR/bin/1s.py"

QT_QPA_PLATFORM=xcb QDBUS_DEBUG=0 "$BASEDIR/env/bin/python3" $PY_SCRIPT $1
 
