# Yijie Patch Policy

Runtime Baseline 0 的 patch 集必须为空。`scripts/apply-yijie-patches.sh` 会在发现任何 `.yijie/patches/*.patch` 时失败。

优先通过上游配置、稳定 app-server API、MCP、Skills、Plugins 或 `yijie-agent-host` 适配解决需求。只有这些边界无法满足经过确认的产品或安全要求时，才可以提议 Runtime patch。

新增 patch 前必须取得用户对修改范围的明确确认，并为每个 patch 记录：

- 上游 issue/限制和不能在 Host 层解决的原因；
- 依赖的固定 commit；
- 应用顺序；
- 行为和协议影响；
- 构建、测试和 Agent Host 兼容性验证；
- 回滚方式；
- 下一次上游升级时的删除条件。

patch 必须能从 `UPSTREAM.md` 固定的零修改源码重复应用。不得直接修改 `codex-rs/` 后再补写 patch 文件。
