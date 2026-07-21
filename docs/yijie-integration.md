# Yijie Integration

Runtime Baseline 0 为 `yijie-agent-host` 提供两个输入：

- `.yijie/build/macos/aarch64-apple-darwin/codex`：本地构建产物；
- `.yijie/schemas/app-server/generated-json-schema/`：与固定 Runtime 版本匹配的稳定协议 Schema。

Desktop MVP 的首选边界是由 Agent Host 启动 `codex app-server --listen stdio:// --strict-config`，通过 JSONL 发送 `initialize`、`initialized`、thread 和 turn 请求，并消费通知。Agent Host 不应以当前占位的 HTTP URL 配置替代本地 stdio 进程生命周期管理。

Baseline 0 没有决定 cloud runner transport，也没有授权通过公网暴露 app-server。真实集成必须继续遵守 token、审批、MCP 工具和日志脱敏边界。
