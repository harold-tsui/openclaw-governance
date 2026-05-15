---
name: orchestrating-pipeline
description: |
  Orchestrating task execution pipelines with step sequencing, weight adaptation, and state management.
  
  Activates when: Task creation or execution, pipeline management needed
  
  Capabilities:
  - Pipeline step sequencing and orchestration
  - Weight adaptation for different task types
  - Pipeline state management and tracking
  - Integration with DOD and Review-gate checks
  
  Keywords: pipeline, orchestration, execution, workflow, state-management
  
  For detailed documentation, see:
  - references/pipeline-guide.md

author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "2.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L2"
  os: ["darwin", "linux"]
  owner: "main"
  tags: ["pipeline", "orchestration", "execution", "state-management", "10-step"]
---

# Governance Pipeline - 流水线编排 Skill

> **触发模式**：任务创建/执行时自动加载
> **v2.1.0**: 补充 When to Use / Pitfalls 章节

## 何时使用

- **Task execution**: 运行 10 步流水线（triage → archive）
- **Weight determination**: 根据自动化级别选择 lightweight/medium/heavyweight
- **Pipeline state management**: 检查进度、推进步骤、处理失败
- **Do NOT use for**: 审核执行（那是 `governance-quality`）或审核权限（那是 `governance-delegation`）

## 常见陷阱

1. **Pipeline 编排 vs Quality 执行 vs Delegation 判定**: Pipeline 决定何时审核，Quality 执行审核，Delegation 决定谁批准。不要混淆这些边界。
2. **权重决定步骤跳过**: Lightweight（L4-L5）跳过 Planning + 自动审批。Heavyweight（L2）不跳过任何步骤。启动前确保自动化级别映射到正确的权重。
3. **Review-Gate 对 L0-L3 是强制的**: L4 自动通过，L5 不需要。所有其他级别必须通过 Review-Gate（Step 8）。
4. **Pipeline 状态文件是 per-task 的**: `pipeline-state.json` 是任务特定的。不要在不同任务间复用状态。

---

## 一、核心定义

### 1.0 Review-Gate 职责边界

| Skill | 职责 | 关键问题 |
|-------|------|----------|
| **pipeline** | **编排** Review-Gate | "什么时候审查" |
| **quality** | **执行** Review-Gate | "审查什么" |
| **delegation** | **判定** Review-Gate | "谁能批准" |

**防自我认证**：DOD 创建者 ≠ DOD 验证者；任务执行者 ≠ 质量审查者。

### 1.1 流水线步骤（10-Step）

| Step | Name | Description |
|------|------|-------------|
| 1 | Triage | 任务分类 |
| 2 | Checkpoint | 会话恢复 |
| 3 | Context | 加载上下文 |
| 4 | Audit | 代码库审计 |
| 5 | Planning | 方案规划 |
| 6 | Approve | 门禁 |
| 7 | Execute | 构建 + 审查 |
| 8 | Review-Gate | 审查门禁 |
| 9 | Complete | 完成确认 |
| 10 | Archive | 归档 |

### 1.2 权重适配

| 权重 | 自动化级别 | 跳过步骤 | 自动审批 |
|------|-----------|----------|----------|
| **Lightweight** | L4-L5 | Planning | Approve |
| **Medium** | L3 | Planning | Approve |
| **Heavyweight** | L2 | 无 | 无 |
| **Strategic** | L0-L1 | 无 | 无 |

> 详细职责边界、步骤说明、权重适配：[references/pipeline-guide.md]({baseDir}/references/pipeline-guide.md)

---

## 二、核心函数（摘要）

### init_pipeline()
- **输入**：`{task_id, automation_level}`
- **处理**：确定权重 → 生成步骤 → 初始化状态 → 写入 pipeline-state.json
- **输出**：`{status, pipeline_id, weight, steps[], skipped[]}`

### advance_pipeline()
- **输入**：`{task_id, current_step}`
- **处理**：验证步骤 → 执行 → 更新状态 → 检查门禁
- **输出**：`{status, completed_step, next_step, pipeline_progress}`

### get_pipeline_status()
- **输入**：`{task_id}`
- **输出**：`{status, pipeline_id, weight, current_step, progress, steps[]}`

> 详细函数实现、输入/输出格式：[references/pipeline-guide.md]({baseDir}/references/pipeline-guide.md)

---

## 三、步骤函数（摘要）

| Step | 调用方 | 输出 |
|------|--------|------|
| Triage | governance-dispatch | `{task_type, automation_level, weight}` |
| Checkpoint | LLM session check | `{resumed, last_step, session_data}` |
| Context | LLM reads | `{context_tree, files_loaded}` |
| Audit | governance-quality.review() | `{audit_report, ground_truth}` |
| Planning | LLM planning | `{options[], recommended}` |
| Approve | governance-delegation.check_authorization() | `{approved, approver, approved_at}` |
| Execute | LLM execution | `{deliverables[], reviews[]}` |
| Review-Gate | governance-quality.validate_review_gate() | `{status, errors, warnings}` |
| Complete | governance-task.close_task() | `{completed, ll_template_generated}` |
| Archive | governance-knowledge.sync_to_feishu() | `{archived, knowledge_captured, feishu_synced}` |

> 详细步骤函数说明：[references/pipeline-guide.md]({baseDir}/references/pipeline-guide.md)

---

## 四、状态管理（摘要）

**状态文件**：`pipeline-state.json`

| 状态 | 说明 |
|------|------|
| pending | 待执行 |
| in_progress | 执行中 |
| completed | 已完成 |
| failed | 失败 |
| skipped | 已跳过 |

> 详细状态文件结构：[references/pipeline-guide.md]({baseDir}/references/pipeline-guide.md)

---

## 五、协作关系（摘要）

```
governance-pipeline (编排)
    ├── governance-dispatch (Triage)
    ├── governance-quality (Audit, Review-Gate)
    ├── governance-delegation (Approve)
    ├── governance-task (Planning, Execute)
    ├── governance-knowledge (Archive)
    └── governance-hierarchy (Complete)
```

---

## 六、错误码

| 错误码 | 说明 |
|--------|------|
| E_PIPELINE_NOT_FOUND | 流水线不存在 |
| E_STEP_INVALID | 步骤无效 |
| E_STEP_ORDER_INVALID | 步骤顺序错误 |
| E_GATE_FAILED | 门禁未通过 |
| E_ALREADY_COMPLETED | 步骤已完成 |

---

*版本: 2.1.0 | 更新: 2026-04-23 | 变更: 补充 When to Use / Pitfalls 章节*

## Related Skills
- [[openclaw-governance-dispatch]] - 意图识别，Triage 入口
- [[openclaw-governance-quality]] - 质量管控，Audit 和 Review-Gate 执行
- [[openclaw-governance-delegation]] - 授权与等级判定，Approve 门禁
- [[openclaw-governance-task]] - 任务管理，Planning 和 Execute
- [[openclaw-governance-knowledge]] - 知识管理，Archive 知识沉淀
