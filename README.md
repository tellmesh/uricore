# uricore


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.8-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.36-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-4.9h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.3612 (8 commits)
- 👤 **Human dev:** ~$489 (4.9h @ $100/h, 30min dedup)

Generated on 2026-06-17 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

`uricore` is a small URI-native control-plane core. It provides a thin deterministic layer over software, services, devices and operating-system capabilities.

The Python distribution is named **`uricore`**, while the runtime module is **`uri_control`**:

```python
from uri_control import CapabilityRegistry, UriControlRuntime, JsonlEventStore
```

**URI intent routing** (resolve targets, HTTP/MQTT delegate, wire envelopes) lives in the sibling package **[`urirouter`](https://github.com/tellmesh/urirouter)** (`uri_router`). `uri_control.resolver`, `.transport`, and `.envelope` are compatibility shims over `uri_router`.

The repository also contains placeholder SDK folders for Node/TypeScript, Go and PHP. Those SDKs intentionally remain thin: the source of truth is the URI, the manifest, and the protobuf-style command/event envelope.

## Edge runtime (`uri_control.edge`)

Edge HTTP server, flow runner, and pack composition — formerly the separate **`urisysedge`** package (removed 2026-06):

```python
from uri_control.edge.runtime import Runtime, run_flow
from uri_control.edge.compose import build_runtime
from uri_control.edge.http import serve
```

Used by edge CLIs (`urirdpedge`, `urikvmedge`, …) and orchestrated by **[urisys](https://github.com/tellmesh/urisys)**.

## Architecture

```text
URI
  ↓
Capability manifest
  ↓
Policy decision
  ↓
Command / Query dispatch
  ↓
Handler in Python / Node / Go / PHP / any runtime
  ↓
Append-only event log
  ↓
Projection / status / result
```

Core rules:

1. URI does not execute.
2. URI identifies a resource, operation or intent.
3. Manifest declares capabilities, handlers and policy.
4. Handler performs the technical work.
5. Event store records facts.
6. Projection builds read models from events.

## Repository layout

```text
uricore/
  core/
    python/
      uri_control/
        parser.py
        registry.py
        dispatcher.py
        event_store.py
        projection.py
        policy.py
    node/uri-control/
    go/uricontrol/
    php/UriControl/
  contracts/
    proto/uricore/v1/envelope.proto
  examples/
    packs/browser_mock/
    packs/systemd_mock/
    call_browser_mock.py
    call_systemd_mock.py
  tests/
```

## Install locally

```bash
cd uricore
python -m pip install -e .
```

For tests:

```bash
python -m pip install -e .[dev]
python -m pytest
```

## CLI examples

Explain a URI against a manifest:

```bash
uricore explain browser://default/page/open \
  --manifest examples/packs/browser_mock/manifest.yaml
```

Call a command:

```bash
uricore call browser://default/page/open \
  --manifest examples/packs/browser_mock/manifest.yaml \
  --payload '{"url":"https://example.com","wait_until_loaded":true}' \
  --approve \
  --events output/events.jsonl
```

Query a projection from JSONL events:

```bash
uricore projection latest --events output/events.jsonl
```

## Minimal Python usage

```python
from uri_control import CapabilityRegistry, JsonlEventStore, UriControlRuntime

registry = CapabilityRegistry.from_manifest_files([
    "examples/packs/browser_mock/manifest.yaml"
])

runtime = UriControlRuntime(
    registry=registry,
    event_store=JsonlEventStore("output/events.jsonl"),
)

result = runtime.call(
    "browser://default/page/open",
    payload={"url": "https://example.com"},
    context={"approved": True, "environment": "mock"},
)

print(result.ok, result.result)
```

## Manifest example

```yaml
id: browser-mock-pack
version: 1
scheme: browser

uri_patterns:
  - pattern: browser://{session}/page/open
    kind: command
    operation: open_page
    command_type: browser.v1.OpenPageCommand
    success_event_type: browser.v1.PageOpenedEvent
    side_effects: true
    approval: required

handlers:
  python:
    open_page: python://examples.packs.browser_mock.handlers:open_page
```

## Relationship to `urisys`

`uricore` should stay small and deterministic. A future `urisys` project can reuse it and add:

- concrete device/software packs,
- HTTP or gRPC gateway,
- dashboard,
- scheduler,
- LLM planner,
- policy UI,
- multi-language runners.

`uricore` should not contain those heavier orchestration concerns.


## Ekosystem TellMesh

Orchestrator: **[urisys](https://github.com/tellmesh/urisys)** · Mapa: **[MESH.md](https://github.com/tellmesh/urisys/blob/main/docs/MESH.md)** · Model: **[ECOSYSTEM.md](https://github.com/tellmesh/urisys/blob/main/../docs/ECOSYSTEM.md)**

| Pole | Wartość |
|------|---------|
| **Warstwa** | Control plane + edge runtime |
| **Moduł** | `uri_control`, `uri_control.edge` |
| **Zależności** | `urirouter` |
| **Rola** | CapabilityRegistry, policy, handlers, `Runtime`, `compose`, `http.serve` |
| **Uwaga** | Zastępuje legacy `urisysedge` (usunięty 2026-06) |

Runtime edge: **`uri_control.edge`** w pakiecie **`uricore`** (legacy `urisysedge` usunięty 2026-06).
Router intencji: **`urirouter`** (`uri_router`) — resolve + HTTP/MQTT delegate.

<!-- end-ecosystem -->

## License

Licensed under Apache-2.0.
