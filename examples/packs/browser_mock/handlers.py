from __future__ import annotations

from typing import Any


_SESSIONS: dict[str, dict[str, Any]] = {}


def open_page(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    variables = context.get("variables") or {}
    session_id = payload.get("session_id") or variables.get("session") or "default"
    url = payload["url"]
    title = payload.get("title") or f"Mock title for {url}"
    html = payload.get("html") or f"<html><body><h1>{title}</h1><p>{url}</p></body></html>"

    _SESSIONS[session_id] = {
        "session_id": session_id,
        "url": url,
        "title": title,
        "html": html,
    }

    return {
        "session_id": session_id,
        "url": url,
        "title": title,
        "adapter": "mock",
    }


def get_dom(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    variables = context.get("variables") or {}
    session_id = payload.get("session_id") or variables.get("session") or "default"
    session = _SESSIONS.get(session_id)
    if not session:
        return {
            "session_id": session_id,
            "html": "<html><body>No active mock session.</body></html>",
            "adapter": "mock",
        }
    return {
        "session_id": session_id,
        "html": session["html"],
        "adapter": "mock",
    }
