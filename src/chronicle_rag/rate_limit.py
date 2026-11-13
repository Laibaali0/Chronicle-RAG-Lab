"""Thread-safe, monotonic token bucket for local API rate limiting."""
from threading import Lock
from time import monotonic


class TokenBucket:
    def __init__(self, capacity=30, refill_per_second=1.0, clock=monotonic):
        if capacity <= 0 or refill_per_second <= 0:
            raise ValueError("positive capacity and refill rate required")
        self.capacity = float(capacity)
        self.refill = float(refill_per_second)
        self.tokens = float(capacity)
        self.clock = clock
        self.updated = self.clock()
        self._lock = Lock()

    def allow(self, cost=1):
        if cost <= 0:
            raise ValueError("cost must be positive")
        with self._lock:
            now = self.clock()
            elapsed = max(0.0, now-self.updated)
            self.tokens = min(self.capacity, self.tokens+elapsed*self.refill)
            self.updated = now
            if self.tokens >= cost:
                self.tokens -= cost
                return True
            return False
