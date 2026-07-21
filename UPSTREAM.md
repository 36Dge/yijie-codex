# Upstream

## 固定版本

| 字段 | 值 |
|---|---|
| upstream remote | `https://github.com/openai/codex.git` |
| fork remote | `https://github.com/36Dge/yijie-codex.git` |
| pinned tag | `rust-v0.144.6` |
| pinned commit | `5d1fbf26c43abc65a203928b2e31561cb039e06d` |
| Runtime version | `0.144.6` |
| Rust toolchain | `1.95.0` |
| primary release target | `aarch64-apple-darwin` |
| synchronized at | `2026-07-21` |

机器可读值位于 `.yijie/upstream.env`。tag 必须解析到上表完整 commit，否则同步失败。

## 源码策略

- 将固定 commit 的 `codex-rs/` 子树物化到本仓库 `codex-rs/`；
- 同时保留上游根目录 `LICENSE` 和 `NOTICE`；
- 不导入 Codex 的 IDE extension、cloud 或其它非 Runtime 源码；
- 同步时通过临时目录生成候选源码，内容一致时保持幂等，内容不一致且目标存在本地改动时拒绝覆盖；
- `scripts/verify-upstream-source.sh` 使用上游 Git object 对 `codex-rs/`、`LICENSE` 和 `NOTICE` 做字节级比较，忽略本地 `target/` 构建缓存。

## Patch 顺序

Runtime Baseline 0 的易界 patch 集为空。`.yijie/patches/` 中出现任何 `*.patch` 都会使 Baseline 0 验证失败。

## Release lock 正规化

此 release tag 的 `workspace.package.version` 是 `0.144.6`，但上游 `Cargo.lock` 中 132 个本地 workspace package 仍记录为 `0.0.0`。直接执行 `cargo build --locked` 会失败。

构建脚本不会修改上游 lockfile，而是在临时、从固定 commit 重新物化的构建工作树中执行目标平台解析。`verify-release-lock-drift.py` 要求解析结果与上游 lock 的唯一差异是本地 workspace package 的 `0.0.0 -> 0.144.6`；其它任何依赖或 checksum 漂移都会使构建失败。两个 lock 的 SHA-256 会进入构建报告和 Runtime manifest。

## 兼容性结论

在 `2026-07-21` 对 macOS Apple Silicon 完成：

- 固定源码和零 patch 比对：通过；
- `codex-cli 0.144.6` release 构建：通过；
- stable app-server JSON Schema 生成：267 个文件；
- Schema 独立重生成一致性：通过；
- 无凭据 JSONL-over-stdio `initialize` / `initialized` 握手：通过；
- manifest、binary SHA-256、Schema tree SHA-256 和 lock 正规化记录：已生成。

未包含真实模型 turn、MCP 工具调用、审批链、Agent Host 事件映射、Desktop sidecar 签名或 cloud runner 验证。
