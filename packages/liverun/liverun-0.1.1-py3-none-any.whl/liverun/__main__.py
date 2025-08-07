"""Module entry point to support `python -m liverun`."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
