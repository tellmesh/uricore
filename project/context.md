# System Architecture Analysis
<!-- generated in 0.00s -->

## Overview

- **Project**: /home/tom/github/tellmesh/uricore
- **Primary Language**: python
- **Languages**: python: 34, yaml: 3, shell: 2, json: 2, proto: 2
- **Analysis Mode**: static
- **Total Functions**: 125
- **Total Classes**: 24
- **Modules**: 47
- **Entry Points**: 58

## Architecture by Module

### core.python.uri_control.edge.runtime
- **Functions**: 18
- **Classes**: 3
- **File**: `runtime.py`

### core.python.uri_control.edge.flow_refs
- **Functions**: 10
- **File**: `flow_refs.py`

### core.python.uri_control.registry
- **Functions**: 10
- **Classes**: 1
- **File**: `registry.py`

### core.python.uri_control.event_store
- **Functions**: 9
- **Classes**: 3
- **File**: `event_store.py`

### core.python.uri_control.edge.compose
- **Functions**: 9
- **File**: `compose.py`

### core.python.uri_control.edge.flow_expect
- **Functions**: 9
- **File**: `flow_expect.py`

### core.python.uri_control.cli
- **Functions**: 9
- **File**: `cli.py`

### core.python.uri_control.edge.env
- **Functions**: 7
- **File**: `env.py`

### core.python.uri_control.edge.manifest
- **Functions**: 5
- **File**: `manifest.py`

### core.python.uri_control.handlers
- **Functions**: 5
- **File**: `handlers.py`

### core.python.uri_control.projection
- **Functions**: 5
- **Classes**: 1
- **File**: `projection.py`

### core.python.uri_control.dispatcher
- **Functions**: 4
- **Classes**: 1
- **File**: `dispatcher.py`

### core.python.uri_control.edge.http
- **Functions**: 4
- **File**: `http.py`

### core.python.uri_control.runtime_handlers
- **Functions**: 3
- **File**: `runtime_handlers.py`

### core.python.uri_control.edge.cli
- **Functions**: 3
- **File**: `cli.py`

### examples.packs.systemd_mock.handlers
- **Functions**: 2
- **File**: `handlers.py`

### examples.packs.browser_mock.handlers
- **Functions**: 2
- **File**: `handlers.py`

### core.python.uri_control.edge.risk_policy
- **Functions**: 2
- **File**: `risk_policy.py`

### core.python.uri_control.parser
- **Functions**: 2
- **File**: `parser.py`

### core.python.uri_control.policy
- **Functions**: 2
- **Classes**: 1
- **File**: `policy.py`

## Key Entry Points

Main execution flows into the system:

### core.python.uri_control.edge.cli.build_edge_cli
> Return a ``main(argv)`` argparse entry point for an edge package.
- **Calls**: core.python.uri_control.edge.cli._json_arg, getattr, getattr, core.python.uri_control.edge.compose.build_runtime, rt.call, core.python.uri_control.edge.cli._emit, core.python.uri_control.edge.compose.build_runtime, rt.resolve

### core.python.uri_control.edge.runtime.Runtime.call
- **Calls**: bool, core.python.uri_control.edge.risk_policy.check_risk_requirements, check_operation_limits, check_shell_policy, dict, ctx.update, self.events.append, resolve_uri

### core.python.uri_control.registry.CapabilityRegistry.load_manifest
- **Calls**: str, data.get, str, CapabilityManifest, self._manifests.append, RegistryError, RegistryError, data.get

### core.python.uri_control.dispatcher.UriControlRuntime.call
- **Calls**: self.registry.match, self.policy_engine.decide, core.python.uri_control.dispatcher._new_id, EventEnvelope, self.event_store.append, EventEnvelope, self.event_store.append, DispatchResult

### core.python.uri_control.edge.env.load_urisys_env
> Load urisys/.env without overriding existing environment variables.
- **Calls**: os.environ.get, candidates.append, candidates.append, None.splitlines, str, Path, core.python.uri_control.edge.env._urisys_root, path.is_file

### core.python.uri_control.edge.runtime.JsonlEventStore.append
- **Calls**: dict, row.setdefault, row.setdefault, str, int, self.path.open, f.write, uuid.uuid4

### core.python.uri_control.event_store.JsonlEventStore.read_all
- **Calls**: self.path.exists, self.path.open, line.strip, json.loads, events.append, EventEnvelope, int, data.get

### core.python.uri_control.edge.env.resolve_env_var
> Resolve env var via env:// policy when available, else process environment.
- **Calls**: name.upper, os.environ.get, core.python.uri_control.edge.env._env_config, core.python.uri_control.edge.env.load_env_policy, isinstance, secret_value, result.get, var_value

### core.python.uri_control.cli.cmd_call
- **Calls**: core.python.uri_control.cli._registry_from_args, JsonlEventStore, UriControlRuntime, runtime.call, print, json.dumps, core.python.uri_control.cli._load_payload, result.to_dict

### core.python.uri_control.policy.PolicyEngine.decide
- **Calls**: PolicyDecision, PolicyDecision, PolicyDecision, PolicyDecision, PolicyDecision, bool, context.get

### core.python.uri_control.edge.runtime.Route.compile
- **Calls**: re.compile, len, self.pattern.index, parts.append, parts.append, re.escape, None.join

### core.python.uri_control.edge.runtime.Runtime.resolve
- **Calls**: KeyError, Route, route.match, self._registry.match_route, dict, KeyError, self._operation_risk.get

### core.python.uri_control.projection.ProjectionBuilder.status_by_source_uri
- **Calls**: self.event_store.read_all, status.setdefault, event.metadata.get, event.data.get, event.data.get, event.event_type.endswith

### core.python.uri_control.registry.CapabilityRegistry.load_manifest_file
- **Calls**: Path, self.load_manifest, manifest_path.open, isinstance, RegistryError, yaml.safe_load

### core.python.uri_control.registry.CapabilityRegistry.match_route
> Resolve a URI to its route and variables, WITHOUT loading the handler.

Pure routing. Useful for runtimes that load handlers lazily with their
own loa
- **Calls**: core.python.uri_control.parser.parse_uri, parsed.body.strip, RouteNotFoundError, compiled.match, MatchedRoute, match.groupdict

### core.python.uri_control.edge.http.serve
- **Calls**: ThreadingHTTPServer, print, core.python.uri_control.edge.http._routes_list, server.serve_forever, core.python.uri_control.edge.http.make_uri_handler, print

### core.python.uri_control.edge.runtime.Runtime.register
- **Calls**: isinstance, self.routes.append, None.compile, self._registry.register, pattern.rsplit, Route

### examples.packs.browser_mock.handlers.open_page
- **Calls**: context.get, payload.get, variables.get, payload.get, payload.get

### core.python.uri_control.cli.cmd_projection_latest
- **Calls**: JsonlEventStore, ProjectionBuilder, print, json.dumps, builder.latest_by_source_uri

### core.python.uri_control.cli.cmd_projection_status
- **Calls**: JsonlEventStore, ProjectionBuilder, print, json.dumps, builder.status_by_source_uri

### core.python.uri_control.projection.ProjectionBuilder.events_by_type
- **Calls**: defaultdict, self.event_store.read_all, dict, None.append, event.to_dict

### core.python.uri_control.edge.runtime.Route.match
- **Calls**: self._regex.match, self.compile, unquote, None.items, m.groupdict

### core.python.uri_control.edge.runtime.JsonlEventStore.tail
- **Calls**: None.splitlines, self.path.exists, self.path.read_text, out.append, json.loads

### core.python.uri_control.edge.runtime.load_json
- **Calls**: Path, json.loads, p.exists, FileNotFoundError, p.read_text

### core.python.uri_control.event_store.JsonlEventStore.append
- **Calls**: self.path.open, f.write, json.dumps, event.to_dict

### examples.packs.browser_mock.handlers.get_dom
- **Calls**: _SESSIONS.get, context.get, payload.get, variables.get

### core.python.uri_control.cli.cmd_explain
- **Calls**: core.python.uri_control.cli._registry_from_args, print, json.dumps, registry.explain

### core.python.uri_control.cli.main
- **Calls**: core.python.uri_control.cli.build_parser, parser.parse_args, int, args.func

### core.python.uri_control.registry.CapabilityRegistry.match
- **Calls**: self.match_route, MatchedRoute, self._handler_cache.get, core.python.uri_control.edge.runtime.Runtime._load_handler

### examples.packs.systemd_mock.handlers.unit_status
- **Calls**: None.get, _UNIT_STATE.get, context.get

## Process Flows

Key execution flows identified:

### Flow 1: build_edge_cli
```
build_edge_cli [core.python.uri_control.edge.cli]
  └─> _json_arg
  └─ →> build_runtime
      └─> _split
      └─> register_packs
          └─> register_pack
```

### Flow 2: call
```
call [core.python.uri_control.edge.runtime.Runtime]
  └─ →> check_risk_requirements
      └─> _violation
```

### Flow 3: load_manifest
```
load_manifest [core.python.uri_control.registry.CapabilityRegistry]
```

### Flow 4: load_urisys_env
```
load_urisys_env [core.python.uri_control.edge.env]
```

### Flow 5: append
```
append [core.python.uri_control.edge.runtime.JsonlEventStore]
```

### Flow 6: read_all
```
read_all [core.python.uri_control.event_store.JsonlEventStore]
```

### Flow 7: resolve_env_var
```
resolve_env_var [core.python.uri_control.edge.env]
  └─> _env_config
  └─> load_env_policy
      └─> _env_policy_candidates
          └─> _urisys_root
```

### Flow 8: cmd_call
```
cmd_call [core.python.uri_control.cli]
  └─> _registry_from_args
```

### Flow 9: decide
```
decide [core.python.uri_control.policy.PolicyEngine]
```

### Flow 10: compile
```
compile [core.python.uri_control.edge.runtime.Route]
```

## Key Classes

### core.python.uri_control.registry.CapabilityRegistry
> In-memory registry of capability manifests and URI patterns.
- **Methods**: 10
- **Key Methods**: core.python.uri_control.registry.CapabilityRegistry.__init__, core.python.uri_control.registry.CapabilityRegistry.from_manifest_files, core.python.uri_control.registry.CapabilityRegistry.manifests, core.python.uri_control.registry.CapabilityRegistry.routes, core.python.uri_control.registry.CapabilityRegistry.load_manifest_file, core.python.uri_control.registry.CapabilityRegistry.load_manifest, core.python.uri_control.registry.CapabilityRegistry.register, core.python.uri_control.registry.CapabilityRegistry.match_route, core.python.uri_control.registry.CapabilityRegistry.match, core.python.uri_control.registry.CapabilityRegistry.explain

### core.python.uri_control.projection.ProjectionBuilder
> Build read models from events.

This is intentionally generic. Domain-specific projections should li
- **Methods**: 5
- **Key Methods**: core.python.uri_control.projection.ProjectionBuilder.__init__, core.python.uri_control.projection.ProjectionBuilder.latest_by_source_uri, core.python.uri_control.projection.ProjectionBuilder.status_by_source_uri, core.python.uri_control.projection.ProjectionBuilder.events_by_type, core.python.uri_control.projection.ProjectionBuilder.from_events

### core.python.uri_control.edge.runtime.Runtime
- **Methods**: 5
- **Key Methods**: core.python.uri_control.edge.runtime.Runtime.__init__, core.python.uri_control.edge.runtime.Runtime.register, core.python.uri_control.edge.runtime.Runtime.resolve, core.python.uri_control.edge.runtime.Runtime._load_handler, core.python.uri_control.edge.runtime.Runtime.call

### core.python.uri_control.event_store.InMemoryEventStore
- **Methods**: 3
- **Key Methods**: core.python.uri_control.event_store.InMemoryEventStore.__init__, core.python.uri_control.event_store.InMemoryEventStore.append, core.python.uri_control.event_store.InMemoryEventStore.read_all
- **Inherits**: EventStore

### core.python.uri_control.event_store.JsonlEventStore
- **Methods**: 3
- **Key Methods**: core.python.uri_control.event_store.JsonlEventStore.__init__, core.python.uri_control.event_store.JsonlEventStore.append, core.python.uri_control.event_store.JsonlEventStore.read_all
- **Inherits**: EventStore

### core.python.uri_control.edge.runtime.JsonlEventStore
- **Methods**: 3
- **Key Methods**: core.python.uri_control.edge.runtime.JsonlEventStore.__init__, core.python.uri_control.edge.runtime.JsonlEventStore.append, core.python.uri_control.edge.runtime.JsonlEventStore.tail

### core.python.uri_control.event_store.EventStore
- **Methods**: 2
- **Key Methods**: core.python.uri_control.event_store.EventStore.append, core.python.uri_control.event_store.EventStore.read_all
- **Inherits**: ABC

### core.python.uri_control.dispatcher.UriControlRuntime
> URI → manifest route → policy → handler → event.
- **Methods**: 2
- **Key Methods**: core.python.uri_control.dispatcher.UriControlRuntime.__init__, core.python.uri_control.dispatcher.UriControlRuntime.call

### core.python.uri_control.policy.PolicyEngine
> Small deterministic policy gate.

This is intentionally simple. A future `urisys` project can replac
- **Methods**: 2
- **Key Methods**: core.python.uri_control.policy.PolicyEngine.__init__, core.python.uri_control.policy.PolicyEngine.decide

### core.python.uri_control.edge.runtime.Route
- **Methods**: 2
- **Key Methods**: core.python.uri_control.edge.runtime.Route.compile, core.python.uri_control.edge.runtime.Route.match

### core.php.UriControl.src.UriControl.UriControl.UriControl
- **Methods**: 1
- **Key Methods**: core.php.UriControl.src.UriControl.UriControl.describePlaceholder

### core.python.uri_control.models.ParsedUri
- **Methods**: 1
- **Key Methods**: core.python.uri_control.models.ParsedUri.body

### core.python.uri_control.models.EventEnvelope
- **Methods**: 1
- **Key Methods**: core.python.uri_control.models.EventEnvelope.to_dict

### core.python.uri_control.models.DispatchResult
- **Methods**: 1
- **Key Methods**: core.python.uri_control.models.DispatchResult.to_dict

### core.python.uri_control.errors.UriControlError
> Base exception for uri_control.
- **Methods**: 0
- **Inherits**: Exception

### core.python.uri_control.errors.UriParseError
> Raised when a URI cannot be parsed.
- **Methods**: 0
- **Inherits**: UriControlError

### core.python.uri_control.errors.RegistryError
> Raised for invalid manifests or registry state.
- **Methods**: 0
- **Inherits**: UriControlError

### core.python.uri_control.errors.RouteNotFoundError
> Raised when no route matches a URI.
- **Methods**: 0
- **Inherits**: UriControlError

### core.python.uri_control.errors.HandlerLoadError
> Raised when a handler reference cannot be loaded.
- **Methods**: 0
- **Inherits**: UriControlError

### core.python.uri_control.errors.PolicyDeniedError
> Raised when policy denies a command or query.
- **Methods**: 0
- **Inherits**: UriControlError

## Data Transformation Functions

Key functions that process and transform data:

### core.python.uri_control.runtime_handlers.parse_runtime_handler
> Return ``(binding, operation)`` from ``runtime://<binding>/<operation>``.

``runtime://resolver/step
- **Output to**: None.strip, rest.split, handler_ref.startswith, HandlerLoadError, HandlerLoadError

### core.python.uri_control.parser.parse_uri
> Parse a URI into a stable internal structure.

The parser intentionally keeps the model simple. For 
- **Output to**: uri.strip, urlsplit, dict, tuple, ParsedUri

### core.python.uri_control.cli.build_parser
- **Output to**: argparse.ArgumentParser, parser.add_subparsers, sub.add_parser, explain.add_argument, explain.add_argument

### core.python.uri_control.edge.runtime._parse_flow_step
> Normalize one flow step to ``(uri, payload, step_id)``.
- **Output to**: isinstance, isinstance, ValueError, step.get, step.items

## Behavioral Patterns

### recursion_interpolate_value
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: core.python.uri_control.edge.flow_refs.interpolate_value

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `core.python.uri_control.edge.cli.build_edge_cli` - 57 calls
- `core.python.uri_control.edge.runtime.Runtime.call` - 50 calls
- `core.python.uri_control.edge.http.make_uri_handler` - 47 calls
- `core.python.uri_control.registry.CapabilityRegistry.load_manifest` - 37 calls
- `core.python.uri_control.edge.runtime.run_flow` - 37 calls
- `core.python.uri_control.dispatcher.UriControlRuntime.call` - 31 calls
- `core.python.uri_control.cli.build_parser` - 25 calls
- `core.python.uri_control.edge.flow_refs.evaluate_step_if` - 22 calls
- `core.python.uri_control.edge.flow_artifacts.sync_artifacts_to_runtime` - 21 calls
- `core.python.uri_control.edge.manifest.register_manifest_data` - 21 calls
- `core.python.uri_control.edge.runtime.load_yaml_flow` - 21 calls
- `core.python.uri_control.edge.flow_expect.evaluate_flow_expect` - 19 calls
- `core.python.uri_control.edge.risk_policy.check_risk_requirements` - 17 calls
- `core.python.uri_control.edge.env.load_urisys_env` - 17 calls
- `core.python.uri_control.handlers.make_remote_handler` - 15 calls
- `core.python.uri_control.edge.flow_refs.interpolate_value` - 11 calls
- `core.python.uri_control.edge.flow_refs.resolve_step_uri` - 11 calls
- `core.python.uri_control.edge.flow_refs.seed_flow_inputs` - 11 calls
- `core.python.uri_control.edge.compose.bundle_packs` - 11 calls
- `core.python.uri_control.parser.parse_uri` - 11 calls
- `core.python.uri_control.handlers.load_python_handler` - 11 calls
- `core.python.uri_control.edge.runtime.JsonlEventStore.append` - 10 calls
- `core.python.uri_control.event_store.JsonlEventStore.read_all` - 9 calls
- `core.python.uri_control.edge.env.resolve_env_var` - 9 calls
- `core.python.uri_control.runtime_handlers.make_runtime_handler` - 8 calls
- `core.python.uri_control.edge.compose.build_runtime` - 8 calls
- `core.python.uri_control.cli.cmd_call` - 8 calls
- `core.python.uri_control.runtime_handlers.parse_runtime_handler` - 7 calls
- `core.python.uri_control.edge.flow_refs.resolve_ref` - 7 calls
- `core.python.uri_control.policy.PolicyEngine.decide` - 7 calls
- `core.python.uri_control.handlers.load_handler` - 7 calls
- `core.python.uri_control.registry.CapabilityRegistry.register` - 7 calls
- `core.python.uri_control.edge.runtime.Route.compile` - 7 calls
- `core.python.uri_control.edge.runtime.Runtime.resolve` - 7 calls
- `core.python.uri_control.edge.compose.register_pack` - 6 calls
- `core.python.uri_control.projection.ProjectionBuilder.status_by_source_uri` - 6 calls
- `core.python.uri_control.registry.CapabilityRegistry.load_manifest_file` - 6 calls
- `core.python.uri_control.registry.CapabilityRegistry.match_route` - 6 calls
- `core.python.uri_control.edge.http.serve` - 6 calls
- `core.python.uri_control.edge.runtime.Runtime.register` - 6 calls

## System Interactions

How components interact:

```mermaid
graph TD
    build_edge_cli --> _json_arg
    build_edge_cli --> getattr
    build_edge_cli --> build_runtime
    build_edge_cli --> call
    call --> bool
    call --> check_risk_requireme
    call --> check_operation_limi
    call --> check_shell_policy
    call --> dict
    load_manifest --> str
    load_manifest --> get
    load_manifest --> CapabilityManifest
    load_manifest --> append
    call --> match
    call --> decide
    call --> _new_id
    call --> EventEnvelope
    call --> append
    load_urisys_env --> get
    load_urisys_env --> append
    load_urisys_env --> splitlines
    load_urisys_env --> str
    append --> dict
    append --> setdefault
    append --> str
    append --> int
    read_all --> exists
    read_all --> open
    read_all --> strip
    read_all --> loads
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.