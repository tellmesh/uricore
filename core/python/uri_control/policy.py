from __future__ import annotations

from typing import Any

from .models import MatchedRoute, PolicyDecision


class PolicyEngine:
    """Small deterministic policy gate.

    This is intentionally simple. A future `urisys` project can replace it with
    OPA, Cedar, Casbin, custom RBAC, signed approvals or device-specific policy.
    """

    def __init__(
        self,
        *,
        allowed_schemes: set[str] | None = None,
        denied_schemes: set[str] | None = None,
    ) -> None:
        self.allowed_schemes = allowed_schemes
        self.denied_schemes = denied_schemes or set()

    def decide(self, matched: MatchedRoute, context: dict[str, Any] | None = None) -> PolicyDecision:
        context = context or {}
        route = matched.route

        if route.scheme in self.denied_schemes:
            return PolicyDecision(
                allowed=False,
                reason=f"Scheme {route.scheme!r} is denied.",
                requires_approval=False,
                route_kind=route.kind,
                operation=route.operation,
            )

        if self.allowed_schemes is not None and route.scheme not in self.allowed_schemes:
            return PolicyDecision(
                allowed=False,
                reason=f"Scheme {route.scheme!r} is not in allowed_schemes.",
                requires_approval=False,
                route_kind=route.kind,
                operation=route.operation,
            )

        requires_approval = route.side_effects and route.approval == "required"
        if requires_approval and not bool(context.get("approved")):
            return PolicyDecision(
                allowed=False,
                reason="Approval required for side-effect operation.",
                requires_approval=True,
                route_kind=route.kind,
                operation=route.operation,
            )

        if route.approval == "never":
            return PolicyDecision(
                allowed=False,
                reason="Operation is marked approval=never and cannot be executed.",
                requires_approval=False,
                route_kind=route.kind,
                operation=route.operation,
            )

        return PolicyDecision(
            allowed=True,
            reason="Allowed.",
            requires_approval=requires_approval,
            route_kind=route.kind,
            operation=route.operation,
        )
