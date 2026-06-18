"""Normalize URI call envelopes across HTTP/MQTT transports."""

from __future__ import annotations

from typing import Any

# Top-level wire fields promoted into context when absent there.
CONTEXT_PROMOTE = frozenset({"request_id", "reply_to", "trace_id", "deadline_ms"})


def normalize_call_envelope(body: dict[str, Any] | None) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Return ``(uri, payload, context)`` with optional wire fields merged into context."""
    req = dict(body or {})
    uri = str(req.get("uri") or "")
    payload = req.get("payload") if isinstance(req.get("payload"), dict) else {}
    context = dict(req.get("context") or {}) if isinstance(req.get("context"), dict) else {}

    for key in CONTEXT_PROMOTE:
        if key in req and req[key] is not None and key not in context:
            context[key] = req[key]

    return uri, payload, context


__all__ = ["CONTEXT_PROMOTE", "normalize_call_envelope"]
