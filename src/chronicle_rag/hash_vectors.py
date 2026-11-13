"""Feature-hashing baseline (NOT neural embeddings)."""
import hashlib
import numpy as np
from .tokenize import tokens


def vector(text: str, dimensions: int = 256) -> np.ndarray:
    if not 8 <= dimensions <= 16384:
        raise ValueError("dimensions must be in [8, 16384]")
    output = np.zeros(dimensions, dtype=np.float32)
    for term in tokens(text):
        digest = hashlib.blake2b(term.encode(), digest_size=8).digest()
        value = int.from_bytes(digest, "big")
        sign = 1 if value & 1 else -1
        output[(value >> 1) % dimensions] += sign
    length = float(np.linalg.norm(output))
    return output / length if length else output


def cosine_scores(query: str, rows: list[str], dimensions: int = 256) -> list[float]:
    q = vector(query, dimensions)
    return [float(q @ vector(row, dimensions)) for row in rows]
