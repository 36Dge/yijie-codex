# 公开写作预告的原生收尾修复

2026-11-04，Owner 明确允许本轮最小 Runtime 修复及必要本地来源固化，不推送。
`contract-impact = semantic`。无协议、权限、历史格式或预算变化；新增 0015 只在
原有 `process_only` 动词表补齐“写一版、写一份、起草、撰写、draft、write a”。

真实 Kimi 回合只有未标 phase 的“我会按 copywriting 技能直接写一版……”后结束，
固定 Runtime 的普通回环已复现只请求一次且缺正文。该分类缺口会让过程预告被
当作可交付答案。原生 `end_turn=false`、工具 needs_follow_up、明确阶段及
同响应多消息均已存在；本次不重复实现它们。

保留既有长度/事实/代码/列表/问题排除、明确只要计划及原样引用例外；保留最多
两次无工具 answer-only 补答、原生失败终态与完整记录。写作识别仍是保守语言兜底，
不证明所有未标阶段消息的语义或答案质量，不把补答当作进度调度。

补丁从既有 0014 后顺序重放，只进入 canonical 临时构建工作区，不修改上游子树。
`bash scripts/build-public-progress-completion.sh` 复用既有构建、core 定向测试、
Clippy、来源重验与 schema 对照；产物存 `public-progress-completion-v1`，拒绝
覆盖已有产物。先完成实际验证并固定 Runtime，再更新 Contracts→Host→Desktop
引用后正常接入。旧 Runtime 保留，无数据库迁移或历史补造。

新增正常正反例覆盖真实写作预告、完整文案、前缀加实际结果、明确只要计划和原样
引用；正常续行与工具保持由 Host 的固定 Runtime 回环另验。未执行的提供方效果、
覆盖率及真实界面验收不得写为通过。

本地 canonical 构建已完成：9 项 answer_completion core 测试、定向 Clippy、
源码重放重验及 stdio initialize/initialized→正常 EOF 退出通过。新二进制 SHA-256
为 `b9991f4136b91428ab220e41186b04cae114f88892c44f239455fb5754b2325d`；269 个
schema 的树摘要仍为 `d8c3265d8923ef4437203c0a2ded954549b4abc0c5079ecd6bcdf7c6da72f11e`。
未改固定上游源码，旧制品保持。release 编译保留既有 app-server unused_mut 警告。

`make lint` 通过；`make test` 被仓库既有脚本执行位门禁阻断（16 个历史脚本以
100644 提交），没有修改这些无关权限或把完整管理测试标为通过。分别执行其正常
契约/manifest/无强杀 smoke 驱动检查 11+2+3 项均通过，上游逐字一致性检查通过。
