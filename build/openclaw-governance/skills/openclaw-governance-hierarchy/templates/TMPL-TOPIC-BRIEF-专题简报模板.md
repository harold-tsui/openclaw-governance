
---
title: [TOPIC_NAME]
tags: []
type: topic
id: [TOPIC_ID]
status: active
owner: [AGENT_ID]
project: [PROJECT_ID]
phase: [PHASE 标识]
priority: [P0-P3]
privacy: [P0-P3]
related_tasks: []
related_topics: []
start_date: [YYYY-MM-DD]
target_date: [YYYY-MM-DD]
---
# TOPIC-BRIEF · [TOPIC_NAME]

> **文件性质**：Topic 层上下文定义文件
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/10_Projects/[PROJECT_ID]/[TOPIC_ID]/TOPIC-BRIEF.md`
> **上位引用**：ZT-2026-005_工作流程与约束规则.md、HEARTBEAT.md
> **读写权限**：Topic PIC 可写；Project PIC、银月可读写；Harold 可读
> **版本**：v1.2

---

## 一、Topic 基本信息

| 字段 | 内容 |
|---|---|
| **Topic ID** | [TOPIC_ID] ← 命名规范：`[PROJECT_ID]-TP[序号]`，如 `NUC-01-TP01` |
| **Topic 名称** | [TOPIC_NAME] |
| **归属 Project** | [PROJECT_ID] · [PROJECT_NAME] |
| **Topic PIC** | [AGENT_NAME] |
| **状态** | 🟢 Active / 🟡 On Hold / 🔴 Blocked / ✅ Done |
| **Review 级别** | L3 / L2 / L1 / L0 ← 默认 L3；以 HAROLD-DELEGATION.md 中授权记录为准；如有授权填写授权编号 `DA-[编号]` |
| **创建时间** | [CREATED_AT] |
| **最后更新** | [LAST_UPDATED] |
| **计划完成日期** | [END_DATE] |

---

## 二、Topic 目标与验收标准

### 2.1 目标陈述
> 本 Topic 要解决什么问题，产出什么结果？

[TOPIC_GOAL]

### 2.2 验收标准
> 如何判断本 Topic 完成了？

| 序号 | 验收标准 | 验收方式 | Review 级别 |
|---|---|---|---|
| 1 | [CRITERIA_1] | 银月验收 / Harold Review | L3 / L2 / L1 / L0 |
| 2 | [CRITERIA_2] | — | — |

---

## 三、输入物（Inputs）

> 启动本 Topic 所需的前置材料、信息或前置 Topic 的输出。

| 输入物 | 类型 | 来源 | 状态 |
|---|---|---|---|
| [INPUT_1] | 文件 / 数据 / 前置 Topic 输出 / 决策 | [SOURCE 或 TOPIC_ID] | ✅ 已就绪 / ⚠️ 待准备 |
| [INPUT_2] | — | — | — |

---

## 四、Task 列表

> 本 Topic 下所有 Task 的索引。未完成的 Task 同步记录至 MISSION_BOARD。

| Task ID | Task 标题 | Task PIC | 优先级 | Review 级别 | 状态标记 | 文件路径 |
|---|---|---|---|---|---|---|
| [TASK_ID] | [TASK_TITLE] | [PIC] | P0/P1/P2/P3 | L3/L2/L1/L0 | `[?]/[!]/[V]/[x]` | `./tasks/TASK-CARD-[TASK_ID].md` |

**Task 完成进度**：`[x] 已完成` / `全部 Task 数` ← 银月在每次 Heartbeat 时更新

---

## 五、参与人员

| 角色 | 姓名 / Agent | 职责说明 |
|---|---|---|
| **Topic PIC** | [NAME] | 对本 Topic 所有 Task 推进和交付负责 |
| **协作 Agent** | [NAME] | [COLLABORATION_DESCRIPTION] |
| **银月** | 银月 | 进度监控、阻塞协调、Topic 状态向上冒泡 |

---

## 六、执行流程

> **Topic 执行流程规范**：详细定义见 ZT-2026-005_工作流程与约束规则.md 第三章
> **状态同步与冒泡规则**：详细定义见 HEARTBEAT.md Step 3

```
[按 ZT-2026-005 执行，具体步骤根据实际 Task 填充]
```

---

## 七、关键依赖

| 依赖类型 | 依赖对象 | 说明 | 状态 |
|---|---|---|---|
| **前置 Topic** | [TOPIC_ID] | 需要该 Topic 完成后才能启动 | ✅ 已完成 / ⚠️ 进行中 |
| **并行 Topic** | [TOPIC_ID] | 与该 Topic 并行推进，需信息同步 | — |
| **外部依赖** | [DESCRIPTION] | [说明] | — |

---

## 八、Deliverable 汇总

> 汇总本 Topic 下所有 Task 的交付物。
> **Review 级别**以各 Task 的 Review 级别为准，如 Topic 级有特殊要求可单独标注。

| Deliverable | 来源 Task | Review 级别 | Harold Review 状态 | 验收状态 |
|---|---|---|---|---|
| [DELIVERABLE_1] | [TASK_ID] | L3 全量 / L2 抽样 / L1 异常 / L0 免审 | ⬜ 待提交 / 🟡 审阅中 / ✅ 已通过 / N/A | ⬜ / 🟡 / ✅ |
| [DELIVERABLE_2] | [TASK_ID] | — | — | — |

**Topic 整体 Review 级别规则**：
- Topic 下有任意 L3 的 Deliverable → Topic 完成时，银月须出具「Topic 完成报告」提交 Harold 全量审阅
- Topic 下最高为 L2 → 银月抽样后，出具「Topic 完成报告」，Harold 按抽样结果介入
- Topic 下全部 L1/L0 → 银月验收后直接确认 Topic 完成，Harold 不介入，定期汇报即可

---

## 九、Topic 完成报告

> 所有 Task 状态为 `[x]` 后，Topic PIC 填写，银月复核后按 Review 级别决定是否提交 Harold。
> **Topic 完成报告是 Topic 关闭的前置条件。**

| 字段 | 内容 |
|---|---|
| **填写时间** | [DATETIME] |
| **填写人** | [Topic PIC] |
| **目标达成情况** | [对照第二章验收标准，逐条说明是否达成] |
| **Deliverable 完成率** | [已完成数] / [总数] |
| **Harold Review 完成率** | [已通过数] / [需 Harold Review 总数] |
| **未达成项说明** | [如有，说明原因和后续处理方案] |
| **DL 新增条目数** | [本 Topic 执行过程中新增的 Decision Library 条目数] |
| **银月复核状态** | ⚠️ 待复核 / ✅ 已复核 |
| **Harold 最终确认** | ⚠️ 待确认 / ✅ 已确认 / N/A（L1/L0 免Harold确认） |

---

## 十、状态同步规则

> **状态同步与冒泡规则**：详细定义见 HEARTBEAT.md Step 3

| 触发条件 | 银月动作 |
|---|---|
| Task 状态变更 | 按 HEARTBEAT.md Step 3 规则执行 |
| Topic 完成 | 按 HEARTBEAT.md Step 3c 规则向上冒泡至 Project |

---

## 十一、状态历史

| 日期 | 状态变更 | 变更原因 | 记录人 |
|---|---|---|---|
| [DATE] | 创建 → 🟢 Active | Topic 启动 | [NAME] |

---

## 版本信息

- **Version**: v1.1
- **Changes from v1.0**:
  - 基本信息表新增 `Review 级别` 字段，引用 HAROLD-DELEGATION.md
  - 验收标准表新增 `Review 级别` 列
  - Task 列表新增 `Review 级别` 列，新增「Task 完成进度」计数行
  - Deliverable 汇总表 `[HR]` 升级为 `Review 级别` 四级，新增 Harold Review 状态列
  - Deliverable 汇总新增「Topic 整体 Review 级别规则」
  - 新增「九、Topic 完成报告」章节
  - 新增「十、状态同步规则」章节（含 Task→Topic、Topic→Project 两级冒泡规则及时限）
  - 执行流程补充「Review 级别确认」和「向上冒泡」步骤
  - 参与人员银月职责补充「Topic 状态向上冒泡」
- **Created At**: 2026-02-24
- **Approved By**: Harold Tsui

*本文件由 Topic PIC 维护，Project PIC 审批重大变更，银月监督推进并负责状态冒泡。*
