# uricore

Thin URI-native control-plane core for software, services and devices.

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `uricore`
- **version**: `0.1.8`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(2), app.doql.less, goal.yaml, .env.example, project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: uricore;
  version: 0.1.8;
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

## Interfaces

### CLI Entry Points

- `uricore`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m uricore
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m uricore --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m uricore --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m uricore --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 12 assertions from pytest
ASSERT[12]{field, operator, expected}:
  result.error, ==, "Approval required for side-effect operation."
  store.read_all()[-1].event_type, ==, "PolicyDenied"
  result.result.url, ==, "https://example.com"
  store.read_all()[-1].event_type, ==, "browser.v1.PageOpenedEvent"
  extra.transport, ==, "http"
  extra.target_profile.endpoint, ==, "http://esp32-tic.local:8791/uri/call"
  result.error, ==, "Approval required for side-effect operation."
  store.read_all()[-1].event_type, ==, "PolicyDenied"
  result.result.url, ==, "https://example.com"
  store.read_all()[-1].event_type, ==, "browser.v1.PageOpenedEvent"
  extra.transport, ==, "http"
  extra.target_profile.endpoint, ==, "http://esp32-tic.local:8791/uri/call"
```

## Workflows

## Configuration

```yaml
project:
  name: uricore
  version: 0.1.8
  env: local
```

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

## Deployment

```bash markpact:run
pip install uricore

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`uricore`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `.venv/lib/python3.13/site-packages/_pytest/__init__.py:__version__`

## Makefile Targets

- `install`
- `test`
- `lint`
- `example-browser`
- `example-systemd`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# uricore | 26f 1093L | python:23,shell:2,less:1 | 2026-06-18
# stats: 59 func | 1 cls | 26 mod | CC̄=3.4 | critical:0 | cycles:0
# alerts[5]: CC test_parse_flow_step_graph_format=8; CC test_normalize_promotes_wire_fields_into_context=7; CC test_parse_custom_uri=7; CC open_page=6; CC test_match_route_does_not_load_handler=6
# hotspots[5]: test_load_urisys_flow_handler_runs_steps fan=8; test_run_flow_if_skips_step fan=6; test_run_flow_save_as_and_ref fan=5; test_run_flow_payload_from fan=5; test_match_route_does_not_load_handler fan=5
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[26]:
  app.doql.less,63
  examples/__init__.py,1
  examples/call_browser_mock.py,31
  examples/call_systemd_mock.py,23
  examples/packs/__init__.py,1
  examples/packs/browser_mock/__init__.py,1
  examples/packs/browser_mock/handlers.py,46
  examples/packs/systemd_mock/__init__.py,1
  examples/packs/systemd_mock/handlers.py,29
  project.sh,59
  tests/conftest.py,5
  tests/test_dispatcher.py,50
  tests/test_envelope.py,25
  tests/test_flow_expect.py,33
  tests/test_flow_inputs.py,21
  tests/test_flow_refs.py,86
  tests/test_operation_policy.py,73
  tests/test_parser.py,12
  tests/test_register.py,93
  tests/test_registry.py,29
  tests/test_resolver.py,137
  tests/test_risk_policy.py,30
  tests/test_runtime_handlers.py,74
  tests/test_transport.py,77
  tests/test_urisys_handlers.py,91
  tree.sh,2
D:
  examples/__init__.py:
  examples/call_browser_mock.py:
  examples/call_systemd_mock.py:
  examples/packs/__init__.py:
  examples/packs/browser_mock/__init__.py:
  examples/packs/browser_mock/handlers.py:
    e: open_page,get_dom
    open_page(payload;context)
    get_dom(payload;context)
  examples/packs/systemd_mock/__init__.py:
  examples/packs/systemd_mock/handlers.py:
    e: unit_status,unit_restart
    unit_status(payload;context)
    unit_restart(payload;context)
  tests/conftest.py:
  tests/test_dispatcher.py:
    e: _runtime,test_command_requires_approval,test_command_executes_when_approved,test_query_does_not_require_approval
    _runtime()
    test_command_requires_approval()
    test_command_executes_when_approved()
    test_query_does_not_require_approval()
  tests/test_envelope.py:
    e: test_normalize_promotes_wire_fields_into_context
    test_normalize_promotes_wire_fields_into_context()
  tests/test_flow_expect.py:
    e: test_evaluate_transport_ok_and_required_steps,test_evaluate_required_step_missing,test_evaluate_ocr_contains
    test_evaluate_transport_ok_and_required_steps()
    test_evaluate_required_step_missing()
    test_evaluate_ocr_contains()
  tests/test_flow_inputs.py:
    e: test_seed_flow_inputs_enables_uri_interpolation
    test_seed_flow_inputs_enables_uri_interpolation()
  tests/test_flow_refs.py:
    e: test_resolve_ref_nested,test_interpolate_payload,test_run_flow_save_as_and_ref,test_run_flow_payload_from,test_run_flow_if_skips_step
    test_resolve_ref_nested()
    test_interpolate_payload()
    test_run_flow_save_as_and_ref(tmp_path)
    test_run_flow_payload_from(tmp_path)
    test_run_flow_if_skips_step(tmp_path)
  tests/test_operation_policy.py:
    e: _runtime,test_within_limit_executes,test_exceeds_limit_denied_before_handler,test_limit_enforced_even_on_dry_run,test_approval_still_checked_before_policy
    _runtime(tmp_path)
    test_within_limit_executes(tmp_path)
    test_exceeds_limit_denied_before_handler(tmp_path)
    test_limit_enforced_even_on_dry_run(tmp_path)
    test_approval_still_checked_before_policy(tmp_path)
  tests/test_parser.py:
    e: test_parse_custom_uri
    test_parse_custom_uri()
  tests/test_register.py:
    e: test_register_matches_like_edge_pack,test_register_defaults_match_edge_runtime,test_match_route_does_not_load_handler,test_register_requires_scheme,test_register_and_manifest_coexist
    test_register_matches_like_edge_pack()
    test_register_defaults_match_edge_runtime()
    test_match_route_does_not_load_handler()
    test_register_requires_scheme()
    test_register_and_manifest_coexist()
  tests/test_registry.py:
    e: test_registry_matches_browser_route,test_registry_explain
    test_registry_matches_browser_route()
    test_registry_explain()
  tests/test_resolver.py:
    e: test_load_and_apply_resolver,test_resolve_uri_remaps_authority,test_resolve_uri_runtime_profile_overlay,test_apply_uri_aliases,test_apply_resolver_config_loads_uri_aliases,test_runtime_call_applies_resolver,test_run_flow_applies_resolver_runtime_defaults,test_order_flow_steps_after,test_order_flow_steps_cycle
    test_load_and_apply_resolver(tmp_path)
    test_resolve_uri_remaps_authority()
    test_resolve_uri_runtime_profile_overlay()
    test_apply_uri_aliases()
    test_apply_resolver_config_loads_uri_aliases(tmp_path)
    test_runtime_call_applies_resolver(tmp_path)
    test_run_flow_applies_resolver_runtime_defaults(tmp_path)
    test_order_flow_steps_after()
    test_order_flow_steps_cycle()
  tests/test_risk_policy.py:
    e: test_high_risk_requires_dry_run_or_allow_real,test_audit_required_for_critical
    test_high_risk_requires_dry_run_or_allow_real()
    test_audit_required_for_critical()
  tests/test_runtime_handlers.py:
    e: test_parse_runtime_handler,test_parse_runtime_handler_rejects_missing_operation,test_load_handler_dispatches_runtime_scheme,test_runtime_handler_dry_run_is_mock,test_runtime_handler_mock_environment_is_mock,test_runtime_handler_real_without_binding_errors_cleanly,test_runtime_handler_via_runtime_call_mock,test_runtime_handler_resolver_transport_wins_over_local
    test_parse_runtime_handler()
    test_parse_runtime_handler_rejects_missing_operation()
    test_load_handler_dispatches_runtime_scheme()
    test_runtime_handler_dry_run_is_mock()
    test_runtime_handler_mock_environment_is_mock()
    test_runtime_handler_real_without_binding_errors_cleanly()
    test_runtime_handler_via_runtime_call_mock(tmp_path)
    test_runtime_handler_resolver_transport_wins_over_local(tmp_path)
  tests/test_transport.py:
    e: _with_http_server,test_runtime_call_delegates_before_route_match,test_runtime_unsupported_transport_returns_clean_error,test_runtime_local_transport_still_uses_handler,_Handler
    _Handler: log_message(0),do_POST(0)
    _with_http_server()
    test_runtime_call_delegates_before_route_match(tmp_path)
    test_runtime_unsupported_transport_returns_clean_error(tmp_path)
    test_runtime_local_transport_still_uses_handler(tmp_path)
  tests/test_urisys_handlers.py:
    e: test_parse_urisys_flow_handler,test_load_urisys_flow_handler_runs_steps,test_resolve_flow_path_from_manifest_map,test_resolve_flow_path_missing,test_parse_flow_step_graph_format
    test_parse_urisys_flow_handler()
    test_load_urisys_flow_handler_runs_steps(tmp_path)
    test_resolve_flow_path_from_manifest_map(tmp_path)
    test_resolve_flow_path_missing()
    test_parse_flow_step_graph_format()
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('uricore', '0.1.9', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 63, 'less').
project_file('examples/__init__.py', 1, 'python').
project_file('examples/call_browser_mock.py', 31, 'python').
project_file('examples/call_systemd_mock.py', 23, 'python').
project_file('examples/packs/__init__.py', 1, 'python').
project_file('examples/packs/browser_mock/__init__.py', 1, 'python').
project_file('examples/packs/browser_mock/handlers.py', 46, 'python').
project_file('examples/packs/systemd_mock/__init__.py', 1, 'python').
project_file('examples/packs/systemd_mock/handlers.py', 29, 'python').
project_file('project.sh', 59, 'shell').
project_file('tests/conftest.py', 5, 'python').
project_file('tests/test_dispatcher.py', 50, 'python').
project_file('tests/test_envelope.py', 25, 'python').
project_file('tests/test_flow_expect.py', 33, 'python').
project_file('tests/test_flow_inputs.py', 21, 'python').
project_file('tests/test_flow_refs.py', 86, 'python').
project_file('tests/test_operation_policy.py', 73, 'python').
project_file('tests/test_parser.py', 12, 'python').
project_file('tests/test_register.py', 93, 'python').
project_file('tests/test_registry.py', 29, 'python').
project_file('tests/test_resolver.py', 137, 'python').
project_file('tests/test_risk_policy.py', 30, 'python').
project_file('tests/test_runtime_handlers.py', 74, 'python').
project_file('tests/test_transport.py', 77, 'python').
project_file('tests/test_urisys_handlers.py', 91, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('examples/packs/browser_mock/handlers.py', 'open_page', 2, 6, 1).
python_function('examples/packs/browser_mock/handlers.py', 'get_dom', 2, 5, 1).
python_function('examples/packs/systemd_mock/handlers.py', 'unit_status', 2, 3, 1).
python_function('examples/packs/systemd_mock/handlers.py', 'unit_restart', 2, 2, 1).
python_function('tests/test_dispatcher.py', '_runtime', 0, 1, 3).
python_function('tests/test_dispatcher.py', 'test_command_requires_approval', 0, 4, 3).
python_function('tests/test_dispatcher.py', 'test_command_executes_when_approved', 0, 4, 3).
python_function('tests/test_dispatcher.py', 'test_query_does_not_require_approval', 0, 3, 2).
python_function('tests/test_envelope.py', 'test_normalize_promotes_wire_fields_into_context', 0, 7, 2).
python_function('tests/test_flow_expect.py', 'test_evaluate_transport_ok_and_required_steps', 0, 2, 1).
python_function('tests/test_flow_expect.py', 'test_evaluate_required_step_missing', 0, 2, 2).
python_function('tests/test_flow_expect.py', 'test_evaluate_ocr_contains', 0, 2, 1).
python_function('tests/test_flow_inputs.py', 'test_seed_flow_inputs_enables_uri_interpolation', 0, 3, 2).
python_function('tests/test_flow_refs.py', 'test_resolve_ref_nested', 0, 3, 1).
python_function('tests/test_flow_refs.py', 'test_interpolate_payload', 0, 2, 1).
python_function('tests/test_flow_refs.py', 'test_run_flow_save_as_and_ref', 1, 4, 5).
python_function('tests/test_flow_refs.py', 'test_run_flow_payload_from', 1, 3, 5).
python_function('tests/test_flow_refs.py', 'test_run_flow_if_skips_step', 1, 3, 6).
python_function('tests/test_operation_policy.py', '_runtime', 1, 1, 3).
python_function('tests/test_operation_policy.py', 'test_within_limit_executes', 1, 3, 2).
python_function('tests/test_operation_policy.py', 'test_exceeds_limit_denied_before_handler', 1, 5, 3).
python_function('tests/test_operation_policy.py', 'test_limit_enforced_even_on_dry_run', 1, 3, 2).
python_function('tests/test_operation_policy.py', 'test_approval_still_checked_before_policy', 1, 3, 2).
python_function('tests/test_parser.py', 'test_parse_custom_uri', 0, 7, 1).
python_function('tests/test_register.py', 'test_register_matches_like_edge_pack', 0, 5, 3).
python_function('tests/test_register.py', 'test_register_defaults_match_edge_runtime', 0, 5, 2).
python_function('tests/test_register.py', 'test_match_route_does_not_load_handler', 0, 6, 5).
python_function('tests/test_register.py', 'test_register_requires_scheme', 0, 4, 5).
python_function('tests/test_register.py', 'test_register_and_manifest_coexist', 0, 3, 5).
python_function('tests/test_registry.py', 'test_registry_matches_browser_route', 0, 4, 2).
python_function('tests/test_registry.py', 'test_registry_explain', 0, 4, 2).
python_function('tests/test_resolver.py', 'test_load_and_apply_resolver', 1, 4, 4).
python_function('tests/test_resolver.py', 'test_resolve_uri_remaps_authority', 0, 4, 1).
python_function('tests/test_resolver.py', 'test_resolve_uri_runtime_profile_overlay', 0, 5, 2).
python_function('tests/test_resolver.py', 'test_apply_uri_aliases', 0, 3, 2).
python_function('tests/test_resolver.py', 'test_apply_resolver_config_loads_uri_aliases', 1, 3, 3).
python_function('tests/test_resolver.py', 'test_runtime_call_applies_resolver', 1, 3, 3).
python_function('tests/test_resolver.py', 'test_run_flow_applies_resolver_runtime_defaults', 1, 3, 5).
python_function('tests/test_resolver.py', 'test_order_flow_steps_after', 0, 2, 1).
python_function('tests/test_resolver.py', 'test_order_flow_steps_cycle', 0, 1, 2).
python_function('tests/test_risk_policy.py', 'test_high_risk_requires_dry_run_or_allow_real', 0, 5, 1).
python_function('tests/test_risk_policy.py', 'test_audit_required_for_critical', 0, 4, 1).
python_function('tests/test_runtime_handlers.py', 'test_parse_runtime_handler', 0, 2, 1).
python_function('tests/test_runtime_handlers.py', 'test_parse_runtime_handler_rejects_missing_operation', 0, 1, 2).
python_function('tests/test_runtime_handlers.py', 'test_load_handler_dispatches_runtime_scheme', 0, 2, 2).
python_function('tests/test_runtime_handlers.py', 'test_runtime_handler_dry_run_is_mock', 0, 5, 2).
python_function('tests/test_runtime_handlers.py', 'test_runtime_handler_mock_environment_is_mock', 0, 2, 2).
python_function('tests/test_runtime_handlers.py', 'test_runtime_handler_real_without_binding_errors_cleanly', 0, 4, 2).
python_function('tests/test_runtime_handlers.py', 'test_runtime_handler_via_runtime_call_mock', 1, 3, 3).
python_function('tests/test_runtime_handlers.py', 'test_runtime_handler_resolver_transport_wins_over_local', 1, 3, 4).
python_function('tests/test_transport.py', '_with_http_server', 0, 1, 3).
python_function('tests/test_transport.py', 'test_runtime_call_delegates_before_route_match', 1, 4, 5).
python_function('tests/test_transport.py', 'test_runtime_unsupported_transport_returns_clean_error', 1, 4, 2).
python_function('tests/test_transport.py', 'test_runtime_local_transport_still_uses_handler', 1, 4, 4).
python_function('tests/test_urisys_handlers.py', 'test_parse_urisys_flow_handler', 0, 3, 2).
python_function('tests/test_urisys_handlers.py', 'test_load_urisys_flow_handler_runs_steps', 1, 5, 8).
python_function('tests/test_urisys_handlers.py', 'test_resolve_flow_path_from_manifest_map', 1, 2, 5).
python_function('tests/test_urisys_handlers.py', 'test_resolve_flow_path_missing', 0, 1, 3).
python_function('tests/test_urisys_handlers.py', 'test_parse_flow_step_graph_format', 0, 8, 1).

% ── Python Classes ───────────────────────────────────────
python_class('tests/test_transport.py', '_Handler').
python_method('_Handler', 'log_message', 0, 1, 0).
python_method('_Handler', 'do_POST', 0, 1, 13).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────
makefile_target('install', '').
makefile_target('test', '').
makefile_target('lint', '').
makefile_target('example-browser', '').
makefile_target('example-systemd', '').

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
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

## Intent

Thin URI-native control-plane core for software, services and devices.
