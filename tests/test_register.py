"""Programmatic register() — the urisys edge-pack contract on the uricore engine.

These mirror how edge packs (urillm, uristt, urisysnode, ...) wire routes via
``runtime.register(pattern, handler, kind=..., operation=...)`` so the same pack
``register()`` functions can target uricore directly, without a manifest.yaml.
"""

from uri_control import CapabilityRegistry


def test_register_matches_like_edge_pack():
    registry = CapabilityRegistry()
    # Real urillm route shape (see urillm/urillm/routes.py); handler is an
    # importable stub so match() can eagerly load it inside uricore's own venv.
    registry.register(
        "llm://{host}/chat/query/completion",
        "python://json:dumps",
        kind="query",
        operation="llm.chat.completion",
    )

    matched = registry.match("llm://lenovo/chat/query/completion")

    assert matched.route.operation == "llm.chat.completion"
    assert matched.route.kind == "query"
    assert matched.route.scheme == "llm"
    assert matched.variables == {"host": "lenovo"}


def test_register_defaults_match_edge_runtime():
    registry = CapabilityRegistry()
    route = registry.register("node://{target}/query/health", "python://m:f")

    # operation defaults to the last path segment, exactly like urisysedge
    assert route.operation == "health"
    # edge defaults: side-effect-free, no approval unless asked
    assert route.side_effects is False
    assert route.approval == "not_required"
    assert route.kind == "command"


def test_match_route_does_not_load_handler():
    """Edge runtimes load handlers lazily; match_route must stay pure routing."""
    registry = CapabilityRegistry()
    registry.register(
        "stt://{host}/session/{session}/query/transcript",
        "python://does_not_exist_pkg.handlers:nope",  # intentionally unimportable
        kind="query",
        operation="stt.session.transcript",
    )

    matched = registry.match_route("stt://lenovo/session/abc/query/transcript")
    assert matched.route.operation == "stt.session.transcript"
    assert matched.variables == {"host": "lenovo", "session": "abc"}
    assert matched.handler is None  # NOT loaded

    # match() (handler-loading) would fail on the same unimportable ref
    try:
        registry.match("stt://lenovo/session/abc/query/transcript")
    except Exception:
        pass
    else:  # pragma: no cover
        raise AssertionError("match() should have raised on unimportable handler")


def test_register_requires_scheme():
    registry = CapabilityRegistry()
    try:
        registry.register("no-scheme/path", "python://m:f")
    except Exception as exc:  # RegistryError
        assert "scheme" in str(exc).lower()
    else:  # pragma: no cover
        raise AssertionError("expected RegistryError for scheme-less pattern")


def test_register_and_manifest_coexist():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    registry = CapabilityRegistry.from_manifest_files([
        root / "examples/packs/browser_mock/manifest.yaml",
    ])
    registry.register(
        "llm://{host}/text/query/plan",
        "python://json:dumps",
        kind="query",
        operation="llm.text.plan",
    )

    # both styles resolve through the one registry
    assert registry.match("browser://default/page/open").route.operation == "open_page"
    assert registry.match("llm://lenovo/text/query/plan").route.operation == "llm.text.plan"
