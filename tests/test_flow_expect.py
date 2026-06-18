"""Flow expect evaluation (unit tests without full pack runtime)."""

from __future__ import annotations

from uri_control.edge.flow_expect import evaluate_flow_expect


def test_evaluate_transport_ok_and_required_steps():
    flow = {
        "expect": {
            "transport_ok": True,
            "required_steps": ["a", "b"],
        }
    }
    results = [{"ok": True, "uri": "x://a"}, {"ok": True, "uri": "x://b"}]
    step_outputs = {
        "a": {"ok": True},
        "b": {"ok": True},
    }
    assert evaluate_flow_expect(flow, results, step_outputs) == []


def test_evaluate_required_step_missing():
    flow = {"expect": {"required_steps": ["missing"]}}
    failures = evaluate_flow_expect(flow, [], {})
    assert any("missing" in f for f in failures)


def test_evaluate_ocr_contains():
    flow = {"expect": {"ocr_contains": ["OK"]}}
    results = [{"ok": True, "result": {"text": "Start OK Cancel"}}]
    assert evaluate_flow_expect(flow, results, {}) == []
