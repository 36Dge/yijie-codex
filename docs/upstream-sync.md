# Upstream Sync

当前固定版本见 `UPSTREAM.md` 和 `.yijie/upstream.env`。

## 同步流程

1. 确认工作区和 `codex-rs/` 没有需要保留的未提交改动；
2. 取得用户对新 upstream URL、tag、完整 commit、升级窗口和 patch 策略的明确确认；
3. 更新 `.yijie/upstream.env` 和 `UPSTREAM.md`；
4. 执行 `make sync`；
5. 执行 `make apply-patches`，Baseline 0 必须报告空 patch；
6. 执行 `make build && make generate && make runtime-test`；
7. 审查 Schema diff、binary/Schema/lock hash 和兼容性结果；
8. 更新 `CHANGELOG.yijie.md`、兼容性文档和下游通知。

`make sync` 会添加缺失的 `upstream` remote，但拒绝接受 URL 不一致的已有 fetch remote，并把 upstream push URL 固定为 `DISABLED`。tag 必须解引用到固定 commit。源码先在临时目录生成；只有目标内容不同且目标无本地改动时才替换。

## 禁止事项

- 不从 `main`、浮动 branch 或 latest URL 构建发布产物；
- 不把 Cargo 自动修改的 lockfile 静默写回固定源码；
- 不为消除上游 warning 创建易界 patch；
- 不在同步时覆盖用户或前序任务改动；
- 不在未完成 Agent Host 兼容性评估时宣称升级完成。
