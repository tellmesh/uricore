from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .loader import load_yaml_flow
from .steps import order_flow_steps, parse_flow_step

if TYPE_CHECKING:
    from ..runtime import Runtime


class FlowRunner:
    """Sequential UriFlow executor bound to an edge ``Runtime``."""

    def __init__(self, runtime: Runtime):
        self._runtime = runtime

    @property
    def runtime(self) -> Runtime:
        return self._runtime

    def run(self, path: str, context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        from ..flow_artifacts import sync_artifacts_to_runtime
        from ..flow_refs import (
            evaluate_step_if,
            interpolate_value,
            merge_payload_from,
            output_key,
            resolve_step_uri,
            seed_flow_inputs,
            store_step_output,
        )

        flow = load_yaml_flow(path)
        defaults = dict(flow.get("defaults") or {})
        config = getattr(self._runtime, "config", None) or {}
        resolver_runtime = ((config.get("resolver") or {}).get("runtime") or {})
        for key, value in resolver_runtime.items():
            defaults.setdefault(key, value)

        if context:
            defaults.update(context)

        step_outputs: dict[str, Any] = {}
        seed_flow_inputs(flow, context, step_outputs)
        results: list[dict[str, Any]] = []
        steps = order_flow_steps(list(flow.get("do") or []))

        for index, step in enumerate(steps):
            uri, payload, step_id = parse_flow_step(step)
            step_dict = step if isinstance(step, dict) else None

            if not evaluate_step_if(step_dict.get("if") if step_dict else None, step_outputs):
                skipped = {
                    "ok": True,
                    "uri": uri,
                    "skipped": True,
                    "reason": "condition_not_met",
                    "step_id": step_id,
                }
                store_step_output(step_outputs, key=output_key(step, step_id, index), call_result=skipped)
                results.append(skipped)
                continue

            payload = merge_payload_from(payload, step_outputs)
            payload = interpolate_value(payload, step_outputs)
            uri = resolve_step_uri(uri, step_dict, step_outputs)

            call_ctx = dict(defaults)
            call_ctx["step_outputs"] = step_outputs
            if step_id:
                call_ctx["step_id"] = step_id

            result = self._runtime.call(uri, payload, call_ctx)
            sync_artifacts_to_runtime(self._runtime, result)
            if step_id:
                result["step_id"] = step_id
            store_step_output(step_outputs, key=output_key(step, step_id, index), call_result=result)
            if step_id and output_key(step, step_id, index) != step_id:
                store_step_output(step_outputs, key=step_id, call_result=result)
            results.append(result)

        expect_block = flow.get("expect")
        if isinstance(expect_block, dict) and expect_block:
            from ..flow_expect import evaluate_flow_expect

            expect_failures = evaluate_flow_expect(flow, results, step_outputs)
            if expect_failures:
                results.append(
                    {
                        "ok": False,
                        "type": "expect_failed",
                        "uri": "flow://expect",
                        "failures": expect_failures,
                    }
                )
            else:
                results.append({"ok": True, "type": "expect_passed", "uri": "flow://expect"})

        return results


def run_flow(runtime: Runtime, path: str, context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return FlowRunner(runtime).run(path, context)
