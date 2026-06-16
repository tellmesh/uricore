from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal

UriKind = Literal["command", "query", "event", "resource", "view"]
ApprovalMode = Literal["required", "not_required", "never"]


@dataclass(frozen=True)
class ParsedUri:
    raw: str
    scheme: str
    authority: str
    path: tuple[str, ...]
    query: dict[str, str]
    fragment: str | None = None

    @property
    def body(self) -> str:
        """Return the matchable URI body after ``scheme://``.

        Example:
            ``browser://default/page/open`` -> ``default/page/open``
        """

        joined_path = "/".join(self.path)
        if self.authority and joined_path:
            return f"{self.authority}/{joined_path}"
        if self.authority:
            return self.authority
        return joined_path


@dataclass(frozen=True)
class Route:
    manifest_id: str
    scheme: str
    pattern: str
    kind: UriKind
    operation: str
    handler_ref: str | None = None
    command_type: str | None = None
    query_type: str | None = None
    result_type: str | None = None
    success_event_type: str | None = None
    side_effects: bool = False
    approval: ApprovalMode = "not_required"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MatchedRoute:
    route: Route
    parsed_uri: ParsedUri
    variables: dict[str, str] = field(default_factory=dict)
    handler: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None


@dataclass(frozen=True)
class CapabilityManifest:
    id: str
    version: str | int
    scheme: str
    routes: tuple[Route, ...]
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str = ""
    requires_approval: bool = False
    route_kind: str | None = None
    operation: str | None = None


@dataclass(frozen=True)
class EventEnvelope:
    event_id: str
    event_type: str
    source_uri: str
    occurred_at_unix_ms: int
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source_uri": self.source_uri,
            "occurred_at_unix_ms": self.occurred_at_unix_ms,
            "data": self.data,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class DispatchResult:
    ok: bool
    uri: str
    operation: str | None = None
    result: dict[str, Any] = field(default_factory=dict)
    event: EventEnvelope | None = None
    error: str | None = None
    policy: PolicyDecision | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "uri": self.uri,
            "operation": self.operation,
            "result": self.result,
            "event": self.event.to_dict() if self.event else None,
            "error": self.error,
            "policy": {
                "allowed": self.policy.allowed,
                "reason": self.policy.reason,
                "requires_approval": self.policy.requires_approval,
                "route_kind": self.policy.route_kind,
                "operation": self.policy.operation,
            }
            if self.policy
            else None,
            "metadata": self.metadata,
        }
