"""Minimal ping handler for urisys flow handler unit tests."""

from __future__ import annotations

from typing import Any


def ping(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {"pong": True, "payload": payload}
