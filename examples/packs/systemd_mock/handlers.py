from __future__ import annotations

from typing import Any


_UNIT_STATE: dict[str, str] = {}


def unit_status(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    unit = (context.get("variables") or {}).get("unit", "unknown.service")
    state = _UNIT_STATE.get(unit, "active")
    return {
        "unit": unit,
        "active_state": state,
        "sub_state": "running" if state == "active" else "dead",
        "adapter": "mock",
    }


def unit_restart(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    unit = (context.get("variables") or {}).get("unit", "unknown.service")
    _UNIT_STATE[unit] = "active"
    return {
        "unit": unit,
        "active_state": "active",
        "action": "restart",
        "adapter": "mock",
    }
