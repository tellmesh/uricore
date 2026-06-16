from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .dispatcher import UriControlRuntime
from .event_store import JsonlEventStore
from .projection import ProjectionBuilder
from .registry import CapabilityRegistry


def _load_payload(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    candidate = Path(value)
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return json.loads(value)


def _registry_from_args(args: argparse.Namespace) -> CapabilityRegistry:
    if not args.manifest:
        raise SystemExit("At least one --manifest path is required.")
    return CapabilityRegistry.from_manifest_files(args.manifest)


def cmd_explain(args: argparse.Namespace) -> int:
    registry = _registry_from_args(args)
    print(json.dumps(registry.explain(args.uri), ensure_ascii=False, indent=2))
    return 0


def cmd_call(args: argparse.Namespace) -> int:
    registry = _registry_from_args(args)
    store = JsonlEventStore(args.events)
    runtime = UriControlRuntime(registry=registry, event_store=store)
    result = runtime.call(
        args.uri,
        payload=_load_payload(args.payload),
        context={"approved": args.approve, "environment": args.environment},
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.ok else 2


def cmd_list(args: argparse.Namespace) -> int:
    registry = _registry_from_args(args)
    data = [
        {
            "manifest_id": route.manifest_id,
            "scheme": route.scheme,
            "pattern": route.pattern,
            "kind": route.kind,
            "operation": route.operation,
            "side_effects": route.side_effects,
            "approval": route.approval,
        }
        for route in registry.routes
    ]
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def cmd_projection_latest(args: argparse.Namespace) -> int:
    store = JsonlEventStore(args.events)
    builder = ProjectionBuilder(store)
    print(json.dumps(builder.latest_by_source_uri(), ensure_ascii=False, indent=2))
    return 0


def cmd_projection_status(args: argparse.Namespace) -> int:
    store = JsonlEventStore(args.events)
    builder = ProjectionBuilder(store)
    print(json.dumps(builder.status_by_source_uri(), ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uricore")
    sub = parser.add_subparsers(dest="command", required=True)

    explain = sub.add_parser("explain", help="Explain how a URI matches a manifest route.")
    explain.add_argument("uri")
    explain.add_argument("--manifest", action="append", required=True)
    explain.set_defaults(func=cmd_explain)

    call = sub.add_parser("call", help="Call a URI through policy, handler and event store.")
    call.add_argument("uri")
    call.add_argument("--manifest", action="append", required=True)
    call.add_argument("--payload", default="{}", help="JSON string or path to JSON file.")
    call.add_argument("--events", default="output/events.jsonl")
    call.add_argument("--environment", default="local")
    call.add_argument("--approve", action="store_true")
    call.set_defaults(func=cmd_call)

    list_cmd = sub.add_parser("list", help="List capability routes from manifests.")
    list_cmd.add_argument("--manifest", action="append", required=True)
    list_cmd.set_defaults(func=cmd_list)

    projection = sub.add_parser("projection", help="Build projections from events.")
    projection_sub = projection.add_subparsers(dest="projection_command", required=True)

    latest = projection_sub.add_parser("latest", help="Latest event by source URI.")
    latest.add_argument("--events", default="output/events.jsonl")
    latest.set_defaults(func=cmd_projection_latest)

    status = projection_sub.add_parser("status", help="Status projection by source URI.")
    status.add_argument("--events", default="output/events.jsonl")
    status.set_defaults(func=cmd_projection_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
