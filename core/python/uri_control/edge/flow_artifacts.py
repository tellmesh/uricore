"""Sync flow step artifacts into runtime.state for downstream URI handlers."""

from __future__ import annotations

import time
from typing import Any


def sync_artifacts_to_runtime(runtime: Any, call_result: dict[str, Any]) -> None:
    """Register screenshot-like results so OCR/LLM can resolve by ``image_id``."""
    result = call_result.get("result")
    if not isinstance(result, dict):
        return
    if not result.get("base64"):
        return

    state = getattr(runtime, "state", None)
    if not isinstance(state, dict):
        return

    image_id = str(result.get("image_id") or f"shot-{int(time.time() * 1000)}")
    entry = {
        "image_id": image_id,
        "mime": result.get("mime", "image/png"),
        "base64": result.get("base64"),
        "monitor": result.get("monitor"),
        "driver": result.get("driver"),
        "path": result.get("path"),
        "width": result.get("width"),
        "height": result.get("height"),
        "text": result.get("text"),
        "captured_at": result.get("captured_at") or time.time(),
    }
    state.setdefault("images", {})[image_id] = entry
    state["latest_screenshot"] = entry
    if not result.get("image_id"):
        result["image_id"] = image_id


__all__ = ["sync_artifacts_to_runtime"]
