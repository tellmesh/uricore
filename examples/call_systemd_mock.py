from pathlib import Path

from uri_control import CapabilityRegistry, JsonlEventStore, UriControlRuntime

ROOT = Path(__file__).resolve().parents[1]

registry = CapabilityRegistry.from_manifest_files([
    ROOT / "examples/packs/systemd_mock/manifest.yaml",
])

runtime = UriControlRuntime(
    registry=registry,
    event_store=JsonlEventStore(ROOT / "output/systemd-events.jsonl"),
)

print(runtime.call("systemd://unit/docker.service/query/status").to_dict())
print(
    runtime.call(
        "systemd://unit/docker.service/command/restart",
        context={"approved": True, "environment": "mock"},
    ).to_dict()
)
