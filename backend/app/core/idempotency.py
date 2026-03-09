from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional


class InMemoryIdempotencyStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: Dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            value = self._store.get(key)
            if not value:
                return None
            expires_at, payload = value
            if time.time() > expires_at:
                self._store.pop(key, None)
                return None
            return payload

    def put(self, key: str, payload: Any, ttl_seconds: int) -> None:
        with self._lock:
            self._store[key] = (time.time() + max(1, ttl_seconds), payload)


idempotency_store = InMemoryIdempotencyStore()

