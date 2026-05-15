---
name: managing-tasks
description: |
  Creating, executing, reviewing, and archiving tasks throughout lifecycle.
  
  Activates when: User intent matches task-related keywords
  
  Capabilities:
  - Task-CARD creation and assignment
  - Task lifecycle management (receive/execute/submit/review)
  - Deliverable review routing (L0-L3)
  - MISSION_BOARD synchronization
  - Task archiving with knowledge capture
  
  Keywords: task, task-card, deliverable, review, mission-board
  
  For detailed documentation, see:
  - references/task-lifecycle.md
  - scripts/task_functions.py
  
author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "8.0.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L2"
  os: ["darwin", "linux"]
  lastRefactor: "2026-04-26"
  tags: ["task-management", "lifecycle", "task-card", "mission-board", "workflow", "pdca"]
---

# 工作流程与任务管理 · Skill

Tags: #governance, #task-management, #workflow, #pdca

> **触发模式**：描述匹配触发 + 模型主动 read()
> **v8.0.0**: 任务执行统一为 PDCA 模型；人类驱动与 heartbeat 驱动走同一流程

## 何时使用

- **Task creation**: 用户要求创建任务、分配工作或管理 Task-CARD
- **Task execution**: 任何任务的执行——无论是 heartbeat 自动推进还是人类直接驱动
- **Task lifecycle**: 接收、审核、关闭或归档任务
- **Deliverable routing**: 确定交付物的 Review 级别（L0-L3）
- **MISSION_BOARD sync**: 任何必须反映到任务看板的状态变更
- **Do NOT use for**: 项目/Topic 创建 — 委托给 `governance-hierarchy`

## 常见陷阱

1. **不能有孤儿 Task-CARD**: 每个任务必须属于某个 Topic，Topic 必须属于某个 Project。创建任务前必须先验证层级。
2. **MISSION_BOARD 是派生视图**: §一 状态总览的数字从各 section 计数得出，不可手写。Task-CARD 是唯一真相源。
3. **任务启动前必须验证输入物**: PIC 必须确认输入物状态为 Active（不能是 Draft/Stale/Archived）才能开始工作。
4. **模板创建受限**: 只有 CDO 可以创建/修改模板。不得私自创建临时模板。
5. **关闭时触发 Zone C**: 关闭任务时必须触发 Zone C 知识沉淀 — 不能跳过这一步。
6. **PDCA 是强制的**: 任何任务执行（heartbeat 驱动或人类驱动）都必须跑完一轮 Plan→Do→Check→Act。不存在"跳过 Check 直接交付"。

---

## 一、Task 定义与归属

### 1.1 Task 类型

| Task 类型 | 归属规则 | 示例 |
|------|------|------|
| **业务 Task** | 所属 Project 的 Topic 下 | ZT-P001-T01-T01 |
| **方法论 Task** | 所属 Project 的 Topic 下 | ZT-P008-T06-T01 |
| **临时 Task** | Agent 个人工作台 | ZT-P-AGT-cqo-T01 |
| **孤儿 Task** | NUCLEUS 治理基础 | ZT-P000-T99 |

### 1.2 规范引用

- **ZT-2026-005**: 工作流程与约束规则
- **ZT-2026-007**: 交付物路径规范
- **TMPL-TASK-CARD**: Task-Card 模板 v3.1

---

## 二、核心原则

### 2.1 MISSION_BOARD 派生规则

**核心原则**：Task-CARD 是唯一真相源；MISSION_BOARD 是派生视图。

| 触发事件 | MISSION_BOARD 变更 |
|---------|-------------------|
| Task-Card 创建 | 新增条目，状态 `[ ]` + §一 派生刷新 |
| Task-Card accept | `[ ]` → `[P]` + §一 派生刷新 |
| PDCA Act 完成 | 按 verdict 更新状态 + §一 派生刷新 |
| Task 阻塞 | `[P]` → `[?]` + §一 派生刷新 |

**§一 派生算法**：活跃=§三 Task ID 数，待处理=§五 Task ID 数，阻塞=§二 Task ID 数，本周完成=§六中 close_date 在本周的 Task ID 数。

### 2.2 任务执行 = PDCA 循环

**无论哪种入口，任务执行都是一轮 Plan→Do→Check→Act。**

| 入口 | 触发方式 | 区别 |
|------|---------|------|
| **Heartbeat 驱动** | OpenClaw Gateway 定时触发 | Agent 自主选 Task |
| **人类驱动** | Harold 在会话中直接推进 | Harold 指定 Task |

**两种入口走同一个 PDCA 流程，没有"快速通道"**。人类驱动的好处是可以即时获得 Review 结果（Harold 在会话中直接 approve/reject），但 PDCA 步骤不可跳过。

### 2.3 PDCA 各步骤对应 Task-CARD 操作

| PDCA Step | Task-CARD 操作 | 可否跳过 |
|-----------|---------------|---------|
| **Plan** | 读 Zone B，判断状态，规划下一步 | 否（除非是简单 follow-up） |
| **Do** | 写 Zone B 执行日志，产出可见输出物 | 否 |
| **Check** | 对照 §五 验收标准（DOD）逐项验证 | 否 |
| **Act** | 更新 §七.1 状态 + MISSION_BOARD 派生刷新 + pdca.py 记录 | 否 |

### 2.4 Zone B 执行日志最小格式

Do 步骤必须向 Task-CARD Zone B 写入执行日志。每轮 PDCA 一条记录，最小字段：

| 字段 | 必填 | 说明 |
|------|------|------|
| `pdca_cycle` | 是 | 周期序号（从 1 递增） |
| `step` | 是 | 本轮 PDCA 执行到哪一步（plan/do/check/act） |
| `plan_summary` | 是 | Plan 产出：下一步动作 / 改进方向 / 解除方案 |
| `do_summary` | 是 | 实际执行了什么（产出物、修改文件、分析结论等） |
| `check_result` | 是 | 对照 DOD 的验证结果（逐项 pass/fail + Review 级别） |
| `verdict` | 是 | pass / partial / fail / pending |
| `timestamp` | 是 | 本轮 PDCA 完成时间 |

**禁止**：只写"执行了 PDCA"而无具体内容。每条日志必须让第三方能判断"做了什么、效果如何"。

### 2.5 Review 阻塞点

PDCA 的唯一停顿是"需要人类决策"：

| 阻塞点 | 时机 | 谁决定 |
|--------|------|--------|
| **Plan Review** | 复杂/战略性任务，Plan 后需 Harold 审批方案 | Harold 或 Task-CARD 标注 `plan_review_required` |
| **Check Review** | 交付物验证后，按 Review 级别决定谁 Review | Review 级别 + LLM 可升级 |

**Review 级别**：

| 级别 | Review 人 | 规则 |
|------|----------|------|
| L0 | Agent 自验收 | Check 自动完成 |
| L1 | 银月 | 银月判断是否上报 |
| L2 | 银月抽样 Harold | 银月抽样 20-30% |
| L3 | Harold 全量 | 必须等 Harold approve |

**LLM 可主动升级 Review 级别**：质量不确定、发现风险、超出自身判断能力时。

---

## 三、函数接口

> **详细实现**：[scripts/task_functions.py]({baseDir}/scripts/task_functions.py)

### 3.1 create_task()

**职责**：创建任务并分派给 Task PIC。

**输入**：task_title, task_type, project_id, topic_id, assignee, task_pic, reviewer, priority, review_level, deliverables

**输出**：task_id, state `[ ]`, next_action

### 3.2 accept_task()

**职责**：Task PIC 确认接收任务，状态 `[ ]` → `[P]`。

### 3.3 review_deliverable()

**职责**：验收交付物，按 Review 级别路由。

| Review 级别 | 路由逻辑 |
|-------------|---------|
| **L0** | 银月直接验收 |
| **L1** | 银月判断是否上报 |
| **L2** | 银月抽样 20-30% |
| **L3** | Harold 全量审阅 |

### 3.4 close_task()

**职责**：关闭任务，状态 `[V]` → `[x]`，触发 Zone C。

### 3.5 archive_task()

**职责**：归档任务，状态 `[x]` → `[archived]`。

---

## 四、状态流转

> **详细说明**：[references/task-lifecycle.md]({baseDir}/references/task-lifecycle.md)

### 通用状态

| 状态 | 标记 | 含义 |
|------|------|------|
| 待接收 | `[ ]` | 已创建，等待接收 |
| 执行中 | `[P]` | 已接收，执行中 |
| 待验收 | `[V]` | 已提交，等待验收 |
| 已完成 | `[x]` | 验收通过，已关闭 |
| 归档 | `[archived]` | 知识沉淀完成 |
| 阻塞 | `[?]` | 需解除后继续 |

### Issue Ticket 特殊状态

| 状态 | 标记 | 含义 |
|------|------|------|
| 分析中 | `[A]` | 进行根因分析 |
| 修复中 | `[F]` | 执行修复 |
| 待测试 | `[T]` | 修复完成，等待测试 |
| 待抽查 | `[Q]` | 测试通过，等待抽查 |

---

## 五、约束规则

### 5.1 输入物管理

**MUST**：每个 Task 启动前，PIC 必须确认输入物已就绪且状态为 Active。

**MUST NOT**：引用状态为 Draft / Stale / Archived 的文件作为正式输入。

### 5.2 交付物生命周期

| 流转 | 触发条件 |
|------|----------|
| Draft → Active | 元数据齐全 + Quality Gate 通过 |
| Active → Stale | 90 天未更新 |
| Stale → Archived | 进入 Stale 超 30 天 |

### 5.3 模板管理

- 所有交付物模板由 CDO 统一管理
- 任何 Agent 无权私自创建模板
- 新模板需求需经数据治理委员会评审

---

## 六、生命周期闭环

> **详细说明**：[references/task-lifecycle.md]({baseDir}/references/task-lifecycle.md)

### 创建时闭环

1. 生成 Task-Card（Zone A 预填）
2. 更新 MISSION_BOARD §五 待处理队列
3. 通知 Task PIC

### 接收时闭环

1. Task-Card §七.1 状态改为 `[P]`
2. 更新 MISSION_BOARD §三 进行中区
3. 通知指派人已接收

### 关闭时闭环

1. verify_task_closed() 全部通过
2. Task-Card §七.1 状态改为 `[x]`
3. 更新 MISSION_BOARD §六 已完成区
4. Zone C 沉淀状态设为 `⏳ pending`

---

## 七、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **8.0.0** | 2026-04-26 | 任务执行统一为 PDCA 模型；人类驱动与 heartbeat 驱动走同一流程；MISSION_BOARD 改为派生视图；Review 阻塞点定义 |
| **7.0.0** | 2026-04-22 | Skills 最佳实践重构：函数分离(scripts/)、生命周期分离(references/)、SKILL.md 精简 |
| **6.0.4** | 2026-04-18 | Issue Ticket review_level 按 severity 分级 |
| **6.0.0** | 2026-04-08 | 对齐 TMPL-TASK-CARD v3.1 |

---

*版本: 8.0.0 | 更新: 2026-04-26 | 变更: 任务执行统一为 PDCA 模型；人类驱动与 heartbeat 驱动走同一流程*

## Related Skills
- [[openclaw-governance-delegation]] - 授权与等级判定
- [[openclaw-governance-quality]] - 质量管控
- [[openclaw-governance-hierarchy]] - 层级管理