# Runtime Compatibility

## 既有 Baseline 0 自动门禁

| 检查 | 当前结果 |
|---|---|
| tag 解引用为固定 commit | 通过 |
| `codex-rs/`、`LICENSE`、`NOTICE` 与上游一致 | 通过 |
| canonical source 零漂移、既有 FEAT-126 `0001` 可重放 | 通过 |
| Rust `1.95.0` release build | 通过 |
| macOS Apple Silicon binary 版本为 `0.144.6` | 通过 |
| stable app-server Schema 生成 | 267 个 JSON 文件 |
| Schema canonical 重生成比对 | 通过 |
| 空白 `CODEX_HOME`、无凭据 stdio initialize/initialized | 通过 |
| Runtime manifest 和 SHA-256 | 已生成 |
| sibling `yijie-contracts` Runtime/Host 投影一致性 | checkout 存在时严格校验；缺失时明确跳过 |

以上结果属于此前 Runtime commit `0ce5902ed400866be0196886bb78f693a004d68d` 的单 patch Baseline 0。其 stdio 冒烟只验证 transport、JSONL framing、初始化生命周期、binary 版本和正常 EOF 退出。它故意不读取开发者现有 Codex 登录态，也不调用模型。

## FEAT-136 双 patch candidate

当前 candidate 在相同固定上游 `rust-v0.144.6` / `5d1fbf26c43abc65a203928b2e31561cb039e06d` 上严格应用：

1. `0001-feat-126-filter-persistent-diagnostics.patch`；
2. `0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch`。

`0002` 修复 early sandbox-denial 在 emitter 前返回造成的 Runtime producer 空洞：同一 Command identity 依次产生 canonical started 和 failed completed，terminal 保留 nonzero exit code、duration 和聚合输出，原错误及 retry/approval、sandbox、权限决策保持不变。该变化分类为 `semantic`，未设计新的 wire 类型或字段；Schema shape 不变只是当前预期，仍需最终隔离生成确认。

| FEAT-136 candidate 检查 | 当前结果 |
|---|---|
| focused `codex-core` early-denial lifecycle | 通过 |
| safe fake exec-server lifecycle scenarios | 4/4 通过；测试线程使用任务专用 `RUST_MIN_STACK=16777216` |
| focused `codex-app-server-protocol` v2 mapping | 通过 |
| fmt 与 scoped clippy | 通过；`codex-core` / `codex-app-server-protocol` 使用 `--no-deps -D warnings` |
| `scripts/test-fork-management.sh` | 通过 |
| 精确 `0001` → `0002` allowlist 与独立 replay | 随 fork-management 通过 |
| 隔离 Rust `1.95.0` release build | 通过；`codex-cli 0.144.6` / `aarch64-apple-darwin` |
| stable Schema 生成和逐文件 diff | 通过；267 files / `82ee9de771cf1d41bac16d87380f1121e7794107aa3aa526ad702d5d1bf7afe1` / tracked diff 为空 |
| 完整 `runtime-test`、binary/manifest identity | 通过；每次 fresh build 的精确 binary size/SHA-256 与 manifest SHA-256 只记录在该次 ignored artifact manifest 和下游 artifact lock，不写死在源码文档 |
| Runtime→Contracts 双向兼容 | 通过；精确 compatibility digest 由最终 Contracts candidate 与下游 lock 固化 |
| Runtime→Contracts→Host→Desktop conformance | 待执行 |

Runtime 自身候选门禁和 Runtime→Contracts 双向检查已通过，但不能解释为 Host/Desktop conformance。旧 Contracts commit `3c3000a6fbe2f08ab2131a463a1691e867d661b1` 仍 pin 此前 Runtime provenance；必须由新的 Contracts candidate repin，随后才能执行 Host/Desktop conformance 和 fresh Command D4。Tool D4 保持 `BLOCKED/NOT RUN`，本 candidate 不注册或制造 Tool producer。

## FEAT-137 四 patch candidate

Owner 授权的 `0003-feat-137-stable-sandbox-provenance.patch` 在既有 `0001`、`0002` 之后应用。它为 stable `item/commandExecution/requestApproval` 增加必填 `sandboxPermissions`，枚举严格限定为 `use_default`、`require_escalated`、`with_additional_permissions`，并保持 tool request → core `ExecApprovalRequestEvent` → app-server wire 的原值。该字段不授予权限，不改变审批或执行决策，也不扩张 public v6 API。

Owner 授权的 `0004-feat-137-deterministic-approval-producer.patch` 继续叠加在 `0003` 之后，默认关闭。exact D4 进程 gate 开启时，它以 zero-argument strict tool 和 Runtime-owned fixed arguments 消除 Provider 截断 JSON 对 approval producer 的影响；首 call 后 no-tools。该变化分类为 `semantic`，不新增 stable wire shape。

| FEAT-137 Runtime 检查 | 当前结果 |
|---|---|
| 精确 `0001` → `0002` → `0003` → `0004` allowlist 与独立 replay | 通过 |
| deterministic producer focused | 6/6 通过；包含 gate-off equality、zero-argument required、one-shot 和 truncated arguments isolation |
| core 三枚举 provenance focused test | 1/1 通过 |
| stable projection strip focused test | 1/1 通过 |
| app-server stable wire focused test | 1/1 通过，`use_default` 原样出现 |
| fmt 与 scoped Clippy | 通过；app-server 只放行未被 patch 触及的既有 `unused_mut` |
| Rust `1.95.0` release build | 通过；`codex-cli 0.144.6` / `aarch64-apple-darwin` |
| stable Schema | 267 files / `d82a33f683e554c10dd056a0101c26fd24477928e3f98ee3d9ef250b97395228`；`0004` equality 通过 |
| binary | SHA-256 `896d303658a0978c3628f10e9e78f12139168be9508dd5f2abc658db186a828b` |
| normal-EOF stdio smoke | 通过；无凭据、无 Provider/模型调用 |
| Contracts/Host/Desktop | 等待本 Runtime immutable commit 后依次 source-first repin |
| D4 | `NOT RUN`；真实调用 0 |

## Agent Host Contracts 双向门禁

`make runtime-test` 在生成 Runtime artifact manifest 后调用
`scripts/check_agent_host_contracts.py`。默认读取相邻目录
`../yijie-contracts/compatibility/agent-host-runtime-v1.json` 和当前
`agent-host-runtime-approval-v6-v3.json`，也可通过
`YIJIE_CONTRACTS_REPO=/path/to/yijie-contracts` 指向其它 checkout。

门禁会严格比较以下内容：

- 历史 v1 投影从其固定 Runtime Git object 验证，当前 approval v3 投影精确匹配
  `yijie-codex` `HEAD`；
- Runtime 版本、上游 tag/完整 commit、stdio transport 和 experimental API 状态；
- 已提交协议 Schema 的 JSON 文件数及整个 Schema tree SHA-256；
- active v3 四个 stable Schema artifact digest、必填 `sandboxPermissions` 和精确三值 enum；
- Agent Host 的 HTTP/SSE、认证、sandbox、approval policy 固定投影；
- Contracts v0.7.0 的 7 个 Runtime request method 和 13 个 notification 的完整、有序集合，并确认每一项实际存在于 `ClientRequest.json` 或 `ServerNotification.json`；
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
