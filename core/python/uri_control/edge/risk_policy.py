"""Risk class requirements for high-impact URI operations."""

from __future__ import annotations

from typing import Any


def check_risk_requirements(
    risk: dict[str, Any] | None,
    context: dict[str, Any] | None,
    *,
    operation: str,
) -> dict[str, Any] | None:
    """Return violation dict when *context* does not satisfy declared ``risk.requires``."""
    if not isinstance(risk, dict):
        return None

    ctx = context or {}
    level = str(risk.get("level") or "").lower()
    requires = [str(r) for r in (risk.get("requires") or [])]

    if "approval" in requires and not ctx.get("approved"):
        return _violation(
            operation,
            "risk_approval_required",
            "approval required by capability risk profile",
        )

    if level in {"high", "critical"}:
        if "dry_run_supported" in requires and not ctx.get("dry_run") and not ctx.get("allow_real"):
            return _violation(
                operation,
                "risk_dry_run_required",
                f"operation {operation!r} risk level {level!r} requires dry_run or allow_real",
            )
        if "audit" in requires:
            audit = ctx.get("audit")
            if not isinstance(audit, dict) or not str(audit.get("reason") or "").strip():
                return _violation(
                    operation,
                    "risk_audit_required",
                    f"operation {operation!r} requires context.audit.reason",
                )

    return None


def _violation(operation: str, vtype: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "type": vtype,
        "operation": operation,
        "error": message,
    }


__all__ = ["check_risk_requirements"]
