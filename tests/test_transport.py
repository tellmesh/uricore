"""Tests for resolver transport delegation."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from uri_control.edge.runtime import Runtime
from uri_control.transport import delegate_transport_call, normalize_http_endpoint


class _Handler(BaseHTTPRequestHandler):
    last_body: dict | None = None

    def log_message(self, *_args, **_kwargs):
        return

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        _Handler.last_body = json.loads(raw)
        body = json.dumps({"ok": True, "result": {"remote": True, "uri": _Handler.last_body.get("uri")}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _with_http_server():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/uri/call"


def test_normalize_http_endpoint():
    assert normalize_http_endpoint({"endpoint": "http://edge:8790/uri/call"}) == "http://edge:8790/uri/call"
    assert (
        normalize_http_endpoint({"endpoint": "/uri/call", "options": {"base_url": "http://gw"}})
        == "http://gw/uri/call"
    )


def test_delegate_http():
    server, url = _with_http_server()
    try:
        result = delegate_transport_call(
            transport="http",
            source_uri="stepper://machine-01/axis/x/query/status",
            resolved_uri="stepper://gateway/axis/x/query/status",
            payload={"x": 1},
            context={"approved": True},
            profile={"endpoint": url},
        )
        assert result is not None
        assert result["ok"] is True
        assert result["delegated"] is True
        assert result["result"]["remote"] is True
        assert _Handler.last_body["uri"] == "stepper://gateway/axis/x/query/status"
    finally:
        server.shutdown()


def test_delegate_mqtt_requires_bridge():
    result = delegate_transport_call(
        transport="mqtt",
        source_uri="stepper://machine-01/axis/x/query/status",
        resolved_uri="stepper://machine-01/axis/x/query/status",
        payload={},
        context={},
        profile={"endpoint": "urisys/machine-01/call"},
    )
    assert result is not None
    assert result["ok"] is False
    assert result["type"] == "transport_config_error"


def test_resolve_mqtt_topics_legacy_and_modern():
    from uri_control.transport import resolve_mqtt_topics

    legacy = {"endpoint": "uritic/tic-t249/call/{request_id}",
              "options": {"response_topic": "uritic/tic-t249/response/{request_id}"}}
    pub, sub, mode = resolve_mqtt_topics(legacy, "abc")
    assert (pub, sub, mode) == ("uritic/tic-t249/call/abc", "uritic/tic-t249/response/abc", "legacy")

    modern = {"endpoint": "uritic/tic-t249/request"}
    pub, sub, mode = resolve_mqtt_topics(modern, "abc")
    assert pub == "uritic/tic-t249/request"
    assert sub == "uritic/tic-t249/response/abc"
    assert mode == "modern"


def test_delegate_mqtt_native_broker_roundtrip(monkeypatch):
    import uri_control.transport as T

    seen = {}

    def fake_hook(*, broker, pub_topic, sub_topic, body, timeout):
        seen.update(broker=broker, pub_topic=pub_topic, sub_topic=sub_topic, body=body)
        return {"ok": True, "result": {"echoed_uri": body["uri"], "executed": True}}

    monkeypatch.setattr(T, "MQTT_REQUEST_HOOK", fake_hook)
    result = delegate_transport_call(
        transport="mqtt",
        source_uri="stepper://tic-t249/axis/x/command/move-relative",
        resolved_uri="stepper://tic-t249/axis/x/command/move-relative",
        payload={"steps": 100},
        context={"approved": True},
        profile={
            "endpoint": "uritic/tic-t249/call/{request_id}",
            "options": {"broker": "tcp://rpi3.local:1883",
                        "response_topic": "uritic/tic-t249/response/{request_id}"},
        },
    )
    assert result["ok"] is True
    assert result["delegated"] is True
    assert result["result"]["echoed_uri"] == "stepper://tic-t249/axis/x/command/move-relative"
    # native path used the broker + templated topics (no {request_id} left)
    assert seen["broker"] == "tcp://rpi3.local:1883"
    assert seen["pub_topic"].startswith("uritic/tic-t249/call/") and "{request_id}" not in seen["pub_topic"]
    assert seen["sub_topic"].startswith("uritic/tic-t249/response/")
    assert seen["body"]["uri"] == "stepper://tic-t249/axis/x/command/move-relative"


def test_delegate_mqtt_native_missing_dependency(monkeypatch):
    import uri_control.transport as T

    monkeypatch.setattr(T, "MQTT_REQUEST_HOOK", None)
    monkeypatch.setattr(T, "mqtt_available", lambda: False)
    result = delegate_transport_call(
        transport="mqtt",
        source_uri="stepper://tic-t249/axis/x/command/stop",
        resolved_uri="stepper://tic-t249/axis/x/command/stop",
        payload={},
        context={"approved": True},
        profile={"endpoint": "uritic/tic-t249/call/{request_id}",
                 "options": {"broker": "tcp://rpi3.local:1883"}},
    )
    assert result["ok"] is False
    assert result["type"] == "transport_dependency_missing"


def test_delegate_mqtt_via_bridge():
    server, url = _with_http_server()
    try:
        result = delegate_transport_call(
            transport="mqtt",
            source_uri="stepper://machine-01/axis/x/query/status",
            resolved_uri="stepper://machine-01/axis/x/query/status",
            payload={"steps": 1},
            context={"approved": True},
            profile={
                "endpoint": "urisys/machine-01/call",
                "options": {"bridge_url": url, "qos": 2},
            },
        )
        assert result is not None
        assert result["ok"] is True
        assert _Handler.last_body["topic"] == "urisys/machine-01/call"
        assert _Handler.last_body["qos"] == 2
    finally:
        server.shutdown()


def test_delegate_dry_run_skips_network():
    result = delegate_transport_call(
        transport="http",
        source_uri="demo://remote/query/ping",
        resolved_uri="demo://remote/query/ping",
        payload={},
        context={"dry_run": True},
        profile={"endpoint": "http://unreachable/uri/call"},
    )
    assert result is not None
    assert result["ok"] is True
    assert result["result"]["dry_run"] is True


def test_runtime_call_delegates_before_route_match(tmp_path):
    server, url = _with_http_server()
    try:
        rt = Runtime(
            events_path=tmp_path / "ev.jsonl",
            config={
                "targets": {
                    "remote": {
                        "transport": "http",
                        "endpoint": url,
                    }
                }
            },
        )
        res = rt.call("demo://remote/query/ping", {}, {"approved": True})
        assert res["ok"] is True
        assert res.get("delegated") is True
        assert res["result"]["remote"] is True
    finally:
        server.shutdown()


def test_runtime_unsupported_transport_returns_clean_error(tmp_path):
    # esp32 platform export emits ``transport: unsupported`` for authorities with
    # no on-device adapter; the runtime must surface a clean error, not mis-route.
    rt = Runtime(
        events_path=tmp_path / "ev.jsonl",
        config={"targets": {"operator": {"transport": "unsupported", "note": "no edge adapter on device"}}},
    )
    res = rt.call("screen://operator/query/state", {}, {"approved": True})
    assert res["ok"] is False
    assert res["type"] == "transport_unsupported"
    assert "no edge adapter" in res["error"]


def test_runtime_local_transport_still_uses_handler(tmp_path):
    rt = Runtime(events_path=tmp_path / "ev.jsonl", config={"targets": {"local": {"transport": "local"}}})
    rt.register("demo://local/query/ping", "python://uri_control.urisys_handlers_test_support:ping")
    res = rt.call("demo://local/query/ping", {}, {"approved": True})
    assert res["ok"] is True
    assert res.get("delegated") is not True
    assert res["result"]["pong"] is True
