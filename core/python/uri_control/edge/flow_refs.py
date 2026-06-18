"""Flow step references — ``save_as``, ``${ref}``, ``payload_from``, ``if:``."""

from __future__ import annotations

import re
from typing import Any

_REF_PATTERN = re.compile(r"\$\{([^}]+)\}")
_BOOL_IF = re.compile(r"^([a-zA-Z0-9_]+)\.([a-zA-Z0-9_.]+)\s*==\s*(true|false)$", re.I)
_STRING_IF = re.compile(r"""^([a-zA-Z0-9_]+)\.([a-zA-Z0-9_.]+)\s*==\s*(?:"([^"]*)"|'([^']*)')$""")


def resolve_ref(ref: str, step_outputs: dict[str, Any]) -> Any:
    ref = ref.strip()
    if not ref:
        return None
    if "." not in ref:
        return step_outputs.get(ref)
    step_id, _, field_path = ref.partition(".")
    cur: Any = step_outputs.get(step_id)
    for part in field_path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def interpolate_string(value: str, step_outputs: dict[str, Any]) -> str:
    def repl(match: re.Match[str]) -> str:
        resolved = resolve_ref(match.group(1), step_outputs)
        if resolved is None:
            return match.group(0)
        return str(resolved)

    return _REF_PATTERN.sub(repl, value)


def interpolate_value(value: Any, step_outputs: dict[str, Any]) -> Any:
    if isinstance(value, str):
        stripped = value.strip()
        full = _REF_PATTERN.fullmatch(stripped)
        if full:
            return resolve_ref(full.group(1), step_outputs)
        if "${" in value:
            return interpolate_string(value, step_outputs)
        return value
    if isinstance(value, dict):
        return {k: interpolate_value(v, step_outputs) for k, v in value.items()}
    if isinstance(value, list):
        return [interpolate_value(v, step_outputs) for v in value]
    return value


def _result_payload(step_value: Any) -> dict[str, Any]:
    if isinstance(step_value, dict):
        inner = step_value.get("result")
        if isinstance(inner, dict):
            return dict(inner)
        return dict(step_value)
    return {}


def merge_payload_from(payload: dict[str, Any], step_outputs: dict[str, Any]) -> dict[str, Any]:
    out = dict(payload or {})
    if "payload_from" in out:
        ref = str(out.pop("payload_from"))
        merged = _result_payload(resolve_ref(ref, step_outputs) or {})
        out = {**merged, **out}
    return out


def resolve_step_uri(
    uri: str,
    step: dict[str, Any] | None,
    step_outputs: dict[str, Any],
) -> str:
    if isinstance(step, dict) and step.get("uri_from"):
        ref = str(step["uri_from"])
        src = resolve_ref(ref, step_outputs)
        if isinstance(src, dict):
            candidate = src.get("uri") or (src.get("result") or {}).get("uri")
            if isinstance(candidate, str) and candidate:
                uri = candidate
    resolved = interpolate_value(uri, step_outputs)
    return str(resolved) if resolved is not None else uri


def evaluate_step_if(expr: Any, step_outputs: dict[str, Any]) -> bool:
    if expr is None:
        return True
    text = str(expr).strip()
    if not text:
        return True

    match = _BOOL_IF.match(text)
    if match:
        actual = resolve_ref(f"{match.group(1)}.{match.group(2)}", step_outputs)
        expected = match.group(3).lower() == "true"
        if isinstance(actual, bool):
            return actual == expected
        if actual is None:
            return expected is False
        return str(actual).lower() == str(expected).lower()

    match = _STRING_IF.match(text)
    if match:
        actual = resolve_ref(f"{match.group(1)}.{match.group(2)}", step_outputs)
        expected = match.group(3) if match.group(3) is not None else match.group(4)
        if actual is None:
            return expected in ("", None)
        return str(actual) == str(expected)

    return True


def store_step_output(
    step_outputs: dict[str, Any],
    *,
    key: str,
    call_result: dict[str, Any],
) -> None:
    step_outputs[key] = {
        "ok": call_result.get("ok"),
        "uri": call_result.get("uri"),
        "result": call_result.get("result"),
        "error": call_result.get("error"),
        "operation": call_result.get("operation"),
    }


def seed_flow_inputs(
    flow: dict[str, Any],
    context: dict[str, Any] | None,
    step_outputs: dict[str, Any],
) -> None:
    """Seed ``step_outputs`` from flow ``inputs`` defaults and call ``context`` overrides."""
    inputs_block = flow.get("inputs")
    if not isinstance(inputs_block, dict):
        return
    resolved: dict[str, Any] = {}
    for name, spec in inputs_block.items():
        if isinstance(spec, dict) and "default" in spec:
            resolved[str(name)] = spec["default"]
        else:
            resolved[str(name)] = spec
    ctx = context or {}
    for name in list(resolved):
        if name in ctx:
            resolved[name] = ctx[name]
    payload = ctx.get("payload")
    if isinstance(payload, dict):
        for name in list(resolved):
            if name in payload:
                resolved[name] = payload[name]
    for name, value in resolved.items():
        step_outputs[name] = value


def output_key(step: Any, step_id: str | None, index: int) -> str:
    if isinstance(step, dict) and step.get("save_as"):
        return str(step["save_as"])
    if step_id:
        return step_id
    return f"step_{index}"


__all__ = [
    "evaluate_step_if",
    "interpolate_value",
    "merge_payload_from",
    "output_key",
    "resolve_ref",
    "resolve_step_uri",
    "seed_flow_inputs",
    "store_step_output",
]
