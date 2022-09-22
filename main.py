#!/usr/bin/python3
# Developed by Rui Lopes (ruilopes.com). Released under the MIT license.
import argparse
import base64
import logging
import os
import sys
import textwrap
import typing
from pypsrp.client import WSMan, Client
from pypsrp.shell import WinRS, Process, SignalCode, CommandState
from pypsrp._utils import to_unicode

def split_lines(buffer, encoding):
    lines = []
    for line in to_unicode(buffer, encoding).splitlines(True):
        if line[-1] != '\r' and line[-1] != '\n':
            return line.encode(encoding), lines
        lines.append(line.rstrip())
    return b'', lines

def execute_process(conn: WSMan, env: typing.List[str], cmd: str, args: typing.List[str]):
    encoding = '437'
    environment = {}
    for e in env:
        parts = e.split('=', 2)
        key = parts[0]
        value = parts[1] if len(parts) > 1 else os.getenv(key, '')
        environment[key] = value
    if len(environment) == 0:
        environment = None
    with WinRS(conn, environment=environment, no_profile=False) as shell:
        process = Process(shell, cmd, args, no_shell=True)
        process.begin_invoke()
        while not process.state == CommandState.DONE:
            process.poll_invoke()
            process.stdout, stdout = split_lines(process.stdout, encoding)
            for line in stdout:
                print(line)
        process.end_invoke()
        process.signal(SignalCode.CTRL_C)
        exit_code = process.rc if process.rc is not None else -1
        stdout = to_unicode(process.stdout, encoding)
        stderr = Client.sanitise_clixml(to_unicode(process.stderr, encoding))
        if stdout:
            print(stdout)
        if stderr:
            sys.stdout.flush()
            print(stderr, file=sys.stderr)
        return exit_code

def execute_main(args):
    script = sys.stdin.read() if args.script == '-' else args.script
    with WSMan(
            server=args.host,
            port=args.port,
            ssl=args.ssl,
            auth=args.auth,
            encryption=args.encryption,
            username=args.username,
            password=args.password) as conn:
        return execute_process(conn, args.env, "PowerShell.exe", [
            "-NoLogo",
            "-NonInteractive",
            "-ExecutionPolicy", "Bypass",
            "-EncodedCommand",
            base64.b64encode(script.encode('utf-16le')).decode('ascii')])

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            remote execute a powershell command on a windows machine using winrm/psrp.
            example:
            %(prog)s -v execute
            '''))
    parser.add_argument(
        '--verbose',
        '-v',
        default=0,
        action='count',
        help='verbosity level. specify multiple to increase logging.')
    subparsers = parser.add_subparsers(help='sub-command help')
    execute_parser = subparsers.add_parser('execute', help='execute remote powershell script')
    execute_parser.add_argument(
        '--host',
        default='windows.example.com',
        help='host.')
    execute_parser.add_argument(
        '--port',
        type=int,
        default=5985,
        help='port.')
    execute_parser.add_argument(
        '--ssl',
        type=bool,
        default=False,
        help='ssl.')
    execute_parser.add_argument(
        '--auth',
        default='credssp',
        help='auth.')
    execute_parser.add_argument(
        '--encryption',
        default='never',
        help='encryption.')
    execute_parser.add_argument(
        '--username',
        default='vagrant',
        help='username.')
    execute_parser.add_argument(
        '--password',
        default='vagrant',
        help='password.')
    execute_parser.add_argument(
        '--env',
        action='append',
        default=[],
        help='environment variables.')
    execute_parser.add_argument(
        '--script',
        default=textwrap.dedent('''\
            $FormatEnumerationLimit = -1

            function Write-Title($title) {
                Write-Output "`n#`n# $title`n#`n"
            }

            Write-Title 'User rights'
            whoami /all

            Write-Title 'UAC remote settings'
            # dump the UAC remote settings.
            # 0=This value builds a filtered token. It's the default value. The administrator credentials are removed.
            # 1=This value builds an elevated token.
            # see https://learn.microsoft.com/en-US/troubleshoot/windows-server/windows-security/user-account-control-and-remote-restriction
            $localAccountTokenFilterPolicy = (
                    Get-ItemProperty `
                        HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System `
                        -Name LocalAccountTokenFilterPolicy
                ).LocalAccountTokenFilterPolicy
            Write-Output "LocalAccountTokenFilterPolicy=$localAccountTokenFilterPolicy"

            Write-Title 'Environment variables'
            dir env: `
                | Sort-Object -Property Name `
                | Format-Table -AutoSize `
                | Out-String -Stream -Width ([int]::MaxValue) `
                | ForEach-Object {$_.TrimEnd()}

            # show that we can stream lines in realtime.
            Write-Title 'Slowly write lines'
            for ($i = 3; $i -gt 0; --$i) {
                Write-Output "T-$i"
                Start-Sleep -Seconds 1
            }

            # # throw an error to see how they appear.
            # Write-Title 'Throw error'
            # throw "ops"
            '''),
        help='powershell script to execute or - to read it from stdin.')
    execute_parser.set_defaults(sub_command=execute_main)
    args = parser.parse_args()

    LOGGING_FORMAT = '%(asctime)-15s %(levelname)s %(name)s: %(message)s'
    if args.verbose >= 3:
        logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT)
        from http.client import HTTPConnection
        HTTPConnection.debuglevel = 1
    elif args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT)
    elif args.verbose >= 1:
        logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)

    return args.sub_command(args)

sys.exit(main())
