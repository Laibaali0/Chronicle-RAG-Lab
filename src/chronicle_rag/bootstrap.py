"""Paired bootstrap over query-level differences; toy samples are not significant evidence."""
import numpy as np


def paired_interval(first: list[float], second: list[float], confidence=.95,
                    resamples=1000, seed=42) -> dict:
    a, b = np.asarray(first, dtype=float), np.asarray(second, dtype=float)
    if a.ndim != 1 or b.ndim != 1 or len(a) != len(b) or not len(a):
        raise ValueError("need equal, non-empty 1D score arrays")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("scores must be finite")
    if resamples < 2 or not 0 < confidence < 1:
        raise ValueError("resamples >= 2, confidence in (0,1)")
    difference = a-b
    rng = np.random.default_rng(seed)
    samples = rng.integers(0, len(a), size=(resamples, len(a)))
    means = difference[samples].mean(axis=1)
    low, high = np.quantile(means, [(1-confidence)/2, 1-(1-confidence)/2])
    return {"mean_difference": float(difference.mean()), "ci_low": float(low),
            "ci_high": float(high), "resamples": resamples, "seed": seed,
            "sampling_unit": "query"}
