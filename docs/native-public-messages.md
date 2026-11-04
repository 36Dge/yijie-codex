# 模型显式公开消息声明：原生适配候选

2026-11-05，Owner 明确批准机制复审报告第 5 节的限定候选。此前批准仅覆盖写作
预告完成保护，本次批准另外覆盖显式阶段声明、原生流式投影与同 turn 续行。
`contract-impact = semantic`：AgentMessage 的有效阶段可来自经校验的模型声明，
不等同 Provider 原始 phase 已存在。预期不改变 app-server 字段形状；仍需实际
生成 schema、Contracts 固定来源及各 consumer 验证后才能启用。

## 原生复用与缺口

既有 Runtime 已支持同响应多个 Item、工具 needs_follow_up、end_turn=false、
pending input、Stop hook、消息/历史投影和预算/取消。候选不重复这些机制。
当前真实 Kimi/MiniMax 样本未给独立消息/phase/继续条件；Native fixture 通过
不能补出模型未生成的信号。Stop hook 仍由现有策略关闭，未启用外部脚本；
TurnItemContributor 不能单独完成流式首字的阶段投影，因此候选使用现有事件
分发前的有界投影，再回到同一个 native dispatch / run_turn。

## 作用域与输入

必须同时满足：普通非 input_only turn、无 final_output_json_schema、原生
Default collaboration mode、模型精确为 kimi-k3.1-pro 或 MiniMax-M3、当前
developer 含 `[yijie-public-message-v1]`。其他配置保持原行为。

每个实际 Provider assistant Message 的首行可以为以下之一，随后换行与正文：

```text
[[yijie.public-message.v1:commentary]]
[[yijie.public-message.v1:final_answer]]
```

每个真实 Item 只投影一个公开 Item，保留实际 ID 和顺序；不拆段落、不改写
推理、不从工具日志生成进展。纯文本里的后续同样字样保持字面内容。简单任务
允许直接 final_answer；不强迫每轮三条消息或等满指定步骤。

## 三个有意不同的事实

1. Provider 原始 ResponseItem：原文本、声明和原始 phase（包括缺失）保留。
   `OutputItemDone` 在适配器中不变，record_conversation_items 仍记录它。
2. 模型输入历史：下一次请求回传上述真实消息，模型能识别自己已给过的阶段。
   不把展示阶段回填为 Provider phase，不注入虚构用户消息。
3. 公开 AgentMessage：同 ID 的临时显示投影消费声明，生成可读正文和有效阶段。
   该阶段是模型声明的适配语义。实际 Provider phase 存在时优先保留；不存在且
   没有有效声明时仍 unknown。legacy public events 及 thread/read 用于展示重开。

流式声明首行有界，完成前最多保留 128 bytes 的候选首行；有效声明判定后才
发 started，并立即沿既有 assistant text parser 发送可见 delta。正文不等待
response/turn 完成。未知声明在精确内部命名空间中只移除控制行、保留正文为
unknown；空正文没有正常继续权，进入现有有界补答，不伪报有结果。
超长、无法识别为该首行的普通文本保守透传，不能以此声明阶段或请求正常续行。

## 续行、终态与保护

每次 sampling 的最后一条完成公开消息，只有在其原始 phase 缺失、有效声明为
commentary、正文非空，且 response.end_turn 缺失时，才能为已有 needs_follow_up
补充一个显式继续条件。end_turn=false 和真实工具继续原生处理；明确 end_turn
存在时不由候选覆盖。原生补答 finalizing 已开启时，候选不再请求正常继续，
避免把两次 answer-only 上限变成播报调度。队列处理前同样检查原生取消 token。

没有新 HTTP 请求器、Host 轮询/任务、工具、计时器、预算计数器或 Goal。新取样
会消耗现有模型额度与原生预算，不承诺零额外请求。保留原权限与审批路径。

同时最小补齐已观察到的未标阶段“我按……来写”：要求第一分句以“我按”开头且
以“来写”结尾，沿既有保守 process_only 与两次无工具补答；已有结果、原样
引用及只给计划的例外保持。这条兜底不计作正常进度生成成功。

## 构建与验证

`0016-native-public-messages.patch` 在 0015 后重放到专用临时构建目录，上游
codex-rs 子树不改。`bash scripts/build-native-public-messages.sh` 复用 canonical
源码重放、lock 验证、10 项完成保护测试、5 项声明投影测试、scoped Clippy、
release 构建、schema 生成/对照和来源重验。新目录为
`.yijie/build/native-public-messages-v1/aarch64-apple-darwin`；旧制品不覆盖。

原生测试需分别证明：跨文本分块、首个 delta 及时可见、started/完成态一致、
同响应多消息、声明驱动正常续行、工具续行、直接 final、缺阶段保留、补答
上限、模型原始历史、正常退出重开、取消与 input-only 隔离。客户端再验证
Native 保存/IPC/阅读投影，最终用真实模型检验内容质量，不能以 fixture 代替。

当前记录为候选实施中；实际 build/schema/集成结果另行写入完成证据。回退只
停用新轮声明与对应产品策略；新旧已保存公开消息继续可读，不清库、不迁移，
不在旧会话历史中补造声明或改 phase。

本地 canonical 构建已通过：10 项完成保护、5 项声明投影、scoped Clippy、
release 与源码重验；二进制 SHA 为
`c5917922f0d7b58b68eb6120c67bb8f3a53781c24655e175d58911692c91e8ac`。
269 个 schema 的树摘要仍为
`d8c3265d8923ef4437203c0a2ded954549b4abc0c5079ecd6bcdf7c6da72f11e`；
无凭据 stdio 握手与正常 EOF 退出、上游子树逐字比对通过。

已修复复用的 16 个 canonical 脚本缺少执行位的问题，各脚本内容哈希保持不变。
`make lint` 通过；完整 `make test` 因既有 FEAT-137 静态 checker 要求 0004 patch
包含 `app-server/src/lib.rs` 而未通过。该 checker 与 0004 patch 本轮均未改，
该根补丁检查不包含新增 0016；不放宽检查或修改已退役 D4 producer 来造绿。
普通契约/manifest/无强杀驱动检查已在此前步骤正常执行；候选原生集成和消费者
验收继续独立取证，完整仓库管理门禁不记为 PASS。
