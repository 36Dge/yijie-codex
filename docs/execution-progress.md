# 原生预算复用与重复计划收尾

2026-11-03，Owner 要求复审执行循环方案、强制复用仓库已有机制并开始实施。

`contract-impact = semantic`：Host 明确启用的普通聊天，重复未推进的计划转入原有补答流程；普通聊天投影原生 rollout budget。app-server schema、权限、审批、历史格式与模型选择保持，实际 schema 一致性和消费者 pin 验证后才可激活。无发布、推送或额外付费验证授权。

## 复用清单与上一版审计更正

| 原生机制 | 权威代码 | 本次处理 |
|---|---|---|
| `model_auto_compact_token_limit` / catalog `auto_compact_token_limit` | `core/src/session/turn.rs` 与 `context_manager` | 保留原生压缩，不把上下文阈值当费用预算 |
| `features.token_budget` | `core/src/session/token_budget.rs` | 保留原生上下文提醒与 guidance；不复制提醒机制 |
| `features.rollout_budget` | `core/src/rollout_budget.rs`、`session/rollout_budget.rs` | 直接配置，复用共享根会话树累计、提醒和 `SessionBudgetExceeded` |
| `goal.token_budget` | `ext/goal` | 维持显式目标语义，不为普通问题自动创建 Goal |
| 既有 `answer_completion` | 已审 `0013` | 复用同一 turn 状态、无工具补答、最多两次补答和原生失败终态 |
| `UpdatePlanArgs` 与 `PlanHandler` | `protocol/src/plan_tool.rs`、`tools/handlers/plan.rs` | 使用原生参数与真实成功事件识别连续相同计划 |

上一版审计遗漏了 `features.rollout_budget`，其“需要另建消费计数器”的建议撤回。Host、Desktop 和新增补丁均不得再累计一份用量或实现另一套预算、重试、planner、执行循环。

原生 rollout budget 的真实口径是 `output_tokens * sampling_token_weight + max(input_tokens-cached_input_tokens,0) * prefill_token_weight`。范围是一次加载的根线程会话树，包含子代理；不是每个用户问题的独立预算，也不是跨重载永久账本或人民币封顶。原生计数在响应 usage 结算时检查，因此已经在途的一次请求可能超过阈值。重载、Goal 和压缩的既有语义不得被 Host 偷换。

## 确认的缺口与最小补丁

固定源码没有成功但未推进的重复计划检测。`0013` 的外层 `needs_follow_up && !finalizing` 提前返回，令连续工具调用永远不进入已有补答上限。

新 `0014-execution-progress.patch` 只补这个入口：原生 `PlanHandler` 接受参数后观察 `args.plan`；忽略 explanation，连续相同计划达到三次后调用既有补答决策。其它普通工具调用可能推进工作，清除这个窄判定；不按 shell 字符串静默去重或全局禁止 `pwd/true`。更一般的循环由原生 rollout budget 控制。

进入补答后使用 `0013` 原有工具过滤、执行前拒绝与最多两次补答。hosted `web_search` 同样被移除；不重新提交用户任务，不伪造答案或工具结果，不改变模型 `max`。结构化输出和无 Host 标记的消费者不启用此检查。

## 构建与来源

`bash scripts/build-execution-progress.sh` 复用既有 canonical source replay、Rust 1.95.0、原 Cargo cache、编译和 schema 验证逻辑；仅扩展补丁链。新产物在 `.yijie/build/execution-progress-v1/aarch64-apple-darwin`，拒绝覆盖已有产物。`codex-rs/` 上游子树不修改。

Runtime 候选验证后，按既有不可变源码 → Contracts 投影 → Host/Desktop 精确 pin 的顺序接入。旧受审 Runtime 保留。没有把尚未固定的源、尚未执行的真实模型验证或尚未激活的客户端写成通过。
