"""Runtime-level transport delegation (``Runtime.call``).

The transport implementation and its unit tests live in the ``urirouter`` package
(``uri_router.transport``); these tests cover the uricore runtime wiring that
delegates a call before matching a local route.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from uri_control.edge.runtime import Runtime


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


def test_runtime_call_delegates_before_route_match(tmp_path):
    server, url = _with_http_server()
    try:
        rt = Runtime(
            events_path=tmp_path / "ev.jsonl",
            config={"targets": {"remote": {"transport": "http", "endpoint": url}}},
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
