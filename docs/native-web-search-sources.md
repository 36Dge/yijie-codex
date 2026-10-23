# 原生搜索来源候选（2026-10-23）

用户要求修复 Kimi 对话的真实过程与来源展示，继续复用原生链路。上游仍固定
`rust-v0.144.6` / `5d1fbf26c43abc65a203928b2e31561cb039e06d`，不编辑上游子树。

`0006-native-web-search-sources.patch` 在现有五补丁之后独立重放：仅对启用内置网页搜索的
`kimi-k3` Responses 请求加入 `web_search_call.action.sources`；在已有 WebSearchAction
中保留可选 URL/title 元数据，经原生 core → app-server 投影。来源不是 assistant 引用，
不生成或改写正文、进度、推理、执行事件、权限与工具调用。

构建复用 `bash scripts/build-chat-model-stream-args.sh --web-search-sources`，写入独立
`.yijie/build/chat-models-web-sources/aarch64-apple-darwin/`；拒绝覆盖已存在产物。
旧 `chat-models-stream-args` 产物保留。manifest 复用原有生成与哈希检查，canonical schema
比较只允许增加可选 sources 与对应来源类型，其余字段必须与固定 input-only schema 相等。

Runtime 字段属于可选增量；整个闭合消费者扩展按 `contract-impact=breaking` 处理。
顺序为 Runtime canonical schema → Contracts 精确候选 → Host → Desktop。Host history v4、
SSE v11、Desktop IPC v4/storage format 4 保持旧版本读取与降级投影，不升级写入旧记录。
这是未发布本地候选，不代表生产兼容或独立人工批准。回滚保留旧二进制；新格式记录必须由
兼容 reader 读取，不能降级写入或删除数据。

验证仅使用普通解析、投影、兼容样例、标准编译及 normal-EOF 握手；不运行攻击 fixture、
强杀、故障注入或权限破坏测试。真实验证结果与来源字段计数见元仓本轮报告。
