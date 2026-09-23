# Upstream

## 固定版本

| 字段 | 值 |
|---|---|
| upstream remote | `https://github.com/openai/codex.git` |
| fork remote | `https://github.com/36Dge/yijie-codex.git` |
| pinned tag | `rust-v0.144.6` |
| pinned commit | `5d1fbf26c43abc65a203928b2e31561cb039e06d` |
| Runtime version | `0.144.6` |
| Rust toolchain | `1.95.0` |
| primary release target | `aarch64-apple-darwin` |
| synchronized at | `2026-07-21` |

机器可读值位于 `.yijie/upstream.env`。tag 必须解析到上表完整 commit，否则同步失败。

## 源码策略

- 将固定 commit 的 `codex-rs/` 子树物化到本仓库 `codex-rs/`；
- 同时保留上游根目录 `LICENSE` 和 `NOTICE`；
- 不导入 Codex 的 IDE extension、cloud 或其它非 Runtime 源码；
- 同步时通过临时目录生成候选源码，内容一致时保持幂等，内容不一致且目标存在本地改动时拒绝覆盖；
- `scripts/verify-upstream-source.sh` 使用上游 Git object 对 `codex-rs/`、`LICENSE` 和 `NOTICE` 做字节级比较，忽略本地 `target/` 构建缓存。

## Patch 顺序

固定上游源码物化保持零漂移。构建时按文件名字典序向临时工作区应用：

1. `0001-feat-126-filter-persistent-diagnostics.patch`：阻止路径承载的 HTTP、stream、shell、feedback、rollout、core util 和根级 app-server 配置诊断进入本地 SQLite；保留经审查的 state 与 app-server 子 target 日志。该 patch 不改变 app-server schema 或 transport。
2. `0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch`：基于同一上游 `rust-v0.144.6` / `5d1fbf26c43abc65a203928b2e31561cb039e06d`，并以此前易界 Runtime commit `0ce5902ed400866be0196886bb78f693a004d68d` 为 candidate 起点，修复 unified exec 在 early sandbox-denial 检测后、既有 emitter 创建前直接返回，导致 Command lifecycle 从 Runtime→Host→Desktop 链路消失的问题。它只在最终 `SandboxDenied` 返回分支，以相同 call/process identity 依次发布 canonical `item/started`（`inProgress`）和 `item/completed`（`failed`，保留 nonzero exit code、duration 与聚合输出），随后返回原错误；不删除检测、不改变 ToolOrchestrator retry/approval、sandbox 或权限语义，也不制造 Tool producer。
3. `0003-feat-137-stable-sandbox-provenance.patch`：为 stable `item/commandExecution/requestApproval` 增加必填 `sandboxPermissions`。字段只允许 Runtime 已有枚举 `use_default`、`require_escalated`、`with_additional_permissions`，并从 shell/unified-exec tool request 经 `ExecApprovalRequestEvent` 原样传递到 app-server stable wire；不改变执行权限、审批决策或 public v6 API。
4. `0004-feat-137-deterministic-approval-producer.patch`：默认关闭；仅当 Host 在 exact Owner-run D4 进程显式设置 `YIJIE_FEAT137_DETERMINISTIC_APPROVAL_PRODUCER=1` 时，每个新 user turn 首步只向 Provider 暴露一个 zero-argument、strict、closed `exec_command`，强制 `tool_choice=required` 且禁止 parallel。gate-on 的 raw Added/argument delta 在 client `items_added`、`LastResponse`、rollout trace、session telemetry/history/hooks/OTEL/dispatch 前抑制；首个 exact plain/nonempty-call-id Done 原子接纳并替换为唯一固定的 `use_default` 只读仓库检查，handler 再验证相同 call-id 与 one-shot lifecycle。无 admitted Done 的 Provider terminal、hidden/namespaced/empty-id/duplicate/后续 tool call 或未完成 handler 均 stable fail；fatal 直接丢弃未 poll tool future。首 call 后同一 TurnContext 即使收到 steer 仍保持 no-tools/auto。gate-on 在 hook/plugin 与 MCP extension contributor 之前返回空 surface，managed profile 必须显式关闭 hooks/plugins/apps/tool search，configured/runtime/effective MCP server 与 connector 均为零。shell snapshot capture 禁用；direct、exec-server、override 与 no-snapshot non-login wrapper 精确移除 reviewed private credential/gate/startup-file names。不提升权限、不修改审批/执行决定，也不改变 public v6 或 stable app-server schema。

`0002` 的 `contract-impact = semantic`：可观察的失败生命周期被补齐，但 stable wire 类型和字段 shape 不变。隔离 release build、Schema 生成和逐文件比较已确认仍为 267 个 stable JSON 文件且无 tracked diff。

`0004` 的 `contract-impact = semantic`：stable wire shape 不变，但显式 D4 gate 开启时的 Provider 工具可见性、turn-scoped admission/lifecycle、hook/plugin/MCP surface、wire logging 与 child-process environment 发生受限变化；gate 关闭时 tools、`tool_choice=auto`、parallel、Provider item/arguments、MCP composition、hook/plugin discovery 和环境 map/policy 均保持原结构/字节值。

patch 的相对路径和 SHA-256 进入 Runtime manifest。管理脚本只接受上述 `0001` → `0002` → `0003` → `0004` 精确名称与顺序，拒绝缺失、重命名、额外或乱序 patch。`make apply-patches` 必须从上述固定 commit 独立重放成功，且不得修改 canonical `codex-rs/` 物化目录。

`0002` 的回滚必须恢复此前受支持的 Runtime commit `0ce5902ed400866be0196886bb78f693a004d68d` 及其匹配的 Contracts provenance；若从 candidate 删除 patch，也必须在同一治理变更中同步 allowlist、manifest 和文档，不能临时跳过。下一次上游升级只有在新上游已经原生保证 early sandbox-denial 对同一 Command 恰好发布一次 canonical started/failed terminal、focused core/protocol 与下游 reconciliation 回归通过、Schema 和权限语义完成复核后，才可删除 `0002` 并重新 pin Runtime/Contracts。

## Release lock 正规化

此 release tag 的 `workspace.package.version` 是 `0.144.6`，但上游 `Cargo.lock` 中 132 个本地 workspace package 仍记录为 `0.0.0`。直接执行 `cargo build --locked` 会失败。

构建脚本不会修改上游 lockfile，而是在临时、从固定 commit 重新物化的构建工作树中执行目标平台解析。`verify-release-lock-drift.py` 要求解析结果与上游 lock 的唯一差异是本地 workspace package 的 `0.0.0 -> 0.144.6`；其它任何依赖或 checksum 漂移都会使构建失败。两个 lock 的 SHA-256 会进入构建报告和 Runtime manifest。

## 兼容性结论

既有单 patch Baseline 0 在 `2026-07-21` 对 macOS Apple Silicon 完成：

- 固定源码零漂移和单 patch 重放：通过；
- `codex-cli 0.144.6` release 构建：通过；
- stable app-server JSON Schema 生成：267 个文件；
- Schema 独立重生成一致性：通过；
- 无凭据 JSONL-over-stdio `initialize` / `initialized` 握手：通过；
- manifest、binary SHA-256、Schema tree SHA-256 和 lock 正规化记录：已生成。

未包含真实模型 turn、MCP 工具调用、审批链、Agent Host 事件映射、Desktop sidecar 签名或 cloud runner 验证。

FEAT-136 双 patch candidate 当前已通过：

- focused `codex-core` early sandbox-denial lifecycle 回归；
- 4 个 safe fake exec-server 场景，包括最终 direct denial、legacy exit metadata 和 replay gap；
- focused `codex-app-server-protocol` canonical v2 Command mapping 回归；
- `cargo fmt --all -- --check` 以及 `codex-core` / `codex-app-server-protocol` scoped `clippy --no-deps -D warnings`；
- `scripts/test-fork-management.sh`，包括严格双 patch allowlist、独立重放和 wrapper 单元/安全门禁；
- Rust `1.95.0` macOS Apple Silicon release build、267-file Schema 生成与逐文件零差异比较；
- normal-EOF app-server stdio `initialize` / `initialized`、双补丁 artifact manifest 与 Runtime→Contracts 双向兼容检查。

尚未完成 Contracts 新 immutable candidate、Host/Desktop 精确 repin 及 Runtime→Host→Desktop conformance。旧 Contracts commit `3c3000a6fbe2f08ab2131a463a1691e867d661b1` 仍记录此前 Runtime provenance；必须由新的 Contracts candidate 精确 repin 新 Runtime immutable commit 和已确认 Schema digest。Tool D4 保持 `BLOCKED/NOT RUN`。
# FEAT-155 input-only candidate supplement

2026-09-19: the upstream pin and canonical `codex-rs/` subtree remain unchanged. The separately built input-only candidate applies the two active patches followed by `.yijie/patches/input-only/0003-input-only-execution.patch`. Its schema and binary live in dedicated candidate directories and must be projected through Contracts before Host activation. See [native restriction](docs/input-only-execution.md). Existing historical baseline statements below retain their original meaning.
