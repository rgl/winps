# About

Remote execute a command in a Windows machine using WinRM/WinRS/RDP.

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

Run the calculator in the interactive desktop:

```bash
docker run --rm -i \
    --add-host "$WINPS_HOST:$WINPS_HOST_IP" \
    --env WINPS_USERNAME \
    winps \
    winps \
    execute \
    --host "$WINPS_HOST" \
    --username "$WINPS_USERNAME" \
    --password "$WINPS_PASSWORD" \
    --env WINPS_USERNAME \
    --script - <<'EOF'
$taskName = "winps-$(New-Guid)"
Register-ScheduledTask `
    -TaskName $taskName `
    -Principal (
        New-ScheduledTaskPrincipal `
            -UserId $env:WINPS_USERNAME `
            -LogonType Interactive `
            -RunLevel Highest
    ) `
    -Action (
        New-ScheduledTaskAction `
            -Execute win32calc.exe
    ) `
    | Out-Null
Start-ScheduledTask `
    -TaskName $taskName
Unregister-ScheduledTask `
    -TaskName $taskName `
    -Confirm:$false
EOF
```

Take a screenshoot:

```bash
docker exec winps screenshot /host/screenshot-calculator.png
```

Simulate the `Windows` (aka `Super`) keypress:

```bash
docker exec winps keyboard key Super_L
```

Take a screenshoot:

```bash
docker exec winps screenshot /host/screenshot-keypress.png
```

Logoff all the RDP sessions:

```bash
docker run --rm -i \
    --add-host "$WINPS_HOST:$WINPS_HOST_IP" \
    winps \
    winps \
    execute \
    --host "$WINPS_HOST" \
    --username "$WINPS_USERNAME" \
    --password "$WINPS_PASSWORD" \
    --env WINPS_USERNAME \
    --script - <<'EOF'
query.exe user | ForEach-Object {
    # example query.exe user output:
    #  USERNAME              SESSIONNAME        ID  STATE   IDLE TIME  LOGON TIME
    #  john.doe              rdp-tcp#0           4  Active          9  9/24/2022 12:29 PM
    if ($_ -match '^\s*(?<username>.+?)\s+(?<sessionname>.+?)\s+(?<id>\d+?)\s+') {
        New-Object PSObject -Property @{
            Username = $Matches['username']
            SessionName = $Matches['sessionname']
            SessionId = $Matches['id']
        }
    }
} `
| Where-Object {
    $_.SessionName -like 'rdp-*'
} `
| ForEach-Object {
    Write-Host "Logging off $($_.Username)..."
    logoff.exe $_.SessionId
}
EOF
```
