"""Small bounded in-memory LRU cache for repeat read queries."""
from collections import OrderedDict
from threading import RLock


class LRUCache:
    def __init__(self, capacity=128):
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._items = OrderedDict()
        self._lock = RLock()

    def get(self, key):
        with self._lock:
            if key not in self._items:
                return None
            self._items.move_to_end(key)
            return self._items[key]

    def put(self, key, value):
        with self._lock:
            self._items[key] = value
            self._items.move_to_end(key)
            if len(self._items) > self.capacity:
                self._items.popitem(last=False)

    def clear(self):
        with self._lock:
            self._items.clear()
