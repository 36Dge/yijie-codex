#!/usr/bin/env python3
"""Source conformance for the gated FEAT-137 deterministic approval producer."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PRIVATE_ENV_KEYS = (
    "MINIMAX_API_KEY",
    "OPENAI_API_KEY",
    "CODEX_API_KEY",
    "CODEX_ACCESS_TOKEN",
    "CHATGPT_ACCESS_TOKEN",
    "YIJIE_MINIMAX_API_KEY",
    "YIJIE_MINIMAX_API_KEY_FILE",
    "MINIMAX_API_KEY_FILE",
    "YIJIE_FEAT137_DETERMINISTIC_APPROVAL_PRODUCER",
    "BASH_ENV",
    "ENV",
    "ZDOTDIR",
)

EXPECTED_PATCH_PATHS = {
    "app-server/src/lib.rs",
    "app-server/src/message_processor.rs",
    "app-server/src/models.rs",
    "app-server/src/models_refresh_worker.rs",
    "app-server/src/models_refresh_worker_tests.rs",
    "app-server/src/request_processors/apps_processor.rs",
    "app-server/src/request_processors/catalog_processor.rs",
    "app-server/src/request_processors/mcp_processor.rs",
    "app-server/src/request_processors/plugins.rs",
    "app-server/src/skills_watcher.rs",
    "codex-api/src/endpoint/responses_websocket.rs",
    "codex-api/src/feat137_deterministic_approval.rs",
    "codex-api/src/lib.rs",
    "codex-api/src/sse/responses.rs",
    "codex-api/src/telemetry.rs",
    "core-skills/src/service.rs",
    "core-skills/src/service_tests.rs",
    "core/src/client.rs",
    "core/src/client_common.rs",
    "core/src/client_tests.rs",
    "core/src/compact_remote_request.rs",
    "core/src/compact_remote_v2_attempt.rs",
    "core/src/config/mod.rs",
    "core/src/feat137_deterministic_approval.rs",
    "core/src/lib.rs",
    "core/src/mcp.rs",
    "core/src/session/mod.rs",
    "core/src/session/review.rs",
    "core/src/session/session.rs",
    "core/src/session/turn.rs",
    "core/src/session/turn_context.rs",
    "core/src/session_startup_prewarm.rs",
    "core/src/shell_snapshot.rs",
    "core/src/shell_snapshot_tests.rs",
    "core/src/stream_events_utils.rs",
    "core/src/stream_events_utils_tests.rs",
    "core/src/thread_manager.rs",
    "core/src/thread_manager_tests.rs",
    "core/src/tools/handlers/unified_exec/exec_command.rs",
    "core/src/tools/orchestrator.rs",
    "core/src/tools/registry.rs",
    "core/src/tools/runtimes/mod.rs",
    "core/src/tools/runtimes/mod_tests.rs",
    "core/src/unified_exec/process_manager.rs",
    "core/src/unified_exec/process_manager_tests.rs",
    "http-client/src/default_client.rs",
    "http-client/src/feat137_deterministic_approval.rs",
    "http-client/src/lib.rs",
    "http-client/src/transport.rs",
}


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing FEAT-137 conformance input: {path}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> int:
    index = text.find(needle)
    if index < 0:
        raise SystemExit(f"FEAT-137 conformance missing {label}")
    return index


def require_before(text: str, first: str, second: str, label: str) -> None:
    if require(text, first, f"{label} first marker") >= require(
        text, second, f"{label} second marker"
    ):
        raise SystemExit(f"FEAT-137 conformance order violation: {label}")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: check-feat137-deterministic-approval.py PATCHED_CODEX_RS PATCH"
        )
    workspace = Path(sys.argv[1]).resolve()
    patch_path = Path(sys.argv[2]).resolve()

    patch = read(patch_path)
    changed_paths = set(re.findall(r"^diff --git a/(\S+) b/\1$", patch, re.MULTILINE))
    if changed_paths != EXPECTED_PATCH_PATHS:
        missing = sorted(EXPECTED_PATCH_PATHS - changed_paths)
        extra = sorted(changed_paths - EXPECTED_PATCH_PATHS)
        raise SystemExit(
            f"FEAT-137 patch path boundary mismatch; missing={missing}, extra={extra}"
        )

    api_gate = read(workspace / "codex-api/src/feat137_deterministic_approval.rs")
    sse = read(workspace / "codex-api/src/sse/responses.rs")
    websocket = read(workspace / "codex-api/src/endpoint/responses_websocket.rs")
    api_telemetry = read(workspace / "codex-api/src/telemetry.rs")
    app_message_processor = read(workspace / "app-server/src/message_processor.rs")
    app_lib = read(workspace / "app-server/src/lib.rs")
    app_models = read(workspace / "app-server/src/models.rs")
    app_models_worker = read(workspace / "app-server/src/models_refresh_worker.rs")
    app_apps = read(workspace / "app-server/src/request_processors/apps_processor.rs")
    app_catalog = read(workspace / "app-server/src/request_processors/catalog_processor.rs")
    app_mcp = read(workspace / "app-server/src/request_processors/mcp_processor.rs")
    app_plugins = read(workspace / "app-server/src/request_processors/plugins.rs")
    app_skills_watcher = read(workspace / "app-server/src/skills_watcher.rs")
    remote_control = read(
        workspace / "app-server-transport/src/transport/remote_control/mod.rs"
    )
    remote_control_websocket = read(
        workspace / "app-server-transport/src/transport/remote_control/websocket.rs"
    )
    core_skills = read(workspace / "core-skills/src/service.rs")
    client = read(workspace / "core/src/client.rs")
    client_tests = read(workspace / "core/src/client_tests.rs")
    config = read(workspace / "core/src/config/mod.rs")
    producer = read(workspace / "core/src/feat137_deterministic_approval.rs")
    mcp = read(workspace / "core/src/mcp.rs")
    session = read(workspace / "core/src/session/mod.rs")
    session_init = read(workspace / "core/src/session/session.rs")
    turn = read(workspace / "core/src/session/turn.rs")
    context = read(workspace / "core/src/session/turn_context.rs")
    startup_prewarm = read(workspace / "core/src/session_startup_prewarm.rs")
    stream_utils = read(workspace / "core/src/stream_events_utils.rs")
    stream_utils_tests = read(workspace / "core/src/stream_events_utils_tests.rs")
    thread_manager = read(workspace / "core/src/thread_manager.rs")
    handler = read(workspace / "core/src/tools/handlers/unified_exec/exec_command.rs")
    registry = read(workspace / "core/src/tools/registry.rs")
    orchestrator = read(workspace / "core/src/tools/orchestrator.rs")
    process_manager = read(workspace / "core/src/unified_exec/process_manager.rs")
    shell_snapshot = read(workspace / "core/src/shell_snapshot.rs")
    shell_tests = read(workspace / "core/src/shell_snapshot_tests.rs")
    runtimes = read(workspace / "core/src/tools/runtimes/mod.rs")
    runtime_tests = read(workspace / "core/src/tools/runtimes/mod_tests.rs")
    process_tests = read(workspace / "core/src/unified_exec/process_manager_tests.rs")
    http_gate = read(workspace / "http-client/src/feat137_deterministic_approval.rs")
    http_transport = read(workspace / "http-client/src/transport.rs")
    http_default = read(workspace / "http-client/src/default_client.rs")

    # The private process switch remains exact and the patch does not touch public protocol or
    # stable wire-schema sources.
    require(producer, 'value == Some(OsStr::new("1"))', "exact process gate")
    require(api_gate, 'value == Some(OsStr::new("1"))', "exact API wire gate")
    if any(path.startswith(("protocol/", "app-server-protocol/")) for path in changed_paths):
        raise SystemExit("FEAT-137 deterministic producer must not change public/stable schema")

    # The turn-scoped state, authority, fixed action, and post-call tool closure are closed.
    for needle, label in (
        ("struct TurnAdmissionState", "turn admission state"),
        ("admitted_call_id: OnceLock<String>", "turn-scoped exact call id"),
        ("handler_entered: AtomicBool", "handler entry CAS"),
        ("handler_finished: AtomicBool", "handler terminal state"),
        ("fatal: AtomicBool", "fatal boundary state"),
        ("provider_request_count: AtomicU8", "turn-scoped provider request budget"),
        ('CANONICAL_CALL_ID: &str = "feat137-call-1"', "canonical call identity"),
        ('CANONICAL_RESPONSE_ID: &str = "feat137-response-1"', "canonical response identity"),
        ('name == "exec_command"', "plain exec command admission"),
        ("namespace.is_none()", "namespace rejection"),
        ("!call_id.is_empty()", "empty call id rejection"),
        ('"git rev-parse --is-inside-work-tree"', "fixed read-only action"),
        ('"sandbox_permissions": "use_default"', "fixed sandbox authority"),
        ('"required": []', "zero-argument closed schema test"),
        ("additionalProperties", "closed schema assertion"),
        ("state.admitted_call_id.get().is_some()", "state-first post-call closure"),
        ("admitted_state_keeps_tools_closed_after_same_turn_user_steer", "steer regression"),
        ("validate_provider_completed", "provider terminal validation"),
        ("validate_handler_lifecycle", "handler terminal validation"),
        ("*internal_chat_message_metadata_passthrough = None", "metadata removal"),
        ("provider_retry_limit", "zero provider retry authority"),
        ("model_refresh_strategy", "offline pre-turn model catalog authority"),
        ("admit_provider_request", "single provider request CAS"),
    ):
        require(producer, needle, label)
    require_before(
        producer,
        ".set(call_id.clone())",
        "*arguments = fixed_exec_command_arguments()",
        "atomic admission before argument replacement",
    )
    for variant in (
        "AdditionalTools",
        "LocalShellCall",
        "FunctionCall",
        "ToolSearchCall",
        "FunctionCallOutput",
        "CustomToolCall",
        "CustomToolCallOutput",
        "ToolSearchOutput",
        "WebSearchCall",
        "ImageGenerationCall",
    ):
        require(producer, f"ResponseItem::{variant}", f"tool-like rejection {variant}")

    # Admission/redaction occurs in the client mapper before every persistent or observable sink.
    done = require(client, "Ok(ResponseEvent::OutputItemDone(mut item))", "client done boundary")
    admitted = require(
        client[done:],
        "sanitize_and_admit_provider_output_item",
        "client admission sanitizer",
    )
    items_added = require(client[done:], "items_added.push(item.clone())", "LastResponse items")
    forwarded = require(
        client[done:],
        ".send(Ok(ResponseEvent::OutputItemDone(item)))",
        "session forwarding",
    )
    if not admitted < items_added < forwarded:
        raise SystemExit("FEAT-137 client admission must precede items_added and forwarding")
    completed = require(client, "Ok(ResponseEvent::Completed {", "provider completed")
    completed_guard = require(
        client[completed:], "validate_provider_completed", "completed admission guard"
    )
    completed_trace = require(
        client[completed:], "record_completed", "completed inference trace"
    )
    completed_last = require(
        client[completed:], "tx_last_response.take()", "completed LastResponse"
    )
    if not completed_guard < completed_trace < completed_last:
        raise SystemExit("FEAT-137 completed validation must precede trace and LastResponse")
    for needle, label in (
        ("Ok(_) if feat137_deterministic_approval.is_some()", "closed event catch-all"),
        ("CANONICAL_RESPONSE_ID", "canonical completed identity"),
        ("InferenceTraceAttempt::disabled()", "raw request trace disabled"),
        ("stream_with_feat137_boundary", "crate-private boundary entrypoint"),
    ):
        require(client, needle, label)
    http_trace_gate = require(
        client,
        "let inference_trace_attempt = if feat137_deterministic_approval.is_some()",
        "HTTP inference trace exact gate",
    )
    http_trace_disabled = require(
        client[http_trace_gate:],
        "InferenceTraceAttempt::disabled()",
        "HTTP disabled inference trace",
    )
    http_trace_started = require(
        client[http_trace_gate:],
        "attempt.record_started(&request)",
        "HTTP raw request trace",
    )
    if http_trace_disabled >= http_trace_started:
        raise SystemExit("FEAT-137 HTTP inference trace must disable before raw serialization")
    ws_trace_gate = require(
        client[http_trace_gate + 1 :],
        "let inference_trace_attempt = if warmup || feat137_deterministic_approval.is_some()",
        "WebSocket inference trace exact gate",
    )
    ws_trace = client[http_trace_gate + 1 + ws_trace_gate :]
    require_before(
        ws_trace,
        "InferenceTraceAttempt::disabled()",
        "if feat137_deterministic_approval.is_some()",
        "WebSocket trace disabled before raw record branch",
    )
    require_before(
        ws_trace,
        "if feat137_deterministic_approval.is_some()",
        "inference_trace_attempt.record_started(&request)",
        "WebSocket raw request serialization guarded",
    )
    require(client_tests, "feat137-provider-argument-canary", "raw argument canary")
    require(
        client_tests,
        "forbidden-request-prompt-provider-id-canary",
        "request trace serialization canary",
    )
    require(client_tests, "replay_bundle", "rollout trace canary check")
    require(
        client_tests,
        "feat137_mapper_fails_completed_without_exact_done_for_all_partial_shapes",
        "missing-done terminal cases",
    )
    require(
        client_tests,
        "feat137_mapper_rejects_second_stream_completed_without_its_own_done",
        "second-stream terminal rejection",
    )
    require(
        producer,
        "gate_on_allows_exactly_one_provider_request_and_no_retry_compaction_or_follow_up",
        "second provider request rejection",
    )
    mapper_boundary = client[
        require(client, "fn map_response_events", "response mapper boundary") :
    ]
    require_before(
        mapper_boundary,
        "let mut stream_admitted_canonical_done = false",
        "stream_admitted_canonical_done = true",
        "per-stream canonical Done state initialization",
    )
    require_before(
        mapper_boundary,
        "if stream_admitted_canonical_done",
        "validate_provider_completed(",
        "per-stream Done prerequisite before turn-global terminal validation",
    )

    # Session consumers receive only the sanitized Done item. Tool dispatch is genuinely lazy;
    # an error or missing terminal drops the queue before approval/execute.
    require_before(
        turn,
        "validate_turn_configuration(turn_context.as_ref())",
        "run_pre_sampling_compact",
        "configuration validation before turn side effects",
    )
    event_guard = require(turn, "match &mut event", "session pre-telemetry guard")
    telemetry = require(turn, ".record_responses(&handle_responses, &event)", "session telemetry")
    if event_guard >= telemetry:
        raise SystemExit("FEAT-137 session verifier must run before telemetry")
    require(turn[event_guard:telemetry], "verify_sanitized_output_item", "session verifier")
    require(stream_utils, "tool_future_for_provider_terminal", "lazy tool future factory")
    require(stream_utils, "Box::pin(async move { create().await })", "lazy dispatch closure")
    output_done = stream_utils[
        require(stream_utils, "pub(crate) async fn handle_output_item_done", "output done handler") :
    ]
    require_before(
        output_done,
        "tool_future_for_provider_terminal(defer_until_terminal, move ||",
        "tool_runtime.handle_tool_call(call, cancellation_token)",
        "production tool dispatch enclosed by lazy terminal factory",
    )
    require(
        stream_utils_tests,
        "is_inert_until_authoritative_terminal_drain",
        "lazy dispatch regression",
    )
    terminal_flag = require(turn, "authoritative_provider_completed = true", "terminal flag")
    queue_drop = require(turn, "in_flight.clear()", "non-terminal queue drop")
    drain = require(turn, "drain_in_flight(&mut in_flight", "tool future drain")
    if not terminal_flag < queue_drop < drain:
        raise SystemExit("FEAT-137 tool queue must be authorized or dropped before drain")
    require_before(
        turn,
        "drain_in_flight(&mut in_flight",
        "validate_handler_lifecycle(turn_context.as_ref())",
        "handler terminal after tool drain",
    )
    require(
        context,
        "Arc<crate::feat137_deterministic_approval::TurnAdmissionState>",
        "shared turn admission state",
    )
    turn_context_builder = context[
        require(
            context,
            "async fn new_turn_context_from_configuration",
            "turn-context constructor",
        ) :
    ]
    snapshot_gate = require(
        turn_context_builder,
        "feat137_turn_skills_snapshot_for_gate(",
        "turn-context skill snapshot gate call",
    )
    snapshot_gate_body = turn_context_builder[snapshot_gate:]
    require_before(
        snapshot_gate_body,
        "environment_gate_enabled()",
        "plugins_for_config(&plugins_input)",
        "turn-context plugin discovery enclosed by exact gate",
    )
    require_before(
        snapshot_gate_body,
        "environment_gate_enabled()",
        "snapshot_for_config(&skills_input, fs)",
        "turn-context filesystem skill scan enclosed by exact gate",
    )
    require(handler, "admitted_exec_command_arguments", "handler admission recheck")
    require_before(
        handler,
        "admitted_exec_command_arguments",
        "parse_arguments(&arguments)",
        "handler admission before parsing",
    )
    require(handler, "mark_handler_finished", "handler terminal publication")
    require(stream_utils, "deterministic approval tool admitted", "payload-free tool log")

    # Plugin/hook discovery is disabled before session/turn side effects, while the exact managed
    # profile is also required to keep all default-on surfaces disabled.
    require(config, "plugin_startup_flags", "early plugin startup gate")
    hooks_builder = session[
        require(session, "async fn build_hooks_for_config", "hook builder") :
    ]
    require_before(
        hooks_builder,
        "environment_gate_enabled()",
        "config.plugins_config_input()",
        "empty hooks before plugin discovery",
    )
    for feature in ("CodexHooks", "Plugins", "PluginHooks", "Apps", "ToolSuggest"):
        require(producer, f"Feature::{feature}", f"managed feature-off boundary {feature}")
    require(registry, "bypass_tool_hooks", "pre/post tool hook bypass")
    require(orchestrator, "bypass_tool_hooks", "permission hook bypass")
    require(config, "feat137_empty_mcp_config", "empty config/plugin MCP projection")
    mcp_gate = require(
        mcp,
        "if feat137_deterministic_approval",
        "runtime MCP early gate",
    )
    contributor = require(
        mcp[mcp_gate:],
        "self.extensions.mcp_server_contributors()",
        "ambient MCP contributor loop",
    )
    gated_return = require(
        mcp[mcp_gate:],
        "config.feat137_empty_mcp_config()",
        "empty runtime MCP return",
    )
    if gated_return >= contributor:
        raise SystemExit("FEAT-137 MCP gate must return before extension contributors")
    require(mcp, "plugins_available: false", "empty plugin availability")
    require(
        mcp,
        "feat137_gate_keeps_configured_runtime_effective_and_connectors_empty",
        "configured/runtime/effective MCP zero-count test",
    )
    require_before(
        thread_manager,
        "feat137_thread_extensions_for_gate(feat137_gate_enabled, extensions)",
        "McpManager::new_with_extensions",
        "extension removal before MCP manager",
    )
    require_before(
        thread_manager,
        "feat137_thread_extensions_for_gate(feat137_gate_enabled, extensions)",
        "SkillsService::new_without_system_skill_mutation",
        "extension removal before skills service",
    )
    require(core_skills, "new_without_system_skill_mutation", "no-mutation skills constructor")
    require(session_init, "warm_plugins_and_skills_for_session_init", "session warmup gate")
    require(turn, "async fn build_skills_and_plugins", "turn skills/plugins gate")
    require(app_skills_watcher, "FileWatcher::noop()", "disabled app file watcher")
    require(app_skills_watcher, "if self.disabled", "watch registration early return")
    require(app_message_processor, "ModelsRefreshWorker::disabled()", "disabled model refresh")
    require(app_models_worker, "pub(crate) fn disabled()", "no-task model worker")
    require(app_models, "supported_models_refresh_strategy", "offline app model list")
    require_before(
        app_apps,
        "feat137_empty_apps_response",
        "let installed_start = Instant::now()",
        "app list gate before config/auth/contributors",
    )
    require(app_plugins, "return Ok(empty_plugin_list_response())", "empty plugin list")
    require(app_plugins, "return Ok(empty_plugin_installed_response())", "empty installed list")
    require_before(
        app_catalog,
        "feat137_empty_skills_response",
        "let SkillsListParams",
        "skills list gate before config/auth/filesystem",
    )
    require_before(
        app_catalog,
        "feat137_empty_hooks_response",
        "let HooksListParams",
        "hooks list gate before config/auth/hooks",
    )
    require(app_catalog, "FEAT137_CATALOG_MUTATION_DISABLED", "catalog mutation failure")
    status_surface = app_mcp[
        require(
            app_mcp,
            "pub(crate) async fn mcp_server_status_list",
            "MCP status surface",
        ) :
    ]
    require_before(
        status_surface,
        "feat137_empty_mcp_status_response",
        "self.list_mcp_server_status(request_id, params)",
        "MCP status empty response before config/thread/auth/task path",
    )
    require_before(
        status_surface,
        "send_result(request_id.clone(), Ok::<_, JSONRPCErrorError>(response))",
        "self.list_mcp_server_status(request_id, params)",
        "MCP status response sent before active MCP path",
    )
    for method, inner_call in (
        ("mcp_server_oauth_login", "self.mcp_server_oauth_login_response(params)"),
        ("mcp_server_refresh", "self.mcp_server_refresh_response(params)"),
        ("mcp_resource_read", "self.read_mcp_resource(request_id, params)"),
        ("mcp_server_tool_call", "self.call_mcp_server_tool(request_id, params)"),
    ):
        surface = app_mcp[
            require(app_mcp, f"pub(crate) async fn {method}", f"{method} surface") :
        ]
        require_before(
            surface,
            "mcp_surface_allowed_for_gate",
            inner_call,
            f"{method} denial before active MCP operation",
        )

    # Startup prewarm is closed before either bearer/auth bootstrap or websocket/TurnContext/tool
    # setup can be spawned. The helper is lazy, and the production method places its full body in
    # that closure.
    prewarm_method = startup_prewarm[
        require(
            startup_prewarm,
            "pub(crate) async fn schedule_startup_prewarm",
            "startup prewarm method",
        ) :
    ]
    require_before(
        prewarm_method,
        "feat137_startup_prewarm_for_gate(",
        "responses_websocket_enabled()",
        "startup prewarm exact gate before websocket branch",
    )
    require_before(
        prewarm_method,
        "feat137_startup_prewarm_for_gate(",
        "model_client.prewarm_auth()",
        "startup prewarm exact gate before auth bootstrap",
    )
    require(
        startup_prewarm,
        "exact_gate_skips_auth_websocket_turn_context_and_tool_prewarm_closure",
        "startup prewarm lazy call-count regression",
    )

    # Remote control is forced closed at app-server entry before config/auth/persisted preference
    # or transport startup. Upstream DisabledEphemeral semantics remain a closed desired state:
    # no persisted resolution, auth lookup, target construction, or outbound websocket occurs.
    app_entry = app_lib[
        require(
            app_lib,
            "pub async fn run_main_with_transport_options",
            "app-server runtime entry",
        ) :
    ]
    for later, label in (
        ("loader_overrides_with_test_user_config_file", "config loader"),
        ("AuthManager::shared_from_config", "auth manager"),
        ("start_remote_control(", "remote-control task"),
    ):
        require_before(
            app_entry,
            "feat137_remote_control_startup_mode_for_gate(",
            later,
            f"remote-control exact gate before {label}",
        )
    require(
        app_entry,
        "remote_control_startup_mode,",
        "closed remote-control mode production wiring",
    )
    require(
        app_lib,
        "feat137_gate_closes_remote_control_before_persisted_auth_or_websocket_resolution",
        "remote-control lazy gate regression",
    )
    require(
        remote_control,
        "RemoteControlStartupMode::DisabledEphemeral => RemoteControlDesiredState::Disabled",
        "disabled-ephemeral closed desired state",
    )
    require_before(
        remote_control,
        "let initial_enabled = desired_state.is_enabled()",
        "let remote_control_target = if initial_enabled",
        "remote-control target requires enabled state",
    )
    websocket_run = remote_control_websocket[
        require(remote_control_websocket, "pub(crate) async fn run(", "remote websocket loop") :
    ]
    require_before(
        websocket_run,
        "RemoteControlDesiredState::Unknown",
        ".resolve_unknown_desired_state(",
        "persisted resolution only for unknown state",
    )
    require_before(
        websocket_run,
        "if !self.wait_until_enabled().await",
        ".connect(&shutdown_token",
        "outbound websocket only after enabled state",
    )

    # HTTP SSE and WebSocket transports do not emit payload-bearing trace, parse logs, or OTEL
    # callbacks while the exact gate is enabled.
    for text, transport in ((sse, "SSE"), (websocket, "WebSocket")):
        require(text, "redact_provider_wire_payloads", f"{transport} payload gate")
        require(text, "if !redact_wire_payload", f"{transport} telemetry suppression")
    require(sse, "payload redacted", "SSE safe trace/log")
    require(websocket, "redacted websocket event", "WebSocket safe parse log")
    require(sse, "t.on_sse_poll", "SSE OTEL callback")
    require(websocket, "t.on_ws_event", "WebSocket OTEL callback")
    require(api_telemetry, "telemetry_transport_error_for_gate", "safe API telemetry")

    # The generic HTTP transport precedes codex-api. Exact-gate logs and errors never evaluate or
    # retain request bodies, URLs, headers, response bodies, or reqwest error strings.
    require(http_gate, 'value == Some(OsStr::new("1"))', "exact HTTP gate")
    require(http_gate, "raw_diagnostic_for_gate", "lazy HTTP diagnostics")
    require(http_transport, "trace_request(&req)", "redacted HTTP trace")
    require(http_transport, "url: None", "redacted HTTP error URL")
    require(http_transport, "headers: None", "redacted HTTP error headers")
    require(http_transport, "body: None", "redacted HTTP error body")
    require(http_default, "deterministic approval provider request completed", "safe HTTP log")
    require(http_default, "deterministic approval provider request failed", "safe HTTP error log")

    # Child processes cannot inherit or resurrect reviewed private state. Snapshot capture itself
    # is disabled gate-on; the no-snapshot path still uses a non-login wrapper and exact unsets.
    approval = require(process_manager, "let exec_approval_requirement =", "approval lifecycle")
    manager_prefix = process_manager[:approval]
    if manager_prefix.count("scrub_unified_exec_environment") < 2:
        raise SystemExit("FEAT-137 must scrub local and request execution environments")
    require(manager_prefix, "scrub_exec_server_environment_policy", "exec-server scrub")
    require(shell_snapshot, "shell_snapshot_capture_allowed", "snapshot capture gate")
    require(shell_snapshot, "try_create_for_gate", "no snapshot file boundary")
    require(runtimes, "private_exec_environment_unset_shell", "exact post-profile unset")
    require(runtimes, '"-c".to_string()', "non-login no-snapshot wrapper")
    require(runtimes, '"-f".to_string()', "zsh no-RCS wrapper")
    for key in PRIVATE_ENV_KEYS:
        require(producer, f'"{key}"', f"exact environment scrub key {key}")
    require(shell_tests, "prevents_shell_snapshot_file_creation", "snapshot no-file test")
    require(runtime_tests, "cannot_be_resurrected_by_shell_snapshot", "snapshot scrub test")
    require(runtime_tests, "gate_without_snapshot_uses_non_login_shell", "no-snapshot test")
    require(runtime_tests, "gate_off_without_snapshot_preserves_argv", "argv equality test")
    require(
        process_tests,
        "covers_direct_and_exec_server_overlay_environments",
        "direct/exec-server production overlays",
    )
    require(producer, "gate_off_preserves_output_item", "gate-off item equality test")
    require(producer, "gate_off_preserves_exec_environment", "gate-off env equality test")

    print("FEAT-137 deterministic approval source conformance is valid.")


if __name__ == "__main__":
    main()
