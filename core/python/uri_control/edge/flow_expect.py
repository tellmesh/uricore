"""Evaluate optional ``expect:`` blocks after ``run_flow`` (UriFlow v1 / lab contracts)."""

from __future__ import annotations

from typing import Any


def _ocr_texts(results: list[dict[str, Any]]) -> list[str]:
    texts: list[str] = []
    for step in results:
        if step.get("skipped") or step.get("type") in {"expect_failed", "expect_passed"}:
            continue
        result = step.get("result") or {}
        if isinstance(result.get("text"), str):
            texts.append(result["text"])
        pipeline = result.get("pipeline")
        if isinstance(pipeline, dict):
            for stage in pipeline.values():
                if isinstance(stage, dict):
                    inner = stage.get("result") if "result" in stage else stage
                    if isinstance(inner, dict) and isinstance(inner.get("text"), str):
                        texts.append(inner["text"])
    return texts


def _vision_confidences(results: list[dict[str, Any]]) -> list[float]:
    out: list[float] = []
    for step in results:
        if step.get("skipped"):
            continue
        result = step.get("result") or {}
        candidates = [result]
        pipeline = result.get("pipeline")
        if isinstance(pipeline, dict):
            for stage in pipeline.values():
                if isinstance(stage, dict):
                    candidates.append(stage.get("result") if "result" in stage else stage)
        for res in candidates:
            if isinstance(res, dict) and {"action", "confidence", "model"} <= res.keys():
                out.append(float(res.get("confidence") or 0.0))
    return out


def _transport_ok(results: list[dict[str, Any]]) -> bool:
    for step in results:
        if step.get("skipped") or step.get("type") in {"expect_failed", "expect_passed"}:
            continue
        if not step.get("ok"):
            return False
    return True


def _required_steps(step_outputs: dict[str, Any], names: list[Any]) -> list[str]:
    failures: list[str] = []
    for raw in names:
        name = str(raw)
        entry = step_outputs.get(name)
        if entry is None:
            failures.append(f"required_steps: missing step {name!r}")
            continue
        if isinstance(entry, dict) and entry.get("ok") is False:
            failures.append(f"required_steps: step {name!r} ok=false")
    return failures


def _nested_result_expect(
    expect_result: dict[str, Any],
    step_outputs: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    for step_id, wanted in expect_result.items():
        if not isinstance(wanted, dict):
            continue
        entry = step_outputs.get(str(step_id))
        if not isinstance(entry, dict):
            failures.append(f"result.{step_id}: step output missing")
            continue
        for key, expected in wanted.items():
            actual = entry.get(key)
            if actual != expected:
                failures.append(f"result.{step_id}.{key}: expected {expected!r}, got {actual!r}")
    return failures


def _ocr_contains(expect: dict[str, Any], results: list[dict[str, Any]]) -> list[str]:
    wanted = expect.get("ocr_contains") or []
    if not wanted:
        return []
    haystack = " \n".join(_ocr_texts(results)).lower()
    return [
        f"ocr_contains: '{needle}' not found in OCR output"
        for needle in wanted
        if str(needle).lower() not in haystack
    ]


def _opened_url_contains(expect: dict[str, Any], results: list[dict[str, Any]]) -> list[str]:
    if "opened_url_contains" not in expect:
        return []
    needle = str(expect["opened_url_contains"]).lower()
    urls: list[str] = []
    for step in results:
        result = step.get("result") or {}
        if isinstance(result.get("url"), str):
            urls.append(result["url"])
        inner = result.get("result")
        if isinstance(inner, dict) and isinstance(inner.get("url"), str):
            urls.append(inner["url"])
    if any(needle in u.lower() for u in urls):
        return []
    return [f"opened_url_contains: '{expect['opened_url_contains']}' not in browser URLs {urls!r}"]


def _min_vision_confidence(expect: dict[str, Any], results: list[dict[str, Any]]) -> list[str]:
    if "min_vision_confidence" not in expect:
        return []
    threshold = float(expect["min_vision_confidence"])
    confidences = _vision_confidences(results)
    best = max(confidences) if confidences else 0.0
    if best >= threshold:
        return []
    return [f"min_vision_confidence: best {best:.2f} < required {threshold:.2f}"]


def evaluate_flow_expect(
    flow: dict[str, Any],
    results: list[dict[str, Any]],
    step_outputs: dict[str, Any],
) -> list[str]:
    """Return human-readable failure messages; empty list means pass."""
    expect = flow.get("expect")
    if not isinstance(expect, dict) or not expect:
        return []

    failures: list[str] = []

    if "transport_ok" in expect:
        want = bool(expect["transport_ok"])
        got = _transport_ok(results)
        if got != want:
            failures.append(f"transport_ok: expected {want}, got {got}")

    if expect.get("required_steps"):
        failures.extend(_required_steps(step_outputs, list(expect["required_steps"])))

    if isinstance(expect.get("result"), dict):
        failures.extend(_nested_result_expect(expect["result"], step_outputs))

    failures.extend(_ocr_contains(expect, results))
    failures.extend(_opened_url_contains(expect, results))
    failures.extend(_min_vision_confidence(expect, results))

    return failures


__all__ = ["evaluate_flow_expect"]
