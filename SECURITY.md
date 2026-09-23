# Security Policy

Codex Runtime 不得直接接触平台 token、真实商家数据或 PII。所有平台 API 调用必须通过 `yijie-connectors` 的工具边界完成。

FEAT-155新增独立的通用input-only本地候选，关闭额外指令发现、工具注册/执行、扩展初始化和非文本输出处理，保留内部历史与文本Provider；不改变普通权限模式。原生策略查询、来源构建与回滚见[设计说明](docs/input-only-execution.md)。Host仍需检查精确产物和当前有效策略，不能只信调用方的开关或prompt。
