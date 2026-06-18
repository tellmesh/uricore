"""Tests for call envelope normalization."""

from __future__ import annotations

from uri_control.envelope import normalize_call_envelope


def test_normalize_promotes_wire_fields_into_context():
    uri, payload, context = normalize_call_envelope(
        {
            "uri": "stepper://tic-t249/axis/x/query/status",
            "payload": {},
            "context": {"approved": True},
            "request_id": "r1",
            "trace_id": "t1",
            "deadline_ms": 5000,
        }
    )
    assert uri.endswith("/query/status")
    assert context["request_id"] == "r1"
    assert context["trace_id"] == "t1"
    assert context["deadline_ms"] == 5000
    assert context["approved"] is True
    assert payload == {}
