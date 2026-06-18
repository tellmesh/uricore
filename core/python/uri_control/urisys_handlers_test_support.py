"""Minimal ping handler for urisys flow handler unit tests."""

from __future__ import annotations

from typing import Any


def ping(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {"pong": True, "payload": payload}


def echo(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {"echo": payload.get("message")}


def seed(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {"alpha": "A", "beta": 2}


def merge(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {"merged": payload}


def flag_ok(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True}


def never(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    raise RuntimeError("should skip")
