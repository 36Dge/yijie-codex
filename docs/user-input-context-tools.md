# request_user_input 与上下文工具适配

用户授权仅本两组；已确认“保留原自动压缩，仅显式 new_context 开新窗口”。最高 contract-impact=breaking，使用独立 local candidate 和配对消费者；上游 rust-v0.144.6 / 5d1fbf26c43abc65a203928b2e31561cb039e06d 不变。

0022 复用原生 Protocol 问题/回答、Session oneshot、RequestUserInputHandler、context_window_token_status、compact 与 compact_token_budget。只修正工具声明/归一化中的 options/isSecret 缺口，增加已公开文案对应的有界问题校验、诊断预览脱敏和根代理声明约束。没有 Host 自研 Agent 执行、摘要或 token 算法。

TokenBudgetConfig.reset_on_compact 默认 true，与旧配置一致；Host 本地 profile 显式设 false，自动阈值与普通手动压缩保留摘要；显式 new_context 调用原生无摘要窗口重建。任务取消和直接新任务入口均清除原生待切换标记，不能把未完成的切换转交下一轮。

isSecret 是显示遮罩；答案仍进入模型输入及原生 rollout。客户端不可宣称凭据保险库或不落盘。Stable ToolRequestUserInputParams/Response 位于 schema 根部；不用开启整个 experimentalApi。config/read 的 ToolsV2 只投影 web_search，不能假设它会回传 experimental_request_user_input；特性/上下文策略可以由 config/read 验证，工具门由 canonical config schema 与实际调用验证。

`prepare-interaction-tools.py` 只物化固定来源与 reviewed patch；`build-interaction-tools.sh` 创建按来源摘要独立的可复现开发产物，旧 native-tools-v1 制品不覆盖。Contracts → Host → Desktop 完成精确同步及定向验证后才从原开发入口激活。所有真实供应商验收均需当前任务额度，只允许 Kimi K3.1 Pro；本阶段构建/本地回环不调用供应商。

实现/失败记录/验证边界见元仓 `docs/features/FEAT-169-native-tool-integration/04-user-input-context-audit-and-plan.md` 与 `06-user-input-context-execution.md`。本候选不是发布或完整 App E2E 结论。
