---
title: [PROJECT_NAME]
tags: []
type: project
id: [PROJECT_ID]
status: planning
owner: [AGENT_ID]
priority: [P0-P3]
start_date: [YYYY-MM-DD]
end_date: [YYYY-MM-DD]
privacy: [P0-P3]
related_projects: []
related_topics: []
aliases: []
description: [一句话描述]
---
# PROJECT-CHARTER · [PROJECT_NAME]

> **文件性质**：Project 层上下文定义文件
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/10_Projects/[PROJECT_ID]/PROJECT-CHARTER.md`
> **模板路径**：`${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/template/TMPL-PROJECT-CHARTER-项目章程模板.md`
> **读写权限**：PM 可写；银月可读写；Harold 可读
> **版本**：v1.5

---

## 一、Project 基本信息

| 字段 | 内容 |
|---|---|
| **Project ID** | [PROJECT_ID] ← 命名规范：`ZT-PXXX` |
| **Project 名称** | [PROJECT_NAME] |
| **PM（Project Manager）** | [AGENT_NAME 或 Harold] |
| **PMO** | 银月（固定） |
| **状态** | 🔵 Planning / 🟢 Active / 🟡 On Hold / ⚫ Closed |
| **章程 Review 状态** | ⚠️ 待 Harold Review / ✅ Harold 已通过 / 🔄 打回修订中 |
| **Harold 参与阶段** | 🔴 建立期 / 🟡 过渡期 / 🟢 巡航期 |
| **创建时间** | [CREATED_AT] |
| **最后更新** | [LAST_UPDATED] |
| **计划结束日期** | [END_DATE 或 持续运营] |

> ⚠️ **章程 Review 状态为「✅ Harold 已通过」之前，任何 Agent 不得投入实质性工作。**

---

## 二、Project 目标

### 2.1 目标陈述
[目标描述]

### 2.2 成功标准
| 序号 | 成功标准 | 衡量方式 |
|------|---------|---------|
| 1 | | |

### 2.3 范围边界
- **包含**：
- **不包含**：

---

## 三、输入物

| 输入物 | 类型 | 来源 | 状态 |
|--------|------|------|------|
| | | | ✅/⚠️ |

---

## 四、Topic 列表

| Topic ID | Topic 名称 | Topic PM | Review 级别 | 状态 | 文件路径 |
|----------|-----------|----------|-------------|------|----------|
| | | | L3/L2/L1/L0 | | |

**Topic 完成进度**：`✅ Done` / `全部 Topic 数`

---

## 五、参与人员

| 角色 | 姓名 / Agent | 职责 |
|------|-------------|------|
| PM | | |
| PMO | 银月 | 跨 Topic 协调、进度监控、状态冒泡 |
| Topic PM | | |
| Harold | | 战略确认、章程 Review、关闭裁定 |

---

## 六、Harold Review 节点

| 里程碑 | 触发条件 | Review 内容 | 级别 | 预计时间 | 状态 |
|---------|----------|-------------|------|----------|------|
| 章程 Review | PM 提交 | 目标、规划、资源、Topic 拆解 | L3 | | |
| | | | | | |

---

## 七、Harold 参与度策略

> 详见：`${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/frameworks/HAROLD-DECISION-LIBRARY-规范.md`

| 阶段 | 标志 | 默认 Review 级别 |
|------|------|-----------------|
| 🔴 建立期 | 初始状态 | L3 全量 |
| 🟡 过渡期 | DL ≥ 3条，无重大偏差 | L2 抽样 |
| 🟢 巡航期 | 已获授权 | L1/L0 免审 |

**当前阶段**：🔴 建立期

---

## 八、执行流程与状态同步

> 本章节仅包含 Project 层特有流程。Task/Review/知识沉淀等流程在 Topic/Task 层处理。

### 8.1 Project 生命周期流程

| 流程 | 引用文档 | 说明 |
|------|----------|------|
| **Project 创建** | `PROJECT-CREATION-SOP.md` | 从提案到章程Review的完整流程 |
| **Project 关闭** | 本 §八.2 | 所有 Topic 完成后的关闭流程 |
| **状态变更** | `ZT-2026-005_工作流程与约束规则.md` | 状态标记含义与变更规则 |

### 8.2 Project 关闭流程

```
全部 Topic Done
    ↓
银月出具完成汇报
    ↓
Harold 审阅
    ↓
Harold 决策：确认关闭 / 要求补充 / 转为持续运营
```

### 8.3 状态同步规则（Topic → Project 冒泡）

| 触发 | 银月动作 | 时限 |
|------|---------|------|
| Topic 状态变更 | 更新 Topic 列表 | 24h |
| Topic Blocked | 评估影响，必要时通知 Harold | 2h |
| Topic Done | 更新进度计数 | 4h |
| 全部 Done | 出具 Project 完成汇报 | 24h |

---

## 九、Project 特有流程入口

> 本章节用于 Project 根据实际情况补充特有流程。通用流程已在 §八 或 Topic/Task 层处理。

| 流程名称 | 引用文档/位置 | 状态 | 说明 |
|----------|--------------|------|------|
| （待 Project 补充） | — | — | 本 Project 特有的执行流程在此填充 |

**示例填充方式**：
- 方式一：引用治理体系中的标准化文档
- 方式二：在本 Project 的 Topic/Task 中定义
- 方式三：创建本 Project 专用的 SOP 文档

---

## 十、关键依赖与风险

| 类型 | 描述 | 影响 | 应对 |
|------|------|------|------|
| 外部依赖 | | 高/中/低 | |
| 已知风险 | | 高/中/低 | |

---

## 十一、Project 完成汇报

> 模板见下方，完整内容在 Project 关闭时填写。

| 字段 | 内容 |
|------|------|
| 汇报时间 | |
| 目标达成情况 | |
| Topic 完成率 | |
| DL 新增条目数 | |
| 知识沉淀完成率 | |
| Harold 关闭决策 | ⚠️ 待决策 |

---

## 十二、状态历史

| 日期 | 状态 | 章程 Review | 阶段 | 变更原因 |
|------|------|-------------|------|----------|
| [DATE] | 🔵 Planning | ⚠️ 待 Review | 🔴 建立期 | 创建 |

---

## 版本信息

- **Version**: v1.5
- **Changes from v1.4**:
  - 合并 §八 + §十一，精简模板结构
  - §八 仅保留 Project 层特有流程（生命周期 + 状态同步）
  - 删除 §八.2-8.5（Task/Review/知识沉淀/阶段评估）→ 在 Topic/Task 层处理
  - §九 重命名为「Project 特有流程入口」，删除 §九.2 引用索引
  - 原章节重新编号（§十二→§十一，状态历史→§十二）
- **Created At**: 2026-02-24
- **Last Updated**: 2026-04-15
- **Approved By**: Harold Tsui

---

*本文件由 PM 维护，银月监督状态冒泡与阶段评估，Harold 审批章程、里程碑与 Project 关闭。*