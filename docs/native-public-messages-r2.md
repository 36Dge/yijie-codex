# 原生公开消息 r2：单 Item 声明校验与流式显示保护

2026-11-05，在 Owner 已批准的限定适配候选范围内修复真实 MiniMax C-N01 暴露的
缺口。`contract-impact = semantic`，无公共 schema 字段、传输、权限或数据格式
变化。不实现 Host 循环，不增加模型、不降低推理配置，不用补答调度正常进展。

## 证据与修复边界

该回合实际第一条 Message 同时包含 commentary 开场和 final_answer 声明及
完整正文；它们不是两个原生 Item。0016 仅消费首行，把第二条声明留在正文中，
又依据首个 commentary 继续采样；随后一个响应没有公开消息，既有补答才给出
另一条 final。真实界面展开过程时可见控制标记，正常生成验收失败，后续付费
用例已停止。不能把正文交付或两个最终文本当作有意义的中途更新通过。

0017 仅补齐该声明合同的接收校验：

- 复用 `codex-utils-stream-parser` 的 TaggedLineParser，增加显式 standalone
  marker 模式；现有 block-tag 模式保持默认行为。新模式有界候选行，保留行内、
  引用、缩进代码、反引号/波浪线 fenced code，包括不同 fence 长度。
- 识别到首行声明后，正文内额外未引用的独立阶段声明属于格式违约；流式和
  完成态只去掉这些控制行，保留全部可读内容。无首行声明的普通消息不走该清理。
- 一条真实 Item 仍只产生一个 started/completed。多个未引用声明不能证明一份
  可靠的声明阶段；无原生 Provider phase 时，完成态投影降为 unknown，且不再
  作为正常续行依据。实际 Provider phase 存在时仍优先保留它的独立权威。
- streaming 开始时可以先显示首行声明的阶段；发现完整消息违约后，由既有
  item/completed 完整快照替换为 unknown，不另造 Item 或修改原始 ResponseItem。
  Native 已有的全快照替换支持此行为，不能粘住旧的暂定阶段。
- 既有 answer-only 保护继续根据规范化后的正文与有效阶段判断。正文完整时
  不因失效的 commentary 声明再取样；确实缺结果时仍受原有两次补答上限约束。

原始 phase（包括缺失）、所有声明和正文继续记录并回传模型。原始事实与公开
阅读语义分开，不能把 unknown 猜写成 final，不能按字符串把一条 Message 拆成
多个虚构 Item。保留 inline / quoted / code 的字面声明示例；内部控制声明不得
作为未引用独立行混入正文。Host 指令同步明确“一次模型响应至多一条当前公开
消息”，而不是一次输出整轮对话剧本；真实需要的 tool-only response 不强凑播报。

已保存的 0016 异常记录由 Desktop 只读阅读投影隐藏 commentary 中独立的内部
控制行，存储正文与 phase 均不改。当前格式会话不清库、不迁移、不重放生成。

## 来源与验证

0016 与其旧制品保持；0017 顺序重放到临时构建目录，`codex-rs/` 上游原件不改。
canonical 入口 `scripts/build-native-public-messages-r2.sh`，产物独立保存于
`.yijie/build/native-public-messages-r2/aarch64-apple-darwin`。

已通过 10 项完成保护、7 项公开消息核心测试、29 项原生文本解析测试、core/文本
解析器 scoped Clippy、release、源码重验、schema 对照及正常 stdio 握手/EOF。
新 binary SHA-256 为
`6f38c8035eaa34ccdff8e5840ddbe5c9c0e510b97e35014f5b5fd888f9fdc9f4`；
269 份 schema 树仍为
`d8c3265d8923ef4437203c0a2ded954549b4abc0c5079ecd6bcdf7c6da72f11e`。
后续 Host 真 Runtime 混合声明回环、Native 保存/重开与旧记录 UI 验证逐项取证。
这些不替代真实模型遵循和 90%/80% 生成覆盖率，当前不能声称整体目标完成。

旧 FEAT-137 管理 checker 与其冻结投影的已记录限制保持，没有放宽检查来制造
全仓 PASS。此修复不启用已退役 producer，也没有强杀、权限破坏或攻击性 fixture。
