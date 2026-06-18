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
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
sumd_workflow('install', 'manual').
sumd_workflow_step('install', 1, 'python -m pip install -e .').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, 'python -m pytest').
sumd_workflow('lint', 'manual').
sumd_workflow_step('lint', 1, 'python -m ruff check core/python tests examples').
sumd_workflow('example-browser', 'manual').
sumd_workflow_step('example-browser', 1, 'PYTHONPATH=core/python:. python examples/call_browser_mock.py').
sumd_workflow('example-systemd', 'manual').
sumd_workflow_step('example-systemd', 1, 'PYTHONPATH=core/python:. python examples/call_systemd_mock.py').

