from __future__ import annotations

import time
import uuid
from typing import Any

from .event_store import EventStore, InMemoryEventStore
from .models import DispatchResult, EventEnvelope
from .policy import PolicyEngine
from .registry import CapabilityRegistry


def _now_ms() -> int:
    return int(time.time() * 1000)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


class UriControlRuntime:
    """URI → manifest route → policy → handler → event."""

    def __init__(
        self,
        *,
        registry: CapabilityRegistry,
        event_store: EventStore | None = None,
        policy_engine: PolicyEngine | None = None,
    ) -> None:
        self.registry = registry
        self.event_store = event_store or InMemoryEventStore()
        self.policy_engine = policy_engine or PolicyEngine()

    def call(
        self,
        uri: str,
        payload: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> DispatchResult:
        payload = payload or {}
        context = context or {}
        matched = self.registry.match(uri)
        route = matched.route
        policy = self.policy_engine.decide(matched, context)

        if not policy.allowed:
            event = EventEnvelope(
                event_id=_new_id("evt"),
                event_type="PolicyDenied",
                source_uri=uri,
                occurred_at_unix_ms=_now_ms(),
                data={"reason": policy.reason, "payload": payload},
                metadata={
                    "operation": route.operation,
                    "manifest_id": route.manifest_id,
                },
            )
            self.event_store.append(event)
            return DispatchResult(
                ok=False,
                uri=uri,
                operation=route.operation,
                event=event,
                error=policy.reason,
                policy=policy,
                metadata={"manifest_id": route.manifest_id, "pattern": route.pattern},
            )

        command_id = _new_id("cmd")
        accepted = EventEnvelope(
            event_id=_new_id("evt"),
            event_type="CommandAccepted" if route.kind == "command" else "QueryAccepted",
            source_uri=uri,
            occurred_at_unix_ms=_now_ms(),
            data={"payload": payload, "variables": matched.variables},
            metadata={
                "command_id": command_id,
                "operation": route.operation,
                "manifest_id": route.manifest_id,
                "kind": route.kind,
            },
        )
        self.event_store.append(accepted)

        if matched.handler is None:
            event = EventEnvelope(
                event_id=_new_id("evt"),
                event_type="OperationFailed",
                source_uri=uri,
                occurred_at_unix_ms=_now_ms(),
                data={"error": "No handler configured for route."},
                metadata={"command_id": command_id, "operation": route.operation},
            )
            self.event_store.append(event)
            return DispatchResult(
                ok=False,
                uri=uri,
                operation=route.operation,
                event=event,
                error="No handler configured for route.",
                policy=policy,
                metadata={"manifest_id": route.manifest_id, "pattern": route.pattern},
            )

        handler_context = {
            **context,
            "uri": uri,
            "operation": route.operation,
            "kind": route.kind,
            "command_id": command_id,
            "variables": matched.variables,
            "parsed_uri": matched.parsed_uri,
            "route": route,
        }

        try:
            result = matched.handler(payload, handler_context)
            if result is None:
                result = {}
            if not isinstance(result, dict):
                result = {"value": result}

            event = EventEnvelope(
                event_id=_new_id("evt"),
                event_type=route.success_event_type or "OperationCompleted",
                source_uri=uri,
                occurred_at_unix_ms=_now_ms(),
                data=result,
                metadata={"command_id": command_id, "operation": route.operation},
            )
            self.event_store.append(event)

            return DispatchResult(
                ok=True,
                uri=uri,
                operation=route.operation,
                result=result,
                event=event,
                policy=policy,
                metadata={
                    "manifest_id": route.manifest_id,
                    "pattern": route.pattern,
                    "variables": matched.variables,
                },
            )

        except Exception as exc:
            event = EventEnvelope(
                event_id=_new_id("evt"),
                event_type="OperationFailed",
                source_uri=uri,
                occurred_at_unix_ms=_now_ms(),
                data={"error": str(exc), "payload": payload},
                metadata={"command_id": command_id, "operation": route.operation},
            )
            self.event_store.append(event)

            return DispatchResult(
                ok=False,
                uri=uri,
                operation=route.operation,
                event=event,
                error=str(exc),
                policy=policy,
                metadata={"manifest_id": route.manifest_id, "pattern": route.pattern},
            )
