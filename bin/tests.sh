#!/bin/bash

set -e

BASEDIR="` dirname $( dirname $( realpath $0 ) ) `"

ENV_DIR="$BASEDIR/env"
ENV_BIN="$ENV_DIR/bin"
ROBOT="$ENV_BIN/robot"
BEHAVIOUR_TEST_DIR="$BASEDIR/test/behaviour"

$ROBOT \
    --outputdir "$BEHAVIOUR_TEST_DIR/var/" \
    $BEHAVIOUR_TEST_DIR/*.robot
