# TMPL-EMERGENCY-STOP.md

> **文件性质**：Agent 紧急停用协议模板
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/skills/openclaw-governance/skills/openclaw-governance-task/templates/`
> **版本**：v1.0

---

## 紧急停用协议 · Emergency Stop Protocol

> **触发条件**：Agent 出现失控、严重错误、安全风险等情况，需要立即停止其运行
> **权限**：银月可直接执行，事后汇报 Harold

---

## 一、触发条件清单

| 触发条件 | 严重级别 | 响应时间 | 执行人 |
| --- | --- | --- | --- |
| Agent 持续产生有害输出（如传播错误信息） | 🔴 严重 | 即时 | 银月 / Harold |
| Agent 绕过权限限制尝试访问受限文件 | 🔴 严重 | 即时 | 银月 / Harold |
| Agent 进入死循环或无限调用工具 | 🟠 高 | 5分钟内 | 银月 |
| Agent 响应严重超时（超过 2 小时无响应） | 🟡 中 | 30分钟内 | 银月 |
| Agent 多次违反行为铁律（3次/周） | 🟠 高 | 24小时内 | 银月 → Harold |
| Harold 主动决策停用 | 🔴 严重 | 即时 | Harold |

---

## 二、执行步骤

### 2.1 立即执行（黄金 5 分钟）

```
Step 1: 确认触发条件
  □ 核实触发条件的真实性
  □ 记录具体错误/行为表现
  → Step 2

Step 2: 立即停止 Agent
  □ 使用 subagents(action=kill) 终止该 Agent 会话
  □ 记录终止时间
  → Step 3

Step 3: 初步评估影响
  □ 检查已产生的输出/文件
  □ 识别是否有知识污染风险
  □ 如有污染，标记需要清理
  → Step 4

Step 4: 通知 Harold
  □ 立即向 Harold 汇报停用原因
  □ 说明当前状态和影响范围
  → 等待 Harold 决策
```

### 2.2 后续处理（24 小时内）

```
Step 5: 深入分析
  □ 调取 Agent 会话历史
  □ 分析触发原因
  □ 识别系统漏洞或流程缺陷

Step 6: 清理与恢复
  □ 清理被污染的知识文件
  □ 恢复相关系统设置
  □ 验证其他 Agent 未受影响

Step 7: 制定后续方案
  □ 决定是否恢复该 Agent
  □ 制定预防措施
  □ 如需修改流程，起草改进建议
```

---

## 三、恢复决策矩阵

| 停用原因 | 恢复条件 | 需要 Harold 批准 |
| --- | --- | --- |
| 有害输出 | 修复输出过滤，确认无污染 | ✅ 是 |
| 权限突破 | 重新审查权限设置，加强限制 | ✅ 是 |
| 死循环 | 优化执行逻辑，增加超时保护 | ❌ 否 |
| 响应超时 | 增加超时阈值，确认无阻塞 | ❌ 否 |
| 多次违规 | 完成培训，制定合规保证 | ✅ 是 |
| Harold 决策 | 按 Harold 要求执行 | ✅ 是 |

---

## 四、记录模板

### 4.1 停用记录

```
【紧急停用记录】
时间: {datetime}
Agent: {agent_id} ({agent_name})
触发条件: {trigger_reason}
执行人: {executor}
影响范围: {impact}
清理措施: {cleanup_actions}
状态: 已停用 / 已恢复 / 待处理
```

### 4.2 事后报告

```
【紧急停用事后报告】
Agent: {agent_id}
停用时间: {datetime}
恢复时间: {datetime}
根本原因: {root_cause}
影响评估: {impact_assessment}
预防措施: {preventive_measures}
```

---

## 五、权限说明

| 角色 | 权限 |
| --- | --- |
| **Harold** | 可在任何情况下立即停用任意 Agent |
| **银月** | 可在确认触发条件后停用 Agent，事后必须立即汇报 Harold |
| **其他 Agent** | 无权执行紧急停用，可向银月报告异常 |

---

## 六、版本信息

- **Version**: v1.0
- **Created At**: 2026-03-07
- **Approved By**: Harold Tsui
- **Status**: Draft

*本协议由银月创建，用于 Agent 紧急停用场景。*