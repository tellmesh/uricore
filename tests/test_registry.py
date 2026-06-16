from pathlib import Path

from uri_control import CapabilityRegistry

ROOT = Path(__file__).resolve().parents[1]


def test_registry_matches_browser_route():
    registry = CapabilityRegistry.from_manifest_files([
        ROOT / "examples/packs/browser_mock/manifest.yaml",
    ])

    matched = registry.match("browser://default/page/open")

    assert matched.route.operation == "open_page"
    assert matched.variables == {"session": "default"}
    assert matched.handler is not None


def test_registry_explain():
    registry = CapabilityRegistry.from_manifest_files([
        ROOT / "examples/packs/browser_mock/manifest.yaml",
    ])
    explanation = registry.explain("browser://abc/page/dom")

    assert explanation["kind"] == "query"
    assert explanation["operation"] == "get_dom"
    assert explanation["variables"] == {"session": "abc"}
