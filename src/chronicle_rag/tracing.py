"""Minimal request-duration recorder without external observability services."""
from contextlib import contextmanager
from time import perf_counter


class Timings:
    def __init__(self):
        self.measured = {}

    @contextmanager
    def record(self, stage: str):
        start = perf_counter()
        try:
            yield
        finally:
            self.measured[stage] = round((perf_counter()-start)*1000, 3)
