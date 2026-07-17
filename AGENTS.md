# AGENTS.md

## 适用范围

本文件适用于 `yijie-codex` 整个仓库。若将来上游源码目录内存在更具体的 `AGENTS.md`，修改该目录时同时遵守其规则，且以更具体的规则为准。

## 仓库职责与当前状态

`yijie-codex` 是 Codex Runtime 的易界 fork 管理仓库，负责固定上游版本、维护最小补丁集、构建 Runtime、执行兼容性验证和记录易界侧变更。

当前仓库只有 fork 管理骨架：

- `UPSTREAM.md` 尚未配置上游地址和固定版本；
- `codex-rs/` 尚未放入可构建的上游源码；
- `.yijie/patches/` 尚无正式补丁；
- 构建和 Runtime 测试脚本在源码缺失时会明确退出，不能把该结果视为验证通过。

Codex 不得擅自 clone 上游、添加或改写远端、选择版本、同步源码或创建核心补丁。执行这些动作前必须取得用户对上游地址、目标 tag/commit 和变更范围的明确确认。

## 仓库边界

- 不写跨境电商业务逻辑、易界业务 prompt 或平台连接器逻辑；
- 不持有平台 token、商家数据、PII、cookie 或生产凭据；
- 不直接依赖 `yijie-api`、`yijie-connectors`、`yijie-skills` 或 `yijie-knowledge`；
- 易界业务通过稳定协议和 `yijie-agent-host` 接入，不把业务耦合写入 Runtime 内核；
- 不为规避上游接口而复制、替换或重写大块上游实现。

## 目录约定

- `codex-rs/`：配置上游后承载上游 Runtime 工作树，尽量保留上游结构和工具链；
- `.yijie/patches/`：按顺序保存必要且可审计的易界补丁；
- `.yijie/config/`：保存不含秘密的 Runtime 配置样例；
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
make test          # 验证 fork 管理骨架和脚本约束
make sync          # 仅在上游已确认并正确配置后执行
make apply-patches # 仅在补丁集已确认后执行
make build         # 需要 codex-rs/Cargo.toml
make runtime-test  # 需要可构建的 Runtime 源码
```

`make test` 通过只代表 fork 管理骨架有效，不代表 Codex Runtime 已构建或兼容。`make build` 或 `make runtime-test` 因源码缺失而退出时，必须如实报告为“未执行 Runtime 验证”。

## 完成标准

- 变更符合仓库边界，且没有引入业务逻辑或秘密；
- `make lint` 和 `make test` 通过；
- 涉及上游源码时，`make build` 和 `make runtime-test` 也通过；
- 新增或调整补丁已验证可从固定版本重复应用和回滚；
- 上游版本、补丁顺序、兼容性结果和易界侧变更记录保持同步；
- 未完成的 Runtime 验证、风险和人工步骤在交付说明中明确列出。
