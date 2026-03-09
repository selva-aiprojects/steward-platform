from __future__ import annotations

import threading
import time
from collections import deque
from typing import Deque, Dict


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._buckets: Dict[str, Deque[float]] = {}

    def allow(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        now = time.time()
        with self._lock:
            bucket = self._buckets.setdefault(key, deque())
            while bucket and now - bucket[0] > window_seconds:
                bucket.popleft()
            if len(bucket) >= max(1, limit):
                return False
            bucket.append(now)
            return True


rate_limiter = InMemoryRateLimiter()

