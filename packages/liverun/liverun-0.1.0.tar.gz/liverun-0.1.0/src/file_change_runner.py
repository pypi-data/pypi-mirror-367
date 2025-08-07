import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterable, Sequence, Tuple, Union

from .logging import LOGGER as logger


class FileChangeRunner:
    """
    Generic file watcher that runs a command/callback when any watched file changes.

    Requirements:
      - Accept any number of files to watch.
      - Run a command or callable whenever any file changes its last modified date.
      - No legacy or PDF-specific behavior.
    """

    def __init__(
        self,
        files_to_watch: Iterable[Union[str, Path]],
        action: Union[Callable[[], None], str, Sequence[str]],
        *,
        loud: bool = False,
        run_immediately: bool = True,
    ) -> None:
        """
        Initialize the FileChangeRunner.

        Args:
            files_to_watch: Iterable of file paths (str or Path) to watch.
            action: What to run on change:
                - Callable with no arguments
                - Shell command string
                - Sequence command argv (e.g. ["bash", "-lc", "make build"])
            loud: When True, emits info logs with timestamps.
            run_immediately: If True, run action once before starting to watch.
        """
        watched: set[Path] = set()
        for file_path in files_to_watch:
            # Use resolve() for normalized absolute paths across OSes.
            watched.add(Path(file_path).resolve())
        if not watched:
            raise ValueError("files_to_watch cannot be empty.")

        self.watched_files: Tuple[Path, ...] = tuple(sorted(watched))
        # Store last modified times as integers (nanoseconds when available) for precision.
        self._last_modified_map: Dict[Path, int] = {}
        self._action: Union[Callable[[], None], str, Sequence[str]] = action
        self.loud: bool = loud
        self.run_immediately: bool = run_immediately

    def get_last_modified_date(self, file_path: Union[str, Path]) -> int:
        """
        Get the last modified timestamp of a file as an integer.

        Returns:
            Integer nanoseconds since the epoch when available, otherwise seconds coerced to int.
        """
        path = Path(file_path)
        stat = path.stat()
        # Prefer highest precision when available.
        mtime_ns = getattr(stat, "st_mtime_ns", None)
        if mtime_ns is not None:
            return int(mtime_ns)
        # Fallback: seconds to integer. This is less precise but cross-platform safe.
        return int(stat.st_mtime)

    def _run_action(self) -> None:
        """
        Execute the configured action:
          - If callable, call it.
          - If string, run via shell.
          - If sequence[str], run as argv.
        """
        try:
            return_code: Union[int, None] = None
            if callable(self._action):
                self._action()
                return_code = 0
            elif isinstance(self._action, str):
                # shell=True uses OS default shell: cmd.exe on Windows, /bin/sh on POSIX.
                completed = subprocess.run(  # noqa: S603
                    self._action,
                    shell=True,  # noqa: S602
                    check=False,
                )
                return_code = getattr(completed, "returncode", None)
            else:
                argv = list(self._action)
                if not argv:
                    raise ValueError("Empty command argv.")
                completed = subprocess.run(argv, shell=False, check=False)
                return_code = getattr(completed, "returncode", None)

            if self.loud:
                logger.info(
                    "- Action executed at %s (returncode=%s)",
                    datetime.now(),
                    return_code,
                )
        except Exception:  # pylint: disable=broad-exception-caught
            # Log and continue watching instead of crashing.
            logger.exception("Error while executing action")

    def _snapshot_mtimes(self) -> None:
        for path in self.watched_files:
            try:
                self._last_modified_map[path] = self.get_last_modified_date(path)
            except FileNotFoundError:
                # If a file is temporarily missing, treat as 0 to detect appearance later
                self._last_modified_map[path] = 0

    def _detect_change(self) -> bool:
        """
        Returns True if any watched file changed since last snapshot.
        """
        for path in self.watched_files:
            try:
                current = self.get_last_modified_date(path)
            except FileNotFoundError:
                current = 0
            previous = self._last_modified_map.get(path)
            if previous is None or current != previous:
                return True
        return False

    def observe(self, poll_interval: float = 1.0) -> None:
        """
        Observe watched files and run the action when any file changes.

        Long-running action policy (serialized with coalescing):
        - While an action run is in progress, additional file changes are
          coalesced into a single pending run.
        - When the current run completes, if a change occurred during execution,
          exactly one additional run is performed.
        - This prevents overlapping executions and avoids thrashing while
          ensuring the latest state is processed.
        """
        if self.run_immediately:
            self._run_action()
        self._snapshot_mtimes()

        try:
            while True:
                # Sleep/poll boundary to avoid busy-waiting
                time.sleep(poll_interval)

                # If any change since last snapshot, run once
                if self._detect_change():
                    self._run_action()
                    # Snapshot after the run to the latest state
                    self._snapshot_mtimes()

                    # Coalesced single rerun: if further changes happened during
                    # the run, run exactly once more
                    if self._detect_change():
                        self._run_action()
                        self._snapshot_mtimes()
        except KeyboardInterrupt:
            if self.loud:
                logger.info("Interrupted by user.")
