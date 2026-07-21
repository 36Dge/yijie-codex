# App-server Schema Baseline

本目录由固定 Runtime binary 生成并提交，用于 `yijie-agent-host` 的版本化协议适配。

- `baseline.json` 记录生成版本、commit、transport 和 experimental API 选择；
- `generated-json-schema/` 是未启用 `--experimental` 的 app-server JSON Schema；
- 所有 JSON 在提交前按键排序和统一缩进，消除上游生成器的对象遍历顺序差异；
- 禁止手工修改生成文件；使用 `make generate` 更新，再用 `make runtime-test` 验证。
