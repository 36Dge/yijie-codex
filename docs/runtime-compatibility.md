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
| sibling `yijie-contracts` Runtime/Host 投影一致性 | checkout 存在时严格校验；缺失时明确跳过 |

Baseline 0 的 stdio 冒烟只验证 transport、JSONL framing、初始化生命周期、binary 版本和正常 EOF 退出。它故意不读取开发者现有 Codex 登录态，也不调用模型。

## Agent Host Contracts 双向门禁

`make runtime-test` 在生成 Runtime artifact manifest 后调用
`scripts/check_agent_host_contracts.py`。默认读取相邻目录
`../yijie-contracts/compatibility/agent-host-runtime-v1.json`，也可通过
`YIJIE_CONTRACTS_REPO=/path/to/yijie-contracts` 指向其它 checkout。

门禁会严格比较以下内容：

- 易界 Runtime 仓库 URL 和当前 `yijie-codex` `HEAD`；
- Runtime 版本、上游 tag/完整 commit、stdio transport 和 experimental API 状态；
- 已提交协议 Schema 的 JSON 文件数及整个 Schema tree SHA-256；
- Agent Host 的 HTTP/SSE、认证、sandbox、approval policy 固定投影；
- 4 个 Runtime request method 和 8 个 notification 的完整、有序集合，并确认每一项实际存在于 `ClientRequest.json` 或 `ServerNotification.json`；
- 刚生成的 Runtime artifact manifest 与上述源数据仍然一致。

Runtime manifest 写入器与该门禁共用 `scripts/runtime_manifest.py` 中的文件和
Schema tree 哈希实现，避免两套算法独立漂移。若 sibling checkout 整体不存在，命令输出
`SKIP` 并成功退出，使 `yijie-codex` 可独立检出和验证；如果 checkout 已存在但清单缺失、
结构非法或任一值不一致，则视为真实兼容性错误并失败。

## 后续兼容性层级

1. `yijie-contracts` 定义稳定 Agent Host 服务、任务事件和 Runtime 投影清单；
2. `yijie-agent-host` 基于本目录 Schema 实现 stdio transport、版本协商和未知事件策略；
3. 使用测试凭据执行 thread/start、turn/start、流式事件和 interrupt；
4. 验证 MCP 工具 proposal、审批、执行和审计链；
5. 验证 Desktop sidecar 生命周期、签名、升级和故障恢复；
6. cloud runner transport 确认后建立独立矩阵。

每次上游升级都必须重新生成 Schema，并将兼容性差异映射到 Agent Host。Schema 无 diff 也不能替代真实下游集成测试。
