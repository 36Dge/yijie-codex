# Runtime Baseline 0

## 定义

Runtime Baseline 0 是易界首次可消费的 Codex Runtime 技术基线。它固定一个不可变上游 commit，并保持 canonical source 零漂移。经授权的易界 patch 只在临时工作区可重放应用，构建仍需导出版本匹配的 app-server Schema，并通过不依赖真实凭据的本地 stdio 协议握手。

Baseline 0 解决的是“我们究竟基于哪一份 Runtime、能否重复得到同一协议面、Agent Host 可以从哪里开始适配”。它不负责跨境电商业务逻辑，也不宣称真实任务链路已完成。

此前受支持的易界 Runtime commit 为 `0ce5902ed400866be0196886bb78f693a004d68d`，只包含 FEAT-126 `0001`。当前 FEAT-136 工作是在相同上游源码上增加 Owner 单独授权的 `0002` candidate；隔离 build/generate/runtime-test 已通过，但在 Contracts repin 和下游 conformance 完成前，它仍不是新的受支持 Baseline。

## 固定决策

- upstream：`https://github.com/openai/codex.git`；
- tag：`rust-v0.144.6`；
- commit：`5d1fbf26c43abc65a203928b2e31561cb039e06d`；
- source：上游 `codex-rs/` 子树加根目录 `LICENSE`、`NOTICE`；
- patch 顺序：`0001-feat-126-filter-persistent-diagnostics.patch` → `0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch` → `0003-feat-137-stable-sandbox-provenance.patch` → `0004-feat-137-deterministic-approval-producer.patch`；
- Rust：`1.95.0`；
- primary target：`aarch64-apple-darwin`；
- app-server：稳定 API，`experimentalApi=false`，JSONL-over-stdio。

## 完成标准

1. `UPSTREAM.md` 和 `.yijie/upstream.env` 记录一致的上游 URL、tag、完整 commit、Runtime 版本和工具链。
2. `make sync` 从固定 commit 重建源码，验证 tag 解引用结果，内容相同时幂等，目标存在改动时不覆盖。
3. `verify-upstream-source.sh` 证明 `codex-rs/`、`LICENSE` 和 `NOTICE` 与上游一致。
4. `make apply-patches` 从固定上游按精确名称与顺序重放 reviewed `0001` → `0002` → `0003` → `0004` patch set，拒绝缺失、额外、乱序 patch 及对 canonical `codex-rs/` 的修改。
5. `make build` 使用固定 Rust 工具链和目标平台，以临时构建工作树产出 `codex-cli 0.144.6` release binary。
6. 上游 release lock 的正规化只能改变本地 workspace package 版本，且正规化前后 SHA-256 被记录。
7. `make generate` 使用构建产物导出 stable app-server JSON Schema，并进行 canonical JSON serialization。
8. `make runtime-test` 独立重生成 Schema 并逐文件比较，随后使用空白临时 `CODEX_HOME` 完成 `initialize` / `initialized` stdio 握手。
9. `runtime-manifest.json` 按顺序记录全部 patch 路径和 SHA-256，以及 upstream、target、Runtime 版本、binary SHA-256、Schema tree SHA-256 和 build lock 哈希。
10. CI 分开执行管理骨架门禁和 Runtime baseline 门禁。

## FEAT-136 candidate 状态

`0002` 修复 early sandbox-denial 在既有 emitter 创建前返回所造成的 Command lifecycle 缺失。它对同一 identity 发布 canonical `item/started` 和 failed `item/completed` 后仍返回原错误，不改变 retry/approval、sandbox 或权限决策。该变化的 `contract-impact = semantic`；隔离 build、Schema 生成和逐文件比较已确认 stable Schema shape 不变。

当前只确认以下门禁通过：

- focused `codex-core` early sandbox-denial lifecycle；
- 4 个 safe fake exec-server 场景；
- focused `codex-app-server-protocol` v2 Command notification mapping；
- `cargo fmt --all -- --check` 和 `codex-core` / `codex-app-server-protocol` scoped `clippy --no-deps -D warnings`；
- `scripts/test-fork-management.sh` 的 patch replay、精确 allowlist、Contracts v0.7.0 投影和安全 smoke wrapper 测试；
- Rust `1.95.0` macOS Apple Silicon release build、267-file stable Schema 生成/零差异比较；
- normal-EOF stdio smoke、双补丁 Runtime manifest 和 Runtime→Contracts 双向检查。

不得据此宣称 Runtime→Host→Desktop conformance 已通过。旧 Contracts `3c3000a6fbe2f08ab2131a463a1691e867d661b1` 必须由新的 candidate 精确 repin repaired Runtime immutable commit 与确认后的 Schema digest。

## FEAT-137 stable sandbox provenance candidate

Owner 授权的 `0003` 在 stable Command approval request 上增加必填 `sandboxPermissions`，只允许 `use_default`、`require_escalated`、`with_additional_permissions`。值从 originating tool request 经 core approval event 原样进入 app-server wire；它不改变 Runtime 的权限、审批或执行决策，public v6 API 也保持不变。对 strict stable-wire consumer，该新增必填字段分类为 `breaking`，必须由 Contracts 新的版本化 v6 compatibility 投影承接。

admission hardening 之前的 immutable Runtime source/focused tests、精确四补丁 replay、fmt、scoped Clippy、Rust `1.95.0` release build、267-file Schema 生成与 normal-EOF smoke 曾通过；其 Schema tree SHA-256 为 `d82a33f683e554c10dd056a0101c26fd24477928e3f98ee3d9ef250b97395228`，binary SHA-256 为 `896d303658a0978c3628f10e9e78f12139168be9508dd5f2abc658db186a828b`。当前 `0004` re-repair 已使该 binary/manifest 失去 authority；跨仓门禁必须等待新的 Runtime immutable freeze/build，再按 Contracts→Host→Desktop 顺序执行。

## FEAT-137 deterministic approval producer candidate

Owner 授权的 `0004` 默认关闭，只在 exact D4 进程 gate 值为 `1` 时生效。每个新 user turn 首步仅暴露一个 zero-argument strict `exec_command`，强制 required/non-parallel；raw Added/delta 在 client、rollout、session/OTEL sink 前抑制，首个 exact plain/nonempty-call-id Done 原子接纳并替换为固定 `use_default` 只读仓库检查。Provider 无 admitted Done、handler 未完成或 duplicate/hidden/invalid call 均 stable fail，fatal 不 drain 未 poll tool future；首 call 后同一 TurnContext 的 steer/follow-up 继续 no-tools/auto。exact managed profile 要求 hooks/plugins/apps/tool search 全关，Runtime 在 hook/plugin/MCP contributor 前 fail closed，configured/runtime/effective MCP server 与 connector 投影为零。shell snapshot capture 禁用；direct、exec-server、override 和 no-snapshot non-login wrapper 精确清除 reviewed private credential/gate/startup-file names。开关关闭时原工具列表、auto choice、parallel、Provider item/arguments、hook/plugin/MCP composition 和 env map/policy 保持相等。

该变化 `contract-impact = semantic`：不改变 stable app-server/public v6 shape，不提升权限，也不改变 approval/execute decision。当前 re-repair 的 25/25 safe focused（`codex-core` 24、`codex-api` 1）、精确四补丁 fresh replay/equality、scoped Clippy 与 source-conformance checker 已通过；新的 immutable freeze、release build、267-file Schema/manifest equality、Runtime→Contracts→Host→Desktop repin 与 post-repair fresh D4 仍须按顺序完成。admission hardening 之前的 binary/manifest 不再具有当前 authority。

## 非完成项

- 不执行真实模型 turn，不需要 OpenAI API key 或 Codex access token；
- 不验证 MCP 工具、审批和业务任务；Tool D4 保持 `BLOCKED/NOT RUN`，不得制造 Tool producer；
- 不完成 `yijie-agent-host` transport；
- 不打包、签名或 notarize Desktop sidecar；
- 不确定 cloud runner transport、认证和部署模型；
- `0002` 仅补齐 Command producer 的可观察失败 lifecycle，不改变 app-server 认证、sandbox 权限或模型错误处理决策。

## 产物

```text
.yijie/build/<platform>/<target>/
  codex
  resolved-Cargo.lock
  lock-normalization.json
  runtime-manifest.json

.yijie/schemas/app-server/
  baseline.json
  generated-json-schema/
```

构建目录不提交 Git；Schema 和 baseline metadata 提交并由 CI 检查漂移。
