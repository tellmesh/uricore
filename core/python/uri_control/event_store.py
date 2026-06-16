from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from .models import EventEnvelope


class EventStore(ABC):
    @abstractmethod
    def append(self, event: EventEnvelope) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_all(self) -> list[EventEnvelope]:
        raise NotImplementedError


class InMemoryEventStore(EventStore):
    def __init__(self) -> None:
        self._events: list[EventEnvelope] = []

    def append(self, event: EventEnvelope) -> None:
        self._events.append(event)

    def read_all(self) -> list[EventEnvelope]:
        return list(self._events)


class JsonlEventStore(EventStore):
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: EventEnvelope) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")

    def read_all(self) -> list[EventEnvelope]:
        if not self.path.exists():
            return []
        events: list[EventEnvelope] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                events.append(
                    EventEnvelope(
                        event_id=data["event_id"],
                        event_type=data["event_type"],
                        source_uri=data["source_uri"],
                        occurred_at_unix_ms=int(data["occurred_at_unix_ms"]),
                        data=data.get("data") or {},
                        metadata=data.get("metadata") or {},
                    )
                )
        return events


def dump_events(events: Iterable[EventEnvelope]) -> list[dict]:
    return [event.to_dict() for event in events]
