"""Central operation-policy enforcement in the edge runtime (before the handler)."""

from __future__ import annotations

from uri_control.edge.runtime import Runtime

POLICY_CONFIG = {
    "policy": {"operations": {"stepper.move_relative": {"max": {"steps": 10000}}}},
    "targets": {"tic-t249": {"transport": "local"}},
}


def _runtime(tmp_path):
    rt = Runtime(events_path=tmp_path / "ev.jsonl", config=dict(POLICY_CONFIG))
    rt.register(
        "stepper://{device}/axis/{axis}/command/move-relative",
        "runtime://resolver/stepper.move_relative",
        kind="command",
        operation="stepper.move_relative",
        approval="required",
        side_effects=True,
    )
    return rt


def test_within_limit_executes(tmp_path):
    rt = _runtime(tmp_path)
    res = rt.call(
        "stepper://tic-t249/axis/x/command/move-relative",
        {"steps": 100},
        {"approved": True, "dry_run": True},
    )
    assert res["ok"] is True
    assert res["result"]["runtime"] == "mock"


def test_exceeds_limit_denied_before_handler(tmp_path):
    rt = _runtime(tmp_path)
    res = rt.call(
        "stepper://tic-t249/axis/x/command/move-relative",
        {"steps": 50000},
        {"approved": True, "dry_run": True},
    )
    assert res["ok"] is False
    assert res["type"] == "policy_limit_exceeded"
    assert res["field"] == "steps"
    # the handler never ran -> no mock result leaked through
    assert "result" not in res or res.get("result", {}).get("runtime") != "mock"


def test_limit_enforced_even_on_dry_run(tmp_path):
    # dry-run planning must still be gated by policy.
    rt = _runtime(tmp_path)
    res = rt.call(
        "stepper://tic-t249/axis/x/command/move-relative",
        {"steps": 999999},
        {"approved": True, "dry_run": True},
    )
    assert res["ok"] is False
    assert res["type"] == "policy_limit_exceeded"


def test_approval_still_checked_before_policy(tmp_path):
    # missing approval is denied regardless of payload size.
    rt = _runtime(tmp_path)
    res = rt.call(
        "stepper://tic-t249/axis/x/command/move-relative",
        {"steps": 50000},
        {"approved": False},
    )
    assert res["ok"] is False
    assert res["type"] == "policy_denied"
