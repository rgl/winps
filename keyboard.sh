#!/bin/bash
set -euo pipefail

export DISPLAY=:99.0
export XAUTHORITY="$(realpath /tmp/xvfb-run.*/Xauthority)"

exec xdotool "$@"
