"""Flow inputs seeding for ${device} style refs."""

from __future__ import annotations

from uri_control.edge.flow_refs import interpolate_value, seed_flow_inputs


def test_seed_flow_inputs_enables_uri_interpolation():
    flow = {
        "inputs": {
            "device": {"default": "machine-01"},
            "axis": {"default": "x"},
        },
        "do": [],
    }
    step_outputs: dict = {}
    seed_flow_inputs(flow, {"payload": {"steps": 50}}, step_outputs)
    assert step_outputs["device"] == "machine-01"
    uri = interpolate_value("stepper://${device}/axis/${axis}/query/status", step_outputs)
    assert uri == "stepper://machine-01/axis/x/query/status"
