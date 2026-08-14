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
- 构建时应用一个可重放的 FEAT-126 持久诊断日志安全 patch；
- 首个发布目标为 `aarch64-apple-darwin`；
- app-server 客户端基线使用稳定 API、JSONL-over-stdio；
- 版本匹配的 JSON Schema 位于 `.yijie/schemas/app-server/`。

构建产物写入 `.yijie/build/<platform>/<target>/`，不提交 Git。产物目录包含 Runtime binary、解析后的构建 lock、lock 正规化报告和 `runtime-manifest.json`。

## Runtime Baseline 0

Baseline 0 固定不可变上游源码、协议 Schema 和工具链。易界 overlay 只在临时构建工作区应用，当前单一 patch 收紧本地 SQLite 诊断日志，不改变 app-server 协议面。它不表示 Desktop sidecar、真实模型回合或云端 runner 已完成。

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
`compatibility/agent-host-runtime-v1.json`；可用 `YIJIE_CONTRACTS_REPO` 指定其它位置，
未检出 sibling 时该跨仓检查会输出 `SKIP`，不影响独立仓验证。
