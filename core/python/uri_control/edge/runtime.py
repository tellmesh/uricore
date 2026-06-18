from __future__ import annotations

import importlib
import json
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import unquote

from .env import load_env_policy

# Surgical delegation to the uricore engine (the single source of truth for URI
# routing). When ``uricore`` (module ``uri_control``) is installed, route
# storage + pattern matching are delegated to its CapabilityRegistry, killing
# the duplicate regex compiler. When it is absent, the local implementation
# below is used unchanged, so existing edge deployments never break.
try:  # pragma: no cover - exercised by environment, not unit tests
    from uri_control import CapabilityRegistry as _UriCoreRegistry
    from uri_control.errors import RouteNotFoundError as _UriCoreRouteNotFound
except Exception:  # uricore not installed in this environment
    _UriCoreRegistry = None  # type: ignore[assignment]
    _UriCoreRouteNotFound = Exception  # type: ignore[assignment,misc]


def _result_ok(result: Any) -> bool:
    if isinstance(result, dict):
        if result.get("ok") is False:
            return False
        exit_code = result.get("exit_code")
        if exit_code is not None and exit_code != 0:
            return False
    return True


@dataclass
class Route:
    pattern: str
    kind: str
    operation: str
    handler_ref: str
    approval: str = "not_required"
    side_effects: bool = False
    risk: dict[str, Any] | None = None
    _regex: re.Pattern | None = None

    def compile(self) -> "Route":
        parts: list[str] = []
        i = 0
        while i < len(self.pattern):
            if self.pattern[i] == "{":
                j = self.pattern.index("}", i)
                name = self.pattern[i + 1:j]
                parts.append(f"(?P<{name}>[^/]+)")
                i = j + 1
            else:
                parts.append(re.escape(self.pattern[i]))
                i += 1
        self._regex = re.compile("^" + "".join(parts) + "$")
        return self

    def match(self, uri: str) -> dict[str, str] | None:
        if self._regex is None:
            self.compile()
        assert self._regex is not None
        m = self._regex.match(uri)
        if not m:
            return None
        return {k: unquote(v) for k, v in m.groupdict().items()}


class JsonlEventStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: dict[str, Any]) -> None:
        row = dict(event)
        row.setdefault("event_id", str(uuid.uuid4()))
        row.setdefault("occurred_at_unix_ms", int(time.time() * 1000))
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def tail(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        out: list[dict[str, Any]] = []
        for line in lines[-limit:]:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out


class Runtime:
    def __init__(self, events_path: str | Path = "data/events.jsonl", config: dict[str, Any] | None = None):
        # ``self.routes`` is always populated (local Route objects) so that
        # ``/uri/routes``, ``serve()`` and inspection behave identically in both
        # modes. When uricore is available, ``self._registry`` additionally holds
        # the same routes and drives matching.
        self.routes: list[Route] = []
        self._operation_risk: dict[str, dict[str, Any]] = {}
        self.events = JsonlEventStore(events_path)
        self.config = config or {}
        self.state: dict[str, Any] = {}
        self._registry = _UriCoreRegistry() if _UriCoreRegistry is not None else None
        from .call.pipeline import RuntimeCallPipeline

        self._pipeline = RuntimeCallPipeline(self)

    def register(
        self,
        pattern: str,
        handler: str,
        *,
        kind: str = "command",
        operation: str | None = None,
        approval: str = "not_required",
        side_effects: bool = False,
        risk: dict[str, Any] | None = None,
    ) -> None:
        op = operation or pattern.rsplit("/", 1)[-1]
        if isinstance(risk, dict):
            self._operation_risk[op] = risk
        self.routes.append(Route(pattern, kind, op, handler, approval, side_effects, risk).compile())
        if self._registry is not None:
            self._registry.register(
                pattern,
                handler,
                kind=kind,
                operation=op,
                approval=approval,
                side_effects=side_effects,
            )

    def resolve(self, uri: str) -> tuple[Route, dict[str, str]]:
        if self._registry is not None:
            # Delegate matching to the uricore engine (pure routing, no handler
            # load — this runtime loads handlers lazily itself in call()).
            try:
                matched = self._registry.match_route(uri)
            except _UriCoreRouteNotFound:
                raise KeyError(f"No route for URI: {uri}")
            core = matched.route
            # Adapt the uricore Route to this runtime's local Route shape so the
            # rest of call() (approval, events, handler load) is unchanged.
            route = Route(
                pattern=core.pattern,
                kind=core.kind,
                operation=core.operation,
                handler_ref=core.handler_ref,
                approval=core.approval,
                side_effects=core.side_effects,
                risk=self._operation_risk.get(core.operation),
            )
            return route, dict(matched.variables)
        for route in self.routes:
            params = route.match(uri)
            if params is not None:
                return route, params
        raise KeyError(f"No route for URI: {uri}")

    def _load_handler(self, ref: str) -> Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]:
        # Delegate to the uricore multi-technology loader (python/http/https/node)
        # when available, so the same edge runtime can serve URIs backed by any
        # technology behind the HTTP wire ABI. Fall back to in-process python://.
        try:
            from uri_control.handlers import load_handler
        except Exception:
            load_handler = None
        if load_handler is not None:
            return load_handler(ref)
        if ref.startswith("python://"):
            ref = ref[len("python://"):]
        module_name, func_name = ref.split(":", 1)
        mod = importlib.import_module(module_name)
        return getattr(mod, func_name)

    def call(self, uri: str, payload: dict[str, Any] | None = None, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._pipeline.call(uri, payload, context)

    def _check_policies(self, route: Route, uri: str, payload: dict[str, Any], params: dict[str, str], context: dict[str, Any]) -> dict[str, Any] | None:
        approved = bool(context.get("approved"))
        if route.side_effects and route.approval == "required" and not approved:
            return {"ok": False, "uri": uri, "type": "policy_denied", "reason": "approval required"}

        from .risk_policy import check_risk_requirements

        risk_violation = check_risk_requirements(route.risk, context, operation=route.operation)
        if risk_violation is not None:
            self._log_event(route, uri, f"{route.operation}.risk_denied", violation=risk_violation)
            return {**risk_violation, "uri": uri}

        from uri_router.policy import check_operation_limits

        violation = check_operation_limits(route.operation, payload, self.config)
        if violation is not None:
            self._log_event(route, uri, f"{route.operation}.policy_denied", violation=violation)
            return {**violation, "uri": uri}

        from uri_router.policy import check_shell_policy

        shell_violation = check_shell_policy(route.operation, payload, params, self.config)
        if shell_violation is not None:
            self._log_event(route, uri, f"{route.operation}.policy_denied", violation=shell_violation)
            return {**shell_violation, "uri": uri}
        return None

    def _log_event(self, route: Route, uri: str, event_type: str, **extra: Any) -> dict[str, Any]:
        event = {"event_id": str(uuid.uuid4()), "source_uri": uri, "operation": route.operation, "kind": route.kind, "occurred_at_unix_ms": int(time.time() * 1000), "event_type": event_type, **extra}
        self.events.append(event)
        return event

    def _build_call_context(self, uri: str, resolved_uri: str, params: dict[str, str], context: dict[str, Any]) -> dict[str, Any]:
        ctx = dict(context)
        ctx.update({"uri": resolved_uri, "source_uri": uri, "params": params, "config": self.config, "runtime": self, "state": self.state, "event_store": self.events})
        if "env_config" not in ctx:
            policy = load_env_policy()
            if policy:
                ctx["env_config"] = policy
        return ctx

    def _execute_handler(self, route: Route, uri: str, resolved_uri: str, payload: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        event_base = self._log_event(route, uri, "operation.accepted", payload=payload)
        try:
            handler = self._load_handler(route.handler_ref)
            result = handler(payload, ctx)
            ok = _result_ok(result)
            self._log_event(route, uri, f"{route.operation}.completed", result=result, event_id=str(uuid.uuid4()))
            return {"ok": ok, "uri": uri, "operation": route.operation, "params": ctx["params"], "result": result, "event": {**event_base, "event_type": f"{route.operation}.completed", "result": result}}
        except Exception as exc:
            self._log_event(route, uri, f"{route.operation}.failed", error=str(exc), event_id=str(uuid.uuid4()))
            return {"ok": False, "uri": uri, "resolved_uri": resolved_uri, "operation": route.operation, "error": str(exc), "event": {**event_base, "event_type": f"{route.operation}.failed", "error": str(exc)}}


def load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return json.loads(p.read_text(encoding="utf-8"))


from .flow import (  # noqa: E402
    FlowRunner,
    _order_flow_steps,
    _parse_flow_step,
    load_yaml_flow,
    order_flow_steps,
    parse_flow_step,
    run_flow,
)

# HTTP transport now lives in uri_control.edge.http (the single shared implementation).
# These thin wrappers preserve the historical urisysedge entry points so callers
# and edge shims keep working unchanged.
from .http import make_uri_handler, serve as _serve  # noqa: E402


def make_handler(runtime: Runtime):
    return make_uri_handler(runtime, service="urirdp")


def serve(runtime: Runtime, host: str, port: int) -> None:
    _serve(runtime, host, port, service="urirdp")
