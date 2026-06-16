from pathlib import Path

from uri_control import CapabilityRegistry, InMemoryEventStore, UriControlRuntime

ROOT = Path(__file__).resolve().parents[1]


def _runtime():
    registry = CapabilityRegistry.from_manifest_files([
        ROOT / "examples/packs/browser_mock/manifest.yaml",
    ])
    store = InMemoryEventStore()
    return UriControlRuntime(registry=registry, event_store=store), store


def test_command_requires_approval():
    runtime, store = _runtime()

    result = runtime.call(
        "browser://default/page/open",
        payload={"url": "https://example.com"},
    )

    assert not result.ok
    assert result.error == "Approval required for side-effect operation."
    assert store.read_all()[-1].event_type == "PolicyDenied"


def test_command_executes_when_approved():
    runtime, store = _runtime()

    result = runtime.call(
        "browser://default/page/open",
        payload={"url": "https://example.com"},
        context={"approved": True},
    )

    assert result.ok
    assert result.result["url"] == "https://example.com"
    assert store.read_all()[-1].event_type == "browser.v1.PageOpenedEvent"


def test_query_does_not_require_approval():
    runtime, _ = _runtime()

    result = runtime.call("browser://default/page/dom")

    assert result.ok
    assert "html" in result.result
