"""Multi-technology handler loader.

A capability handler reference (``handler_ref``) selects *how* a URI operation is
executed. Historically only ``python://module:function`` (in-process Python) was
supported. This loader generalises that so the same URI/manifest/contract can be
served by any technology behind the URI wire ABI (``POST /uri/call``):

* ``python://module:function`` — import and call an in-process Python callable.
* ``http://host:port[/path]``  — forward the URI envelope over HTTP to a remote
  URI runtime (any language: a Python edge, a uricore-js Node server, a C/ESP32
  firmware…). Defaults the path to ``/uri/call``.
* ``https://…``                — same, over TLS.
* ``node://host:port[/path]``  — sugar for forwarding to a uricore-js HTTP runtime
  (mapped to ``http://``).

The remote forms reuse the same envelope as ``urisys.managers.bridge_manager``:
``{"uri": <uri>, "payload": <payload>, "context": <json-safe context>}``.
"""

from __future__ import annotations

import importlib
import json
from typing import Any, Callable
from urllib import error, request
from urllib.parse import urlsplit

from .errors import HandlerLoadError

Handler = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]

PYTHON_PREFIX = "python://"
REMOTE_SCHEMES = ("http", "https")
DEFAULT_REMOTE_PATH = "/uri/call"
DEFAULT_TIMEOUT = 30

# Context keys that carry live, non-serialisable runtime objects; never forwarded.
_NON_SERIALIZABLE_KEYS = frozenset({"runtime", "event_store", "state"})


def load_python_handler(handler_ref: str) -> Handler:
    """Import a ``python://module:function`` handler (strict, descriptive errors)."""
    if not handler_ref.startswith(PYTHON_PREFIX):
        raise HandlerLoadError(
            f"Unsupported handler reference {handler_ref!r}. Expected python://module:function."
        )
    target = handler_ref[len(PYTHON_PREFIX) :]
    if ":" not in target:
        raise HandlerLoadError(f"Handler reference must be python://module:function, got {handler_ref!r}.")

    module_name, function_name = target.split(":", 1)
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - message wrapping
        raise HandlerLoadError(f"Cannot import handler module {module_name!r}: {exc}") from exc
    try:
        handler = getattr(module, function_name)
    except AttributeError as exc:
        raise HandlerLoadError(
            f"Handler function {function_name!r} not found in module {module_name!r}."
        ) from exc
    if not callable(handler):
        raise HandlerLoadError(f"Handler {handler_ref!r} is not callable.")
    return handler


def _safe_context(context: dict[str, Any] | None) -> dict[str, Any]:
    """Drop live runtime objects and any non-JSON-serialisable values."""
    out: dict[str, Any] = {}
    for key, value in (context or {}).items():
        if key in _NON_SERIALIZABLE_KEYS:
            continue
        try:
            json.dumps(value)
        except (TypeError, ValueError):
            continue
        out[key] = value
    return out


def _normalise_endpoint(handler_ref: str) -> str:
    if handler_ref.startswith("node://"):
        handler_ref = "http://" + handler_ref[len("node://") :]
    parts = urlsplit(handler_ref)
    if parts.path in ("", "/"):
        handler_ref = handler_ref.rstrip("/") + DEFAULT_REMOTE_PATH
    return handler_ref


def make_remote_handler(handler_ref: str, *, timeout: int = DEFAULT_TIMEOUT) -> Handler:
    """Build a handler that forwards the URI envelope to a remote URI runtime."""
    endpoint = _normalise_endpoint(handler_ref)

    def handler(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        envelope = {
            "uri": context.get("uri"),
            "payload": payload or {},
            "context": _safe_context(context),
        }
        body = json.dumps(envelope).encode("utf-8")
        req = request.Request(endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with request.urlopen(req, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            return {"ok": False, "error": f"remote {exc.code}: {exc.reason}", "endpoint": endpoint}
        except Exception as exc:  # network/JSON errors
            return {"ok": False, "error": str(exc), "endpoint": endpoint}
        if not isinstance(data, dict):
            return {"ok": False, "error": "remote returned a non-object response", "endpoint": endpoint}
        if data.get("ok") is False:
            return {"ok": False, "error": data.get("error", "remote call failed"), "remote": data}
        # The remote /uri/call returns the full envelope; unwrap its inner result.
        return data.get("result", data)

    return handler


def load_handler(handler_ref: str, *, timeout: int = DEFAULT_TIMEOUT) -> Handler:
    """Load a handler for any supported scheme (python/http/https/node)."""
    if not handler_ref or "://" not in handler_ref:
        raise HandlerLoadError(f"Handler reference must include a scheme, got {handler_ref!r}.")
    scheme = handler_ref.split("://", 1)[0]
    if scheme == "python":
        return load_python_handler(handler_ref)
    if scheme in REMOTE_SCHEMES or scheme == "node":
        return make_remote_handler(handler_ref, timeout=timeout)
    raise HandlerLoadError(
        f"Unsupported handler scheme {scheme!r} in {handler_ref!r}. "
        "Supported: python://, http://, https://, node://."
    )


__all__ = ["Handler", "load_handler", "load_python_handler", "make_remote_handler"]
