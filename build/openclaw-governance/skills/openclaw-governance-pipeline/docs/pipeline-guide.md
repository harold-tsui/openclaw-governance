# Pipeline 使用指南

> **版本**：v1.0.0
> **作者**：张铁 (cqo)
> **日期**：2026-03-23
> **适用**：NUCLEUS 2.0 闭环流程增强

---

## 一、概述

### 1.1 定义

**Pipeline** 是任务执行的显式流水线，将 NUCLEUS 闭环流程 6 步展开为 10 个显式步骤。

### 1.2 与闭环流程对应

```
闭环流程 6 步           Pipeline 10 步
────────────────────────────────────────
创建                    → Triage
                       → Checkpoint
                       → Context
分派                    → Audit
                       → Planning
接收                    → Approve
执行                    → Execute
验收                    → Review-Gate
关闭                    → Complete
                       → Archive
```

---

## 二、流水线步骤

### 2.1 完整步骤

| 步骤 | 名称 | 职责 | 调用 Skill |
|------|------|------|------------|
| 1 | Triage | 任务分类 | governance-dispatch |
| 2 | Checkpoint | 会话恢复 | governance-core |
| 3 | Context | 加载上下文 | governance-data |
| 4 | Audit | 代码库审计 | governance-quality |
| 5 | Planning | 方案规划 | governance-task |
| 6 | Approve | 门禁 | governance-delegation |
| 7 | Execute | 构建 + 审查 | governance-task |
| 8 | Review-Gate | 审查门禁 | governance-quality |
| 9 | Complete | 完成确认 | governance-hierarchy |
| 10 | Archive | 归档 | governance-data |

### 2.2 步骤状态

| 状态 | 说明 |
|------|------|
| **pending** | 待执行 |
| **in_progress** | 执行中 |
| **completed** | 已完成 |
| **failed** | 失败 |
| **skipped** | 已跳过 |

---

## 三、权重适配

### 3.1 权重定义

| 权重 | 自动化级别 | 说明 |
|------|------------|------|
| **Lightweight** | L4-L5 | 快速执行，自动审批 |
| **Medium** | L3 | 标准流程，自动审批 |
| **Heavyweight** | L2 | 完整流程，人工审批 |
| **Strategic** | L0-L1 | 完整流程 + 审议轮 |

### 3.2 步骤适配

| 步骤 | Lightweight | Medium | Heavyweight | Strategic |
|------|-------------|--------|-------------|-----------|
| Triage | ✅ | ✅ | ✅ | ✅ |
| Checkpoint | ✅ | ✅ | ✅ | ✅ |
| Context | ✅ | ✅ | ✅ | ✅ |
| Audit | ✅ | ✅ | ✅ | ✅ |
| Planning | ⏭️ 跳过 | ⏭️ 跳过 | ✅ | ✅ + 审议 |
| Approve | ⚡ 自动 | ⚡ 自动 | 🔒 人工 | 🔒 人工 |
| Execute | ✅ | ✅ | ✅ | ✅ |
| Review-Gate | ✅ | ✅ | ✅ | ✅ |
| Complete | ✅ | ✅ | ✅ | ✅ |
| Archive | ✅ | ✅ | ✅ | ✅ |

---

## 四、使用方法

### 4.1 初始化流水线

```json
{
  "action": "init_pipeline",
  "task_id": "ZT-P008-T01-T001",
  "automation_level": "L3"
}
```

**输出**：
```json
{
  "status": "OK",
  "pipeline_id": "PL-ZT-P008-T01-T001",
  "weight": "Medium",
  "steps": [...],
  "skipped": ["planning"]
}
```

### 4.2 推进流水线

```json
{
  "action": "advance_pipeline",
  "task_id": "ZT-P008-T01-T001",
  "current_step": "triage"
}
```

**输出**：
```json
{
  "status": "OK",
  "completed_step": "triage",
  "next_step": "checkpoint",
  "pipeline_progress": "2/8"
}
```

### 4.3 获取状态

```json
{
  "action": "get_pipeline_status",
  "task_id": "ZT-P008-T01-T001"
}
```

---

## 五、与 DOD/Review-gate 集成

### 5.1 集成点

```
Execute 步骤
    ↓
生成交付物
    ↓
Review-Gate 步骤
    ↓
调用 governance-quality.validate_review_gate()
    ├─ 检查审查产物
    ├─ 检查自我审查
    ├─ 验证 DOD          ← DOD 集成点
    └─ 检查零问题审查
    ↓
通过 → Complete
失败 → 返回 Execute
```

### 5.2 DOD 在 Execute 中创建

```
Execute 步骤开始
    ↓
调用 governance-quality.create_dod()
    ↓
DOD 锁定
    ↓
Builder 执行
    ↓
DOD 验证
```

---

## 六、错误处理

### 6.1 错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| E_PIPELINE_NOT_FOUND | 流水线不存在 | 初始化流水线 |
| E_STEP_INVALID | 步骤无效 | 检查步骤 ID |
| E_STEP_ORDER_INVALID | 步骤顺序错误 | 按顺序执行 |
| E_GATE_FAILED | 门禁未通过 | 检查 DOD/Review |
| E_ALREADY_COMPLETED | 步骤已完成 | 检查当前步骤 |

### 6.2 失败恢复

```
步骤失败
    ↓
状态 = failed
    ↓
记录错误信息
    ↓
可重试 / 跳过 / 终止
```

---

## 七、最佳实践

### 7.1 流水线使用时机

| 场景 | 是否使用 Pipeline |
|------|-------------------|
| 常规任务 | ✅ 是 |
| 周期性任务 | ✅ 是（简化版） |
| 应急任务 | ❌ 否（直接执行） |
| Issue Ticket | ✅ 是（简化版） |

### 7.2 状态文件管理

```
pipeline-state.json
    ↓
存储位置：{task_dir}/processes/pipeline-state.json
    ↓
每次步骤变更时更新
    ↓
支持会话恢复（Checkpoint）
```

---

## 八、参考资源

- `schemas/pipeline.schema.json` - Pipeline Schema
- `templates/TMPL-PIPELINE-STATE.json` - 状态模板
- `governance-quality/SKILL.md` - DOD 和 Review-gate
- `governance-task/SKILL.md` - 任务执行

---

*本指南 v1.0.0 | 作者：张铁 (cqo) | 日期：2026-03-23*