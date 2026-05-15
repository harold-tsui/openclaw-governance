# Project 生命周期引导细化设计（P0 + P1）

> **版本**: v2.0
> **创建日期**: 2026-04-15
> **作者**: 张铁 (cqo)
> **Harold 指导**: 先细化 Project 生命周期引导

---

## 一、细化范围

**优先级排序**：

| 优先级 | 引导类型 | 介入入口 | 细化状态 |
|--------|----------|----------|----------|
| **P0** ⭐ | ① 创建Project引导 | ① 创建 - 主动创建 | ✅ 本次细化 |
| **P0** ⭐ | ② 执行Task引导 | ② 执行 - 主动执行（不明确归属） | ✅ 本次细化 |
| **P1** ⭐ | ⑤ 阻塞处理引导 | ⑤ 被动介入 - Agent上报 | ✅ 本次细化 |
| **P2** | ③ 监控范围引导 | ③ 监控 - 主动监控 | ⬜ 后续细化 |
| **P2** | ④ 决策类型引导 | ④ 完成/关闭 - 主动决策 | ⬜ 后续细化 |
| **P3** | ⑥ 突发需求引导 | ⑥ 意外介入 - 突发需求 | ⬜ 后续细化 |

---

## 二、引导类型 ①：创建Project引导（P0） ⭐

### 2.1 触发条件

**介入入口**：① 创建 - 主动创建

**触发关键词**：
- "创建项目"
- "新建项目"
- "我想做一个新项目"
- "帮我创建一个项目"
- "有个新想法，需要立项"

**判断逻辑**：

```python
def is_create_project_intent(user_message):
    """判断是否为创建Project意图"""
    
    keywords = [
        "创建项目", "新建项目", "立项",
        "新项目", "我想做一个项目", "有个新想法"
    ]
    
    for keyword in keywords:
        if keyword in user_message:
            return True
    
    return False
```

---

### 2.2 引导流程

**流程图**：

```
用户消息到达
    ↓
意图识别（create_project）
    ↓
判断归属是否明确？
    ├─ 明确（用户已指定Project名称） → 直接创建（不引导）
    └─ 不明确（用户无具体Project信息） → 引导 ⭐
    ↓
引导层级 1：是否确实需要新Project？
    ├─ A. 在已有项目基础上创建新Task/Topic → 层级 2
    ├─ B. 确实需要创建新Project → 提示需要Harold审批
    └─ C. 只是查询/讨论 → 进入查询模式
```

---

### 2.3 引导内容

**层级 1 引导模板**：

```
我理解您想创建新项目。请确认：

A. 在已有项目基础上创建新Task/Topic（推荐，避免重复）
B. 确实需要创建新Project（需要Harold审批）
C. 只是查询/讨论，不需要创建

回复 A/B/C 或描述具体需求。
```

**选项数量**：3 个（A/B/C）

---

### 2.4 用户选择后续动作

**用户选择 A → 层级 2 引导**：

```
请选择已有Project：

1. ZT-P015 NUCLEUS 4.0（NUCLEUS灵枢计划）
2. ZT-P009 NUCLEUS 2.0（治理体系）
3. ZT-P-AGT-cqo（张铁个人工作台）
4. 其他（列出更多）

回复数字或Project名称。
```

**用户选择 B → 提示审批流程**：

```
创建新Project需要Harold审批。

审批流程：
1. 银月整理提议 → PROJECT-PROPOSAL.md
2. Harold审批 → 状态变为 approved
3. 创建 PROJECT-CHARTER.md

请描述项目提议内容，我会帮您整理成提案文档。
```

**用户选择 C → 进入查询模式**：

```
已确认：查询/讨论模式。

请输入您的需求：
```

---

### 2.5 状态文件关联

**更新 dispatch-state.json**：

```json
{
  "session_state": {
    "intent_type": "create_project",
    "guidance_stage": "层级1",
    "last_user_choice": "A"
  },
  
  "project_creation": {
    "proposed_project_name": null,
    "approval_status": "pending",
    "proposal_document_path": null
  }
}
```

---

### 2.6 与 governance-hierarchy 的协作

**用户选择 B → 调用 governance-hierarchy**：

```
用户选择 B → 提示审批流程
    ↓
调用 governance-hierarchy.create_project()
    ↓
输入：{
  "action": "create_project",
  "name": "待填写",
  "description": "待填写",
  "source": "harold_proposal"
}
    ↓
输出：PROJECT-PROPOSAL.md 路径
    ↓
等待 Harold 审批
```

---

### 2.7 验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|----------|
| **关键词识别** | 至少 5 个关键词 | 规则测试 |
| **引导流程完整** | 层级 1 → 层级 2 或审批流程 | 流程测试 |
| **选项数量** | ≤ 3 个 | 模板检查 |
| **状态文件更新** | intent_type + guidance_stage | JSON验证 |

---

## 三、引导类型 ②：执行Task引导（P0） ⭐

### 3.1 触发条件

**介入入口**：② 执行 - 主动执行（不明确归属）

**触发关键词**：
- "帮我完成任务"
- "继续工作"
- "执行任务"
- "处理这个任务"

**判断逻辑**：

```python
def is_execute_task_intent(user_message, state):
    """判断是否为执行Task意图"""
    
    # 规则 1：用户显式声明Task ID → 不引导
    if "T" in user_message and "-" in user_message:
        return False, "明确归属"
    
    # 规则 2：dispatch-state.json 有活跃Task → 不引导
    if state.session_state.active_task is not None:
        return False, "明确归属（state记录）"
    
    # 规则 3：用户说"继续工作" → 判断state是否有记录
    if "继续" in user_message and "工作" in user_message:
        if state.session_state.active_project is not None:
            return False, "明确归属（state记录）"
    
    # 其他情况 → 需要引导
    return True, "不明确归属"
```

---

### 3.2 引导流程

**流程图**：

```
用户消息到达
    ↓
意图识别（execute_task）
    ↓
判断归属是否明确？
    ├─ 明确（用户指定Task ID或state有记录） → 直接执行（不引导）
    └─ 不明确 → 引导 ⭐
    ↓
引导层级 1：Task归属确认
    ├─ A. 继续上次未完成的Task → 从 MISSION_BOARD 提取
    ├─ B. 选择已有Project下的Task → 层级 2
    └─ C. 创建新Task → 进入创建Task引导
```

---

### 3.3 引导内容

**层级 1 引导模板**：

```
我理解您想执行任务，但需要确认具体Task：

A. 继续上次未完成的Task
B. 选择已有Project下的Task
C. 创建新Task

回复 A/B/C 或描述具体需求。
```

**选项数量**：3 个（A/B/C）

---

### 3.4 用户选择后续动作

**用户选择 A → 提取未完成Task**：

```
您的未完成Task列表：

1. N4-P1-T07-T02 Dispatch引导入口设计（状态：执行中）
2. ZT-P015-T001 某个任务（状态：阻塞）

请选择Task编号：
```

**用户选择 B → 层级 2 引导**：

```
请选择已有Project：

1. ZT-P015 NUCLEUS 4.0
2. ZT-P009 NUCLEUS 2.0
3. ZT-P-AGT-cqo

回复数字或Project名称。
```

**用户选择 C → 进入创建Task引导**：

```
已确认：创建新Task。

请确认Task归属：
A. 选择已有Project + Topic（推荐）
B. 放入我的临时工作台（ZT-P-AGT-cqo）
C. 放入NUCLEUS治理基础（ZT-P000）

回复 A/B/C 或描述具体需求。
```

---

### 3.5 状态文件关联

**更新 dispatch-state.json**：

```json
{
  "session_state": {
    "intent_type": "execute_task",
    "guidance_stage": "层级1",
    "active_task": "N4-P1-T07-T02",
    "active_project": "ZT-P015"
  },
  
  "user_preferences": {
    "last_choice": "A",
    "choice_history": [
      {"intent": "execute_task", "choice": "A", "timestamp": "2026-04-15T15:45:00+08:00"}
    ]
  }
}
```

---

### 3.6 与 governance-task 的协作

**用户选择 B → 调用 governance-task**：

```
用户选择 B → 层级 2 引导（选择Project）
    ↓
用户选择 Project → 列出该Project下的Task
    ↓
调用 governance-task.list_tasks(project_id)
    ↓
输入：{
  "action": "list_tasks",
  "project_id": "ZT-P015",
  "status": "active"
}
    ↓
输出：Task列表
```

---

### 3.7 验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|----------|
| **归属判断逻辑** | 明确归属 → 不引导 | 逻辑测试 |
| **引导流程完整** | 层级 1 → 层级 2 或 Task列表 | 流程测试 |
| **选项数量** | ≤ 3 个 | 模板检查 |
| **状态文件更新** | active_task + active_project | JSON验证 |

---

## 四、引导类型 ⑤：阻塞处理引导（P1） ⭐

### 4.1 触发条件

**介入入口**：⑤ 被动介入 - Agent上报

**触发关键词**：
- "任务阻塞"
- "需要Harold决策"
- "无法继续执行"
- "阻塞上报"

**判断逻辑**：

```python
def is_blocked_task_intent(agent_message):
    """判断是否为阻塞上报"""
    
    keywords = [
        "任务阻塞", "阻塞上报", "需要Harold决策",
        "无法继续", "等待外部条件"
    ]
    
    for keyword in keywords:
        if keyword in agent_message:
            return True
    
    return False
```

---

### 4.2 引导流程

**流程图**：

```
Agent上报阻塞
    ↓
阻塞原因分类
    ├─ P0 阻塞（紧急） → 立即引导Harold决策
    ├─ P1 阻塞（重要） → 引导处理方式
    └─ P2 阻塞（常规） → 提供选项，不强制引导
    ↓
引导：阻塞处理方式选择
    ├─ A. 取消阻塞条件 → 修改阻塞原因
    ├─ B. 暂停任务 → 标记为阻塞，稍后处理
    ├─ C. 创建替代任务 → 绕过阻塞
    └─ D. 等待外部条件 → 等待阻塞解除
```

---

### 4.3 引导内容

**层级 1 引导模板**：

```
任务已阻塞。阻塞原因：{阻塞描述}

请选择处理方式：

A. 取消阻塞条件（修改阻塞原因）
B. 暂停任务（标记为阻塞，稍后处理）
C. 创建替代任务（绕过阻塞）
D. 等待外部条件（等待阻塞解除）

回复 A/B/C/D 或描述具体需求。
```

**选项数量**：4 个（A/B/C/D）

---

### 4.4 用户选择后续动作

**用户选择 A → 修改阻塞原因**：

```
请输入新的阻塞描述（或描述如何解除阻塞）：
```

**用户选择 B → 暂停任务**：

```
已暂停任务。任务状态已更新为：阻塞。

暂停时间：2026-04-15 15:45
阻塞原因：{原阻塞描述}

稍后可在 MISSION_BOARD §二 阻塞区 查看此任务。
```

**用户选择 C → 创建替代任务**：

```
已确认：创建替代任务。

请输入替代任务名称：
```

**用户选择 D → 等待外部条件**：

```
已确认：等待外部条件。

等待条件：{阻塞描述}
预计解除时间：待填写

任务状态已更新为：阻塞（等待外部）。
```

---

### 4.5 状态文件关联

**更新 dispatch-state.json**：

```json
{
  "blocked_handling": {
    "blocked_task_id": "N4-P1-T07-T02",
    "blocked_reason": "需要Harold审批",
    "blocked_severity": "P1",
    "harold_choice": "B",
    "blocked_time": "2026-04-15T15:45:00+08:00"
  }
}
```

---

### 4.6 与 governance-task 的协作

**用户选择 B → 调用 governance-task**：

```
用户选择 B → 暂停任务
    ↓
调用 governance-task.update_task_status()
    ↓
输入：{
  "action": "update_task_status",
  "task_id": "N4-P1-T07-T02",
  "status": "blocked",
  "blocked_reason": "等待Harold决策"
}
    ↓
输出：状态更新成功
    ↓
更新 MISSION_BOARD §二 阻塞区
```

---

### 4.7 验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|----------|
| **阻塞识别** | Agent上报 → 引导 | 流程测试 |
| **引导流程完整** | 4 种处理方式 | 模板测试 |
| **选项数量** | ≤ 4 个 | 模板检查 |
| **状态文件更新** | blocked_handling | JSON验证 |

---

## 五、dispatch-state.json 补充字段

### 5.1 引导相关字段

```json
{
  "guidance_state": {
    "current_guidance_type": "create_project",
    "current_guidance_stage": "层级1",
    "last_guidance_time": "2026-04-15T15:45:00+08:00",
    "guidance_history": [
      {
        "type": "create_project",
        "stage": "层级1",
        "user_choice": "A",
        "timestamp": "2026-04-15T15:45:00+08:00"
      }
    ]
  },
  
  "project_lifecycle": {
    "current_stage": "创建",
    "stage_history": [
      {"stage": "创建", "time": "2026-04-15T15:45:00+08:00"}
    ]
  },
  
  "blocked_handling": {
    "blocked_task_id": null,
    "blocked_reason": null,
    "blocked_severity": null,
    "harold_choice": null,
    "blocked_time": null
  }
}
```

---

## 六、引导模板汇总（P0 + P1 + P2 + P3）

| 引导类型 | 优先级 | 引导位置 | 选项数量 | 关键词数量 |
|----------|--------|----------|----------|-----------|
| **① 创建Project引导** | P0 ⭐ | 层级 1 | 3 个（A/B/C） | 5 个 |
| **② 执行Task引导** | P0 ⭐ | 层级 1 | 3 个（A/B/C） | 5 个 |
| **⑤ 阻塞处理引导** | P1 ⭐ | 阻塞上报 | 4 个（A/B/C/D） | 5 个 |
| **③ 监控范围引导** | P2 | 范围确认 | 3 个（A/B/C） | 4 个 |
| **④ 决策类型引导** | P2 | 决策选项 | 4 个（A/B/C/D） | 5 个 |
| **⑥ 突发需求引导** | P3 | 意图确认 | 3 个（A/B/C） | 3 个 |

---

## 七、下一步工作

**已完成**：
- ✅ P0 + P1 引导细化（共 3 种）
- ✅ P2 + P3 引导细化（共 3 种）
- ✅ 全部 6 种 Project 生命周期引导细化完成

**待完成**：
- ⬜ 应用到 dispatch SKILL.md

---

*创建时间：2026-04-15 | 作者：张铁 (cqo) | Harold指导：先细化Project生命周期引导*