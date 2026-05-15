---
title: "[TASK_ID] CQO 合规审核报告"
tags: [cqo, compliance, review]
type: cqo-compliance-report
id: CQO-[TASK_ID]-[TIMESTAMP]
status: draft
owner: cqo
task_id: [TASK_ID]
project_id: [PROJECT_ID]
topic_id: [TOPIC_ID]
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
---
# CQO 合规审核报告 · [TASK_ID]

> **文件性质**：CQO 合规审核结果记录
> **存放路径**：`10_Projects/{PROJECT_ID}/{TOPIC_ID}/deliverables/CQO-{TASK_ID}-{TIMESTAMP}.md`
> **读写权限**：CQO 可写；银月、原 Agent 可读
> **版本**：v1.0

---

## 审核概要

| 字段 | 内容 |
|------|------|
| **Task ID** | [TASK_ID] |
| **Task 标题** | [TASK_TITLE] |
| **原执行 Agent** | [AGENT_ID] |
| **交付物路径** | [DELIVERABLE_PATH] |
| **审核时间** | [TIMESTAMP] |
| **审核结果** | pass / revise / reject |

---

## 审核项

| 编号 | 审核项 | 结果 | 说明 |
|------|--------|------|------|
| CQO-01 | 模板匹配 | ✅/❌ | 交付物是否使用正确模板 |
| CQO-02 | 元数据完整 | ✅/❌ | frontmatter 必填字段齐全 |
| CQO-03 | 路径规范 | ✅/❌ | 存放路径符合 ZT-2026-007 |
| CQO-04 | 结构完整 | ✅/❌ | 章节结构符合规范 |
| CQO-05 | 格式合规 | ✅/❌ | 标记、表格、引用格式正确 |

---

## 详细说明

### CQO-01 模板匹配

- **期望模板**：[TMPL-NAME]
- **实际使用**：[ACTUAL_TEMPLATE / 未使用模板]
- **结果**：✅ 匹配 / ❌ 不匹配 — [说明]

### CQO-02 元数据完整

- **缺失字段**：[列出缺失的 frontmatter 字段]
- **结果**：✅ 完整 / ❌ 缺失 — [说明]

### CQO-03 路径规范

- **期望路径**：[EXPECTED_PATH]
- **实际路径**：[ACTUAL_PATH]
- **结果**：✅ 合规 / ❌ 不合规 — [说明]

### CQO-04 结构完整

- **缺失章节**：[列出缺失的章节]
- **结果**：✅ 完整 / ❌ 缺失 — [说明]

### CQO-05 格式合规

- **格式问题**：[列出格式不规范之处]
- **结果**：✅ 合规 / ⚠️ 轻微问题 / ❌ 不合规 — [说明]

---

## 修改建议（revise/reject 时填写）

> 仅在审核结果为 revise 或 reject 时填写。

| # | 建议内容 | 对应审核项 | 优先级 |
|---|---------|-----------|--------|
| 1 | [修改建议] | CQO-XX | 必须/建议 |

---

*版本: v1.0 | 创建: [YYYY-MM-DD] | 审核者: CQO 张铁*
