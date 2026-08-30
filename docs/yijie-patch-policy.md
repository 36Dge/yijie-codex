# Yijie Patch Policy

canonical `codex-rs/` 必须继续与 Runtime Baseline 0 的固定上游 commit 字节级一致。易界 patch 只能保存在 `.yijie/patches/`，并由 `scripts/apply-yijie-patches.sh` 应用到临时构建工作区；脚本明确拒绝修改 canonical 物化目录。

当前 Runtime candidate 只允许以下严格有序 overlay，patch replay 与 manifest 写入器都必须拒绝缺失、重命名、额外或乱序文件：

1. `0001-feat-126-filter-persistent-diagnostics.patch`：解决 FEAT-126 full-case R8 发现的本地 SQLite 路径日志持久化问题，不改变 app-server schema、transport 或外部业务协议。
2. `0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch`：Owner 单独授权的最小 Runtime producer 修复；治理记录如下。

## FEAT-136 `0002` 治理记录

- 原因与 Host 边界：early sandbox-denial 会在 unified exec 创建既有 emitter 前返回，Runtime 虽把失败结果交回模型侧，却没有向 app-server 发布 Command lifecycle。Host 位于 producer 下游，无法可靠重建 Runtime 未发布的 event identity、顺序、duration 或 terminal authority，因此不能在 Host mapper 中伪造。
- 源码基线：上游固定为 `rust-v0.144.6` / `5d1fbf26c43abc65a203928b2e31561cb039e06d`；易界 candidate 从此前 Runtime commit `0ce5902ed400866be0196886bb78f693a004d68d` 开始，只把 `0002` 重放到一次性构建工作区，不修改 canonical `codex-rs/`。
- 顺序：必须先应用 FEAT-126 `0001`，再应用 FEAT-136 `0002`。两个 patch 的路径和 SHA-256 都进入 Runtime manifest。
- 行为：只在最终 `UnifiedExecError::SandboxDenied` 返回分支，对同一 call/process identity 恰好发布一次 canonical `item/started`（`inProgress`）和一次 `item/completed`（`failed`，携带原 nonzero exit code、duration 和聚合输出），随后原样返回错误。不得移除 early denial 检测，也不得改变 retry/approval、sandbox、权限或 ToolOrchestrator 决策。
- 契约影响：`contract-impact = semantic`。可观察 lifecycle 由缺失变为完整；没有设计新增 wire 类型或字段，且隔离 build/generate 与 Schema 逐文件比较已确认 stable shape 不变，但不能因此降为 `none`。
- 已完成验证：focused `codex-core` lifecycle、4 个 safe fake exec-server 场景、focused `codex-app-server-protocol` v2 mapping、fmt、两组 scoped clippy、`scripts/test-fork-management.sh`、隔离 release build、Schema 生成/零差异比较、normal-EOF `runtime-test`、binary/manifest 固化及 Runtime→Contracts 双向检查已通过。Contracts immutable repin 和 Runtime→Host→Desktop conformance 尚未完成。
- Contracts provenance：旧 commit `3c3000a6fbe2f08ab2131a463a1691e867d661b1` 固定的是此前 Runtime，不能作为 repaired candidate 的精确输入。Runtime 形成 immutable commit 且 Schema digest 确认后，必须创建新的 Contracts candidate repin，再允许 Host/Desktop conformance。
- 回滚：恢复此前受支持 Runtime commit `0ce5902ed400866be0196886bb78f693a004d68d` 和与其匹配的 Contracts provenance。若从尚未晋升的 candidate 删除 `0002`，同一治理变更必须同步 allowlist、manifest 与文档；禁止在构建时临时跳过 patch。
- 上游升级删除条件：只有新上游原生提供相同的 exactly-once canonical started/failed terminal，且 focused core/protocol、Schema、Host completed reconciliation、Desktop reducer/hydration 和权限语义复核全部通过后，才删除 `0002` 并更新 Runtime/Contracts pins。若实现或语义不等价，继续移植最小 patch 或停止升级评审。
- D4 边界：本 patch 只修复 Command producer。Tool D4 保持 `BLOCKED/NOT RUN`；不得注册 MCP/Connector/dynamic tool 或制造 producer 来获得证据。

优先通过上游配置、稳定 app-server API、MCP、Skills、Plugins 或 `yijie-agent-host` 适配解决需求。只有这些边界无法满足经过确认的产品或安全要求时，才可以提议 Runtime patch。

新增 patch 前必须取得用户对修改范围的明确确认，并为每个 patch 记录：

- 上游 issue/限制和不能在 Host 层解决的原因；
- 依赖的固定 commit；
- 应用顺序；
- 行为和协议影响；
- 构建、测试和 Agent Host 兼容性验证；
- 回滚方式；
- 下一次上游升级时的删除条件。

patch 必须能从 `UPSTREAM.md` 固定的零修改源码按上述顺序重复应用。不得直接修改 `codex-rs/` 后再补写 patch 文件。每个构建 manifest 必须记录全部 patch 的相对路径和 SHA-256；Host 必须固定接受的完整 patch 集与 binary identity。
