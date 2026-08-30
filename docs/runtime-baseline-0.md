# Runtime Baseline 0

## 定义

Runtime Baseline 0 是易界首次可消费的 Codex Runtime 技术基线。它固定一个不可变上游 commit，并保持 canonical source 零漂移。经授权的易界 patch 只在临时工作区可重放应用，构建仍需导出版本匹配的 app-server Schema，并通过不依赖真实凭据的本地 stdio 协议握手。

Baseline 0 解决的是“我们究竟基于哪一份 Runtime、能否重复得到同一协议面、Agent Host 可以从哪里开始适配”。它不负责跨境电商业务逻辑，也不宣称真实任务链路已完成。

此前受支持的易界 Runtime commit 为 `0ce5902ed400866be0196886bb78f693a004d68d`，只包含 FEAT-126 `0001`。当前 FEAT-136 工作是在相同上游源码上增加 Owner 单独授权的 `0002` candidate；在最终隔离 build/generate/runtime-test、Contracts repin 和下游 conformance 完成前，它不是新的受支持 Baseline。

## 固定决策

- upstream：`https://github.com/openai/codex.git`；
- tag：`rust-v0.144.6`；
- commit：`5d1fbf26c43abc65a203928b2e31561cb039e06d`；
- source：上游 `codex-rs/` 子树加根目录 `LICENSE`、`NOTICE`；
- patch 顺序：`0001-feat-126-filter-persistent-diagnostics.patch` → `0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch`；
- Rust：`1.95.0`；
- primary target：`aarch64-apple-darwin`；
- app-server：稳定 API，`experimentalApi=false`，JSONL-over-stdio。

## 完成标准

1. `UPSTREAM.md` 和 `.yijie/upstream.env` 记录一致的上游 URL、tag、完整 commit、Runtime 版本和工具链。
2. `make sync` 从固定 commit 重建源码，验证 tag 解引用结果，内容相同时幂等，目标存在改动时不覆盖。
3. `verify-upstream-source.sh` 证明 `codex-rs/`、`LICENSE` 和 `NOTICE` 与上游一致。
4. `make apply-patches` 从固定上游按精确名称与顺序重放 reviewed `0001` → `0002` patch set，拒绝缺失、额外、乱序 patch 及对 canonical `codex-rs/` 的修改。
5. `make build` 使用固定 Rust 工具链和目标平台，以临时构建工作树产出 `codex-cli 0.144.6` release binary。
6. 上游 release lock 的正规化只能改变本地 workspace package 版本，且正规化前后 SHA-256 被记录。
7. `make generate` 使用构建产物导出 stable app-server JSON Schema，并进行 canonical JSON serialization。
8. `make runtime-test` 独立重生成 Schema 并逐文件比较，随后使用空白临时 `CODEX_HOME` 完成 `initialize` / `initialized` stdio 握手。
9. `runtime-manifest.json` 按顺序记录全部 patch 路径和 SHA-256，以及 upstream、target、Runtime 版本、binary SHA-256、Schema tree SHA-256 和 build lock 哈希。
10. CI 分开执行管理骨架门禁和 Runtime baseline 门禁。

## FEAT-136 candidate 状态

`0002` 修复 early sandbox-denial 在既有 emitter 创建前返回所造成的 Command lifecycle 缺失。它对同一 identity 发布 canonical `item/started` 和 failed `item/completed` 后仍返回原错误，不改变 retry/approval、sandbox 或权限决策。该变化的 `contract-impact = semantic`；stable Schema shape 预计不变，但最终隔离 build、Schema 生成和逐文件比较仍待完成。

当前只确认以下门禁通过：

- focused `codex-core` early sandbox-denial lifecycle；
- 4 个 safe fake exec-server 场景；
- focused `codex-app-server-protocol` v2 Command notification mapping；
- `cargo fmt --all -- --check` 和 `codex-core` / `codex-app-server-protocol` scoped `clippy --no-deps -D warnings`；
- `scripts/test-fork-management.sh` 的 patch replay、精确 allowlist、Contracts v0.7.0 投影和安全 smoke wrapper 测试。

不得据此宣称完整 `make build`、`make generate`、`make runtime-test`、artifact identity 或 Runtime→Contracts→Host→Desktop conformance 已通过。旧 Contracts `3c3000a6fbe2f08ab2131a463a1691e867d661b1` 必须由新的 candidate 精确 repin repaired Runtime immutable commit 与确认后的 Schema digest。

## 非完成项

- 不执行真实模型 turn，不需要 OpenAI API key 或 Codex access token；
- 不验证 MCP 工具、审批和业务任务；Tool D4 保持 `BLOCKED/NOT RUN`，不得制造 Tool producer；
- 不完成 `yijie-agent-host` transport；
- 不打包、签名或 notarize Desktop sidecar；
- 不确定 cloud runner transport、认证和部署模型；
- `0002` 仅补齐 Command producer 的可观察失败 lifecycle，不改变 app-server 认证、sandbox 权限或模型错误处理决策。

## 产物

```text
.yijie/build/<platform>/<target>/
  codex
  resolved-Cargo.lock
  lock-normalization.json
  runtime-manifest.json

.yijie/schemas/app-server/
  baseline.json
  generated-json-schema/
```

构建目录不提交 Git；Schema 和 baseline metadata 提交并由 CI 检查漂移。
