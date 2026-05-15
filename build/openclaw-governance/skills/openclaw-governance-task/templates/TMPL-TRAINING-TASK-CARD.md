| col1 | col2 | col3 |
| ---- | ---- | ---- |
|      |      |      |
|      |      |      |

# TASK-CARD ·-TRAINING-001

> **文件性质**：Sub Agent 持续培训专用 Task Card
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/AGENT-TP02/tasks/TASK-CARD-{agent_id}-TRAINING-001.md`
> **模板来源**：`${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/templates/TMPL-TRAINING-TASK-CARD.md`
> **版本**：v1.0

---

## 一、Task 基本信息

| 字段                   | 内容                                     |
| ---------------------- | ---------------------------------------- |
| **Task ID**      | {agent_id}-TRAINING-001                  |
| **Task 标题**    | {agent_name} Agent 持续培训              |
| **归属 Topic**   | AGENT-TP02 · Agent Training 管理        |
| **归属 Project** | AGENT-RESOURCE · Agent 资源管理中心     |
| **Task PIC**     | 银月                                     |
| **优先级**       | P2                                       |
| **Review 级别**  | L1                                       |
| **状态标记**     | `[ ]` → `[V]` → `[~]` → `[x]` |
| **创建时间**     | {created_at}                             |
| **计划完成日期** | {planned_completion}                     |
| **实际完成日期** | —                                       |

---

## 二、Task 目标与验收标准

### 2.1 目标陈述

当 TMPL-IDENTITY-SUB.md、TMPL-SOUL-SUB.md 等核心模板更新时，对单个或多个 Agent 进行升级培训，确保 Agent 掌握最新规范和要求。

### 2.2 培训类型

| 类型               | 触发场景                                               | 频率 |
| ------------------ | ------------------------------------------------------ | ---- |
| **模板升级** | TMPL-IDENTITY-SUB.md / TMPL-SOUL-SUB.md 等核心模板更新 | 按需 |
| **技能升级** | 新工具/新流程引入                                      | 按需 |
| **能力补强** | 绩效评估发现短板                                       | 季度 |
| **合规培训** | 规则/政策更新                                          | 按需 |
| **跨域拓展** | 业务需要新领域知识                                     | 按需 |

### 2.3 验收标准

| # | 验收标准     | 交付物                           | Review 级别 |
| - | ------------ | -------------------------------- | ----------- |
| 1 | 培训需求识别 | `TRAINING-NEEDS-{agent_id}.md` | L1          |
| 2 | 培训计划制定 | `TRAINING-PLAN-{agent_id}.md`  | L1          |
| 3 | 培训执行记录 | `TRAINING-LOG-{agent_id}.md`   | L1          |
| 4 | 能力提升确认 | 评估结果                         | L1          |

---

## 三、执行步骤

```
Step 1: 培训需求识别（预计 30min）
  □ 分析 Agent 当前能力水平
  □ 识别与目标能力的差距
  □ 收集银月/其他 Agent 的反馈
  → Step 2

Step 2: 培训计划制定（预计 30min）
  □ 制定培训内容和大纲
  □ 安排培训时间和方式
  □ 确定评估标准
  → Step 3

Step 3: 培训执行（预计 1-2h）
  □ 提供学习资料（Wiki/Docs）
  □ Agent 自主学习
  □ 必要时进行模拟测试
  → Step 4

Step 4: 能力评估（预计 30min）
  □ 验证学习成果
  □ 确认能力提升
  □ 记录评估结果
  → 归档
```

---

## 四、Deliverable 列表

| # | Deliverable  | 类型     | 路径                                                                                                                                           | Review 级别 | 状态 |
| - | ------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ---- |
| 1 | 培训需求识别 | Markdown | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/AGENT-TP02/tasks/{task_id}/deliverables/TRAINING-NEEDS-{agent_id}.md` | L1          | ⬜   |
| 2 | 培训计划     | Markdown | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/AGENT-TP02/tasks/{task_id}/deliverables/TRAINING-PLAN-{agent_id}.md`  | L1          | ⬜   |
| 3 | 培训执行记录 | Markdown | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/AGENT-TP02/tasks/{task_id}/deliverables/TRAINING-LOG-{agent_id}.md`   | L1          | ⬜   |
| 4 | 能力评估确认 | 文本     | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/AGENT-TP02/tasks/{task_id}/deliverables/TRAINING-EVAL-{agent_id}.md`   | L1          | ⬜   |

---

## 五、培训资源

| 资源类型    | 来源                                 | 说明           |
| ----------- | ------------------------------------ | -------------- |
| 知识库 Wiki | 20_Knowledge/                        | Agent 专属知识 |
| 治理规范    | `skills/openclaw-governance/skills/*/policies/` 及 `standards/` | 规则文档       |
| 案例库      | LESSON-LEARN/                        | 经验教训       |
| DL 条目     | HAROLD-DECISION-LIBRARY/             | Harold 偏好    |

---

## 六、执行记录

| 时间         | 动作      | 结果                         | 备注     |
| ------------ | --------- | ---------------------------- | -------- |
| {created_at} | Task 创建 | 启动 {agent_id}-TRAINING-001 | 银月创建 |

---

## 七、验收记录

| 字段                   | 内容      |
| ---------------------- | --------- |
| **提交验收时间** | —        |
| **提交人**       | 银月      |
| **验收人**       | 银月      |
| **验收结果**     | ⬜ 待验收 |

### 评估说明

> （银月填写能力评估结果）

---

## 八、状态历史

| 日期         | 状态变更     | 变更原因               | 记录人 |
| ------------ | ------------ | ---------------------- | ------ |
| {created_at} | `[ ]` 创建 | 银月创建 Training Task | 银月   |

---

## 版本信息

- **Version**: v1.0
- **Created At**: {created_at}
- **Approved By**: （银月审批）
- **Status**: Draft

*本 Task Card 由银月基于 TMPL-TRAINING-TASK-CARD 模板创建。*
