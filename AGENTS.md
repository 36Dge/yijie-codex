# AGENTS.md

## 适用范围

本文件适用于 `yijie-codex` 整个仓库。若将来上游源码目录内存在更具体的 `AGENTS.md`，修改该目录时同时遵守其规则，且以更具体的规则为准。

## 仓库职责与当前状态

`yijie-codex` 是 Codex Runtime 的易界 fork 管理仓库，负责固定上游版本、维护最小补丁集、构建 Runtime、执行兼容性验证和记录易界侧变更。

当前已完成 Runtime Baseline 0：

- 上游固定为 `https://github.com/openai/codex.git`；
- tag 固定为 `rust-v0.144.6`，完整 commit 为 `5d1fbf26c43abc65a203928b2e31561cb039e06d`；
- `codex-rs/` 是该 commit 的上游子树，`LICENSE` 和 `NOTICE` 同步保留；
- `.yijie/patches/` 为空，脚本会验证零 patch；
- macOS Apple Silicon release build、267 个 stable app-server JSON Schema、Schema 重生成比较和无凭据 stdio 初始化握手已通过；
- 构建产物和 Runtime manifest 位于被忽略的 `.yijie/build/`，Schema 位于 `.yijie/schemas/app-server/`。

Baseline 0 不表示 Agent Host、真实模型 turn、MCP 工具、Desktop sidecar、签名或 cloud runner 已完成。Codex 不得擅自改变上游、固定版本、源码策略、transport、patch 集或发布目标；升级和核心修改仍必须取得用户明确确认。

## 仓库边界

- 不写跨境电商业务逻辑、易界业务 prompt 或平台连接器逻辑；
- 不持有平台 token、商家数据、PII、cookie 或生产凭据；
- 不直接依赖 `yijie-api`、`yijie-connectors`、`yijie-skills` 或 `yijie-knowledge`；
- 易界业务通过稳定协议和 `yijie-agent-host` 接入，不把业务耦合写入 Runtime 内核；
- 不为规避上游接口而复制、替换或重写大块上游实现。

## 目录约定

- `codex-rs/`：固定 commit 的原样上游 Runtime 子树，不直接修改；
- `.yijie/patches/`：按顺序保存必要且可审计的易界补丁；
- `.yijie/config/`：保存不含秘密的 Runtime 配置样例；
- `.yijie/schemas/app-server/`：固定 Runtime 生成、canonicalized 且提交的 stable app-server Schema；
- `.yijie/build/`：不提交的 binary、解析 lock、lock 报告和 Runtime manifest；
- `scripts/`：上游同步、补丁应用、构建和测试入口；
- `UPSTREAM.md`：上游地址、固定版本、同步时间和兼容性结论；
- `CHANGELOG.yijie.md`：易界侧行为变化及升级影响；
- `docs/`：同步策略、补丁策略、兼容性、安全和集成边界。

## Fork 开发原则

- 上游优先：能够通过配置、公开扩展点或宿主层完成的需求，不修改 Runtime 内核；
- 最小补丁：每个补丁只解决一个明确问题，并说明原因、影响、依赖顺序、验证方式和回滚方式；
- 可重放：补丁必须能从 `UPSTREAM.md` 记录的固定版本按确定顺序重新应用；
- 可升级：同步上游时先评估冲突和行为差异，再更新固定版本及兼容性记录；
- 可追溯：修改上游源码或补丁集时同步更新 `UPSTREAM.md`、`CHANGELOG.yijie.md` 和相关文档；
- 尊重上游生成物、格式化规则和 lockfile 策略，不手改可由上游工具生成的文件。

## 必须先确认的决策

遇到以下事项时停止实现并向用户确认，不根据猜测作决定：

- 上游仓库地址、fork 远端、固定 tag/commit 或升级窗口；
- 是否修改 Runtime 核心、协议、沙箱、权限、认证、更新或遥测行为；
- 是否新增补丁、依赖、feature flag、构建目标或发布产物；
- 补丁与上游冲突时采用重写、暂缓还是放弃；
- 任何可能改变 Desktop、Agent Host 或云端 Runtime 兼容性的行为。

## 开发与验证命令

```bash
make lint          # 检查仓库脚本语法
make test          # 验证固定元数据、源码材料、零 patch 和脚本约束
make sync          # 获取固定 tag，并幂等物化 codex-rs/LICENSE/NOTICE
make apply-patches # Baseline 0 验证源码一致且 patch 集为空
make build         # 用固定 Rust 工具链为 host 或指定 target 构建 release binary
make generate      # 从构建 binary 生成并 canonicalize stable app-server Schema
make runtime-test  # Schema 重生成比较、无凭据 stdio 握手和 manifest
make runtime-baseline # 串联 sync、build、generate 和 runtime-test
```

`make test` 通过只代表 fork 管理和固定材料有效。只有 `make build`、`make generate` 和 `make runtime-test` 都通过，才能声称 Baseline 0 的目标平台验证完成。

上游 release tag 的 `Cargo.lock` 对本地 workspace package 仍使用 `0.0.0`。构建只能在临时工作树内正规化这些本地 package 到 `0.144.6`，并通过 `verify-release-lock-drift.py` 证明没有其它 lock 漂移；禁止把解析后的 lock 写回 `codex-rs/`。

`codex-rs/target/` 是本地缓存，不属于上游一致性比较。不得手工编辑 `.yijie/schemas/app-server/generated-json-schema/`，必须通过固定 binary 重新生成。

## 完成标准

- 变更符合仓库边界，且没有引入业务逻辑或秘密；
- `make lint` 和 `make test` 通过；
- 涉及上游源码时，`make build` 和 `make runtime-test` 也通过；
- 新增或调整补丁已验证可从固定版本重复应用和回滚；
- 上游版本、补丁顺序、兼容性结果和易界侧变更记录保持同步；
- 未完成的 Runtime 验证、风险和人工步骤在交付说明中明确列出。
