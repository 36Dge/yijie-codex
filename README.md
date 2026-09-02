# yijie-codex

Codex Runtime 的易界 fork 管理仓库。仓库固定上游源码、维持最小补丁集、构建 Runtime，并验证易界 Agent Host 所依赖的 app-server 协议。

## 仓库职责

- 同步 Codex 上游源码；
- 管理易界必要 patch；
- 构建桌面端和云端 runner 所需 runtime binary；
- 维护 app-server 协议兼容性；
- 输出 runtime 版本给 `yijie-agent-host` 使用。

## 禁止事项

- 禁止写跨境电商业务逻辑；
- 禁止处理平台 API token；
- 禁止写 Listing、Ads、Compliance 等领域 prompt；
- 禁止破坏上游目录结构。

## 当前状态

Runtime Baseline 0 已建立：

- 上游固定为 `openai/codex` 的 `rust-v0.144.6`；
- 完整 commit 为 `5d1fbf26c43abc65a203928b2e31561cb039e06d`；
- `codex-rs/` 与该 commit 的上游子树字节级一致；
- 当前 Runtime candidate 构建时严格按 `0001` → `0002` → `0003` → `0004` 应用四个可重放 patch：FEAT-126 持久诊断日志安全 patch、FEAT-136 early sandbox-denial Command lifecycle patch、FEAT-137 stable sandbox provenance patch，以及仅由 exact D4 进程环境 gate 启用的确定性只读 approval producer patch；
- 首个发布目标为 `aarch64-apple-darwin`；
- app-server 客户端基线使用稳定 API、JSONL-over-stdio；
- 版本匹配的 JSON Schema 位于 `.yijie/schemas/app-server/`。

构建产物写入 `.yijie/build/<platform>/<target>/`，不提交 Git。产物目录包含 Runtime binary、解析后的构建 lock、lock 正规化报告和 `runtime-manifest.json`。

## Runtime Baseline 0

Baseline 0 固定不可变上游源码、协议 Schema 和工具链。易界 overlay 只在临时构建工作区应用。`0001-feat-126-filter-persistent-diagnostics.patch` 收紧本地 SQLite 诊断日志；`0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch` 补齐 early sandbox-denial 的 canonical Command terminal；`0003-feat-137-stable-sandbox-provenance.patch` 为 stable `item/commandExecution/requestApproval` 增加必填 `sandboxPermissions`，并从 tool request 经 core approval event 原样投影到 app-server wire；`0004-feat-137-deterministic-approval-producer.patch` 默认关闭，只在 `YIJIE_FEAT137_DETERMINISTIC_APPROVAL_PRODUCER=1` 的 Owner-run D4 进程中，把每个新 user turn 的首步工具面收窄为一个 zero-argument strict `exec_command`。gate 开启时，Runtime 在 client `items_added`、`LastResponse`、rollout trace、session telemetry/history/hooks/OTEL/dispatch 之前抑制 raw Added/delta，并原子接纳首个 exact plain/nonempty-call-id Done、替换为固定 `use_default` 只读仓库检查；无 admitted Done 的 Provider terminal、duplicate/hidden/invalid call 或不完整 handler lifecycle 均以 stable fatal 封口，已排队但未 poll 的首个 tool future 不会在 fatal 后进入审批或执行。admitted 状态在同一 TurnContext 的 steer/follow-up 中继续关闭工具面。exact gate 还在任何 hook/plugin/MCP extension contributor 启动前 fail closed：managed profile 必须关闭 hooks、plugins、apps 与 tool search，所有 configured/runtime/effective MCP server 和 connector projection 为空。shell snapshot capture gate-on 完全禁用；direct、exec-server、override 与 no-snapshot non-login wrapper 精确清除 reviewed private credential/gate/startup-file 名称，不使用模糊 key 匹配。它不提升权限，不改变审批决定，也不改变 public v6 或 stable app-server wire shape。

FEAT-136 的 `contract-impact` 为 `semantic`。隔离 macOS Apple Silicon release build、Schema 生成和逐文件比较已确认 stable app-server Schema 仍为 267 个文件、tree SHA-256 `82ee9de771cf1d41bac16d87380f1121e7794107aa3aa526ad702d5d1bf7afe1` 且无 tracked diff；normal-EOF stdio smoke、focused `codex-core`、4 个 safe fake exec-server 场景、`codex-app-server-protocol`、fmt、scoped clippy、fork-management 及 Runtime→Contracts 双向门禁均通过。这仍不等同于 Runtime→Host→Desktop conformance 已通过。旧 Contracts commit `3c3000a6fbe2f08ab2131a463a1691e867d661b1` 固定此前 Runtime provenance，必须由新的 Contracts candidate 重新 pin。Tool D4 未执行，且本 patch 不制造 Tool producer。

FEAT-137 `0003` 的 `contract-impact` 为 `breaking`，仅因为 closed stable-wire consumer 必须接收新增必填 provenance；public v6 API 仍不变。admission hardening 之前的隔离 release build 与 canonical generation 曾确认 stable Schema 为 267 个文件、tree SHA-256 `d82a33f683e554c10dd056a0101c26fd24477928e3f98ee3d9ef250b97395228`，且 enum 恰好为三种既有 Runtime sandbox permission。Contracts 仍必须在新 Runtime freeze/build 后以版本化 compatibility 投影重新精确 pin。

上述 FEAT-137 binary/Schema 数值属于 admission hardening 之前的 immutable Runtime。当前 `0004` re-repair 的 25/25 safe focused（24 个 `codex-core`、1 个 `codex-api`）覆盖 early client/wire boundary、terminal/handler lifecycle、same-turn closure、hook/plugin/MCP zero surface、snapshot no-file 与 spawn scrub；source replay、scoped Clippy 与 source-conformance 完成后，仍必须重新冻结、构建、生成 Schema/manifest 并依次重 pin Contracts、Host、Desktop，旧 artifact 不得用于 fresh D4。

它不表示 Desktop sidecar、真实模型回合或云端 runner 已完成。

详细定义和完成标准见 [`docs/runtime-baseline-0.md`](docs/runtime-baseline-0.md)。

## 开发与验证

```bash
make lint
make test
make sync
make apply-patches
make build
make generate
make runtime-test
```

`make runtime-baseline` 串联全部步骤。默认构建当前 Rust host target；发布 macOS Apple Silicon 基线时设置：

```bash
YIJIE_RUNTIME_TARGET=aarch64-apple-darwin make runtime-baseline
```

构建要求 Rust `1.95.0`。`make runtime-test` 不读取用户现有 Codex 登录态，也不调用真实模型或平台服务。
相邻 `yijie-contracts` checkout 存在时，它还会严格校验
历史 `compatibility/agent-host-runtime-v1.json` immutable Runtime object 与当前
`compatibility/agent-host-runtime-approval-v6-v3.json` stable approval authority；可用
`YIJIE_CONTRACTS_REPO` 指定其它位置，
未检出 sibling 时该跨仓检查会输出 `SKIP`，不影响独立仓验证。
