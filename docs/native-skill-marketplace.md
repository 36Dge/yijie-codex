# FEAT-174 原生本地技能市场候选

2026-11-13 用户授权按修订2实施。保持 `rust-v0.144.6` / `5d1fbf26c43abc65a203928b2e31561cb039e06d`，在原0001—0024链后追加 `0025-native-skill-marketplace.patch`。canonical `codex-rs/` 源文件未改；不是发布或上游升级。

- N1：可选 `plugin_marketplace_mode=local_only`、`plugin_refresh_mode=explicit`、`plugin_allowed_local_roots`。默认沿用上游；Host启用时只接受两个本地根，抑制远程目录物化和后台内容刷新。
- N2：`plugin/state/read` 从原生PluginStore、配置层和Skill解析器返回独立缓存/配置/有效状态，涵盖缓存孤项、配置孤项、停用和无目录条目。查询不修复、不安装；有界库存512项。
- N3：`plugin/refresh` 桥接现有 IfVersionChanged / ForceReinstall 和缓存失效、变更通知，不重写安装器或版本算法；不改变插件enabled。
- 插件写入与原生线程状态、子任务状态及后台终端协调。复用ThreadWatchManager；空白尚未首轮执行的根会话不误判为资源占用，实际活动工作继续阻止替换。

构建入口：`scripts/build-native-skill-marketplace.sh`；重放/检查：`scripts/prepare-native-skill-marketplace.py [--check]`。独立产物保留旧候选，拒绝覆盖同一来源产物。

| 证据 | 当前值 |
|---|---|
| 来源摘要 | `8d1ac11567b3a7c47296c89ecad1272d6f886c2904a5c23f546874b3a0ba508c` |
| binary SHA-256 | `e03bdbd2b4167022ee85c2df86dacff1a0a5c082321a9aa19875b29136a96cf5` |
| manifest SHA-256 | `eed98a79cd1fb1687faf295df32d2087504f28704d3cb9775afe902d7e6399aa` |
| canonical JSON schema tree | `97489c7264dfd3b827210c6a4132716a1983b2ad89e383a7a80316ec0d8c258c` |
| schema文件数 | 275 |
| 补丁数 | 25 |

已验证：补丁链独立重放、release构建、3个 `managed_plugin_` 原生定向用例；Host使用精确产物验证安装/导入/取消/迁移/版本回滚/规则/正常重开/活动任务门闩。普通本机HTTP回放验证原生显式Skill加载和冷恢复，不代表真实供应商自主选择质量。没有强杀、权限故障、程序替身或攻击归档。完整产品分层证据见元仓 FEAT-174 的验收记录。

自审实际修复：marketplacePath按原生清单文件传递；Host冷启动保留受管原生plugins/marketplaces配置；忙碌判定区分空会话与活动子任务。模型推理、匹配、按需读取、去重、预算及MCP执行仍由原生系统负责。
