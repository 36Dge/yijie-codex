# FEAT-171 原生协作停止候选

Owner 已确认 FEAT-171 和 ADR-0024，2026-11-09 授权实现。保留固定上游和0001—0023，追加 `0024-cooperative-exec-shutdown.patch`；canonical `codex-rs/` 不改。

`scripts/prepare-document-runtime.py` 重放到专用 `.local/document-runtime/workspace`；`scripts/build-document-runtime.sh` 输出内容寻址的新候选，保留旧二进制和来源。canonical config 增加 `exec_shutdown_policy=cooperative_only`，由 Contracts 投影、Host 精确配对后用于文档普通对话。app-server wire schema 未变。

策略在现有 UnifiedExec/PTY 内实现：关闭输入、单次协作中断、保留句柄和输出读取，等待实际退出。创建期间取消也由 registry/reaper 保有拥有权；活进程不被槽淘汰，待停止时不派发新任务。30秒后仍未退出报告 STOP_PENDING，继续保留拥有权，不调用强杀兜底。未配置者保留原默认行为。首期限定本地macOS arm64 direct；远程exec-server在spawn前拒绝。旧shell入口在该策略下引导使用原生exec_command。

不增加文档执行器、Office内核、审批引擎或看图工具。Python/Office/Quartz依赖由Desktop装配；原生执行、Code Mode、审批与view_image继续复用。Office平台访问走已有单次命令审批；不会通过补丁放开网络、沙箱可写根或自动批准。

已执行安全定向证据：专用workspace `cargo check -p codex-core --lib`；PTY正常退出和协作取消2项；patch独立重放；canonical release构建；Host使用该真实Runtime的本地HTTP协议回放，正常执行、用户取消与关闭，以及专用Python/Office经原生单次审批生成页图。真实模型调用0；完整Feature产品验收以元仓FEAT-171为准。没有强杀、二进制替身、权限破坏或攻击fixture。

回退只关闭新能力并选择保留的兼容配对，先正常停止当前拥有者。不得替换运行中的/已审计二进制，不把默认策略的强杀路径用于本需求测试。Owner在实现复审后已明确授权本次Git提交并推送到既有远端分支；产品发布仍未授权。

2026-11-09 实现复审补充：直接子进程退出但 stdout 仍在排空时，继续保留 reader/所有权，但不再向已退出所有者的进程组发送停止信号。新增正常父进程退出、后台输出完成的定向用例，与原正常退出/协作取消共3项通过。未制造 PID 复用、未强杀、未替换程序。更新后按 canonical 脚本生成新内容寻址候选，再更新 Contracts 投影和消费者配对；不覆盖既有候选。完整安装、最低配置、升级回退及深色界面验证按用户本轮指令暂不执行。
