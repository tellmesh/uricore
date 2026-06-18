"""Built-in ``runtime://`` handler — the resolver-bound placeholder.

A process/contract capability may declare ``handler: runtime://resolver/<operation>``
to say *"where this URI actually runs is decided by the platform resolver"* rather
than binding a concrete in-process callable. At call time the resolver normally
forwards such a URI to a device/host over a transport (http/mqtt/ssh) **before** the
handler is ever loaded (see ``Runtime.call`` transport delegation). This handler is
what runs when no transport target claimed the URI — i.e. a pure local invocation:

* under ``context.dry_run`` or ``context.environment == "mock"`` it returns a
  deterministic mock result (``executed: False``) so a contract's own
  ``markpact:flow`` / ``markpact:tests`` run on a developer PC with no hardware;
* otherwise it returns a clear, actionable error instead of a cryptic
  "unsupported handler scheme" — telling the operator to configure a resolver
  target (a transport) for the URI authority, or run a device runtime that
  speaks ``POST /uri/call``.

Approval / side-effect policy is enforced by the runtime from the route metadata
*before* this handler is reached, so it does not re-check approval.
"""

from __future__ import annotations

from typing import Any, Callable

from .errors import HandlerLoadError

Handler = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]

RUNTIME_PREFIX = "runtime://"


def parse_runtime_handler(handler_ref: str) -> tuple[str, str]:
    """Return ``(binding, operation)`` from ``runtime://<binding>/<operation>``.

    ``runtime://resolver/stepper.move_relative`` -> ``("resolver", "stepper.move_relative")``.
    """
    if not handler_ref.startswith(RUNTIME_PREFIX):
        raise HandlerLoadError(f"Expected {RUNTIME_PREFIX}…, got {handler_ref!r}.")
    rest = handler_ref[len(RUNTIME_PREFIX) :].strip("/")
    if "/" not in rest:
        raise HandlerLoadError(
            f"Unsupported runtime handler {handler_ref!r}. Expected runtime://<binding>/<operation>."
        )
    binding, operation = rest.split("/", 1)
    if not binding or not operation:
        raise HandlerLoadError(f"Missing binding or operation in {handler_ref!r}.")
    return binding, operation


def make_runtime_handler(binding: str, operation: str) -> Handler:
    def handler(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        uri = context.get("uri") or context.get("source_uri")
        is_mock = bool(context.get("dry_run")) or context.get("environment") == "mock"
        if is_mock:
            return {
                "operation": operation,
                "runtime": "mock",
                "dry_run": bool(context.get("dry_run")),
                "executed": False,
                "binding": binding,
                "payload": dict(payload or {}),
            }
        return {
            "ok": False,
            "type": "no_runtime_binding",
            "operation": operation,
            "uri": uri,
            "error": (
                f"runtime://{binding}/{operation} has no local binding for {uri!r}. "
                f"Configure a resolver target (transport) for the URI authority, "
                f"or run a device runtime that speaks POST /uri/call."
            ),
        }

    return handler


def load_runtime_handler(handler_ref: str) -> Handler:
    binding, operation = parse_runtime_handler(handler_ref)
    return make_runtime_handler(binding, operation)


__all__ = [
    "RUNTIME_PREFIX",
    "load_runtime_handler",
    "make_runtime_handler",
    "parse_runtime_handler",
]
