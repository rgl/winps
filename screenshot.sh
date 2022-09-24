#!/bin/bash
set -euo pipefail

path="$1"

export DISPLAY=:99.0
export XAUTHORITY="$(realpath /tmp/xvfb-run.*/Xauthority)"

rm -f "$path"

exec scrot "$path"
