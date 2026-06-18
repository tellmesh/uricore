"""Tests for built-in ``urisys://flow/`` handlers."""

from __future__ import annotations

from pathlib import Path

import pytest

from uri_control.errors import HandlerLoadError
from uri_control.handlers import load_handler
from uri_control.urisys_handlers import parse_urisys_flow_handler, resolve_flow_path


def test_parse_urisys_flow_handler():
    assert parse_urisys_flow_handler("urisys://flow/machine-cycle") == "machine-cycle"
    assert parse_urisys_flow_handler("urisys://flow/smoke/") == "smoke"

    with pytest.raises(HandlerLoadError, match="flow"):
        parse_urisys_flow_handler("urisys://unknown/x")


def test_load_urisys_flow_handler_runs_steps(tmp_path):
    from uri_control.edge.runtime import Runtime

    flow_path = tmp_path / "flows" / "machine_cycle.uri.flow.yaml"
    flow_path.parent.mkdir(parents=True)
    flow_path.write_text(
        "defaults:\n  approved: true\ndo:\n  - process://local/query/ping\n",
        encoding="utf-8",
    )

    rt = Runtime(events_path=tmp_path / "events.jsonl", config={"urisys": {"flows_dir": str(flow_path.parent)}})
    rt.register("process://local/query/ping", "python://uri_control.urisys_handlers_test_support:ping")

    handler = load_handler("urisys://flow/machine-cycle")
    result = handler({}, {"runtime": rt, "approved": True})

    assert result["ok"] is True
    assert result["flow_id"] == "machine-cycle"
    assert len(result["steps"]) == 1
    assert result["steps"][0]["result"]["pong"] is True


def test_resolve_flow_path_from_manifest_map(tmp_path):
    from uri_control.edge.runtime import Runtime

    flow_file = tmp_path / "flows" / "cycle.uri.flow.yaml"
    flow_file.parent.mkdir()
    flow_file.write_text("do: []\n", encoding="utf-8")

    rt = Runtime(
        config={
            "urisys": {
                "flows": {"machine-cycle": str(flow_file)},
            }
        }
    )
    assert resolve_flow_path(rt, "machine-cycle") == flow_file


def test_resolve_flow_path_missing():
    from uri_control.edge.runtime import Runtime

    rt = Runtime(config={})
    with pytest.raises(HandlerLoadError, match="not found"):
        resolve_flow_path(rt, "missing")


def test_parse_flow_step_graph_format():
    from uri_control.edge.runtime import _parse_flow_step

    uri, payload, step_id = _parse_flow_step(
        {
            "id": "apt_update",
            "uri": "shell://apt-get",
            "payload": {"args": ["update"]},
            "after": "env_check",
        }
    )
    assert uri == "shell://apt-get"
    assert payload == {"args": ["update"]}
    assert step_id == "apt_update"

    uri2, payload2, _ = _parse_flow_step("kvm://local/monitor/primary/query/screenshot")
    assert uri2 == "kvm://local/monitor/primary/query/screenshot"
    assert payload2 == {}

    uri3, payload3, _ = _parse_flow_step({"kvm://local/task/command/click-text": {"text": "OK"}})
    assert uri3 == "kvm://local/task/command/click-text"
    assert payload3 == {"text": "OK"}
