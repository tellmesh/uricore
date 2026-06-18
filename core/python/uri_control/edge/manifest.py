from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _handler_for_operation(item: dict[str, Any], handlers_data: dict[str, Any]) -> str | None:
    if item.get("handler"):
        return str(item["handler"])
    operation = str(item["operation"])
    for section in ("python", "urisys", "http", "https", "node"):
        ref = ((handlers_data or {}).get(section) or {}).get(operation)
        if ref:
            return str(ref)
    return None


def _register_urisys_flows(runtime, data: dict[str, Any], *, manifest_path: Path | None = None) -> None:
    urisys_meta = data.get("urisys") or {}
    cfg = runtime.config.setdefault("urisys", {})

    if urisys_meta.get("flows"):
        cfg["flows"] = dict(urisys_meta["flows"])

    flows_dir = urisys_meta.get("flows_dir")
    if not flows_dir and manifest_path is not None:
        candidate = manifest_path.parent / "flows"
        if candidate.is_dir():
            flows_dir = str(candidate.resolve())
    if flows_dir:
        cfg["flows_dir"] = str(Path(str(flows_dir)).resolve())

    if manifest_path is not None:
        cfg["manifest_dir"] = str(manifest_path.parent.resolve())


def register_manifest_file(runtime, manifest_path) -> None:
    path = Path(manifest_path)
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    register_manifest_data(runtime, data, source=str(path), manifest_path=path)


def register_manifest_data(
    runtime,
    data: dict[str, Any],
    *,
    source: str = "",
    manifest_path: Path | None = None,
) -> None:
    handlers_data = data.get("handlers") or {}
    if manifest_path is not None:
        _register_urisys_flows(runtime, data, manifest_path=manifest_path)
    elif data.get("urisys"):
        _register_urisys_flows(runtime, data)

    for item in data.get("uri_patterns") or []:
        operation = str(item["operation"])
        handler_ref = _handler_for_operation(item, handlers_data)
        if not handler_ref:
            label = source or data.get("id") or "manifest"
            raise KeyError(f"missing handler for operation {operation!r} in {label}")
        runtime.register(
            str(item["pattern"]),
            handler_ref,
            kind=str(item["kind"]),
            operation=operation,
            approval=str(
                item.get(
                    "approval",
                    "required" if item.get("kind") == "command" else "not_required",
                )
            ),
            side_effects=bool(item.get("side_effects", item.get("kind") == "command")),
            risk=item.get("risk") if isinstance(item.get("risk"), dict) else None,
        )


def register_manifest_files(runtime, manifest_paths) -> None:
    for manifest_path in manifest_paths:
        register_manifest_file(runtime, manifest_path)
