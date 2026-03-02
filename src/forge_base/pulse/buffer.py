from __future__ import annotations

from collections import deque
from collections.abc import Callable
import threading
from typing import TYPE_CHECKING

from forge_base.pulse.exceptions import PulseConfigError

if TYPE_CHECKING:
    from forge_base.pulse.basic_collector import ExecutionRecord

_VALID_DROP_POLICIES = frozenset({"oldest", "newest"})


class AsyncBuffer:
    """Thread-safe buffer with sync push and async flush.

    Uses deque + Lock for O(1) push/pop without requiring an active event loop.
    flush() is an async coroutine that swaps the buffer under lock (fast) and
    calls the handler outside the lock (async-friendly).
    """

    __slots__ = ("_max_size", "_drop_policy", "_lock", "_buf", "_drop_count")

    def __init__(self, max_size: int = 10_000, drop_policy: str = "oldest") -> None:
        if max_size < 1:
            raise PulseConfigError(f"max_size must be >= 1, got {max_size}")
        if drop_policy not in _VALID_DROP_POLICIES:
            raise PulseConfigError(
                f"drop_policy must be one of {sorted(_VALID_DROP_POLICIES)}, got {drop_policy!r}"
            )
        self._max_size = max_size
        self._drop_policy = drop_policy
        self._lock = threading.Lock()
        self._buf: deque[ExecutionRecord] = deque()
        self._drop_count = 0

    def push(self, record: ExecutionRecord) -> bool:
        """Add a record to the buffer (sync, thread-safe).

        Returns True if the record was accepted, False if dropped (newest policy).
        When drop_policy is "oldest", the oldest record is evicted to make room.
        """
        with self._lock:
            if len(self._buf) >= self._max_size:
                if self._drop_policy == "oldest":
                    self._buf.popleft()
                    self._drop_count += 1
                    self._buf.append(record)
                    return True
                else:
                    # newest: reject incoming
                    self._drop_count += 1
                    return False
            self._buf.append(record)
            return True

    async def flush(self, handler: Callable[[ExecutionRecord], None]) -> int:
        """Drain the buffer and call handler for each record (async).

        Swaps the buffer under lock (O(1)), then iterates outside the lock.
        Returns the number of records flushed.
        """
        with self._lock:
            batch = self._buf
            self._buf = deque()
        for record in batch:
            handler(record)
        return len(batch)

    @property
    def size(self) -> int:
        """Current number of records in the buffer."""
        with self._lock:
            return len(self._buf)

    @property
    def drop_count(self) -> int:
        """Total number of records dropped since creation."""
        with self._lock:
            return self._drop_count
