# About

Remote execute a command in a Windows machine using WinRM/WinRS.

This uses:

* [pypsrp library](https://pypi.org/project/pypsrp/)

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
