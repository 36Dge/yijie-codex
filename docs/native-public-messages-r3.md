# 公开消息 r3：已观察到的 v1 声明拼写

2026-11-05，沿 Owner 已批准的显式消息适配候选修正真实缺口。
`contract-impact = semantic`。不更改模型、推理配置、工具权限、执行循环或数据库。

## 编译前根因确认

MiniMax R2-N04 的第一条声明使用点号格式，随后第二条声明使用
`[[yijie-public-message-v1:commentary]]`。后一种拼写来自 Host 提供的启用标记
`[yijie-public-message-v1]`，和原输出示例的点号命名不一致。
Runtime 只识别原点号前缀，第二条实际消息因此保持 unknown；非空的过程承诺
被既有完成启发式接受，turn 完成但无用户所需正文。原始记录、UI 和零付费
真实 Runtime 回环均已复现，旧 r2 在两次请求后结束；没有以重复付费测试猜测。

本轮 Kimi R2-N03 已通过独立开场、合格中途和最终答案三条真实消息的正常续行。
因此没有重写 Runtime 循环的依据，也不能把 MiniMax 的失败解释为所有模型不支持。

## 最小修复

0018 只修改 `core/src/session/public_messages.rs`：识别两个明确的 v1 命名
拼写，各自仅接受完整首行的 commentary/final_answer。逐段流式、完成快照、
正文中的冲突声明检查共用同一组常量；跨两种拼写的混合声明仍是单 Item、
unknown、不据此续行。Provider 原生 phase/end_turn 优先，原始正文与 phase
不改，未知版本、未知阶段与普通文字不猜写为声明阶段。

Host 将输出示例统一为与启用标记相同的连字符命名，两个阶段明确互斥；不再
要求模型在两套命名之间切换。用户“不调用工具”的约束明确包含 update_plan，
不新增 Host 工具筛选循环或 NLP 权限判断。实际违反工具约束的历史样本保留失败。

Desktop 对已保存的 unknown 阶段仅清理这一明确格式的首行控制标记，保留全部
正文和原始 unknown；不回填 phase、不把旧 failed-quality 样本变成成功，不重放生成。
引号、代码和用户消息保持。此读取清理不替代 Runtime 的新消息解析。

## 构建与验证范围

canonical 入口 `scripts/build-native-public-messages-r3.sh`；继续使用同一个
`codex-rs/target` 缓存。旧 r1/r2 制品保留，新制品目录为
`.yijie/build/native-public-messages-r3/aarch64-apple-darwin`。不创建额外完整源码树
或另一份大型 target，不覆盖签名/发布应用，不清理用户数据。

构建前，旧 r2 的真实 Runtime 普通回环已稳定复现原缺口。新候选需通过四个
完整声明的全部 UTF-8 切点、两种命名交叉混合、引用/代码字面保持、实际 Provider
阶段优先、关闭适配、原始历史及正常完成回归，再做一次 canonical 增量构建。
后续来源、schema、握手、Host 回环及 UI 实测单独记录；此说明不宣称测试已通过，
更不把一轮 Kimi 成功换算为两家模型的覆盖率达标。

本次 canonical 单次构建已完成：完成保护 10 项、公开消息 7 项（包含两种命名
及交叉混合的全部分段）、解析器 29 项和 scoped Clippy 均通过，release 用时
8 分 27 秒。269 份 canonical schema 与 r2 完全一致，树摘要仍为
`d8c3265d8923ef4437203c0a2ded954549b4abc0c5079ecd6bcdf7c6da72f11e`。
新二进制 SHA-256：
`cf358a9140a5e1f7e74c02bf94d55c871c28d3f5f871dfd95fbdd0e7a327b0aa`，
大小 356885944 字节。正常 stdio 握手/EOF 另以 canonical smoke 检查记录。
本次恢复任务仅调用一次 Runtime 构建，没有为 Host 指令调整重新编译 Runtime。
