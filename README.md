# yijie-codex

Codex Runtime 的易界 fork 管理仓库。当前只初始化 fork 管理骨架，不 clone 上游源码。

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

上游仓库 URL 尚未配置，`codex-rs/` 为空占位。
