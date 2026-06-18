"""Tests for flow step references (save_as, ${ref})."""

from __future__ import annotations

from pathlib import Path

from uri_control.edge.flow_refs import interpolate_value, resolve_ref
from uri_control.edge.runtime import Runtime, run_flow


def test_resolve_ref_nested():
    outputs = {
        "shot": {"ok": True, "result": {"path": "/tmp/a.png", "image_id": "img-1"}},
    }
    assert resolve_ref("shot.result.path", outputs) == "/tmp/a.png"
    assert resolve_ref("shot.ok", outputs) is True


def test_interpolate_payload():
    outputs = {"shot": {"result": {"image_id": "img-42"}}}
    payload = {"target_text": "${shot.result.image_id}"}
    assert interpolate_value(payload, outputs) == {"target_text": "img-42"}


def test_run_flow_save_as_and_ref(tmp_path):
    flow = tmp_path / "chain.uri.flow.yaml"
    flow.write_text(
        "defaults:\n  approved: true\ndo:\n"
        "  - id: ping\n"
        "    uri: demo://local/query/ping\n"
        "    save_as: hello\n"
        "  - demo://local/query/echo:\n"
        "      message: ${hello.result.pong}\n",
        encoding="utf-8",
    )

    rt = Runtime(events_path=tmp_path / "ev.jsonl")
    rt.register("demo://local/query/ping", "python://uri_control.urisys_handlers_test_support:ping")
    rt.register("demo://local/query/echo", "python://uri_control.urisys_handlers_test_support:echo")

    results = run_flow(rt, str(flow), {"approved": True})
    assert results[0]["ok"] is True
    assert results[1]["ok"] is True
    assert results[1]["result"]["echo"] is True


def test_run_flow_payload_from(tmp_path):
    flow = tmp_path / "merge.uri.flow.yaml"
    flow.write_text(
        "defaults:\n  approved: true\ndo:\n"
        "  - id: seed\n"
        "    uri: demo://local/query/seed\n"
        "  - demo://local/query/merge:\n"
        "      payload_from: seed\n"
        "      extra: 1\n",
        encoding="utf-8",
    )
    rt = Runtime(events_path=tmp_path / "ev.jsonl")
    rt.register("demo://local/query/seed", "python://uri_control.urisys_handlers_test_support:seed")
    rt.register("demo://local/query/merge", "python://uri_control.urisys_handlers_test_support:merge")

    results = run_flow(rt, str(flow), {"approved": True})
    assert results[1]["result"]["merged"]["alpha"] == "A"
    assert results[1]["result"]["merged"]["extra"] == 1


def test_run_flow_if_skips_step(tmp_path):
    flow = tmp_path / "if.uri.flow.yaml"
    flow.write_text(
        "defaults:\n  approved: true\ndo:\n"
        "  - id: gate\n"
        "    uri: demo://local/query/flag\n"
        "    save_as: gate\n"
        "  - id: optional\n"
        "    uri: demo://local/query/never\n"
        "    if: gate.ok == false\n",
        encoding="utf-8",
    )
    rt = Runtime(events_path=tmp_path / "ev.jsonl")
    rt.register("demo://local/query/flag", "python://uri_control.urisys_handlers_test_support:flag_ok")
    rt.register("demo://local/query/never", "python://uri_control.urisys_handlers_test_support:never")

    results = run_flow(rt, str(flow), {"approved": True})
    assert len(results) == 2
    assert results[1]["skipped"] is True
