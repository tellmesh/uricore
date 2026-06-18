"""Capability risk profile enforcement."""

from __future__ import annotations

from uri_control.edge.risk_policy import check_risk_requirements


def test_high_risk_requires_dry_run_or_allow_real():
    risk = {"class": "physical_process", "level": "high", "requires": ["approval", "dry_run_supported"]}
    violation = check_risk_requirements(risk, {"approved": True}, operation="demo.run")
    assert violation is not None
    assert violation["type"] == "risk_dry_run_required"

    assert check_risk_requirements(risk, {"approved": True, "dry_run": True}, operation="demo.run") is None
    assert check_risk_requirements(risk, {"approved": True, "allow_real": True}, operation="demo.run") is None


def test_audit_required_for_critical():
    risk = {"level": "critical", "requires": ["audit"]}
    violation = check_risk_requirements(risk, {"approved": True, "dry_run": True}, operation="shell.run")
    assert violation is not None
    assert violation["type"] == "risk_audit_required"

    ok = check_risk_requirements(
        risk,
        {"approved": True, "dry_run": True, "audit": {"reason": "maintenance"}},
        operation="shell.run",
    )
    assert ok is None
