"""Built-in urisys controller handlers (``urisys://…``).

These are not user-defined pack handlers. They delegate to urisys runtime
facilities — today ``urisys://flow/<flow-id>`` runs a materialised
``.uri.flow.yaml`` through the platform URI resolver.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from .errors import HandlerLoadError

Handler = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]

URISYS_PREFIX = "urisys://"
_FLOW_ID_RE = re.compile(r"[^0-9A-Za-z_]+")


def _safe_flow_id(value: str) -> str:
    value = _FLOW_ID_RE.sub("_", value.strip())
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        raise HandlerLoadError("flow id is empty")
    if value[0].isdigit():
        value = "_" + value
    return value.lower()


def parse_urisys_flow_handler(handler_ref: str) -> str:
    """Return the flow id from ``urisys://flow/<flow-id>``."""
    if not handler_ref.startswith(URISYS_PREFIX):
        raise HandlerLoadError(f"Expected {URISYS_PREFIX}…, got {handler_ref!r}.")
    rest = handler_ref[len(URISYS_PREFIX) :]
    if not rest.startswith("flow/"):
        raise HandlerLoadError(
            f"Unsupported urisys handler {handler_ref!r}. Expected urisys://flow/<flow-id>."
        )
    flow_id = rest[len("flow/") :].strip("/")
    if not flow_id:
        raise HandlerLoadError(f"Missing flow id in {handler_ref!r}.")
    return flow_id


def resolve_flow_path(runtime: Any, flow_id: str) -> Path:
    """Locate a flow YAML for *flow_id* using runtime config set at manifest registration."""
    config = getattr(runtime, "config", None) or {}
    urisys_cfg = config.get("urisys") or {}

    flows_map = urisys_cfg.get("flows") or config.get("flows") or {}
    if flow_id in flows_map:
        path = Path(str(flows_map[flow_id]))
        if path.is_file():
            return path

    flows_dir = urisys_cfg.get("flows_dir") or config.get("flows_dir")
    if flows_dir:
        base = Path(str(flows_dir))
        safe = _safe_flow_id(flow_id)
        for name in (f"{safe}.uri.flow.yaml", f"{flow_id}.uri.flow.yaml"):
            candidate = base / name
            if candidate.is_file():
                return candidate

    manifest_dir = urisys_cfg.get("manifest_dir")
    if manifest_dir:
        base = Path(str(manifest_dir)) / "flows"
        if base.is_dir():
            safe = _safe_flow_id(flow_id)
            for name in (f"{safe}.uri.flow.yaml", f"{flow_id}.uri.flow.yaml"):
                candidate = base / name
                if candidate.is_file():
                    return candidate

    raise HandlerLoadError(
        f"Flow {flow_id!r} not found. Register a manifest with flows/ or set runtime.config['urisys']['flows']."
    )


def make_urisys_flow_handler(flow_id: str) -> Handler:
    def handler(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        runtime = context.get("runtime")
        if runtime is None:
            return {"ok": False, "error": "urisys flow handler requires context.runtime"}

        from uri_control.edge.runtime import run_flow

        try:
            path = resolve_flow_path(runtime, flow_id)
        except HandlerLoadError as exc:
            return {"ok": False, "error": str(exc), "flow_id": flow_id}

        flow_context = dict(context)
        flow_context.update(payload or {})
        results = run_flow(runtime, str(path), flow_context)
        ok = all(r.get("ok") for r in results)
        return {"ok": ok, "flow_id": flow_id, "steps": results}

    return handler


def load_urisys_handler(handler_ref: str) -> Handler:
    """Load a built-in ``urisys://`` handler."""
    if handler_ref.startswith(f"{URISYS_PREFIX}flow/"):
        flow_id = parse_urisys_flow_handler(handler_ref)
        return make_urisys_flow_handler(flow_id)
    raise HandlerLoadError(
        f"Unsupported urisys handler {handler_ref!r}. Supported: urisys://flow/<flow-id>."
    )


__all__ = [
    "URISYS_PREFIX",
    "load_urisys_handler",
    "make_urisys_flow_handler",
    "parse_urisys_flow_handler",
    "resolve_flow_path",
]
