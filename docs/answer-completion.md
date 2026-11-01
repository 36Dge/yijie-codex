# 普通过程说明提前结束修复

2026-11-01，用户明确要求按执行审计修复只有过程说明就结束的问题，复用机制且保留其他能力。

`contract-impact = semantic`。权威源是可重放的 `0013-answer-completion.patch`，消费者是受管本机 Host/普通聊天。原 app-server schema、权限、审批、工具和历史身份不变。仅 Host 的 developer instructions 中明确包含 `[yijie-answer-completion-v1]` 且无结构化输出 schema 时启用。标题及结构化计划不使用此终态判断；非易界消费者不启用。此授权范围是本机开发修复，不是公开或生产发布。

固定版本的 turn loop 原先将没有后续工具的模型消息直接视作结束。供应商不提供 phase 时，一句将来时过程说明也会走相同分支。补丁在原采样结果→结束分支增加检查，沿同一 turn、原 history、cancel/stop/error 生命周期继续，绝不创建新的用户任务、伪造正文或重放已执行步骤。

- 明确 commentary、空回答、保守匹配的未标阶段纯过程说明触发补答；非空正常回答、事实/列表/代码、用户明确要求计划或引用的内容保持原行为。
- 最多两次补答。补答请求不再暴露工具，原工具分发器也在执行前拒绝额外调用，避免重跑副作用；只根据已取得内容回答，资料不足必须说明限制。
- 第二次仍无回答时走原生失败终态和固定原因，不标成功、不无限请求。新用户 steer 清除本轮补答上下文；正常后续任务不受限制。
- 外部 hooks 不启用，不改模型、沙箱或审批授权。状态保存在已有 turn ExtensionData，完整原记录保留。提示通过已有 Warning/Error 通道映射到中文诊断。

未标 phase 的自然语言识别是保守兜底，不声称可以自动判断所有回答的事实质量或任务完整度。已完成的历史轮次不自动重放。测试使用正常本机 Responses 数据和真实 canonical Runtime，正常 Shutdown；不调用供应商、不替换可执行程序、不制造进程/权限故障。

构建入口 `scripts/build-answer-completion.sh`，复用原 `.local/web-retrieval-guard/workspace` 和 Cargo target；旧受审 Runtime 不覆盖。新增产物仅一份有来源记录的 Runtime，客户端仍使用固定开发入口，无安装包或全数据备份。
