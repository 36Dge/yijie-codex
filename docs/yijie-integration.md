# Yijie Integration

Runtime Baseline 0 为 `yijie-agent-host` 提供两个输入：

- `.yijie/build/macos/aarch64-apple-darwin/codex`：本地构建产物；
- `.yijie/schemas/app-server/generated-json-schema/`：与固定 Runtime 版本匹配的稳定协议 Schema。

`yijie-contracts/compatibility/agent-host-runtime-v1.json` 固定 Agent Host 实际消费的
Runtime 版本、Schema tree 和 method/notification 子集。相邻 contracts checkout 存在时，
`make runtime-test` 会把该清单与本仓库基线、实际 Schema 和刚生成的 Runtime manifest
逐项比对；独立 checkout 没有 sibling 时只会明确跳过这项跨仓门禁。

Desktop MVP 的首选边界是由 Agent Host 启动 `codex app-server --listen stdio:// --strict-config`，通过 JSONL 发送 `initialize`、`initialized`、thread 和 turn 请求，并消费通知。Agent Host 不应以当前占位的 HTTP URL 配置替代本地 stdio 进程生命周期管理。

Baseline 0 没有决定 cloud runner transport，也没有授权通过公网暴露 app-server。真实集成必须继续遵守 token、审批、MCP 工具和日志脱敏边界。
