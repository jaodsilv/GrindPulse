"""Cross-platform exclusive file-lock primitive.

Exposes a single public context manager: file_lock(path). Creates and holds
an advisory lock on a sibling .lock file for the duration of the `with` block.

Usage:
    from lib.file_lock import file_lock

    with file_lock(some_path):
        # read-modify-write some_path safely
"""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager

_IS_WINDOWS = sys.platform.startswith("win")

if _IS_WINDOWS:
    import msvcrt  # type: ignore[import-not-found]
else:
    import fcntl  # type: ignore[import-not-found]


@contextmanager
def file_lock(path: str) -> Iterator[None]:
    """Acquire an exclusive advisory lock on the sibling .lock file.

    The lock file is a sibling of `path` with a `.lock` extension.
    Blocks until acquired (30-second deadline, then raises OSError).
    """
    lock_path = f"{path}.lock"
    os.makedirs(os.path.dirname(lock_path) or ".", exist_ok=True)
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        if os.fstat(fd).st_size == 0:
            os.write(fd, b"0")
            os.fsync(fd)
            os.lseek(fd, 0, os.SEEK_SET)

        deadline = time.monotonic() + 30.0
        while True:
            try:
                if _IS_WINDOWS:
                    msvcrt.locking(fd, msvcrt.LK_LOCK, 1)  # pyright: ignore[reportPossiblyUnbound]
                else:
                    fcntl.flock(fd, fcntl.LOCK_EX)  # pyright: ignore[reportPossiblyUnbound, reportAttributeAccessIssue]
                break
            except OSError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(0.05)

        try:
            yield
        finally:
            try:
                if _IS_WINDOWS:
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)  # pyright: ignore[reportPossiblyUnbound]
                else:
                    fcntl.flock(fd, fcntl.LOCK_UN)  # pyright: ignore[reportPossiblyUnbound, reportAttributeAccessIssue]
            except OSError:
                pass
    finally:
        os.close(fd)
