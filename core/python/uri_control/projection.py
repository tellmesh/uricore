from __future__ import annotations

from collections import defaultdict
from typing import Any

from .event_store import EventStore
from .models import EventEnvelope


class ProjectionBuilder:
    """Build read models from events.

    This is intentionally generic. Domain-specific projections should live in a
    future `urisys` project or in concrete capability packs.
    """

    def __init__(self, event_store: EventStore) -> None:
        self.event_store = event_store

    def latest_by_source_uri(self) -> dict[str, dict[str, Any]]:
        latest: dict[str, dict[str, Any]] = {}
        for event in self.event_store.read_all():
            latest[event.source_uri] = event.to_dict()
        return latest

    def status_by_source_uri(self) -> dict[str, dict[str, Any]]:
        status: dict[str, dict[str, Any]] = {}
        for event in self.event_store.read_all():
            current = status.setdefault(
                event.source_uri,
                {
                    "source_uri": event.source_uri,
                    "ok": None,
                    "last_event_type": None,
                    "last_event_id": None,
                    "last_changed_at_unix_ms": None,
                    "operation": None,
                    "error": None,
                },
            )
            current["last_event_type"] = event.event_type
            current["last_event_id"] = event.event_id
            current["last_changed_at_unix_ms"] = event.occurred_at_unix_ms
            current["operation"] = event.metadata.get("operation")
            if event.event_type in {"OperationFailed", "PolicyDenied"}:
                current["ok"] = False
                current["error"] = event.data.get("error") or event.data.get("reason")
            elif event.event_type.endswith("Event") or event.event_type in {
                "OperationCompleted",
                "CommandAccepted",
                "QueryAccepted",
            }:
                current["ok"] = True
                current["error"] = None
        return status

    def events_by_type(self) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for event in self.event_store.read_all():
            grouped[event.event_type].append(event.to_dict())
        return dict(grouped)

    @staticmethod
    def from_events(events: list[EventEnvelope]) -> "ProjectionBuilder":
        from .event_store import InMemoryEventStore

        store = InMemoryEventStore()
        for event in events:
            store.append(event)
        return ProjectionBuilder(store)
