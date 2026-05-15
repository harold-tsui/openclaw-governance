---
title: [TASK_TITLE]
tags: []
type: task
id: [TASK_ID]
status: pending
owner: [AGENT_ID]
topic: [TOPIC_ID]
project: [PROJECT_ID]
priority: [P0-P3]
privacy: [P0-P3]
review_level: [L0-L3]
task_type: [regular/cycle/issue-ticket/emergency]
deliverables: []
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
due: [YYYY-MM-DD]
related_tasks: []
---
# TASK-CARD · [TASK_TITLE]

> **文件性质**：Task 层上下文定义文件
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/10_Projects/[PROJECT_ID]/[TOPIC_ID]/tasks/TASK-CARD-[TASK_ID].md`
> **读写权限**：Task PIC 可写；Topic PIC、银月可读写；Harold 可读
> **上位文件**：`../TOPIC-BRIEF.md`
> **版本**：v3.2

---

## 声明

> **状态标记含义**：详细定义见 HEARTBEAT.md 附录 A
> **通用状态**：`[ ]` 待接收 / `[P]` 执行中 / `[V]` 待验收 / `[x]` 已完成 / `[?]` 阻塞 / `[!]` Harold 待决
> **Issue Ticket 子状态**：`[A]` 分析中 / `[F]` 修复中 / `[T]` 待测试 / `[TT]` 测试中 / `[Q]` 待抽查 / `[QQ]` 抽查中 / `[C]` 待关闭
> **Review 级别规则**：详细定义见 HAROLD-DELEGATION.md（L0=免审 / L1=异常上报 / L2=抽样核查 / L3=全量人工）
> **执行流程规范**：详细定义见 ZT-2026-005_工作流程与约束规则.md 第三章
> **交付物路径规范**：详细定义见 ZT-2026-007_交付物路径规范.md
> **决策记录规范**：详细定义见 TASK-CARD-DECISION-FIELD-SPEC-v1.0.md
> **Issue Ticket 规范**：详细定义见 ZT-P008-T02-D03_issue-ticket类型规范_v1.0.md

---

## ── Zone A：任务定义（创建时填写，基本不变）──────────────

## 一、Task 基本信息

| 字段 | 内容 |
|---|---|
| **Task ID** | [TASK_ID] ← 命名规范：`[TOPIC_ID]-T[序号]`，如 `NUC-01-TP01-T01` |
| **Task 标题** | [TASK_TITLE] |
| **任务类型** | 🔧 系统级 / 📋 常规任务 / 🔄 周期性任务 / 🚨 应急任务 / ⚡ 一次性任务 / 🎫 issue-ticket |
| **归属 Topic** | [TOPIC_ID] · [TOPIC_NAME] |
| **归属 Project** | [PROJECT_ID] · [PROJECT_NAME] |
| **Task PIC** | [AGENT_NAME] |
| **提出人** | [PROPOSER] ← Issue Ticket 必填：问题发现者/报告人（如：Harold / 日常巡检 / Agent） |
| **指派人** | [ASSIGNER] ← 委托任务必填：分派任务的人（如：Harold / 银月 / Agent） |
| **优先级** | P0 / P1 / P2 / P3 |
| **Review 级别** | L0 / L1 / L2 / L3 ← 默认 **L2**；L0=免审，L1=异常上报，L2=抽样核查，L3=全量人工（Harold 必须介入）；有授权填写 `DA-[编号]` |
| **Review 时间窗口** | [留空=默认 24h] ← L3 任务超时规则依赖此字段；如需覆盖请填写，如 `48h`、`2 business days` |
| **创建时间** | [CREATED_AT] |
| **最后更新** | [LAST_UPDATED] |
| **截止日期** | [DUE_DATE] |
| **Story Points** | [POINTS] ← 工作量估算（1/2/3/5/8/13/21） |

> **Issue Ticket 专用字段**（任务类型 = 🎫 issue-ticket 时必填）：
> - **提出时间**：[PROPOSED_AT]
> - **提出渠道**：[CHANNEL] ← Harold 发现 / 日常巡检 / 客户反馈 / Agent 自检
> - **问题严重性**：🔴 P0 / 🟠 P1 / 🟡 P2 / 🟢 P3
> - **关闭条件**：[明确的关闭标准]
> - **子任务**：[测试 Task ID / 抽查 Task ID]
> - **提出人跟踪**：✅ 需要通知提出人（创建/接收/完成/关闭） / ❌ 不需要

> **委托任务专用字段**（任务类型 = 委托任务时必填）：
> - **指派时间**：[ASSIGNED_AT]
> - **指派原因**：[REASON] ← 为什么委托给这个 Agent
> - **指派人跟踪**：✅ 需要通知指派人（创建/接收/完成） / ❌ 不需要

> **周期性任务专用字段**（任务类型 = 🔄 周期性任务时必填）：
> - **部署状态**：`[x]` 完成 / `[?]` 阻塞 / `[!]` 待决
> - **运行状态**：🟢 运行中 / 🟡 暂停 / 🔴 异常 / ⬜ 未启动

---

## 二、Task 描述

### 2.1 任务目标
> 本 Task 要完成什么？一句话说清楚。

[TASK_GOAL]

### 2.2 背景说明
> 为什么需要这个 Task？来自哪里的需求？

[TASK_BACKGROUND]

---

## 三、输入物（Inputs）

> 完成本 Task 所需的具体材料、信息或前置条件。

| 输入物 | 类型 | 来源 | 状态 |
|---|---|---|---|
| [INPUT_1] | 文件 / 数据 / 前置 Task 输出 / Harold 决策 | [SOURCE 或 TASK_ID] | ✅ 已就绪 / ⚠️ 待准备 |
| [INPUT_2] | — | — | — |

---

## 四、Deliverable 定义

> 本 Task 的所有交付物，以及每项交付物的验收标准和 Review 级别。
> **此章节是 `determine_review()` 的唯一读取源**，不在其他位置重复定义。
>
> **交付物根目录**：`10_Projects/[PROJECT_ID]/[TOPIC_ID]/deliverables/`
>
> **Review 级别说明**：L0=免审 / L1=异常上报 / L2=抽样核查 / L3=全量人工（Harold 必须介入）
> 单项 Review 级别覆盖任务级默认值（§一）；为空则继承 §一 Review 级别。
>
> **状态标记与 Review 流转规则**：
> | Review 级别 | Task PIC 操作 | 银月操作 | Harold 操作 |
> |---|---|---|---|
> | **L0** | 完成后银月直接验收 | 验收通过后改 `[x]` | 不介入 |
> | **L1** | 完成后标记 `[V]`；有疑虑标记 `[!?]` | 判断是否上报 Harold | 仅异常上报时介入 |
> | **L2** | 完成后标记 `[V]` | 抽样（20-30%）；抽中标记 `[!]` 进七区；未抽中直接流转 `[V]` | 抽中时审阅 |
> | **L3** | 完成后标记 `[!]` | 录入 MISSION BOARD 七区 | 全量审阅，必须介入 |

| 序号 | Deliverable | 文件名 | 格式 | Review 级别 | 验收标准 | 状态 |
|---|---|---|---|---|---|---|
| 1 | [DELIVERABLE_1] | [FILENAME_1] | .md / .pdf / 代码 / 其他 | L0 / L1 / L2 / L3 | [ACCEPTANCE_CRITERIA] | ⬜ / 🟡 / ✅ |
| 2 | [DELIVERABLE_2] | [FILENAME_2] | — | — | — | ⬜ |

---

## 五、执行计划

> 步骤骨架，定义"做什么"；执行细节和过程记录见 Zone B §七。
> **详细执行流程规范见 ZT-2026-005_工作流程与约束规则.md 第三章**

| 步骤 | 操作 | 执行人 | 状态 |
|---|---|---|---|
| Step 1 | [ACTION_1] | [PIC] | ⬜ / 🟡 / ✅ |
| Step 2 | [ACTION_2] | [PIC] | ⬜ / 🟡 / ✅ |
| Step 3 | [ACTION_3] | [PIC] | ⬜ / 🟡 / ✅ |
| Step N | **DL 检索**：执行前检索 HAROLD-DECISION-LIBRARY，命中引用 `DL-[编号]`，未命中标记 `[!]` 请求裁定 | [PIC] | ⬜ / ✅ |
| **Step 终** | **状态同步**：按 ZT-2026-005 规范更新 MISSION BOARD，标记正确状态 | [PIC] | ⬜ / ✅ |

> `Step N` = 最后一个业务步骤之后、Step 终之前，填写时替换为实际步骤编号。

---

## 六、Context Refs 与关键依赖

### 6.1 上下文加载清单

> Agent 执行本 Task 时，HEARTBEAT Step 0 Scope Declaration 需加载的文件列表。
> 按加载优先级排序，从高到低。

| 优先级 | 文件 | 路径 | 说明 |
|---|---|---|---|
| 1 | SOUL.md | `${OPENCLAW_LOCAL_WORKSPACE}/SOUL.md` | 价值观与行为准则 |
| 2 | IDENTITY.md | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/{agent-id}/IDENTITY.md` | Agent 角色定义 |
| 3 | HAROLD-DECISION-LIBRARY.md | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/decisions/HAROLD-DECISION-LIBRARY-规范.md` | Harold 决策偏好库，执行前必查 |
| 4 | HAROLD-DELEGATION.md | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/frameworks/HAROLD-DELEGATION.md` | 确认本 Task 的 Review 级别授权 |
| 5 | PROJECT-CHARTER.md | `../../../PROJECT-CHARTER.md` | 项目目标与范围 |
| 6 | TOPIC-BRIEF.md | `../../TOPIC-BRIEF.md` | 专题目标与依赖 |
| 7 | [附加文件 1] | [PATH] | [说明] |
| 8 | [附加文件 2] | [PATH] | [说明] |

### 6.2 关键依赖

| 依赖类型 | 依赖对象 | 说明 | 状态 |
|---|---|---|---|
| **前置 Task** | [TASK_ID] | 需要该 Task 完成后才能启动 | ✅ 已完成 / ⚠️ 进行中 |
| **并行 Task** | [TASK_ID] | 需要信息同步 | — |
| **Harold 决策** | [DECISION_TOPIC] | 需要 Harold 先决策 [内容] | ✅ 已决策 / `[!]` 待决策 |
| **Decision Library** | DL-[编号] | 本 Task 执行依据的已有决策条目 | ✅ 已命中 / ⚠️ 未命中 |

---

## ── Zone B：运行时状态（执行中更新）────────────────────

## 七、状态与执行记录

### 7.1 当前状态

| 字段 | 内容 |
|---|---|
| **状态标记** | `[ ]` 待接收 / `[P]` 执行中 / `[V]` 待验收 / `[x]` 已完成 / `[?]` 阻塞 / `[!]` Harold 待决 |
| **当前状态值** | [填写当前状态标记] |
| **PDCA 断点** | null / plan / do / cqo_review / check / act ← v3.2 新增，heartbeat 断点续传依据 |
| **CQO 审核状态** | null / pending / pass / revise / reject ← v3.2 新增，合规闸门审核结果 |
| **阻塞原因** | [BLOCKING_REASON] ← 状态为 `[?]` 时必填 |
| **阻塞于** | [BLOCKED_BY] ← 状态为 `[?]` 时必填（前置 Task ID 或外部依赖） |
| **经验回流** | null / `LL-{YYYY-MM-DD}.md` ← v3.2 新增，已触发的 lesson learned 路径 |
| **MISSION BOARD 同步** | ✅ 已同步 / ⚠️ 待同步 |

> **状态流转**：`[ ]` → `[P]` → `[V]` → `[x]`
> Issue Ticket 在 `[P]` 阶段内细化：`[A]` 分析中 → `[F]` 修复中 → `[T]` 待测试 → `[TT]` 测试中 → `[Q]` 待抽查 → `[QQ]` 抽查中 → `[C]` 待关闭 → `[x]`

### 7.2 执行记录

> 记录执行过程中的关键事件。超过 20 条后将旧记录归档至 `executions/[TASK_ID]-log.jsonl`，此处保留最新 20 条。

| 日期 | 记录类型 | 内容 | 记录人 |
|---|---|---|---|
| [DATE] | 接收 `[P]` | Task 开始执行，Review 级别确认为 [Lx]，依据 [DA-编号 或「默认规则」] | [PIC] |
| [DATE] | DL 命中 | 引用 DL-[编号]：[简述决策内容] | [PIC] |
| [DATE] | DL 未命中 | 场景：[描述]，标记 `[!]` 请求 Harold 裁定 | [PIC] |
| [DATE] | 阻塞 `[?]` | [BLOCKING_ISSUE] | [PIC] |
| [DATE] | 解除阻塞 | [RESOLUTION] | [PIC] |
| [DATE] | 提交 `[V]` | 交付物已提交，等待验收 | [PIC] |

---

## 八、Harold 介入记录

> 记录本 Task 生命周期内所有 Harold 介入事件，包括 Deliverable Review 和过程决策。
> **L0 任务无需填写本章节。**
> **Review 流程与闭环规则**：详细定义见 ZT-2026-005_工作流程与约束规则.md 第六章
> **决策记录规范**：详细定义见 TASK-CARD-DECISION-FIELD-SPEC-v1.0.md

### 8.1 Deliverable Review 记录

> 记录 Harold 对 Deliverable 的验收结论（pass / 需修订）。
> 不记录具体决策内容——决策内容见 §8.2。
> L1 仅在异常上报（标记 `[!?]` 后银月判断上报）时填写；L2 仅在抽中时填写。

| Deliverable | Review 级别 | 提交时间 | Harold 意见 | 修订版本 | 最终状态 |
|---|---|---|---|---|---|
| [DELIVERABLE] | L1 / L2 / L3 | [DATETIME] | [FEEDBACK] | v[N] | ✅ 通过 / 🔄 需修订 |

### 8.2 Harold Decision 记录

> 记录 Harold 在本 Task 过程中做出的所有裁定/决策，包括 Review 过程中产生的决策。
> 每次 Harold 做出决策后，Task PIC 必须在 24 小时内记录。

#### 决策列表

| Decision ID | Type | Content | Timestamp | Source | DL Status |
|---|---|---|---|---|---|
| DEC-[TASK_ID]-001 | [Type] | [决策内容摘要] | [DATETIME] | [Source] | ⏳ 待提取 / ✅ 已提取 (DL-XXX) / ❌ 不适用 |

#### 决策详情

**DEC-[TASK_ID]-001**

| 字段 | 内容 |
|---|---|
| **Decision ID** | DEC-[TASK_ID]-001 |
| **Decision Type** | ✅ Approve / ❌ Reject / 🔄 Revise / ⏸️ Defer |
| **Decision Content** | [Harold 的具体决策内容，一字不差记录] |
| **Decision Timestamp** | [YYYY-MM-DD HH:MM] |
| **Decision Source** | Feishu Group / sessions_send / Email / 其他 |
| **Decision Context** | [简要说明决策背景，可选] |
| **Applicability Check** | [判断是否可提取到 DL，填写适用场景摘要或不适用原因] |
| **DL Extraction Status** | ⏳ 待提取 / ✅ 已提取 (DL-XXX) / ❌ 不适用提取 |

---

## ── Zone C：后处理（关闭后异步完成，不阻塞关闭）────────

## 九、知识沉淀

> **触发时机**：Task 状态标记改为 `[x]`（关闭）后进入后处理队列。
> **宽限期**：关闭后 **3 个工作日**内完成。
> **核查节奏**：银月 **Weekly Review** 中核查（非 daily heartbeat），超期未完成时提醒。
> **归档阻塞**：未完成知识沉淀的 Task 不进入 **[archived]** 状态，但不影响 `[x]` 关闭标记。
> **LL 条目说明**：LL 条目记录"What didn't work"，路径格式：`knowledge/LL-[YYYY-MM-DD].md`

| 字段 | 内容 |
|---|---|
| **沉淀状态** | ⏳ pending（Task 关闭后自动设置）/ ✅ completed |
| **沉淀类型** | 方法论 / 决策记录 / 技术方案 / 经验教训 |
| **是否需要新增 DL 条目** | ✅ 是，已起草 DL 草稿 / ❌ 否 |
| **DL 草稿编号**（如有） | DL-草稿-[TASK_ID] |
| **LL 条目路径**（如有） | `knowledge/LL-[YYYY-MM-DD].md` |
| **Wiki 文件名** | `WIKI-[TASK_ID]-[关键词].md` |
| **Wiki 路径** | `${OPENCLAW_LOCAL_WORKSPACE}/30_Resources/Wiki/` |
| **沉淀摘要** | [SUMMARY] |
| **沉淀完成时间** | [DATETIME] |
| **银月核查状态** | ⚠️ 待核查 / ✅ 已核查 |

---

## 版本变更记录

| 版本 | 日期 | 变更类型 | 变更内容 | 状态 |
|---|---|---|---|---|
| **v3.2** | 2026-05-06 | 增强 | ① §七 7.1 新增「PDCA 断点」字段（heartbeat 断点续传依据）；② 新增「CQO 审核状态」字段（合规闸门审核结果）；③ 新增「经验回流」字段（lesson learned 路径记录） | ✅ 发布 |
| **v3.1** | 2026-04-08 | 补充 + 对齐 | ① §七 7.1 补充 `[ ]` 待接收 / `[P]` 执行中，与 governance-task 状态体系对齐；② 声明块补充通用状态完整枚举和 Issue Ticket 子状态枚举；③ 7.1 新增「当前状态值」填写行和状态流转说明；④ 7.2 执行记录补充「接收」「提交」两种示例行；⑤ §八.1 Review 级别枚举由 `L3/L2/L1` 改为 `L1/L2/L3`（对齐方案 A：L0→L3 升序） | ✅ 发布 |
| **v3.0** | 2026-04-07 | 大版本重构 | 三区分层（Zone A / Zone B / Zone C）；§一瘦身；§四 Deliverable 升级为唯一真相源；知识沉淀改为后处理；Review 级别默认值改为 L2，枚举顺序改为 L0→L3 | ✅ |
| **v2.7** | 2026-04-07 | 优化调整 | 删除「预计耗时」字段 | ✅ |
| **v2.6** | 2026-04-07 | 重要修复 | 新增「阻塞原因」「风险等级」字段 | ✅ |
| **v2.5** | 2026-04-07 | 重要补充 | 新增「Story Points」「检查清单」章节 | ✅ |
| **v2.4** | 2026-04-07 | 重要补充 | 新增「提出人」「指派人」字段 | ✅ |
| **v2.3** | 2026-04-07 | 大版本升级 | 新增 issue-ticket 类型支持 | ✅ |
| v2.2 | 2026-03-13 | 小版本升级 | 新增「Harold Decision 记录」章节 | ✅ |
| v2.1 | 2026-03-13 | 小版本升级 | 新增「部署状态」「运行状态」字段 | ✅ |
| v2.0 | 2026-03-03 | 大版本升级 | 新增 Review 反馈与 DL 提取相关章节 | ✅ |
| v1.2 | 2026-03-03 | 小版本升级 | 新增状态同步闭环四步骤 | ✅ |
| v1.1 | 2026-02-24 | 小版本升级 | 新增 Review 级别字段和 DL 检索 | ✅ |
| v1.0 | 2026-02-24 | 初始版本 | 基础 TASK-CARD 模板 | ✅ |

---

- **Version**：v3.2
- **Created At**：2026-02-24
- **Last Updated**：2026-04-08
- **Approved By**：Harold Tsui

*本文件由 Task PIC 维护，Topic PIC 审核，银月监督知识沉淀与 DL 条目起草完成。每个决策都被记录、可追溯、可复用。*