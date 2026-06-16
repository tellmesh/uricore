from pathlib import Path

from uri_control import CapabilityRegistry, JsonlEventStore, UriControlRuntime

ROOT = Path(__file__).resolve().parents[1]

registry = CapabilityRegistry.from_manifest_files([
    ROOT / "examples/packs/browser_mock/manifest.yaml",
])

runtime = UriControlRuntime(
    registry=registry,
    event_store=JsonlEventStore(ROOT / "output/browser-events.jsonl"),
)

print(
    runtime.call(
        "browser://default/page/open",
        payload={"url": "https://example.com", "wait_until_loaded": True},
        context={"approved": True, "environment": "mock"},
    ).to_dict()
)

print(
    runtime.call(
        "browser://default/page/dom",
        payload={},
        context={"environment": "mock"},
    ).to_dict()
)
