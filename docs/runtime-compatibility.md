# Runtime Compatibility

## Baseline 0 自动门禁

| 检查 | 当前结果 |
|---|---|
| tag 解引用为固定 commit | 通过 |
| `codex-rs/`、`LICENSE`、`NOTICE` 与上游一致 | 通过 |
| 易界 patch 集为空 | 通过 |
| Rust `1.95.0` release build | 通过 |
| macOS Apple Silicon binary 版本为 `0.144.6` | 通过 |
| stable app-server Schema 生成 | 267 个 JSON 文件 |
| Schema canonical 重生成比对 | 通过 |
| 空白 `CODEX_HOME`、无凭据 stdio initialize/initialized | 通过 |
| Runtime manifest 和 SHA-256 | 已生成 |

Baseline 0 的 stdio 冒烟只验证 transport、JSONL framing、初始化生命周期、binary 版本和正常 EOF 退出。它故意不读取开发者现有 Codex 登录态，也不调用模型。

## 后续兼容性层级

1. `yijie-contracts` 定义稳定 Agent Host 服务和任务事件；
2. `yijie-agent-host` 基于本目录 Schema 实现 stdio transport、版本协商和未知事件策略；
3. 使用测试凭据执行 thread/start、turn/start、流式事件和 interrupt；
4. 验证 MCP 工具 proposal、审批、执行和审计链；
5. 验证 Desktop sidecar 生命周期、签名、升级和故障恢复；
6. cloud runner transport 确认后建立独立矩阵。

每次上游升级都必须重新生成 Schema，并将兼容性差异映射到 Agent Host。Schema 无 diff 也不能替代真实下游集成测试。
