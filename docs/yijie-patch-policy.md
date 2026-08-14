# Yijie Patch Policy

canonical `codex-rs/` 必须继续与 Runtime Baseline 0 的固定上游 commit 字节级一致。易界 patch 只能保存在 `.yijie/patches/`，并由 `scripts/apply-yijie-patches.sh` 应用到临时构建工作区；脚本明确拒绝修改 canonical 物化目录。

当前已授权且唯一允许的 overlay 是 `0001-feat-126-filter-persistent-diagnostics.patch`。它解决 FEAT-126 full-case R8 发现的本地 SQLite 路径日志持久化问题，不改变 app-server schema、transport 或外部业务协议。

优先通过上游配置、稳定 app-server API、MCP、Skills、Plugins 或 `yijie-agent-host` 适配解决需求。只有这些边界无法满足经过确认的产品或安全要求时，才可以提议 Runtime patch。

新增 patch 前必须取得用户对修改范围的明确确认，并为每个 patch 记录：

- 上游 issue/限制和不能在 Host 层解决的原因；
- 依赖的固定 commit；
- 应用顺序；
- 行为和协议影响；
- 构建、测试和 Agent Host 兼容性验证；
- 回滚方式；
- 下一次上游升级时的删除条件。

patch 必须能从 `UPSTREAM.md` 固定的零修改源码重复应用。不得直接修改 `codex-rs/` 后再补写 patch 文件。每个构建 manifest 必须记录 patch 相对路径和 SHA-256；Host 必须固定接受的 patch 集与 binary identity。
