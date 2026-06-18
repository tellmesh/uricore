"""Runtime.call pipeline — normalize → resolve → policy → handler → event."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .resolver_hook import DefaultResolverHook, ResolverHook

if TYPE_CHECKING:
    from ..runtime import Route, Runtime


class RuntimeCallPipeline:
    """Orchestrates a single URI call through the edge runtime stages."""

    def __init__(self, runtime: Runtime, resolver_hook: ResolverHook | None = None):
        self.runtime = runtime
        self.resolver_hook = resolver_hook or DefaultResolverHook()

    def call(
        self,
        uri: str,
        payload: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = payload or {}
        context = dict(context or {})

        resolved_uri, resolver_ctx = self.resolver_hook.resolve(uri, self.runtime.config or {}, context)
        if resolver_ctx:
            context.update(resolver_ctx)

        delegated = self._maybe_delegate(uri, resolved_uri, payload, context, resolver_ctx)
        if delegated is not None:
            return delegated

        try:
            route, params = self.runtime.resolve(resolved_uri)
        except Exception as exc:
            return {"ok": False, "uri": uri, "type": "route_not_found", "error": str(exc)}

        policy_violation = self.runtime._check_policies(route, uri, payload, params, context)
        if policy_violation is not None:
            return policy_violation

        ctx = self.runtime._build_call_context(uri, resolved_uri, params, context)
        return self.runtime._execute_handler(route, uri, resolved_uri, payload, ctx)

    def _maybe_delegate(
        self,
        source_uri: str,
        resolved_uri: str,
        payload: dict[str, Any],
        context: dict[str, Any],
        resolver_ctx: dict[str, Any],
    ) -> dict[str, Any] | None:
        profile = resolver_ctx.get("target_profile") if isinstance(resolver_ctx, dict) else None
        transport = resolver_ctx.get("transport") if isinstance(resolver_ctx, dict) else None
        if not isinstance(profile, dict) or not transport:
            return None
        return self.resolver_hook.delegate_transport(
            source_uri=source_uri,
            resolved_uri=resolved_uri,
            payload=payload,
            context=context,
            profile=profile,
            transport=str(transport),
        )


__all__ = ["RuntimeCallPipeline"]
