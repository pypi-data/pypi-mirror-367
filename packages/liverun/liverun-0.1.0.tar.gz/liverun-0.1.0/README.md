# liverun

*A simple CLI tool to run commands on file changes.*

## Installation

```bash
pip install liverun
```

## Usage

```text
usage: liverun [-h] -f FILES [FILES ...] (-c COMMAND | -x EXEC_ARGV [EXEC_ARGV ...]) [-p POLL_INTERVAL] [--no-initial-run] [-v]

A simple CLI tool to run commands on file changes.

options:
  -h, --help            show this help message and exit
  -f FILES [FILES ...], --files FILES [FILES ...]
                        One or more file paths to watch for changes.
  -c COMMAND, --command COMMAND
                        Shell command to execute when a change is detected (runs in the platform shell).
  -x EXEC_ARGV [EXEC_ARGV ...], --exec EXEC_ARGV [EXEC_ARGV ...]
                        Execute the given program/args directly (no shell). Example: --exec python -m pytest -q
  -p POLL_INTERVAL, --poll-interval POLL_INTERVAL
                        Polling interval in seconds (default: 1.0).
  --no-initial-run      Do not run the action immediately at startup (default is to run once).
  -v, --verbose         Enable info-level logging output.
```

### Example

Run a shell command when Python files change:

```bash
liverun -f main.py -c "echo changed at %TIME%" -p 1.0 -v
```
