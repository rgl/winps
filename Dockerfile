# syntax=docker/dockerfile:1.15

# debian 12 (bookworm).
FROM debian:12-slim

# install dependencies.
RUN <<EOF
#!/bin/bash
set -euxo pipefail
apt-get update
apt-get install -y --no-install-recommends \
    xvfb \
    xauth \
    xdotool \
    freerdp2-x11 \
    scrot \
    iproute2 \
    procps \
    wget \
    python3-pip \
    python3-cryptography \
    python3-openssl
rm -rf /var/lib/apt/lists/*
EOF

# install dependencies.
COPY requirements.txt .
RUN <<EOF
#!/bin/bash
set -euxo pipefail
python3 -m pip install --break-system-packages -r requirements.txt
EOF

# install binaries.
COPY --chmod=0755 screenshot.sh /usr/local/bin/screenshot
COPY --chmod=0755 keyboard.sh /usr/local/bin/keyboard
COPY --chmod=0755 main.py /usr/local/bin/winps
