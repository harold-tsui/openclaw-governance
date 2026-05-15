# TASK-CARD · N4-P1-T11-T02

> **文件性质**：Task 层上下文定义文件
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/10_Projects/ZT-P015_NUCLEUS-4-0/tasks/N4-P1-T11-T02_TASK-CARD.md`
> **上位文件**：`../topics/N4-P1-T11/TOPIC-BRIEF.md`
> **版本**：v3.1

---

## 声明

> **状态标记含义**：详细定义见 HEARTBEAT.md 附录 A
> **通用状态**：`[ ]` 待接收 / `[P]` 执行中 / `[V]` 待验收 / `[x]` 已完成 / `[?]` 阻塞 / `[!]` Harold 待决
> **Review 级别规则**：L0=免审 / L1=异常上报 / L2=抽样核查 / L3=全量人工

---

## ── Zone A：任务定义（创建时填写，基本不变）──────────────

## 一、Task 基本信息

| 字段 | 内容 |
|---|---|
| **Task ID** | N4-P1-T11-T02 |
| **Task 标题** | intelligence 能力完善 |
| **任务类型** | 🔧 能力建设 |
| **归属 Topic** | N4-P1-T11 · nucleus-abilities 开发 |
| **归属 Project** | ZT-P015_NUCLEUS-4-0 · NUCLEUS 4.0 |
| **Task PIC** | CTO (菡云芝) |
| **评审者** | CIO (元瑶) |
| **优先级** | P1 |
| **Review 级别** | L2 ← 抽样核查 |
| **创建时间** | 2026-04-20 |
| **截止日期** | 2026-05-04（Week 5） |
| **Story Points** | 8 |

---

## 二、Task 描述

### 2.1 任务目标
> 本 Task 要完成什么？一句话说清楚。

完成 nucleus-abilities-intelligence 模块的核心函数实现，支持竞品分析、市场调研、信息收集三大能力，并通过 CIO 评审和端到端验证。

### 2.2 背景说明
> 为什么需要这个 Task？来自哪里的需求？

来自 N4-P1-T11 Topic 的 Phase 2 规划。intelligence 能力是 CIO 元瑶的核心专业能力，需要实现情报调研、竞品分析等能力，为决策提供支持。

---

## 三、输入物（Inputs）

| 输入物 | 类型 | 来源 | 状态 |
|---|---|---|---|
| nucleus-abilities 框架 | 框架 | N4-P1-T11-T01 | ✅ 已完成 |
| intelligence 需求定义 | 文档 | topics/N4-P1-T11/ROADMAP.md | ✅ 已定义 |
| CIO 业务场景 | 输入 | CIO 提供 | ⏳ 待收集 |

---

## 四、Deliverable 定义

> **交付物根目录**：`10_Projects/ZT-P015_NUCLEUS-4-0/deliverables/N4-P1-T11-T02/`

| 序号 | Deliverable | 文件名 | 格式 | Review 级别 | 验收标准 | 状态 |
|---|---|---|---|---|---|---|
| 1 | 竞品分析函数 | skills/nucleus-abilities/intelligence/competitor_analysis.py | .py | L2 | 支持功能对比、优劣势分析、定价分析 | [ ] |
| 2 | 市场调研函数 | skills/nucleus-abilities/intelligence/market_research.py | .py | L2 | 支持行业趋势、用户画像、市场规模分析 | [ ] |
| 3 | 信息收集函数 | skills/nucleus-abilities/intelligence/info_collection.py | .py | L2 | 支持多源信息聚合、资料汇总 | [ ] |
| 4 | 技能注册配置 | skills/nucleus-abilities/skills-extension.yaml | .yaml | L2 | 关键词路由配置正确 | [ ] |
| 5 | 端到端测试报告 | deliverables/N4-P1-T11-T02/e2e_test_report.md | .md | L2 | CIO 评审通过，关键词触发正常 | [ ] |

---

## 五、执行计划

| 步骤 | 操作 | 执行人 | 预计 | 状态 |
|---|---|---|---|---|
| Step 1 | 收集 CIO 业务场景和需求 | CTO | 2h | [ ] |
| Step 2 | 设计竞品分析函数接口 | CTO | 3h | [ ] |
| Step 3 | 实现竞品分析函数 | CTO | 8h | [ ] |
| Step 4 | 设计市场调研函数接口 | CTO | 3h | [ ] |
| Step 5 | 实现市场调研函数 | CTO | 8h | [ ] |
| Step 6 | 设计信息收集函数接口 | CTO | 3h | [ ] |
| Step 7 | 实现信息收集函数 | CTO | 8h | [ ] |
| Step 8 | 更新 skills-extension.yaml | CTO | 2h | [ ] |
| Step 9 | 邀请 CIO 评审 | CTO | - | [ ] |
| Step 10 | 端到端测试验证 | CTO+CIO | 4h | [ ] |
| Step 终 | 状态同步 + 知识沉淀 | CTO | 2h | [ ] |

---

## 六、Context Refs 与关键依赖

### 6.1 上下文加载清单

| 优先级 | 文件 | 路径 | 说明 |
|---|---|---|---|
| 1 | SOUL.md | `${OPENCLAW_LOCAL_WORKSPACE}/SOUL.md` | 价值观与行为准则 |
| 2 | IDENTITY.md | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cto/IDENTITY.md` | CTO 角色定义 |
| 3 | TOPIC-BRIEF.md | `../topics/N4-P1-T11/TOPIC-BRIEF.md` | Topic 定义 |
| 4 | ROADMAP.md | `../topics/N4-P1-T11/ROADMAP.md` | 开发路线图 |
| 5 | skills-extension.yaml | `skills/nucleus-abilities/skills-extension.yaml` | 技能注册配置 |

---

## ── Zone B：运行时状态（执行中更新）────────────────────

## 七、状态与执行记录

### 7.1 当前状态

| 字段 | 内容 |
|---|---|
| **状态标记** | `[ ]` 待接收 |
| **当前状态值** | `[ ]` 待接收 |
| **阻塞原因** | - |
| **MISSION BOARD 同步** | ⏳ 待同步 |

### 7.2 执行记录

> 执行过程中更新，保留最新 20 条。

| 日期 | 记录类型 | 内容 | 记录人 |
|---|---|---|---|
| 2026-04-20 | 创建 `[ ]` | Task-CARD 创建完成，等待 CTO 接收 | 张铁 |

---

## ── Zone C：后处理（关闭后异步完成）────────────────────

## 八、知识沉淀

> **宽限期**：关闭后 3 个工作日内完成
> **核查节奏**：银月 Weekly Review 核查

| 字段 | 内容 |
|---|---|
| **知识沉淀内容** | - |
| **LL 条目** | - |
| **改进建议** | - |

---

## 九、归档信息

| 字段 | 内容 |
|---|---|
| **归档状态** | ⏳ 未归档 |
| **归档时间** | - |
| **归档位置** | - |

---

*版本：v3.1 | 创建：2026-04-20 | 负责人：CTO (菡云芝) | 状态：`[ ]` 待接收*
