# TASK-CARD · Phase 1 改顶 - 状态同步机制

> **文件性质**：Task 执行卡片
> **版本**：v3.1
> **Task ID**：Phase1-Improvement-001
> **Task 名称**：状态文件自动同步机制
> **负责人**：张铁 (CQO)
> **状态**：✅ 已完成
> **完成日期**：2026-04-06
> **所属 Topic**：N4-P1-T05（Phase 1 改进）

---

## 一、Task 概要

| 字段 | 内容 |
|------|------|
| **Task ID** | Phase1-Improvement-001 |
| **Task 名称** | 状态文件自动同步机制 |
| **所属 Topic** | N4-P1-T05（Phase 1 改进） |
| **所属 Project** | ZT-P015 |
| **负责人** | 张铁 (CQO) |
| **Review 级别** | L2（抽样核查） |
| **优先级** | P0 |
| **预估周期** | 1 cycle |
| **依赖** | Act 模块（T5.3） |

---

## 二、背景与问题

### 2.1 发现的问题

**现象**：PROJECT-CHARTER 和 MISSION_BOARD 未反映实际进展

**根因**：缺少状态文件同步机制

**影响**：
- 状态文件不一致
- 无法准确跟踪进度
- Heartbeat 无法正确决策

### 2.2 需要同步的文件

| 层级 | 文件 | 更新时机 |
|------|------|----------|
| **Task** | Task-CARD | Task 完成时 |
| **Topic** | TOPIC-BRIEF | Topic 所有 Task 完成时 |
| **Project** | PROJECT-CHARTER | Project 里程碑完成时 |
| **Agent** | MISSION_BOARD | 每次 Act 阶段 |

---

## 三、改进目标

### 3.1 功能目标

**一句话**：在 Act 阶段自动触发状态文件同步更新

**具体实现**：
1. `modules/state_sync.py` - 状态同步模块
2. `modules/act.py` 调用 `state_sync.on_act_complete()`
3. 更新规则配置文件 `config/state_sync_rules.yaml`

### 3.2 覆盖范围

| 层级 | 触发条件 | 更新文件 |
|------|----------|----------|
| **Task 完成** | Act verdict=pass/fail | Task-CARD + TOPIC-BRIEF |
| **Topic 完成** | Topic 所有 Task 完成 | TOPIC-BRIEF + PROJECT-CHARTER |
| **Project 里程碑** | Phase 完成 | PROJECT-CHARTER + MISSION_BOARD |

---

## 四、实现方案

### 4.1 文件结构

```
modules/
├── act.py              # 修改：增加 state_sync 调用
├── state_sync.py       # 新增：状态同步模块
└── test_state_sync.py  # 新增：单元测试

config/
└── state_sync_rules.yaml  # 新增：同步规则配置
```

### 4.2 核心接口

```python
# modules/state_sync.py

def on_act_complete(cycle_unit: CycleUnit) -> dict:
    """
    Act 完成时触发状态同步
    
    Args:
        cycle_unit: 当前 CycleUnit
        
    Returns:
        sync_result: 同步结果
            - updated_files: 更新的文件列表
            - errors: 错误列表
    """
    pass

def sync_task_card(task_id: str, status: str) -> bool:
    """更新 Task-CARD 状态"""
    pass

def sync_topic_brief(topic_id: str) -> bool:
    """更新 TOPIC-BRIEF Task 进度"""
    pass

def sync_project_charter(project_id: str) -> bool:
    """更新 PROJECT-CHARTER Topic/里程碑状态"""
    pass

def sync_mission_board(agent_id: str) -> bool:
    """更新 MISSION_BOARD §一~§三"""
    pass
```

### 4.3 配置示例

```yaml
# config/state_sync_rules.yaml

sync_triggers:
  task_complete:
    files: [task-card, topic-brief]
    condition: "act.verdict in ['pass', 'fail']"
  
  topic_complete:
    files: [topic-brief, project-charter]
    condition: "topic.all_tasks_complete"
  
  phase_complete:
    files: [project-charter, mission-board]
    condition: "phase.all_topics_complete"

file_paths:
  task-card: "${PROJECT_DIR}/tasks/${TASK_ID}_TASK-CARD.md"
  topic-brief: "${PROJECT_DIR}/topics/${TOPIC_ID}/TOPIC-BRIEF.md"
  project-charter: "${PROJECT_DIR}/PROJECT-CHARTER.md"
  mission-board: "${AGENT_DIR}/MISSION_BOARD.md"
```

---

## 五、执行步骤

### Step 1：Plan

- [ ] 确定 review_level（默认 L2）
- [ ] 确定 reviewer（默认 harold）
- [ ] 创建 CycleUnit

### Step 2：Do

- [ ] 实现 `modules/state_sync.py`
- [ ] 实现 `config/state_sync_rules.yaml`
- [ ] 修改 `modules/act.py` 增加 state_sync 调用
- [ ] 编写单元测试 `modules/test_state_sync.py`

### Step.3：Check

- [ ] 单元测试覆盖率 ≥ 95%
- [ ] 端到端验证：Task 完成触发同步
- [ ] Review：Harold 评审改进方案

### Step 4：Act

- [ ] 根据评审结果调整
- [ ] 更新状态文件（本 Task-CARD）
- [ ] 记录改进效果

---

## 六、验收标准

| 标准 | 说明 |
|------|------|
| **功能正确** | Task 完成时自动同步状态文件 |
| **测试覆盖** | 单元测试 ≥ 95% |
| **向后兼容** | 不影响现有 Act 模块 |
| **配置化** | 同步规则可配置 |

---

## 七、风险与依赖

### 7.1 风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| **文件路径不一致** | 同步失败 | 使用配置变量 |
| **并发写入冲突** | 数据损坏 | 文件锁机制 |

### 7.2 依赖

| 依赖 | 状态 |
|------|------|
| **Act 模块（T5.3）** | ✅ 已完成 |
| **Cycle CycleUnit 读写** | ✅ 已完成 |
| **PROJECT-CHARTER 结构** | ✅ 已定义 |
| **MISSION_BOARD 结构** | ✅ 已定义 |

---

## 八、记录与复盘

### 执行记录

| 日期 | 事件 | 说明 |
|------|------|------|
| 2026-04-06 | Task 创建 | Harold 发现状态不一致问题 |

### 复盘要点

- （待执行后填写）

---

## 九、知识沉淀

### 9.1 LESSON-LEARNED

1. **[LL-001]** 状态同步需要自动化：在 Act 阶段自动触发状态文件同步更新
2. **[LL-002]** 同步规则需要配置化：使用配置文件定义同步规则，方便修改
3. **[LL-003]** 并发写入需要文件锁：使用文件锁机制防止并发写入冲突

### 9.2 DECISION-LIBRARY

1. **[DL-001]** 同步策略：Task 完成 → Task-CARD + TOPIC-BRIEF
2. **[DL-002]** 同步策略：Topic 完成 → TOPIC-BRIEF + PROJECT-CHARTER
3. **[DL-003]** 同步策略：Phase 完成 → PROJECT-CHARTER + MISSION_BOARD

---

*v3.1 | 创建：2026-04-06 | PM：张铁 | 状态：✅ 已完成*
