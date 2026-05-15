---
title: CQO 合规闸门 revise 流程测试
tags: [testing, cqo, revise]
type: task
id: N4-P1-T12-T03
status: completed
owner: cqo
topic: N4-P1-T12
project: ZT-P015
priority: P1
privacy: P2
review_level: L1
task_type: regular
deliverables:
  - CQO-REVISE-FLOW-REPORT-N4-P1-T12-T03.md
created: 2026-05-08
updated: 2026-05-08
due: 2026-05-10
related_tasks: []
---
# TASK-CARD · CQO 合规闸门 revise 流程测试

> **文件性质**：Task 层上下文定义文件
> **存放路径**：`10_Projects/ZT-P015_NUCLEUS-4-0/topics/N4-P1-T12-CQO-TEST/tasks/TASK-CARD-N4-P1-T12-T03.md`
> **读写权限**：张铁 (cqo) 可写；银月可读写；Harold 可读
> **版本**：v3.2

---

## 声明

> **状态标记含义**：`[ ]` 待接收 / `[P]` 执行中 / `[V]` 待验收 / `[x]` 已完成
> **Review 级别**：L1（银月 Review）

---

## ── Zone A：任务定义 ──────────────

## 一、Task 基本信息

| 字段 | 内容 |
|---|---|
| **Task ID** | N4-P1-T12-T03 |
| **Task 标题** | CQO 合规闸门 revise 流程测试 |
| **任务类型** | 📋 常规任务 |
| **归属 Topic** | N4-P1-T12 · CQO 合规闸门集成测试 |
| **归属 Project** | ZT-P015 · NUCLEUS 4.0 |
| **Task PIC** | 张铁 (cqo) |
| **优先级** | P1 |
| **Review 级别** | L1 |
| **创建时间** | 2026-05-08 |
| **截止日期** | 2026-05-10 |

## 二、Task 描述

### 2.1 任务目标
验证 CQO 合规闸门 revise 流程：Do → CQO Review(revise) → 回到 Do → 修改交付物 → 再 CQO Review(pass) → Check → Act

### 2.2 背景说明
v8.1 CQO 闸门的 revise 机制是核心安全网——当交付物不合规时，应退回 Do 阶段修改后重新提交，而非直接进入 Check。需要验证 revise_count 正确递增、phase 正确退回 do、修改后能正常推进。

## 三、输入物

| 输入物 | 类型 | 来源 | 状态 |
|---|---|---|---|
| pdca.py v4.1.0 源码 | 代码 | scripts/pdca.py | ✅ 已就绪 |
| CQO 单元测试 (revise 场景) | 测试 | tests/test_pdca.py (TestCQOReview) | ✅ 已就绪 |
| CQO 集成测试 (revise 场景) | 测试 | tests/test_cqo_integration.py (TestCQOIntegrationReviseFlow) | ✅ 已就绪 |
| SKILL.md v9.0.0 协议 | 文档 | heartbeat SKILL.md | ✅ 已就绪 |

## 四、Deliverable 定义

| 序号 | Deliverable | 文件名 | 格式 | Review 级别 | 验收标准 | 状态 |
|---|---|---|---|---|---|---|
| 1 | revise流程测试报告 | CQO-REVISE-FLOW-REPORT-N4-P1-T12-T03.md | .md | L1 | 使用 TMPL-REVIEW 模板；记录 revise→回 Do→修改→再 CQO pass 的完整过程；revise_count 验证；frontmatter 完整 | ✅ |

## 五、执行计划

| 步骤 | 操作 | 执行人 | 状态 |
|---|---|---|---|
| Step 1 | 运行 CQO revise 相关单元测试，收集结果 | 张铁 (cqo) | ✅ |
| Step 2 | 运行 CQO revise 集成测试，收集结果 | 张铁 (cqo) | ✅ |
| Step 3 | 模拟 revise 流程：调用 pdca.py cqo-review --result revise，验证 phase 退回 do | 张铁 (cqo) | ✅ |
| Step 4 | 模拟修改后重新提交：再次 Do → CQO Review(pass) | 张铁 (cqo) | ✅ |
| Step 5 | 使用 TMPL-REVIEW 模板撰写 revise 流程测试报告 | 张铁 (cqo) | ✅ |
| Step 6 | 状态同步：更新 MISSION_BOARD | 张铁 (cqo) | ✅ |

## 六、Context Refs

| 优先级 | 文件 | 路径 | 说明 |
|---|---|---|---|
| 1 | SKILL.md | skills/openclaw-governance-heartbeat/SKILL.md | PDCA 执行协议 v9.0 |
| 2 | pdca-harness.md | skills/openclaw-governance-nucleus/references/pdca-harness.md | CQO Review 详细协议 |
| 3 | TMPL-REVIEW | skills/openclaw-governance-quality/templates/TMPL-REVIEW-审查报告.md | 审查报告模板 |

---

## ── Zone B：运行时状态 ──────────────

## 七、状态与执行记录

### 7.1 当前状态

| 字段 | 内容 |
|---|---|
| **状态标记** | `[x]` 已完成 |
| **当前状态值** | `[x]` |
| **PDCA 断点** | null |
| **CQO 审核状态** | pass (revise_count=1) |
| **阻塞原因** | — |
| **经验回流** | null |
| **MISSION BOARD 同步** | ✅ 已同步 |

### 7.2 执行记录

| 日期 | 记录类型 | 内容 | 记录人 |
|---|---|---|---|
| 2026-05-08 | 创建 | Task-CARD 创建 | 银月 |
| 2026-05-08 | Do(初次) | 运行revise测试(4/4 pass)，产出不合规交付物(缺frontmatter/模板) | 张铁 |
| 2026-05-08 | CQO Review | revise (CQO-01|CQO-02|CQO-04)，phase退回do，revise_count=1 | 张铁 |
| 2026-05-08 | Do(修改后) | 按revise反馈修复交付物，再次completed | 张铁 |
| 2026-05-08 | CQO Review(2nd) | pass，phase=check，revise_count=1 | 张铁 |
| 2026-05-08 | Check | L1 pass, evidence: §4.1-§4.4全pass | 张铁 |
| 2026-05-08 | Act | 完成, next_task=N4-P1-T12-T04 | 张铁 |
