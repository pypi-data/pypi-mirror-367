"""Command-line interface for the liverun tool."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Callable, Sequence, Union

from .file_change_runner import FileChangeRunner
from .log_utils import LOGGER as logger, configure_default_logging


def _build_arg_parser() -> "argparse.ArgumentParser":
    """
    Build the CLI argument parser for the liverun tool.
    """
    parser = argparse.ArgumentParser(
        prog="liverun",
        description="A simple CLI tool to run commands on file changes.",
    )
    parser.add_argument(
        "-f",
        "--files",
        nargs="+",
        required=True,
        help="One or more file paths to watch for changes.",
    )
    cmd_group = parser.add_mutually_exclusive_group(required=True)
    cmd_group.add_argument(
        "-c",
        "--command",
        help=(
            "Shell command to execute when a change is detected "
            "(runs in the platform shell)."
        ),
    )
    cmd_group.add_argument(
        "-x",
        "--exec",
        dest="exec_argv",
        nargs="+",
        help=(
            "Execute the given program/args directly (no shell). "
            "Example: --exec python -m pytest -q"
        ),
    )
    parser.add_argument(
        "-p",
        "--poll-interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds (default: 1.0).",
    )
    parser.add_argument(
        "--no-initial-run",
        action="store_true",
        help="Do not run the action immediately at startup (default is to run once).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable info-level logging output.",
    )
    return parser


def main(argv: "list[str] | None" = None) -> int:
    """
    CLI entry point for liverun.

    Arguments are parsed from argv (or sys.argv if None).
    Returns a POSIX-style exit code (0 = success).
    """
    configure_default_logging()

    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    # Configure module logger level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    files = [Path(p) for p in args.files]

    # Determine the action based on provided options
    action: Union[Callable[[], None], str, Sequence[str]]
    if args.command:
        action = args.command
        if args.verbose:
            logger.info("Action mode: shell string: %r", action)
    else:
        action = list(args.exec_argv)
        if args.verbose:
            logger.info("Action mode: argv list: %r", action)

    if args.verbose:
        logger.info(
            "Watching %d file(s): %r", len(files), [str(p.resolve()) for p in files]
        )

    runner = FileChangeRunner(
        files_to_watch=files,
        action=action,
        loud=args.verbose,
        run_immediately=not args.no_initial_run,
    )
    runner.observe(poll_interval=args.poll_interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
