# Pipeline Orchestration — Detailed Reference

> Moved from pipeline SKILL.md sections to reduce main file size.

## §一 Review-Gate 职责边界

**核心原则**：Pipeline 编排时机，Quality 执行验证，Delegation 判定权限

| Skill | 职责 | 关键问题 | 具体工作 |
|-------|------|----------|----------|
| **pipeline** | **编排** Review-Gate | "什么时候审查" | 定义 Review-Gate 在流水线中的位置、触发条件、门禁状态管理 |
| **quality** | **执行** Review-Gate | "审查什么" | 提供检查清单、验证逻辑、DOD 验证、问题记录 |
| **delegation** | **判定** Review-Gate | "谁能批准" | 定义审批权限、自动化级别判定、审批门禁规则 |

**决策表**：
| Review-Gate 检查点 | 门禁执行者 | 规则提供者 | 权限判定者 |
|-------------------|------------|------------|------------|
| Step 6: Approve（审批门禁） | pipeline（触发） | delegation（规则） | delegation（判定） |
| Step 8: Review-Gate（审查门禁） | pipeline（触发） | quality（规则 + 执行） | delegation（权限） |
| DOD 验证 | quality（执行） | quality（创建 DOD） | delegation（验证权限） |

**防自我认证机制**：
- 谁创建 DOD，谁就不能验证 DOD（由 delegation 判定验证权限）
- 谁执行任务，谁就不能自我审查（quality 独立验证）

## §二 流水线步骤详解

### 10-Step Pipeline

| Step | Name | Description | Caller |
|------|------|-------------|--------|
| 1 | Triage | Task classification by type/weight | governance-dispatch intent |
| 2 | Checkpoint | Session recovery from interruption | LLM session check |
| 3 | Context | Load task context (Task-CARD + deliverables) | LLM reads |
| 4 | Audit | Codebase/deliverable audit | governance-quality.review() |
| 5 | Planning | Solution exploration (Heavyweight/Strategic only) | LLM planning |
| 6 | Approve | Decision-maker approval gate | governance-delegation.check_authorization() |
| 7 | Execute | Task execution with embedded review | LLM execution |
| 8 | Review-Gate | Mandatory review completeness check | governance-quality.validate_review_gate() |
| 9 | Complete | Final confirmation + LL template generation | governance-task.close_task() |
| 10 | Archive | Knowledge capture + Feishu sync | governance-knowledge.sync_to_feishu() |

### Step Function Details

#### Triage
- **Input**: dispatch intent classification
- **Output**: `{task_type, automation_level, weight}`

#### Checkpoint
- **Input**: session state file
- **Output**: `{resumed, last_step, session_data}`

#### Context
- **Input**: task-card path
- **Output**: `{context_tree, files_loaded}`

#### Audit
- **Input**: deliverable path
- **Output**: `{audit_report, ground_truth}`

#### Planning
- **Input**: task-card + audit results
- **Output**: `{options[], recommended}`

#### Approve
- **Automation**: Lightweight/Medium auto-pass; Heavyweight/Strategic need Harold
- **Output**: `{approved, approver, approved_at}`

#### Execute
- **Output**: `{deliverables[], reviews[]}`

#### Review-Gate
- **Checks**: review artifacts, self-review detection, DOD verification, zero-issue warning
- **Output**: `{status, errors, warnings}`

#### Complete
- **Enhanced logic** (PMBOK融合):
  1. Confirm all DOD met
  2. Confirm deliverables submitted
  3. Generate LL template → `lessons/LL-{task_id}-{timestamp}.md`
  4. Update task state
- **Output**: `{completed, completed_at, ll_template_generated}`

#### Archive
- **Enhanced logic** (alignment):
  1. Organize deliverables
  2. Knowledge capture (LL填写完成)
  3. External alignment: sync to Feishu (docs, deliverables, LL, decision library)
- **Output**: `{archived, knowledge_captured, feishu_synced}`

## §三 权重适配

| Weight | Automation Level | Skipped Steps | Auto-Approved |
|--------|-----------------|---------------|---------------|
| **Lightweight** | L4-L5 | Planning | Approve |
| **Medium** | L3 | Planning | Approve |
| **Heavyweight** | L2 | None | None |
| **Strategic** | L0-L1 | None | None |

## §四 流水线状态管理

### pipeline-state.json Structure

```json
{
  "pipeline_id": "PL-ZT-P008-T01-T001",
  "task_id": "ZT-P008-T01-T001",
  "weight": "Medium",
  "automation_level": "L3",
  "created_at": "2026-03-23T14:00:00+08:00",
  "updated_at": "2026-03-23T15:30:00+08:00",
  "current_step": "execute",
  "steps": [
    {
      "id": "triage",
      "status": "completed",
      "started_at": "...",
      "completed_at": "...",
      "output": { ... }
    }
  ]
}
```

### Step States

| State | Meaning |
|-------|---------|
| pending | Not yet started |
| in_progress | Currently executing |
| completed | Successfully finished |
| failed | Execution failed |
| skipped | Skipped (weight adaptation) |

### Core Functions

#### init_pipeline()
- **Input**: `{task_id, automation_level}`
- **Process**: Determine weight → Generate steps → Initialize state → Write pipeline-state.json
- **Output**: `{status, pipeline_id, weight, steps[], skipped[]}`

#### advance_pipeline()
- **Input**: `{task_id, current_step}`
- **Process**: Validate step → Execute → Update state → Check gates
- **Output**: `{status, completed_step, next_step, pipeline_progress}`

#### get_pipeline_status()
- **Input**: `{task_id}`
- **Output**: `{status, pipeline_id, weight, current_step, progress, steps[]}`

## §五 与其他 Skill 的协作

```
governance-pipeline (编排)
    ├── governance-dispatch (Triage)
    ├── governance-core (Checkpoint)
    ├── governance-data (Context, Archive)
    ├── governance-quality (Audit, Review-Gate)
    ├── governance-task (Planning, Execute)
    ├── governance-delegation (Approve)
    └── governance-hierarchy (Complete)
```

### DOD/Review-gate Integration

```
Execute → 生成交付物 → Review-Gate → governance-quality.validate_review_gate()
    ├─ 检查审查产物
    ├─ 检查自我审查
    ├─ 验证 DOD
    └─ 检查零问题审查
    ↓
通过 → Complete
失败 → 返回 Execute
```

### Risk/Knowledge Integration

```
Complete → governance-risk.monitor_risks() + governance-knowledge.create_lesson_learned()
Archive → governance-knowledge.sync_to_feishu()
```

## §六 错误码

| 错误码 | 说明 |
|--------|------|
| E_PIPELINE_NOT_FOUND | 流水线不存在 |
| E_STEP_INVALID | 步骤无效 |
| E_STEP_ORDER_INVALID | 步骤顺序错误 |
| E_GATE_FAILED | 门禁未通过 |
| E_ALREADY_COMPLETED | 步骤已完成 |
