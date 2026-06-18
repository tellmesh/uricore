"""Tests for platform resolver config (Etap 3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from uri_control.edge.runtime import Runtime, _order_flow_steps, run_flow
from uri_control.resolver import apply_resolver_config, load_resolver_file, resolve_uri


def test_load_and_apply_resolver(tmp_path):
    path = tmp_path / "resolver.yaml"
    path.write_text(
        "environment: edge-linux\n"
        "uri_aliases:\n"
        "  package://chromium/command/install: shell://apt-get\n"
        "targets:\n"
        "  machine-01:\n"
        "    transport: mqtt\n"
        "    uri_host: edge-gateway\n"
        "runtime:\n"
        "  device_profile:\n"
        "    axes:\n"
        "      x:\n"
        "        driver: mock\n",
        encoding="utf-8",
    )
    data = load_resolver_file(path)
    rt = Runtime(config={})
    apply_resolver_config(rt, data)
    assert rt.config["targets"]["machine-01"]["transport"] == "mqtt"
    assert rt.config["uri_aliases"]["package://chromium/command/install"] == "shell://apt-get"
    assert rt.config["device_profile"]["axes"]["x"]["driver"] == "mock"


def test_resolve_uri_remaps_authority():
    config = {"targets": {"machine-01": {"transport": "mqtt", "uri_host": "gateway"}}}
    uri, extra = resolve_uri("stepper://machine-01/axis/x/query/status", config)
    assert uri == "stepper://gateway/axis/x/query/status"
    assert extra["target"] == "machine-01"
    assert extra["transport"] == "mqtt"


def test_resolve_uri_runtime_profile_overlay():
    config = {
        "targets": {
            "tic-t249": {
                "transport": "http",
                "endpoint": "http://127.0.0.1:8791/uri/call",
                "profiles": {
                    "esp32-i2c-http-mqtt": {
                        "transport": "http",
                        "endpoint": "http://esp32-tic.local:8791/uri/call",
                    }
                },
            }
        }
    }
    uri, extra = resolve_uri(
        "stepper://tic-t249/axis/x/query/status",
        config,
        {"runtime_profile": "esp32-i2c-http-mqtt"},
    )
    assert uri.endswith("/query/status")
    assert extra["transport"] == "http"
    assert extra["target_profile"]["endpoint"] == "http://esp32-tic.local:8791/uri/call"
    assert "profiles" not in extra["target_profile"]


def test_apply_uri_aliases():
    from uri_control.resolver import apply_uri_aliases, resolve_uri

    config = {
        "uri_aliases": {
            "package://chromium/command/install": "shell://apt-get",
        }
    }
    assert apply_uri_aliases("package://chromium/command/install", config) == "shell://apt-get"
    uri, _ = resolve_uri("package://chromium/command/install", config)
    assert uri == "shell://apt-get"


def test_apply_resolver_config_loads_uri_aliases(tmp_path):
    from uri_control.edge.runtime import Runtime
    from uri_control.resolver import apply_resolver_config

    rt = Runtime(config={})
    apply_resolver_config(rt, {"uri_aliases": {"package://chromium/command/install": "shell://apt-get"}})
    assert rt.config["uri_aliases"]["package://chromium/command/install"] == "shell://apt-get"
    uri, _ = resolve_uri("package://chromium/command/install", rt.config)
    assert uri == "shell://apt-get"


def test_runtime_call_applies_resolver(tmp_path):
    # Authority remap (uri_host) is orthogonal to transport: a ``local`` target
    # is rewritten to the canonical host and still executes the in-process route.
    rt = Runtime(events_path=tmp_path / "ev.jsonl", config={"targets": {"gateway": {"transport": "local"}}})
    rt.register("demo://gateway/query/ping", "python://uri_control.urisys_handlers_test_support:ping")
    rt.config["targets"]["local"] = {"uri_host": "gateway", "transport": "local"}
    res = rt.call("demo://local/query/ping", {}, {"approved": True})
    assert res["ok"] is True
    assert res["result"]["pong"] is True


def test_run_flow_applies_resolver_runtime_defaults(tmp_path):
    flow = tmp_path / "flow.uri.flow.yaml"
    flow.write_text(
        "defaults:\n  approved: true\ndo:\n  - demo://local/query/ping\n",
        encoding="utf-8",
    )
    rt = Runtime(events_path=tmp_path / "ev.jsonl", config={"resolver": {"runtime": {"dry_run": True}}})
    rt.register("demo://local/query/ping", "python://uri_control.urisys_handlers_test_support:ping")
    results = run_flow(rt, str(flow), {"approved": True})
    assert results[0]["ok"] is True
    assert results[0]["result"]["payload"] == {}


def test_order_flow_steps_after():
    steps = [
        {"id": "b", "uri": "a://x", "after": "a"},
        {"id": "a", "uri": "a://y"},
        {"id": "c", "uri": "a://z", "after": "b"},
    ]
    ordered = _order_flow_steps(steps)
    assert [s["id"] for s in ordered] == ["a", "b", "c"]


def test_order_flow_steps_cycle():
    steps = [
        {"id": "a", "uri": "a://x", "after": "b"},
        {"id": "b", "uri": "a://y", "after": "a"},
    ]
    with pytest.raises(ValueError, match="cycle"):
        _order_flow_steps(steps)
