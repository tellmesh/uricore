"""Edge runtime — shared Runtime, HTTP transport, CLI, and pack composition.

These modules were migrated from ``urisysedge`` and are re-exported from there
as shims so all 30+ dependent edge packages keep working unchanged.
"""

from .compose import (
    bundle_packs,
    build_runtime,
    register_manifests,
    register_pack,
    register_packs,
    resolve_pack_module,
)
from .runtime import JsonlEventStore, Route, Runtime, load_json, load_yaml_flow, run_flow

__all__ = [
    "JsonlEventStore",
    "Route",
    "Runtime",
    "load_json",
    "load_yaml_flow",
    "run_flow",
    "build_runtime",
    "register_pack",
    "register_packs",
    "register_manifests",
    "resolve_pack_module",
    "bundle_packs",
]
