# Yijie Changelog

## Unreleased

- Harden the Owner-authorized FEAT-137 `0004-feat-137-deterministic-approval-producer.patch` after live RCA. Under the exact D4 gate, raw tool Added/argument delta/Done payloads are suppressed or fixed before client `items_added`, `LastResponse`, rollout trace, session telemetry/history/hooks/OTEL/dispatch; a Provider terminal without the exact admitted call and a turn without the completed handler lifecycle fail with stable errors. Duplicate/hidden/invalid calls drop queued, unpolled tool work before approval/execute, and admitted state keeps same-turn steer/follow-up tools closed. Hook/plugin startup and ambient configured/plugin/extension/Apps MCP contributions are disabled before contributors run, producing zero configured/runtime/effective MCP servers and connectors. Shell snapshot capture is disabled and the no-snapshot non-login wrapper plus direct/exec-server policies remove only reviewed private credential/gate/startup-file names. Gate-off behavior, permissions, approval decisions, public v6, and stable app-server wire shape remain unchanged (`contract-impact = semantic`).
- Add the Owner-authorized FEAT-137 `0003-feat-137-stable-sandbox-provenance.patch`: stable `item/commandExecution/requestApproval` now requires `sandboxPermissions` (`use_default`, `require_escalated`, or `with_additional_permissions`) carried unchanged from the originating tool request through the core approval event to app-server. Execution authority, approval decisions, and the public v6 API remain unchanged.
- Require the exact ordered `0001` → `0002` → `0003` → `0004` overlay. The versioned Contracts v6 compatibility projection remains authoritative for stable provenance; `0004` adds no wire shape.
- Add the Owner-authorized FEAT-136 candidate patch `0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch` after FEAT-126 `0001`. It emits one canonical Command `item/started` followed by one failed `item/completed` when final early sandbox denial previously returned before emitter creation, while preserving the original error, nonzero exit details, retry/approval decisions, sandbox, and permissions.
- Classify the FEAT-136 Runtime change as `semantic`: isolated macOS Apple Silicon release build and schema regeneration confirm the stable app-server Schema remains 267 files with no tracked diff. Focused core, four safe fake exec-server scenarios, focused app-server-protocol, fmt, scoped clippy, fork-management, normal-EOF stdio smoke, and Runtime→Contracts checks pass; downstream Host/Desktop conformance is not yet claimed.
- Require the exact ordered `0001` → `0002` overlay in patch replay and Runtime manifests, and make the credential-free app-server smoke harness close by stdin EOF without terminate/kill fallback.
- Keep Contracts `3c3000a6fbe2f08ab2131a463a1691e867d661b1` as historical provenance only until a new immutable candidate repins the repaired Runtime and confirmed Schema digest. Tool D4 remains blocked and was not run.
- Add a replayable FEAT-126 Runtime patch that excludes path-bearing HTTP, stream, shell, rollout, core utility, and feedback diagnostic targets from persistent SQLite logs while retaining reviewed state and app-server sub-target logs.
- Bind the reviewed patch path and SHA-256 into the Runtime artifact manifest and apply it only inside disposable build workspaces.
- Add a bidirectional `yijie-contracts` compatibility gate that pins the Runtime source, stable Schema tree, and exact Agent Host method/notification projection while remaining optional for standalone checkouts.
- Ignore local `.DS_Store` metadata consistently in upstream sync and zero-patch source verification while retaining all substantive source-drift checks.
- Establish Runtime Baseline 0 on upstream `rust-v0.144.6` commit `5d1fbf26c43abc65a203928b2e31561cb039e06d`.
- Materialize the exact upstream `codex-rs/` subtree with Apache-2.0 license and notice files.
- Keep canonical `codex-rs/` byte-for-byte equal to upstream and verify any Yijie overlay independently.
- Add reproducible release build orchestration for macOS Apple Silicon and host-target CI.
- Audit the upstream release lock normalization without modifying the pinned source lockfile.
- Generate and canonicalize 267 stable app-server JSON Schema files.
- Add credential-free JSONL-over-stdio app-server handshake compatibility testing.
- Generate artifact manifests with source, binary, Schema, and build-lock SHA-256 records.
## FEAT-155 input-only candidate (2026-09-19)

Add an opt-in native text-input restriction with no executable tools, no task filesystem/network permissions, no inherited instructions/skills/hooks/MCP/plugin contributors, and a stable read-only policy query. Default ordinary behavior and the immutable upstream source remain unchanged. Build from the active two-patch baseline into a separate reproducible candidate; the retired FEAT-137 patch set is excluded. Qualification and downstream activation require actual native evidence and source-first Contracts projection. See [design and validation boundaries](docs/input-only-execution.md).

## FEAT-156 Kimi compatibility candidate (2026-10-02)

Owner explicitly authorized restoring upstream `tool_choice="auto"` after the input-only patch, while retaining its empty advertised/executable tools, input-only admission, non-text output rejection, sandbox, permissions and extension restrictions. `.yijie/patches/chat-models/0004-feat-156-upstream-tool-choice.patch` changes only the Responses request value in `core/src/client.rs`. Upstream tag/commit, transport and toolchain are unchanged. Ordinary nonempty-tool requests already use auto.

`make chat-models-build` replays the active 0001/0002/input-only 0003/new 0004 in a temporary source workspace. It reuses the existing `codex-rs/target` cache (approximately 24 GiB); it does not copy or create another target cache. Candidate binary, manifest, resolved lock and 269 regenerated schemas are stored separately under `.yijie/build/chat-models/aarch64-apple-darwin/`. Existing fixed input-only and FEAT-136 artifacts are retained. The command refuses to overwrite an existing new candidate.

The new schema tree must equal the input-only authority byte for byte. Contracts imports a separate `runtime-chat-models` artifact projection; existing input-only source locks remain intact. Host accepts only exact artifact pins and continues checking each draft's live native policy. Rollback selects the preserved fixed artifact and disables new Kimi draft writes, retaining historical readers. No automatic fallback or provider proxy parameter rewrite is introduced.

The parameter change is semantic; the complete FEAT-156 candidate retains its conservative breaking classification because exact artifact pins change. This local working-tree candidate is not a release or immutable Git promotion. Actual build, schema and paid verification results are recorded in the FEAT-156 package.


## FEAT-156 terminal tool arguments（2026-10-02）

Owner已明确批准最小流式兼容补丁 `chat-models/0005-feat-156-terminal-tool-arguments.patch`（semantic）。固定上游与0001/0002/input-only0003/已批准0004保持。仅在中间function_call完成Item参数为空时暂存后续事件，等完整response.completed后校验Item索引、ID、callID、函数名、namespace、有效JSON对象及参数增量一致，再按原顺序进入工具处理。非空参数继续流式处理；未获完整一致终态时安全错误，不执行空/猜测参数。缓冲有界，不新增权限或工具，input-only原拒绝路径保持。

新候选由 `make chat-model-stream-build` 生成到 `.yijie/build/chat-models-stream-args/aarch64-apple-darwin/`，复用原 `codex-rs/target`。原input-only和chat-models产物不覆盖；原始codex-rs子树不修改。`make chat-model-stream-test`检验重放/逆向、schema和正常EOF握手。实际构建/资格结果及精确hash以FEAT-156 evidence为准，不能把本说明当已通过或已发布。
