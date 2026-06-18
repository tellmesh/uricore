"""FlowRunner class wrapper."""

from __future__ import annotations

from uri_control.edge.flow import FlowRunner, run_flow
from uri_control.edge.runtime import Runtime


def test_flow_runner_matches_run_flow(tmp_path):
    flow = tmp_path / "flow.yaml"
    flow.write_text(
        "defaults:\n  approved: true\ndo:\n  - id: ping\n    uri: mock://local/query/ping\n",
        encoding="utf-8",
    )
    rt = Runtime(events_path=tmp_path / "ev.jsonl")
    rt.register("mock://local/query/ping", "python://uri_control.urisys_handlers_test_support:ping")

    via_fn = run_flow(rt, str(flow), {"approved": True})
    via_cls = FlowRunner(rt).run(str(flow), {"approved": True})
    assert len(via_cls) == len(via_fn) == 1
    assert via_cls[0]["ok"] and via_fn[0]["ok"]
    assert via_cls[0].get("step_id") == via_fn[0].get("step_id") == "ping"
