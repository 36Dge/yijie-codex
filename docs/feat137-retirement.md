# FEAT-137 — Owner 永久终止、未完成验收

2026-09-05 Owner 重申永久终止：实现耗时过长，不再继续实施，未来也不重启。原审批、producer、D4、re-freeze 计划只保留为历史证据，不是待办。未完成的验收不补做、不改写为 PASS。

## 当前有效 Runtime

Contracts 冻结权威：`4d3f967938dde1c86ca34003a0a5628717f96262:docs/retirements/FEAT-137.json`。

Host/Desktop 正常及 stable 入口恢复使用已存在的 FEAT-136 两补丁 artifact：

- source commit：`b2b20e2fc4a0c94834f34d8cc459e488a1b56277`。
- artifact：`yijie-agent-host/.local/runtime-artifacts/feat-136-b2b20e2fc4a0/`。
- binary SHA256：`4efe16d2848680752cf9aacf4c17741ab2eeb7415894a66c2bb03652b00a322d`。
- manifest SHA256：`1cfa2e0a139b2213f4d29b1efeed71d4810110ac865f0bcbd931ff33b0062c1b`。
- stable schemas：267 files，tree SHA256 `82ee9de771cf1d41bac16d87380f1121e7794107aa3aa526ad702d5d1bf7afe1`。
- 保留 FEAT-126 日志安全和 FEAT-136 Command lifecycle；政策固定 `never` / `read-only`，Host 拒绝旧审批和 deterministic producer 激活环境变量。

## 历史源码不等于运行基线

本仓库没有整体回滚。原四补丁 fork source、schema、测试和 canonical build 脚本只保留可审计的历史；它们不能证明 FEAT-137 已验收，也不是当前 Desktop 的 artifact 来源。当前 checkout 的 `make build` 仍描述历史四补丁 candidate，**不得用于此退休后的正常入口或重新开展 FEAT-137 D4**。若其他需求需要重建有效基线，应从上面不可变两补丁 source 开独立需求，按 Runtime→Contracts→Host→Desktop 流程重新冻结，不复制旧 feature gate。

原有 FEAT-137 分支完整 bundle、精确 refs 和其他仓库未提交补丁存放于 `/Users/jack/Downloads/Personal_Info/FEAT-137-retirement-2026-09-05/`。保留归档用于审计和灾难恢复，不代表未来重启需求。
