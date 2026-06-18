"""Tests for the built-in ``runtime://`` resolver-bound handler."""

from __future__ import annotations

import pytest

from uri_control.edge.runtime import Runtime
from uri_control.errors import HandlerLoadError
from uri_control.handlers import load_handler
from uri_control.runtime_handlers import load_runtime_handler, parse_runtime_handler


def test_parse_runtime_handler():
    assert parse_runtime_handler("runtime://resolver/stepper.move_relative") == (
        "resolver",
        "stepper.move_relative",
    )


def test_parse_runtime_handler_rejects_missing_operation():
    with pytest.raises(HandlerLoadError):
        parse_runtime_handler("runtime://resolver")


def test_load_handler_dispatches_runtime_scheme():
    # Previously raised "Unsupported handler scheme 'runtime'".
    handler = load_handler("runtime://resolver/stepper.status")
    assert callable(handler)


def test_runtime_handler_dry_run_is_mock():
    handler = load_runtime_handler("runtime://resolver/stepper.move_relative")
    res = handler({"steps": 100}, {"dry_run": True, "uri": "stepper://tic-t249/axis/x/command/move-relative"})
    assert res["runtime"] == "mock"
    assert res["executed"] is False
    assert res["operation"] == "stepper.move_relative"
    assert res["payload"] == {"steps": 100}


def test_runtime_handler_mock_environment_is_mock():
    handler = load_runtime_handler("runtime://resolver/stepper.status")
    res = handler({}, {"environment": "mock", "uri": "stepper://tic-t249/axis/x/query/status"})
    assert res["runtime"] == "mock"


def test_runtime_handler_real_without_binding_errors_cleanly():
    handler = load_runtime_handler("runtime://resolver/stepper.move_relative")
    res = handler({"steps": 100}, {"environment": "real", "uri": "stepper://tic-t249/axis/x/command/move-relative"})
    assert res["ok"] is False
    assert res["type"] == "no_runtime_binding"
    assert "resolver target" in res["error"]


def test_runtime_handler_via_runtime_call_mock(tmp_path):
    rt = Runtime(events_path=tmp_path / "ev.jsonl")
    rt.register("stepper://{device}/axis/{axis}/query/status", "runtime://resolver/stepper.status", kind="query")
    res = rt.call("stepper://tic-t249/axis/x/query/status", {}, {"dry_run": True})
    assert res["ok"] is True
    assert res["result"]["runtime"] == "mock"


def test_runtime_handler_resolver_transport_wins_over_local(tmp_path):
    # When a resolver target delegates the URI over a transport, the runtime://
    # handler is never reached; an unconfigured remote surfaces a transport error,
    # not a mock — proving delegation happens before handler load.
    rt = Runtime(
        events_path=tmp_path / "ev.jsonl",
        config={"targets": {"tic-t249": {"transport": "mqtt", "endpoint": "uritic/tic-t249/call"}}},
    )
    rt.register("stepper://{device}/axis/{axis}/query/status", "runtime://resolver/stepper.status", kind="query")
    res = rt.call("stepper://tic-t249/axis/x/query/status", {}, {})
    assert res.get("result", {}).get("runtime") != "mock"
    assert res["type"] == "transport_config_error"
