#syntax=docker/dockerfile:1.4

# debian 11 (bullseye).
FROM debian:11-slim

# install dependencies.
RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends \
    xvfb \
    xauth \
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
python3 -m pip install -r requirements.txt
EOF

# install binaries.
COPY --chmod=0755 screenshot.sh /usr/local/bin/screenshot
COPY --chmod=0755 main.py /usr/local/bin/winps
