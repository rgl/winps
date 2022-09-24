# About

Remote execute a command in a Windows machine using WinRM/WinRS.

This uses:

* [pypsrp library](https://pypi.org/project/pypsrp/)
* [xfreerdp application](https://www.freerdp.com/)
* [scrot application](https://github.com/resurrecting-open-source-projects/scrot)
* [xdotool application](https://github.com/jordansissel/xdotool)

# Usage

Start the [windows-domain-controller vagrant environment](https://github.com/rgl/windows-domain-controller-vagrant).

Install docker.

Build the `winps` container image:

```bash
docker build -t winps .
```

Set the environment variables:

```bash
export WINPS_HOST='dc.example.com'
export WINPS_HOST_IP='192.168.56.2'
export WINPS_USERNAME='EXAMPLE\john.doe'
export WINPS_PASSWORD='HeyH0Password'
```

Remote execute the `whoami.exe` command:

```bash
docker run --rm -i \
    --add-host "$WINPS_HOST:$WINPS_HOST_IP" \
    winps \
    winps \
    execute \
    --host "$WINPS_HOST" \
    --username "$WINPS_USERNAME" \
    --password "$WINPS_PASSWORD" \
    --script 'whoami.exe /all'
```

Start an headless RDP session:

```bash
docker run --rm -i \
    --name winps \
    --add-host "$WINPS_HOST:$WINPS_HOST_IP" \
    --volume "$PWD:/host:rw" \
    --env WINPS_HOST \
    --env WINPS_USERNAME \
    --env WINPS_PASSWORD \
    winps \
    bash <<'EOF'
set -euo pipefail
xvfb-run \
    "--server-args=-screen 0 1024x768x24" \
    xfreerdp \
        /log-level:WARN \
        /cert:ignore \
        "/v:$WINPS_HOST" \
        "/u:$WINPS_USERNAME" \
        "/p:$WINPS_PASSWORD" \
        /f \
        /dynamic-resolution \
        +credentials-delegation
EOF
```

Open another shell.

Set the environment variables as done initially.

Take a screenshoot:

```bash
docker exec winps screenshot /host/screenshot.png
```

Simulate the `Windows` (aka `Super`) keypress:

```bash
docker exec winps keyboard key Super_L
```

Take a screenshoot:

```bash
docker exec winps screenshot /host/screenshot-keypress.png
```
