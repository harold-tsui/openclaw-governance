# TASK-CARD · {agent_id}-RETIRE-001

> **文件性质**：Sub Agent 退休/停用专用 Task Card
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/AGENT-TP01/tasks/TASK-CARD-{agent_id}-RETIRE-001.md`
> **模板来源**：`${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/template/TMPL-RETIRE-TASK-CARD.md`
> **版本**：v1.0

---

## 一、Task 基本信息

| 字段 | 内容 |
| --- | --- |
| **Task ID** | {agent_id}-RETIRE-001 |
| **Task 标题** | {agent_name} Agent 退休/停用 |
| **归属 Topic** | AGENT-TP03 · Agent Retire 管理 |
| **归属 Project** | AGENT-RESOURCE · Agent 资源管理中心 |
| **Task PIC** | 银月 |
| **优先级** | P1 |
| **Review 级别** | L3（需 Harold 最终批准） |
| **状态标记** | `[ ]` → `[V]` → `[~]` → `[x]` |
| **创建时间** | {created_at} |
| **计划完成日期** | {planned_completion} |
| **实际完成日期** | — |

---

## 二、Task 目标与验收标准

### 2.1 目标陈述
完成 {agent_name} 的有序退出，确保知识资产完整交接，工作无缝衔接。

### 2.2 验收标准

| # | 验收标准 | 交付物 | Review 级别 |
| --- | --- | --- | --- |
| 1 | 知识资产清单 | `RETIRE-KNOWLEDGE-{agent_id}.md` | L1 |
| 2 | 知识交接完成 | 知识文件转交确认 | L2 |
| 3 | 工作状态报告 | `RETIRE-STATUS-{agent_id}.md` | L2 |
| 4 | 资源清理完成 | 目录/权限清理确认 | L1 |
| 5 | persons.yaml 更新 | onboarding_status → retired | L2 |
| 6 | **Harold 批准** | 批准确认 | **L3** |

---

## 三、输入物（Inputs）

| 输入物 | 类型 | 来源 | 状态 |
| --- | --- | --- | --- |
| {agent_id} 完整工作目录 | 目录 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/{agent_id}/` | ⬜ 待盘点 |
| persons.yaml | 数据 | .system/master_data/ | ✅ 已就绪 |

---

## 四、执行步骤

```
Step 1: 知识资产盘点（预计 30min）
  □ 列出 {agent_name} 所有 Wiki 知识文件
  □ 识别需要交接的关键文档
  □ 输出：知识资产清单
  → Step 2

Step 2: 知识交接（预计 1h）
  □ 将知识文件迁移至知识库归档
  □ 或指定接手 Agent
  □ 确认交接完成
  → Step 3

Step 3: 工作状态盘点（预计 30min）
  □ 盘点当前进行中的任务
  □ 识别需要接手的任务
  □ 撰写工作状态报告
  → Step 4

Step 4: 资源清理（预计 30min）
  □ 清理工作目录（归档或删除）
  □ 清理临时文件
  □ 确认权限已回收
  → Step 5

Step 5: 状态更新
  □ 更新 persons.yaml 中 onboarding_status = retired
  □ 更新银月调度表，移除该 Agent
  → Step 6

Step 6: Harold 审批 ⭐
  □ 提交完整退出报告
  □ Harold Review（L3）
  □ 批准 / 驳回
```

---

## 五、Deliverable 列表

| # | Deliverable | 类型 | 路径 | Review 级别 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 1 | 知识资产清单 | Markdown | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/AGENT-TP01/tasks/{task_id}/deliverables/RETIRE-KNOWLEDGE-{agent_id}.md` | L1 | ⬜ |
| 2 | 知识交接确认 | 文本 | Task Card §六 | L2 | ⬜ |
| 3 | 工作状态报告 | Markdown | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/AGENT-TP01/tasks/{task_id}/deliverables/RETIRE-STATUS-{agent_id}.md` | L2 | ⬜ |
| 4 | 资源清理确认 | 文本 | Task Card §六 | L1 | ⬜ |
| 5 | persons.yaml 更新 | 数据 | .system/master_data/ | L2 | ⬜ |
| 6 | **Harold 批准确认** | 决策 | Task Card §六 | **L3** | ⬜ |

---

## 六、退休原因

> （银月填写原因）
> - [ ] 角色合并（合并到其他 Agent）
> - [ ] 功能停用（业务调整）
> - [ ] 性能不达标（多次警告后）
> - [ ] 严重违规（触发安全红线）
> - [ ] Harold 主动决策

---

## 七、执行记录

| 时间 | 动作 | 结果 | 备注 |
| --- | --- | --- | --- |
| {created_at} | Task 创建 | 启动 {agent_id}-RETIRE-001 | 银月创建 |

---

## 八、验收记录

| 字段 | 内容 |
| --- | --- |
| **提交验收时间** | — |
| **提交人** | 银月 |
| **验收人** | Harold 终审 |
| **验收结果** | ⬜ 待验收 |

### Harold 终审意见
> （Harold 填写）

---

## 九、状态历史

| 日期 | 状态变更 | 变更原因 | 记录人 |
| --- | --- | --- | --- |
| {created_at} | `[ ]` 创建 | 银月创建 Retire Task | 银月 |

---

## 版本信息

- **Version**: v1.0
- **Created At**: {created_at}
- **Approved By**: （待 Harold 确认后填写）
- **Status**: Draft

*本 Task Card 由银月基于 TMPL-RETIRE-TASK-CARD 模板创建。*