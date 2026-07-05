# AGENTS.md

## 仓库职责

`yijie-codex` 是 Codex Runtime 的易界 fork 管理仓库。

## 禁止事项

- 不写跨境电商业务逻辑；
- 不持有平台 token；
- 不写易界业务 prompt；
- 不直接依赖 `yijie-api`、`yijie-connectors`、`yijie-skills` 或 `yijie-knowledge`。

## 开发命令

```bash
./scripts/sync-upstream.sh
./scripts/apply-yijie-patches.sh
./scripts/build-all.sh
./scripts/test-runtime.sh
```

当前脚本为安全占位。
