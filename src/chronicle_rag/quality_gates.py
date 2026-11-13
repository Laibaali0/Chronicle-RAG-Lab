"""Machine-checkable thresholds for local evaluation regressions."""


def evaluate_gates(report: dict, minimum: dict[str, float]) -> dict:
    summary = report.get("mean", {})
    failures = {}
    for metric, threshold in minimum.items():
        if not 0 <= threshold <= 1:
            raise ValueError("thresholds must be between 0 and 1")
        observed = summary.get(metric)
        if observed is None or observed < threshold:
            failures[metric] = {"minimum": threshold, "observed": observed}
    return {"passed": not failures, "failures": failures,
            "checked": sorted(minimum)}
