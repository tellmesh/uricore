from __future__ import annotations

from typing import Any


def parse_flow_step(step: Any) -> tuple[str, dict[str, Any], str | None]:
    """Normalize one flow step to ``(uri, payload, step_id)``."""
    step_id = None
    if isinstance(step, str):
        return step, {}, None
    if isinstance(step, dict):
        step_id = step.get("id")
        if "uri" in step:
            return str(step["uri"]), dict(step.get("payload") or {}), step_id
        for key, value in step.items():
            if isinstance(key, str) and "://" in key:
                return key, dict(value or {}) if isinstance(value, dict) else {}, step_id
        raise ValueError(f"Invalid flow step (no URI): {step!r}")
    raise ValueError(f"Invalid flow step: {step!r}")


def order_flow_steps(steps: list[Any]) -> list[Any]:
    """Topologically order steps that declare ``after``; preserve file order when acyclic."""
    if not any(isinstance(s, dict) and s.get("after") for s in steps):
        return steps

    ids: dict[str, int] = {}
    for i, step in enumerate(steps):
        if isinstance(step, dict) and step.get("id"):
            ids[str(step["id"])] = i

    n = len(steps)
    incoming = [0] * n
    edges: dict[int, list[int]] = {i: [] for i in range(n)}
    for j, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        after = step.get("after")
        if not after:
            continue
        dep_ids = after if isinstance(after, list) else [after]
        for dep in dep_ids:
            dep_key = str(dep)
            if dep_key not in ids:
                raise ValueError(f"Flow step {step.get('id')!r} depends on unknown step {dep_key!r}")
            i = ids[dep_key]
            edges[i].append(j)
            incoming[j] += 1

    queue = [i for i in range(n) if incoming[i] == 0]
    queue.sort()
    ordered: list[int] = []
    while queue:
        i = queue.pop(0)
        ordered.append(i)
        for j in edges[i]:
            incoming[j] -= 1
            if incoming[j] == 0:
                queue.append(j)
                queue.sort()
    if len(ordered) != n:
        raise ValueError("Flow step graph has a cycle (after: dependencies)")
    return [steps[i] for i in ordered]


# Backward-compatible aliases (tests and external callers).
_parse_flow_step = parse_flow_step
_order_flow_steps = order_flow_steps
