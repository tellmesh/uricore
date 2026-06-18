"""Resolver hook protocol — uricore stays independent of uri_router import graph."""

from __future__ import annotations

from typing import Any, Protocol


class ResolverHook(Protocol):
    """Optional placement + transport delegation before local route matching."""

    def resolve(
        self, uri: str, config: dict[str, Any], context: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Return ``(resolved_uri, resolver_context)``."""

    def delegate_transport(
        self,
        *,
        source_uri: str,
        resolved_uri: str,
        payload: dict[str, Any],
        context: dict[str, Any],
        profile: dict[str, Any],
        transport: str,
    ) -> dict[str, Any] | None:
        """Return delegated call result, or ``None`` for local execution."""


class DefaultResolverHook:
    """Uses ``uri_control.resolver`` / ``uri_control.transport`` shims when installed."""

    def resolve(
        self, uri: str, config: dict[str, Any], context: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        try:
            from uri_control.resolver import resolve_uri

            return resolve_uri(uri, config, context)
        except Exception:
            return uri, {}

    def delegate_transport(
        self,
        *,
        source_uri: str,
        resolved_uri: str,
        payload: dict[str, Any],
        context: dict[str, Any],
        profile: dict[str, Any],
        transport: str,
    ) -> dict[str, Any] | None:
        try:
            from uri_control.transport import delegate_transport_call

            return delegate_transport_call(
                transport=transport,
                source_uri=source_uri,
                resolved_uri=resolved_uri,
                payload=payload,
                context=context,
                profile=profile,
            )
        except Exception as exc:
            return {
                "ok": False,
                "uri": source_uri,
                "type": "transport_error",
                "error": str(exc),
            }


__all__ = ["DefaultResolverHook", "ResolverHook"]
