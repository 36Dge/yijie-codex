# Runtime Baseline 0

## 定义

Runtime Baseline 0 是易界首次可消费的 Codex Runtime 技术基线。它固定一个不可变上游 commit，在不引入任何易界 Runtime patch 的前提下，证明该源码能够构建目标 binary、导出版本匹配的 app-server Schema，并通过不依赖真实凭据的本地 stdio 协议握手。

Baseline 0 解决的是“我们究竟基于哪一份 Runtime、能否重复得到同一协议面、Agent Host 可以从哪里开始适配”。它不负责跨境电商业务逻辑，也不宣称真实任务链路已完成。

## 固定决策

- upstream：`https://github.com/openai/codex.git`；
- tag：`rust-v0.144.6`；
- commit：`5d1fbf26c43abc65a203928b2e31561cb039e06d`；
- source：上游 `codex-rs/` 子树加根目录 `LICENSE`、`NOTICE`；
- patch：空；
- Rust：`1.95.0`；
- primary target：`aarch64-apple-darwin`；
- app-server：稳定 API，`experimentalApi=false`，JSONL-over-stdio。

## 完成标准

1. `UPSTREAM.md` 和 `.yijie/upstream.env` 记录一致的上游 URL、tag、完整 commit、Runtime 版本和工具链。
2. `make sync` 从固定 commit 重建源码，验证 tag 解引用结果，内容相同时幂等，目标存在改动时不覆盖。
3. `verify-upstream-source.sh` 证明 `codex-rs/`、`LICENSE` 和 `NOTICE` 与上游一致。
4. `.yijie/patches/` 不包含 `*.patch`，`make apply-patches` 明确验证零 patch。
5. `make build` 使用固定 Rust 工具链和目标平台，以临时构建工作树产出 `codex-cli 0.144.6` release binary。
6. 上游 release lock 的正规化只能改变本地 workspace package 版本，且正规化前后 SHA-256 被记录。
7. `make generate` 使用构建产物导出 stable app-server JSON Schema，并进行 canonical JSON serialization。
8. `make runtime-test` 独立重生成 Schema 并逐文件比较，随后使用空白临时 `CODEX_HOME` 完成 `initialize` / `initialized` stdio 握手。
9. `runtime-manifest.json` 记录 upstream、空 patch 集、target、Runtime 版本、binary SHA-256、Schema tree SHA-256 和 build lock 哈希。
10. CI 分开执行管理骨架门禁和 Runtime baseline 门禁。

## 非完成项

- 不执行真实模型 turn，不需要 OpenAI API key 或 Codex access token；
- 不验证 MCP 工具、审批、事件映射和业务任务；
- 不完成 `yijie-agent-host` transport；
- 不打包、签名或 notarize Desktop sidecar；
- 不确定 cloud runner transport、认证和部署模型；
- 不创建任何 Runtime 核心 patch。

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
