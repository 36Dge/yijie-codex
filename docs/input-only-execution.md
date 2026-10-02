# Input-only native execution candidate

FEAT-155's 2026-09-19 unblock request authorizes implementing the minimum native restriction needed by its text draft flow. The upstream remains `rust-v0.144.6` / `5d1fbf26c43abc65a203928b2e31561cb039e06d`. This candidate uses the active FEAT-126 and FEAT-136 patches plus `input-only/0003-input-only-execution.patch`; it never uses or revives the retired FEAT-137 patches.

`input_only = true` is an opt-in native thread configuration. Default is false. The restriction permits explicitly supplied text, the thread's own native history, normal internal state persistence and the configured text model channel. It grants no task filesystem read/write roots, no tool network permission and no executable/model-visible tools. It does not implement schedules, business prompts, platform tools or a user-facing permission mode.

Native enforcement precedes external instruction and agent-role file loading, remote thread-config loading, user-instruction providers, AGENTS discovery, skills, hooks, plugin and MCP contributors. Thread extensions are empty; memory generation/use, shell snapshots and startup model/auth prewarm are disabled for the thread. The final tool router returns both an empty advertised set and an empty executable registry, including deferred/hidden tools. Non-text inputs and non-lifecycle operations are rejected before input processing. Non-text model output is rejected before item handling or tool follow-up; an unsupported tool response cannot trigger another model request. Permission/environment changes cannot widen the session restriction. Ordinary threads retain their existing behavior.

The stable read-only `thread/inputOnlyPolicy/read` method operates on an already loaded native thread. Ordinary threads return `policy: null`. Restricted threads return versioned evidence only after checking the live permission snapshot, loaded instruction sources and effective MCP catalog. Empty task roots and the native no-tool branch are part of the enforced contract, not a restatement of the caller's intended profile. The Host must bind the receipt to the exact thread/cwd, fixed binary and current managed Runtime generation; cold resume must request the restriction again and recheck it. Host's durable purpose check remains authoritative for which task may resume which thread.

Build with `make input-only-build`. The canonical script archives the immutable upstream subtree into an owned temporary workspace, applies exactly the three reviewed patches, performs offline lock normalization with the existing drift checker, builds with Rust 1.95.0 and generates stable schemas/manifest. New output is `.yijie/build/input-only/aarch64-apple-darwin/`; schemas are `.yijie/schemas/input-only-app-server/`. The existing fixed FEAT-136 artifact and historical four-patch schema are preserved.

Contract impact is conservatively breaking for the complete cross-repository candidate because exact artifact/schema pins change. The new method/config are opt-in, existing method responses stay compatible, and old artifacts remain supported for ordinary behavior. Runtime source/schema precede Contracts projection and Host consumption. No production release, tag, commit or default Desktop activation is implied by a local build. Missing proof keeps drafts unavailable; rollback stops new draft producers while preserving compatible Host/Desktop readers and history.

Validation must separately record replay/build/schema, ordinary compatibility, safe focused tests, actual native start/resume/normal reopen and Provider output-schema support. In-process fixtures cannot qualify the actual native restriction. All tests use normal temporary owned data and orderly shutdown; no forced process kills, permissions sabotage, attack payloads or executable substitution. The FEAT-155 report records actual results; this design document itself is not a PASS claim.

## FEAT-156 Kimi compatibility candidate (2026-10-02)

Owner explicitly authorized restoring upstream `tool_choice="auto"` after the input-only patch, while retaining its empty advertised/executable tools, input-only admission, non-text output rejection, sandbox, permissions and extension restrictions. `.yijie/patches/chat-models/0004-feat-156-upstream-tool-choice.patch` changes only the Responses request value in `core/src/client.rs`. Upstream tag/commit, transport and toolchain are unchanged. Ordinary nonempty-tool requests already use auto.

`make chat-models-build` replays the active 0001/0002/input-only 0003/new 0004 in a temporary source workspace. It reuses the existing `codex-rs/target` cache (approximately 24 GiB); it does not copy or create another target cache. Candidate binary, manifest, resolved lock and 269 regenerated schemas are stored separately under `.yijie/build/chat-models/aarch64-apple-darwin/`. Existing fixed input-only and FEAT-136 artifacts are retained. The command refuses to overwrite an existing new candidate.

The new schema tree must equal the input-only authority byte for byte. Contracts imports a separate `runtime-chat-models` artifact projection; existing input-only source locks remain intact. Host accepts only exact artifact pins and continues checking each draft's live native policy. Rollback selects the preserved fixed artifact and disables new Kimi draft writes, retaining historical readers. No automatic fallback or provider proxy parameter rewrite is introduced.

The parameter change is semantic; the complete FEAT-156 candidate retains its conservative breaking classification because exact artifact pins change. This local working-tree candidate is not a release or immutable Git promotion. Actual build, schema and paid verification results are recorded in the FEAT-156 package.


## FEAT-156 最终响应参数兼容

Owner已明确批准最小流式兼容补丁 `chat-models/0005-feat-156-terminal-tool-arguments.patch`（semantic）。固定上游与0001/0002/input-only0003/已批准0004保持。仅在中间function_call完成Item参数为空时暂存后续事件，等完整response.completed后校验Item索引、ID、callID、函数名、namespace、有效JSON对象及参数增量一致，再按原顺序进入工具处理。非空参数继续流式处理；未获完整一致终态时安全错误，不执行空/猜测参数。缓冲有界，不新增权限或工具，input-only原拒绝路径保持。

新候选由 `make chat-model-stream-build` 生成到 `.yijie/build/chat-models-stream-args/aarch64-apple-darwin/`，复用原 `codex-rs/target`。原input-only和chat-models产物不覆盖；原始codex-rs子树不修改。`make chat-model-stream-test`检验重放/逆向、schema和正常EOF握手。实际构建/资格结果及精确hash以FEAT-156 evidence为准，不能把本说明当已通过或已发布。
