# uricore

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `uricore`
- **version**: `0.1.9`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(2), app.doql.less, goal.yaml, .env.example, project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: uricore;
  version: 0.1.9;
}

dependencies {
  runtime: "PyYAML>=6.0, urirouter>=0.1.0";
  mqtt: urirouter[mqtt]>=0.1.0;
  dev: "pytest>=8.0, ruff>=0.6.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="uricore"] {
  entry: uri_control.cli:main;
}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=python -m pip install -e .;
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=python -m pytest;
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=python -m ruff check core/python tests examples;
}

workflow[name="example-browser"] {
  trigger: manual;
  step-1: run cmd=PYTHONPATH=core/python:. python examples/call_browser_mock.py;
}

workflow[name="example-systemd"] {
  trigger: manual;
  step-1: run cmd=PYTHONPATH=core/python:. python examples/call_systemd_mock.py;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS;
}

deploy {
  target: makefile;
}

environment[name="local"] {
  runtime: python;
  env_file: .env;
  template_file: .env.example;
  python_version: >=3.10;
  vars: LLM_MODEL, OPENROUTER_API_KEY, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
  runtime_llm: OPENROUTER_API_KEY;
  runtime_pfix: PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
}
```

## Workflows

## Dependencies

### Runtime

```text markpact:deps python
PyYAML>=6.0
urirouter>=0.1.0
```

### Development

```text markpact:deps python scope=dev
pytest>=8.0
ruff>=0.6.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Call Graph

*72 nodes · 62 edges · 15 modules · CC̄=4.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `build_edge_cli` *(in core.python.uri_control.edge.cli)* | 1 | 0 | 57 | **57** |
| `call` *(in core.python.uri_control.edge.runtime.Runtime)* | 22 ⚠ | 0 | 50 | **50** |
| `make_uri_handler` *(in core.python.uri_control.edge.http)* | 2 | 2 | 47 | **49** |
| `run_flow` *(in core.python.uri_control.edge.runtime)* | 19 ⚠ | 1 | 37 | **38** |
| `call` *(in core.python.uri_control.dispatcher.UriControlRuntime)* | 10 ⚠ | 0 | 31 | **31** |
| `build_parser` *(in core.python.uri_control.cli)* | 1 | 1 | 25 | **26** |
| `_order_flow_steps` *(in core.python.uri_control.edge.runtime)* | 21 ⚠ | 1 | 25 | **26** |
| `evaluate_step_if` *(in core.python.uri_control.edge.flow_refs)* | 9 | 1 | 22 | **23** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/uricore
# generated in 0.04s
# nodes: 72 | edges: 62 | modules: 15
# CC̄=4.6

HUBS[20]:
  core.python.uri_control.edge.cli.build_edge_cli
    CC=1  in:0  out:57  total:57
  core.python.uri_control.edge.runtime.Runtime.call
    CC=22  in:0  out:50  total:50
  core.python.uri_control.edge.http.make_uri_handler
    CC=2  in:2  out:47  total:49
  core.python.uri_control.edge.runtime.run_flow
    CC=19  in:1  out:37  total:38
  core.python.uri_control.dispatcher.UriControlRuntime.call
    CC=10  in:0  out:31  total:31
  core.python.uri_control.cli.build_parser
    CC=1  in:1  out:25  total:26
  core.python.uri_control.edge.runtime._order_flow_steps
    CC=21  in:1  out:25  total:26
  core.python.uri_control.edge.flow_refs.evaluate_step_if
    CC=9  in:1  out:22  total:23
  core.python.uri_control.edge.manifest.register_manifest_data
    CC=11  in:1  out:21  total:22
  core.python.uri_control.edge.runtime.load_yaml_flow
    CC=14  in:1  out:21  total:22
  core.python.uri_control.edge.flow_expect.evaluate_flow_expect
    CC=7  in:1  out:19  total:20
  core.python.uri_control.edge.risk_policy.check_risk_requirements
    CC=16  in:1  out:17  total:18
  core.python.uri_control.edge.env.load_urisys_env
    CC=8  in:0  out:17  total:17
  core.python.uri_control.edge.manifest._register_urisys_flows
    CC=8  in:2  out:14  total:16
  core.python.uri_control.handlers.make_remote_handler
    CC=1  in:1  out:15  total:16
  core.python.uri_control.edge.flow_expect._ocr_texts
    CC=12  in:1  out:15  total:16
  core.python.uri_control.edge.flow_refs.interpolate_value
    CC=8  in:4  out:11  total:15
  core.python.uri_control.registry._compile_pattern
    CC=6  in:2  out:12  total:14
  core.python.uri_control.edge.flow_expect._vision_confidences
    CC=12  in:1  out:13  total:14
  core.python.uri_control.edge.compose.build_runtime
    CC=6  in:6  out:8  total:14

MODULES:
  core.python.uri_control.cli  [7 funcs]
    _load_payload  CC=3  out:5
    _registry_from_args  CC=2  out:2
    build_parser  CC=1  out:25
    cmd_call  CC=2  out:8
    cmd_explain  CC=1  out:4
    cmd_list  CC=2  out:3
    main  CC=1  out:4
  core.python.uri_control.dispatcher  [2 funcs]
    call  CC=10  out:31
    _new_id  CC=1  out:1
  core.python.uri_control.edge.cli  [3 funcs]
    _emit  CC=1  out:2
    _json_arg  CC=3  out:5
    build_edge_cli  CC=1  out:57
  core.python.uri_control.edge.compose  [9 funcs]
    _bundle_block  CC=2  out:2
    _imports_contracts  CC=8  out:8
    _split  CC=8  out:7
    build_runtime  CC=6  out:8
    bundle_packs  CC=5  out:11
    register_manifests  CC=2  out:4
    register_pack  CC=2  out:6
    register_packs  CC=2  out:2
    resolve_pack_module  CC=4  out:2
  core.python.uri_control.edge.env  [6 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    _urisys_root  CC=1  out:2
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=8  out:17
    resolve_env_var  CC=11  out:9
  core.python.uri_control.edge.flow_expect  [6 funcs]
    _min_vision_confidence  CC=4  out:3
    _ocr_contains  CC=5  out:6
    _ocr_texts  CC=12  out:15
    _transport_ok  CC=5  out:3
    _vision_confidences  CC=12  out:13
    evaluate_flow_expect  CC=7  out:19
  core.python.uri_control.edge.flow_refs  [8 funcs]
    _result_payload  CC=3  out:5
    evaluate_step_if  CC=9  out:22
    interpolate_string  CC=1  out:5
    interpolate_value  CC=8  out:11
    merge_payload_from  CC=4  out:5
    resolve_ref  CC=5  out:7
    resolve_step_uri  CC=9  out:11
    seed_flow_inputs  CC=12  out:11
  core.python.uri_control.edge.http  [3 funcs]
    _routes_list  CC=6  out:6
    make_uri_handler  CC=2  out:47
    serve  CC=2  out:6
  core.python.uri_control.edge.manifest  [5 funcs]
    _handler_for_operation  CC=6  out:6
    _register_urisys_flows  CC=8  out:14
    register_manifest_data  CC=11  out:21
    register_manifest_file  CC=2  out:5
    register_manifest_files  CC=2  out:1
  core.python.uri_control.edge.risk_policy  [2 funcs]
    _violation  CC=1  out:0
    check_risk_requirements  CC=16  out:17
  core.python.uri_control.edge.runtime  [6 funcs]
    _load_handler  CC=4  out:6
    call  CC=22  out:50
    _order_flow_steps  CC=21  out:25
    load_yaml_flow  CC=14  out:21
    make_handler  CC=1  out:1
    run_flow  CC=19  out:37
  core.python.uri_control.handlers  [5 funcs]
    _normalise_endpoint  CC=3  out:4
    _safe_context  CC=5  out:2
    load_handler  CC=8  out:7
    load_python_handler  CC=6  out:11
    make_remote_handler  CC=1  out:15
  core.python.uri_control.parser  [2 funcs]
    canonicalize_uri  CC=1  out:1
    parse_uri  CC=7  out:11
  core.python.uri_control.registry  [5 funcs]
    match  CC=4  out:4
    match_route  CC=4  out:6
    register  CC=4  out:7
    _compile_pattern  CC=6  out:12
    _pattern_body  CC=2  out:4
  core.python.uri_control.runtime_handlers  [3 funcs]
    load_runtime_handler  CC=1  out:2
    make_runtime_handler  CC=1  out:8
    parse_runtime_handler  CC=5  out:7

EDGES:
  core.python.uri_control.dispatcher.UriControlRuntime.call → core.python.uri_control.dispatcher._new_id
  core.python.uri_control.runtime_handlers.load_runtime_handler → core.python.uri_control.runtime_handlers.parse_runtime_handler
  core.python.uri_control.runtime_handlers.load_runtime_handler → core.python.uri_control.runtime_handlers.make_runtime_handler
  core.python.uri_control.edge.cli.build_edge_cli → core.python.uri_control.edge.cli._json_arg
  core.python.uri_control.edge.cli.build_edge_cli → core.python.uri_control.edge.compose.build_runtime
  core.python.uri_control.edge.cli.build_edge_cli → core.python.uri_control.edge.cli._emit
  core.python.uri_control.edge.manifest.register_manifest_file → core.python.uri_control.edge.manifest.register_manifest_data
  core.python.uri_control.edge.manifest.register_manifest_data → core.python.uri_control.edge.manifest._register_urisys_flows
  core.python.uri_control.edge.manifest.register_manifest_data → core.python.uri_control.edge.manifest._handler_for_operation
  core.python.uri_control.edge.manifest.register_manifest_files → core.python.uri_control.edge.manifest.register_manifest_file
  core.python.uri_control.edge.flow_refs.interpolate_string → core.python.uri_control.edge.flow_refs.resolve_ref
  core.python.uri_control.edge.flow_refs.interpolate_value → core.python.uri_control.edge.flow_refs.resolve_ref
  core.python.uri_control.edge.flow_refs.interpolate_value → core.python.uri_control.edge.flow_refs.interpolate_string
  core.python.uri_control.edge.flow_refs.merge_payload_from → core.python.uri_control.edge.flow_refs._result_payload
  core.python.uri_control.edge.flow_refs.merge_payload_from → core.python.uri_control.edge.flow_refs.resolve_ref
  core.python.uri_control.edge.flow_refs.resolve_step_uri → core.python.uri_control.edge.flow_refs.interpolate_value
  core.python.uri_control.edge.flow_refs.resolve_step_uri → core.python.uri_control.edge.flow_refs.resolve_ref
  core.python.uri_control.edge.flow_refs.evaluate_step_if → core.python.uri_control.edge.flow_refs.resolve_ref
  core.python.uri_control.edge.compose.register_pack → core.python.uri_control.edge.compose.resolve_pack_module
  core.python.uri_control.edge.compose.register_pack → core.python.uri_control.registry.CapabilityRegistry.register
  core.python.uri_control.edge.compose.register_packs → core.python.uri_control.edge.compose.register_pack
  core.python.uri_control.edge.compose.register_packs → core.python.uri_control.edge.compose._split
  core.python.uri_control.edge.compose.register_manifests → core.python.uri_control.edge.compose._split
  core.python.uri_control.edge.compose.register_manifests → core.python.uri_control.edge.manifest.register_manifest_file
  core.python.uri_control.edge.compose.bundle_packs → core.python.uri_control.edge.compose._bundle_block
  core.python.uri_control.edge.compose.bundle_packs → core.python.uri_control.edge.compose._imports_contracts
  core.python.uri_control.edge.compose.build_runtime → core.python.uri_control.edge.compose._split
  core.python.uri_control.edge.compose.build_runtime → core.python.uri_control.edge.compose.register_packs
  core.python.uri_control.edge.compose.build_runtime → core.python.uri_control.edge.compose.register_manifests
  core.python.uri_control.edge.compose.build_runtime → core.python.uri_control.edge.compose.bundle_packs
  core.python.uri_control.edge.risk_policy.check_risk_requirements → core.python.uri_control.edge.risk_policy._violation
  core.python.uri_control.edge.flow_expect._ocr_contains → core.python.uri_control.edge.flow_expect._ocr_texts
  core.python.uri_control.edge.flow_expect._min_vision_confidence → core.python.uri_control.edge.flow_expect._vision_confidences
  core.python.uri_control.edge.flow_expect.evaluate_flow_expect → core.python.uri_control.edge.flow_expect._transport_ok
  core.python.uri_control.parser.canonicalize_uri → core.python.uri_control.parser.parse_uri
  core.python.uri_control.cli.cmd_explain → core.python.uri_control.cli._registry_from_args
  core.python.uri_control.cli.cmd_call → core.python.uri_control.cli._registry_from_args
  core.python.uri_control.cli.cmd_call → core.python.uri_control.cli._load_payload
  core.python.uri_control.cli.cmd_list → core.python.uri_control.cli._registry_from_args
  core.python.uri_control.cli.main → core.python.uri_control.cli.build_parser
  core.python.uri_control.handlers.make_remote_handler → core.python.uri_control.handlers._normalise_endpoint
  core.python.uri_control.handlers.make_remote_handler → core.python.uri_control.handlers._safe_context
  core.python.uri_control.handlers.load_handler → core.python.uri_control.handlers.load_python_handler
  core.python.uri_control.handlers.load_handler → core.python.uri_control.runtime_handlers.load_runtime_handler
  core.python.uri_control.handlers.load_handler → core.python.uri_control.handlers.make_remote_handler
  core.python.uri_control.edge.env.load_urisys_env → core.python.uri_control.edge.env._urisys_root
  core.python.uri_control.edge.env._env_policy_candidates → core.python.uri_control.edge.env._urisys_root
  core.python.uri_control.edge.env.load_env_policy → core.python.uri_control.edge.env._env_policy_candidates
  core.python.uri_control.edge.env.resolve_env_var → core.python.uri_control.edge.env._env_config
  core.python.uri_control.edge.env.resolve_env_var → core.python.uri_control.edge.env.load_env_policy
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/tellmesh/uricore
# generated in 0.04s
# nodes: 72 | edges: 62 | modules: 15
# CC̄=4.6

HUBS[20]:
  core.python.uri_control.edge.cli.build_edge_cli
    CC=1  in:0  out:57  total:57
  core.python.uri_control.edge.runtime.Runtime.call
    CC=22  in:0  out:50  total:50
  core.python.uri_control.edge.http.make_uri_handler
    CC=2  in:2  out:47  total:49
  core.python.uri_control.edge.runtime.run_flow
    CC=19  in:1  out:37  total:38
  core.python.uri_control.dispatcher.UriControlRuntime.call
    CC=10  in:0  out:31  total:31
  core.python.uri_control.cli.build_parser
    CC=1  in:1  out:25  total:26
  core.python.uri_control.edge.runtime._order_flow_steps
    CC=21  in:1  out:25  total:26
  core.python.uri_control.edge.flow_refs.evaluate_step_if
    CC=9  in:1  out:22  total:23
  core.python.uri_control.edge.manifest.register_manifest_data
    CC=11  in:1  out:21  total:22
  core.python.uri_control.edge.runtime.load_yaml_flow
    CC=14  in:1  out:21  total:22
  core.python.uri_control.edge.flow_expect.evaluate_flow_expect
    CC=7  in:1  out:19  total:20
  core.python.uri_control.edge.risk_policy.check_risk_requirements
    CC=16  in:1  out:17  total:18
  core.python.uri_control.edge.env.load_urisys_env
    CC=8  in:0  out:17  total:17
  core.python.uri_control.edge.manifest._register_urisys_flows
    CC=8  in:2  out:14  total:16
  core.python.uri_control.handlers.make_remote_handler
    CC=1  in:1  out:15  total:16
  core.python.uri_control.edge.flow_expect._ocr_texts
    CC=12  in:1  out:15  total:16
  core.python.uri_control.edge.flow_refs.interpolate_value
    CC=8  in:4  out:11  total:15
  core.python.uri_control.registry._compile_pattern
    CC=6  in:2  out:12  total:14
  core.python.uri_control.edge.flow_expect._vision_confidences
    CC=12  in:1  out:13  total:14
  core.python.uri_control.edge.compose.build_runtime
    CC=6  in:6  out:8  total:14

MODULES:
  core.python.uri_control.cli  [7 funcs]
    _load_payload  CC=3  out:5
    _registry_from_args  CC=2  out:2
    build_parser  CC=1  out:25
    cmd_call  CC=2  out:8
    cmd_explain  CC=1  out:4
    cmd_list  CC=2  out:3
    main  CC=1  out:4
  core.python.uri_control.dispatcher  [2 funcs]
    call  CC=10  out:31
    _new_id  CC=1  out:1
  core.python.uri_control.edge.cli  [3 funcs]
    _emit  CC=1  out:2
    _json_arg  CC=3  out:5
    build_edge_cli  CC=1  out:57
  core.python.uri_control.edge.compose  [9 funcs]
    _bundle_block  CC=2  out:2
    _imports_contracts  CC=8  out:8
    _split  CC=8  out:7
    build_runtime  CC=6  out:8
    bundle_packs  CC=5  out:11
    register_manifests  CC=2  out:4
    register_pack  CC=2  out:6
    register_packs  CC=2  out:2
    resolve_pack_module  CC=4  out:2
  core.python.uri_control.edge.env  [6 funcs]
    _env_config  CC=7  out:6
    _env_policy_candidates  CC=2  out:7
    _urisys_root  CC=1  out:2
    load_env_policy  CC=6  out:5
    load_urisys_env  CC=8  out:17
    resolve_env_var  CC=11  out:9
  core.python.uri_control.edge.flow_expect  [6 funcs]
    _min_vision_confidence  CC=4  out:3
    _ocr_contains  CC=5  out:6
    _ocr_texts  CC=12  out:15
    _transport_ok  CC=5  out:3
    _vision_confidences  CC=12  out:13
    evaluate_flow_expect  CC=7  out:19
  core.python.uri_control.edge.flow_refs  [8 funcs]
    _result_payload  CC=3  out:5
    evaluate_step_if  CC=9  out:22
    interpolate_string  CC=1  out:5
    interpolate_value  CC=8  out:11
    merge_payload_from  CC=4  out:5
    resolve_ref  CC=5  out:7
    resolve_step_uri  CC=9  out:11
    seed_flow_inputs  CC=12  out:11
  core.python.uri_control.edge.http  [3 funcs]
    _routes_list  CC=6  out:6
    make_uri_handler  CC=2  out:47
    serve  CC=2  out:6
  core.python.uri_control.edge.manifest  [5 funcs]
    _handler_for_operation  CC=6  out:6
    _register_urisys_flows  CC=8  out:14
    register_manifest_data  CC=11  out:21
    register_manifest_file  CC=2  out:5
    register_manifest_files  CC=2  out:1
  core.python.uri_control.edge.risk_policy  [2 funcs]
    _violation  CC=1  out:0
    check_risk_requirements  CC=16  out:17
  core.python.uri_control.edge.runtime  [6 funcs]
    _load_handler  CC=4  out:6
    call  CC=22  out:50
    _order_flow_steps  CC=21  out:25
    load_yaml_flow  CC=14  out:21
    make_handler  CC=1  out:1
    run_flow  CC=19  out:37
  core.python.uri_control.handlers  [5 funcs]
    _normalise_endpoint  CC=3  out:4
    _safe_context  CC=5  out:2
    load_handler  CC=8  out:7
    load_python_handler  CC=6  out:11
    make_remote_handler  CC=1  out:15
  core.python.uri_control.parser  [2 funcs]
    canonicalize_uri  CC=1  out:1
    parse_uri  CC=7  out:11
  core.python.uri_control.registry  [5 funcs]
    match  CC=4  out:4
    match_route  CC=4  out:6
    register  CC=4  out:7
    _compile_pattern  CC=6  out:12
    _pattern_body  CC=2  out:4
  core.python.uri_control.runtime_handlers  [3 funcs]
    load_runtime_handler  CC=1  out:2
    make_runtime_handler  CC=1  out:8
    parse_runtime_handler  CC=5  out:7

EDGES:
  core.python.uri_control.dispatcher.UriControlRuntime.call → core.python.uri_control.dispatcher._new_id
  core.python.uri_control.runtime_handlers.load_runtime_handler → core.python.uri_control.runtime_handlers.parse_runtime_handler
  core.python.uri_control.runtime_handlers.load_runtime_handler → core.python.uri_control.runtime_handlers.make_runtime_handler
  core.python.uri_control.edge.cli.build_edge_cli → core.python.uri_control.edge.cli._json_arg
  core.python.uri_control.edge.cli.build_edge_cli → core.python.uri_control.edge.compose.build_runtime
  core.python.uri_control.edge.cli.build_edge_cli → core.python.uri_control.edge.cli._emit
  core.python.uri_control.edge.manifest.register_manifest_file → core.python.uri_control.edge.manifest.register_manifest_data
  core.python.uri_control.edge.manifest.register_manifest_data → core.python.uri_control.edge.manifest._register_urisys_flows
  core.python.uri_control.edge.manifest.register_manifest_data → core.python.uri_control.edge.manifest._handler_for_operation
  core.python.uri_control.edge.manifest.register_manifest_files → core.python.uri_control.edge.manifest.register_manifest_file
  core.python.uri_control.edge.flow_refs.interpolate_string → core.python.uri_control.edge.flow_refs.resolve_ref
  core.python.uri_control.edge.flow_refs.interpolate_value → core.python.uri_control.edge.flow_refs.resolve_ref
  core.python.uri_control.edge.flow_refs.interpolate_value → core.python.uri_control.edge.flow_refs.interpolate_string
  core.python.uri_control.edge.flow_refs.merge_payload_from → core.python.uri_control.edge.flow_refs._result_payload
  core.python.uri_control.edge.flow_refs.merge_payload_from → core.python.uri_control.edge.flow_refs.resolve_ref
  core.python.uri_control.edge.flow_refs.resolve_step_uri → core.python.uri_control.edge.flow_refs.interpolate_value
  core.python.uri_control.edge.flow_refs.resolve_step_uri → core.python.uri_control.edge.flow_refs.resolve_ref
  core.python.uri_control.edge.flow_refs.evaluate_step_if → core.python.uri_control.edge.flow_refs.resolve_ref
  core.python.uri_control.edge.compose.register_pack → core.python.uri_control.edge.compose.resolve_pack_module
  core.python.uri_control.edge.compose.register_pack → core.python.uri_control.registry.CapabilityRegistry.register
  core.python.uri_control.edge.compose.register_packs → core.python.uri_control.edge.compose.register_pack
  core.python.uri_control.edge.compose.register_packs → core.python.uri_control.edge.compose._split
  core.python.uri_control.edge.compose.register_manifests → core.python.uri_control.edge.compose._split
  core.python.uri_control.edge.compose.register_manifests → core.python.uri_control.edge.manifest.register_manifest_file
  core.python.uri_control.edge.compose.bundle_packs → core.python.uri_control.edge.compose._bundle_block
  core.python.uri_control.edge.compose.bundle_packs → core.python.uri_control.edge.compose._imports_contracts
  core.python.uri_control.edge.compose.build_runtime → core.python.uri_control.edge.compose._split
  core.python.uri_control.edge.compose.build_runtime → core.python.uri_control.edge.compose.register_packs
  core.python.uri_control.edge.compose.build_runtime → core.python.uri_control.edge.compose.register_manifests
  core.python.uri_control.edge.compose.build_runtime → core.python.uri_control.edge.compose.bundle_packs
  core.python.uri_control.edge.risk_policy.check_risk_requirements → core.python.uri_control.edge.risk_policy._violation
  core.python.uri_control.edge.flow_expect._ocr_contains → core.python.uri_control.edge.flow_expect._ocr_texts
  core.python.uri_control.edge.flow_expect._min_vision_confidence → core.python.uri_control.edge.flow_expect._vision_confidences
  core.python.uri_control.edge.flow_expect.evaluate_flow_expect → core.python.uri_control.edge.flow_expect._transport_ok
  core.python.uri_control.parser.canonicalize_uri → core.python.uri_control.parser.parse_uri
  core.python.uri_control.cli.cmd_explain → core.python.uri_control.cli._registry_from_args
  core.python.uri_control.cli.cmd_call → core.python.uri_control.cli._registry_from_args
  core.python.uri_control.cli.cmd_call → core.python.uri_control.cli._load_payload
  core.python.uri_control.cli.cmd_list → core.python.uri_control.cli._registry_from_args
  core.python.uri_control.cli.main → core.python.uri_control.cli.build_parser
  core.python.uri_control.handlers.make_remote_handler → core.python.uri_control.handlers._normalise_endpoint
  core.python.uri_control.handlers.make_remote_handler → core.python.uri_control.handlers._safe_context
  core.python.uri_control.handlers.load_handler → core.python.uri_control.handlers.load_python_handler
  core.python.uri_control.handlers.load_handler → core.python.uri_control.runtime_handlers.load_runtime_handler
  core.python.uri_control.handlers.load_handler → core.python.uri_control.handlers.make_remote_handler
  core.python.uri_control.edge.env.load_urisys_env → core.python.uri_control.edge.env._urisys_root
  core.python.uri_control.edge.env._env_policy_candidates → core.python.uri_control.edge.env._urisys_root
  core.python.uri_control.edge.env.load_env_policy → core.python.uri_control.edge.env._env_policy_candidates
  core.python.uri_control.edge.env.resolve_env_var → core.python.uri_control.edge.env._env_config
  core.python.uri_control.edge.env.resolve_env_var → core.python.uri_control.edge.env.load_env_policy
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 47f 3821L | python:34,yaml:3,shell:2,json:2,proto:2,toml:1,php:1,typescript:1 | 2026-06-18
# generated in 0.01s
# CC̅=4.6 | critical:5/125 | dups:0 | cycles:1

HEALTH[5]:
  🟡 CC    check_risk_requirements CC=16 (limit:15)
  🟡 CC    load_manifest CC=21 (limit:15)
  🟡 CC    call CC=22 (limit:15)
  🟡 CC    _order_flow_steps CC=21 (limit:15)
  🟡 CC    run_flow CC=19 (limit:15)

REFACTOR[2]:
  1. split 5 high-CC methods  (CC>15)
  2. break 1 circular dependencies

PIPELINES[50]:
  [1] Src [unit_status]: unit_status
      PURITY: 100% pure
  [2] Src [unit_restart]: unit_restart
      PURITY: 100% pure
  [3] Src [append]: append
      PURITY: 100% pure
  [4] Src [read_all]: read_all
      PURITY: 100% pure
  [5] Src [__init__]: __init__
      PURITY: 100% pure
  [6] Src [append]: append
      PURITY: 100% pure
  [7] Src [read_all]: read_all
      PURITY: 100% pure
  [8] Src [dump_events]: dump_events
      PURITY: 100% pure
  [9] Src [__init__]: __init__
      PURITY: 100% pure
  [10] Src [call]: call → _new_id
      PURITY: 100% pure
  [11] Src [open_page]: open_page
      PURITY: 100% pure
  [12] Src [get_dom]: get_dom
      PURITY: 100% pure
  [13] Src [build_edge_cli]: build_edge_cli → _json_arg
      PURITY: 100% pure
  [14] Src [register_manifest_files]: register_manifest_files → register_manifest_file → register_manifest_data → _register_urisys_flows
      PURITY: 100% pure
  [15] Src [canonicalize_uri]: canonicalize_uri → parse_uri
      PURITY: 100% pure
  [16] Src [__init__]: __init__
      PURITY: 100% pure
  [17] Src [decide]: decide
      PURITY: 100% pure
  [18] Src [cmd_explain]: cmd_explain → _registry_from_args
      PURITY: 100% pure
  [19] Src [cmd_call]: cmd_call → _registry_from_args
      PURITY: 100% pure
  [20] Src [cmd_list]: cmd_list → _registry_from_args
      PURITY: 100% pure
  [21] Src [cmd_projection_latest]: cmd_projection_latest
      PURITY: 100% pure
  [22] Src [cmd_projection_status]: cmd_projection_status
      PURITY: 100% pure
  [23] Src [main]: main → build_parser
      PURITY: 100% pure
  [24] Src [latest_by_source_uri]: latest_by_source_uri
      PURITY: 100% pure
  [25] Src [status_by_source_uri]: status_by_source_uri
      PURITY: 100% pure
  [26] Src [events_by_type]: events_by_type
      PURITY: 100% pure
  [27] Src [from_events]: from_events
      PURITY: 100% pure
  [28] Src [load_urisys_env]: load_urisys_env → _urisys_root
      PURITY: 100% pure
  [29] Src [resolve_env_var]: resolve_env_var → _env_config
      PURITY: 100% pure
  [30] Src [is_secret_env]: is_secret_env
      PURITY: 100% pure
  [31] Src [from_manifest_files]: from_manifest_files
      PURITY: 100% pure
  [32] Src [load_manifest_file]: load_manifest_file
      PURITY: 100% pure
  [33] Src [load_manifest]: load_manifest → _compile_pattern → _pattern_body
      PURITY: 100% pure
  [34] Src [match_route]: match_route → parse_uri
      PURITY: 100% pure
  [35] Src [match]: match → _load_handler → load_handler → load_python_handler
      PURITY: 100% pure
  [36] Src [explain]: explain
      PURITY: 100% pure
  [37] Src [serve]: serve → _routes_list
      PURITY: 100% pure
  [38] Src [compile]: compile
      PURITY: 100% pure
  [39] Src [match]: match
      PURITY: 100% pure
  [40] Src [__init__]: __init__
      PURITY: 100% pure
  [41] Src [append]: append
      PURITY: 100% pure
  [42] Src [tail]: tail
      PURITY: 100% pure
  [43] Src [__init__]: __init__
      PURITY: 100% pure
  [44] Src [register]: register
      PURITY: 100% pure
  [45] Src [resolve]: resolve
      PURITY: 100% pure
  [46] Src [call]: call → check_risk_requirements → _violation
      PURITY: 100% pure
  [47] Src [load_json]: load_json
      PURITY: 100% pure
  [48] Src [make_handler]: make_handler → make_uri_handler → _as_dict
      PURITY: 100% pure
  [49] Src [serve]: serve
      PURITY: 100% pure
  [50] Src [to_dict]: to_dict
      PURITY: 100% pure

LAYERS:
  core/                           CC̄=4.6    ←in:0  →out:0
  │ !! runtime                    512L  3C   18m  CC=22     ←2
  │ !! registry                   233L  1C   10m  CC=21     ←1
  │ flow_refs                  176L  0C   10m  CC=12     ←1
  │ dispatcher                 167L  1C    4m  CC=10     ←0
  │ cli                        164L  0C    3m  CC=3      ←0
  │ compose                    157L  0C    9m  CC=8      ←1
  │ flow_expect                156L  0C    9m  CC=12     ←1
  │ http                       148L  0C    4m  CC=6      ←1
  │ handlers                   144L  0C    5m  CC=8      ←1
  │ env                        129L  0C    7m  CC=11     ←1
  │ models                     127L  7C    2m  CC=3      ←0
  │ cli                        123L  0C    9m  CC=3      ←0
  │ runtime_handlers            89L  0C    3m  CC=5      ←1
  │ manifest                    83L  0C    5m  CC=11     ←1
  │ policy                      71L  1C    2m  CC=9      ←0
  │ projection                  70L  1C    5m  CC=6      ←0
  │ event_store                 65L  3C    9m  CC=6      ←0
  │ !! risk_policy                 57L  0C    2m  CC=16     ←1
  │ parser                      45L  0C    2m  CC=7      ←1
  │ __init__                    42L  0C    0m  CC=0.0    ←0
  │ flow_artifacts              40L  0C    1m  CC=7      ←1
  │ __init__                    30L  0C    0m  CC=0.0    ←0
  │ errors                      22L  6C    0m  CC=0.0    ←0
  │ composer.json               13L  0C    0m  CC=0.0    ←0
  │ UriControl.php              11L  1C    1m  CC=1      ←0
  │ package.json                11L  0C    0m  CC=0.0    ←0
  │ index.ts                     9L  0C    1m  CC=1      ←0
  │ envelope                     6L  0C    0m  CC=0.0    ←0
  │ resolver                     6L  0C    0m  CC=0.0    ←0
  │ transport                    6L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=4.0    ←in:0  →out:0
  │ handlers                    45L  0C    2m  CC=6      ←0
  │ call_browser_mock           30L  0C    0m  CC=0.0    ←0
  │ handlers                    28L  0C    2m  CC=3      ←0
  │ manifest.yaml               25L  0C    0m  CC=0.0    ←0
  │ manifest.yaml               25L  0C    0m  CC=0.0    ←0
  │ call_systemd_mock           22L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  513L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              90L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ Makefile                    16L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  contracts/                      CC̄=0.0    ←in:0  →out:0
  │ envelope.proto              31L  0C    0m  CC=0.0    ←0
  │ browser.proto               24L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     examples/__init__.py                      0L
     examples/packs/__init__.py                0L
     examples/packs/browser_mock/__init__.py   0L
     examples/packs/systemd_mock/__init__.py   0L

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 0 groups | 8f 125L | 2026-06-18

SUMMARY:
  files_scanned: 8
  total_lines:   125
  dup_groups:    0
  dup_fragments: 0
  saved_lines:   0
  scan_ms:       3365
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 121 func | 22f | 2026-06-18
# generated in 0.00s

NEXT[7] (ranked by impact):
  [1] !! SPLIT           core/python/uri_control/edge/runtime.py
      WHY: 512L, 3 classes, max CC=22
      EFFORT: ~4h  IMPACT: 11264

  [2] !  SPLIT-FUNC      run_flow  CC=19  fan=26
      WHY: CC=19 exceeds 15
      EFFORT: ~1h  IMPACT: 494

  [3] !  SPLIT-FUNC      Runtime.call  CC=22  fan=21
      WHY: CC=22 exceeds 15
      EFFORT: ~1h  IMPACT: 462

  [4] !  SPLIT-FUNC      CapabilityRegistry.load_manifest  CC=21  fan=16
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 336

  [5] !  SPLIT-FUNC      _order_flow_steps  CC=21  fan=14
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 294

  [6] !  SPLIT-FUNC      check_risk_requirements  CC=16  fan=8
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 128

  [7] !! SPLIT           goal.yaml
      WHY: 513L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting goal.yaml may break 0 import paths
  ⚠ Splitting core/python/uri_control/edge/runtime.py may break 18 import paths

METRICS-TARGET:
  CC̄:          4.6 → ≤3.2
  max-CC:      22 → ≤11
  god-modules: 2 → 0
  high-CC(≥15): 5 → ≤2
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  (first run — no previous data)
```

## Intent

Thin URI-native control-plane core for software, services and devices.
