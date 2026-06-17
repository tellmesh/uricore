from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

from .errors import RegistryError, RouteNotFoundError
from .handlers import load_handler as _load_handler, load_python_handler as _load_python_handler
from .models import CapabilityManifest, MatchedRoute, Route
from .parser import parse_uri

_HANDLER_PREFIX = "python://"


def _pattern_body(pattern: str, scheme: str) -> str:
    prefix = f"{scheme}://"
    if not pattern.startswith(prefix):
        raise RegistryError(f"Pattern {pattern!r} must start with {prefix!r}.")
    return pattern[len(prefix) :].strip("/")


def _compile_pattern(pattern: str, scheme: str) -> re.Pattern[str]:
    body = _pattern_body(pattern, scheme)
    parts = []
    for piece in body.split("/"):
        if piece.startswith("{") and piece.endswith("}"):
            name = piece[1:-1]
            if not name.isidentifier():
                raise RegistryError(f"Invalid variable name {name!r} in pattern {pattern!r}.")
            parts.append(fr"(?P<{name}>[^/]+)")
        elif piece == "*":
            parts.append(r".*")
        else:
            parts.append(re.escape(piece))
    return re.compile(r"^" + r"/".join(parts) + r"$")


class CapabilityRegistry:
    """In-memory registry of capability manifests and URI patterns."""

    def __init__(self) -> None:
        self._manifests: list[CapabilityManifest] = []
        self._compiled: list[tuple[Route, re.Pattern[str]]] = []
        self._handler_cache: dict[str, Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]] = {}

    @classmethod
    def from_manifest_files(cls, paths: Iterable[str | Path]) -> "CapabilityRegistry":
        registry = cls()
        for path in paths:
            registry.load_manifest_file(path)
        return registry

    @property
    def manifests(self) -> tuple[CapabilityManifest, ...]:
        return tuple(self._manifests)

    @property
    def routes(self) -> tuple[Route, ...]:
        return tuple(route for route, _ in self._compiled)

    def load_manifest_file(self, path: str | Path) -> CapabilityManifest:
        manifest_path = Path(path)
        with manifest_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise RegistryError(f"Manifest {path} must contain a YAML mapping.")
        manifest = self.load_manifest(data)
        return manifest

    def load_manifest(self, data: dict[str, Any]) -> CapabilityManifest:
        manifest_id = str(data.get("id") or "")
        version = data.get("version", 1)
        scheme = str(data.get("scheme") or "")

        if not manifest_id:
            raise RegistryError("Manifest must define id.")
        if not scheme:
            raise RegistryError(f"Manifest {manifest_id!r} must define scheme.")

        handlers = data.get("handlers", {}) or {}
        python_handlers = (handlers.get("python") or {}) if isinstance(handlers, dict) else {}
        routes: list[Route] = []

        for item in data.get("uri_patterns", []) or []:
            if not isinstance(item, dict):
                raise RegistryError(f"Invalid route in manifest {manifest_id!r}: {item!r}")

            pattern = str(item.get("pattern") or "")
            operation = str(item.get("operation") or "")
            kind = str(item.get("kind") or "")

            if not pattern or not operation or not kind:
                raise RegistryError(
                    f"Route in manifest {manifest_id!r} must define pattern, kind and operation."
                )

            handler_ref = item.get("handler") or python_handlers.get(operation)

            route = Route(
                manifest_id=manifest_id,
                scheme=scheme,
                pattern=pattern,
                kind=kind,  # type: ignore[arg-type]
                operation=operation,
                handler_ref=handler_ref,
                command_type=item.get("command_type"),
                query_type=item.get("query_type"),
                result_type=item.get("result_type"),
                success_event_type=item.get("success_event_type"),
                side_effects=bool(item.get("side_effects", kind == "command")),
                approval=item.get("approval", "required" if kind == "command" else "not_required"),
                metadata={k: v for k, v in item.items() if k not in {"pattern", "kind", "operation"}},
            )
            routes.append(route)
            self._compiled.append((route, _compile_pattern(pattern, scheme)))

        manifest = CapabilityManifest(
            id=manifest_id,
            version=version,
            scheme=scheme,
            routes=tuple(routes),
            raw=data,
        )
        self._manifests.append(manifest)
        return manifest

    def register(
        self,
        pattern: str,
        handler_ref: str,
        *,
        kind: str = "command",
        operation: str | None = None,
        approval: str = "not_required",
        side_effects: bool = False,
        manifest_id: str = "programmatic",
    ) -> Route:
        """Register a single route programmatically.

        Mirrors the ``register(pattern, handler, kind=..., operation=...)``
        contract used by urisys edge packs so the same pack ``register()``
        functions can target the uricore engine directly, without requiring a
        ``manifest.yaml``. Defaults match the edge runtime exactly to keep
        existing packs behaviourally identical.
        """

        if "://" not in pattern:
            raise RegistryError(f"Pattern {pattern!r} must contain a scheme, e.g. scheme://...")
        scheme = pattern.split("://", 1)[0]
        if not scheme:
            raise RegistryError(f"Pattern {pattern!r} has an empty scheme.")

        operation = operation or pattern.rsplit("/", 1)[-1]
        route = Route(
            manifest_id=manifest_id,
            scheme=scheme,
            pattern=pattern,
            kind=kind,  # type: ignore[arg-type]
            operation=operation,
            handler_ref=handler_ref,
            side_effects=side_effects,
            approval=approval,  # type: ignore[arg-type]
        )
        self._compiled.append((route, _compile_pattern(pattern, scheme)))
        return route

    def match_route(self, uri: str) -> MatchedRoute:
        """Resolve a URI to its route and variables, WITHOUT loading the handler.

        Pure routing. Useful for runtimes that load handlers lazily with their
        own loader (e.g. the urisys edge runtime) and for explain/inspection
        that should not import handler modules. The returned ``MatchedRoute``
        has ``handler=None``.
        """

        parsed = parse_uri(uri)
        body = parsed.body.strip("/")

        for route, compiled in self._compiled:
            if parsed.scheme != route.scheme:
                continue
            match = compiled.match(body)
            if not match:
                continue
            return MatchedRoute(
                route=route,
                parsed_uri=parsed,
                variables=match.groupdict(),
                handler=None,
            )

        raise RouteNotFoundError(f"No capability route matches URI {uri!r}.")

    def match(self, uri: str) -> MatchedRoute:
        matched = self.match_route(uri)
        route = matched.route
        handler = None
        if route.handler_ref:
            handler = self._handler_cache.get(route.handler_ref)
            if handler is None:
                handler = _load_handler(route.handler_ref)
                self._handler_cache[route.handler_ref] = handler
        if handler is matched.handler:
            return matched
        return MatchedRoute(
            route=route,
            parsed_uri=matched.parsed_uri,
            variables=matched.variables,
            handler=handler,
        )

    def explain(self, uri: str) -> dict[str, Any]:
        matched = self.match(uri)
        route = matched.route
        return {
            "uri": uri,
            "scheme": matched.parsed_uri.scheme,
            "body": matched.parsed_uri.body,
            "manifest_id": route.manifest_id,
            "pattern": route.pattern,
            "kind": route.kind,
            "operation": route.operation,
            "variables": matched.variables,
            "command_type": route.command_type,
            "query_type": route.query_type,
            "result_type": route.result_type,
            "success_event_type": route.success_event_type,
            "side_effects": route.side_effects,
            "approval": route.approval,
            "handler_ref": route.handler_ref,
        }
