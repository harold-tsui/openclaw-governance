# Project 生命周期引导细化设计（P2 + P3）

> **版本**: v2.1
> **创建日期**: 2026-04-15
> **作者**: 张铁 (cqo)
> **Harold 指导**: 继续细化（方案 A）

---

## 一、P2 引导细化

---

## 二、引导类型 ③：监控范围引导（P2）

### 2.1 触发条件

**介入入口**：③ 监控 - 主动监控

**触发关键词**：
- "查看状态"
- "项目进展"
- "任务状态"
- "最近进展"

**判断逻辑**：

```python
def is_monitoring_intent(user_message):
    """判断是否为监控意图"""
    
    keywords = [
        "查看状态", "项目进展", "任务状态",
        "最近进展", "进展怎么样"
    ]
    
    for keyword in keywords:
        if keyword in user_message:
            # 判断范围是否明确
            if "ZT-P" in user_message or "T" in user_message:
                return False, "明确范围"
            return True, "不明确范围"
    
    return False, "非监控意图"
```

---

### 2.2 引导流程

**流程图**：

```
用户消息到达
    ↓
意图识别（monitoring）
    ↓
判断范围是否明确？
    ├─ 明确（用户指定Project/Task） → 直接查询（不引导）
    └─ 不明确 → 引导 ⭐
    ↓
引导：监控范围确认
    ├─ A. 全局状态（所有Project） → MISSION_BOARD完整输出
    ├─ B. 单项目状态（指定Project） → 层级 2（选择Project）
    └─ C. 单Task状态（指定Task） → 层级 2（选择Task）
```

---

### 2.3 引导内容

**层级 1 引导模板**：

```
请确认查询范围：

A. 全局状态（所有Project）
B. 单项目状态（指定Project）
C. 单Task状态（指定Task）

回复 A/B/C 或描述具体需求。
```

**选项数量**：3 个（A/B/C）

---

### 2.4 用户选择后续动作

**用户选择 A → 输出 MISSION_BOARD完整内容**：

```
全局状态概览：

📊 活跃Project：3 个
   - ZT-P015 NUCLEUS 4.0（状态：active）
   - ZT-P009 NUCLEUS 2.0（状态：active）
   - ZT-P-AGT-cqo（状态：active）

📋 进行中Task：5 个
🚫 阻塞Task：1 个

详细内容请查看 MISSION_BOARD.md
```

**用户选择 B → 层级 2 引导（选择Project）**：

```
请选择Project：

1. ZT-P015 NUCLEUS 4.0
2. ZT-P009 NUCLEUS 2.0
3. ZT-P-AGT-cqo

回复数字或Project名称。
```

**用户选择 C → 层级 2 引导（选择Task）**：

```
请输入Task ID（例如：N4-P1-T07-T02）：
```

---

### 2.5 状态文件关联

**更新 dispatch-state.json**：

```json
{
  "monitoring_state": {
    "query_scope": "single_project",
    "target_project": "ZT-P015",
    "target_task": null,
    "query_time": "2026-04-15T15:48:00+08:00"
  }
}
```

---

### 2.6 验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|----------|
| **范围判断逻辑** | 明确范围 → 不引导 | 逻辑测试 |
| **引导流程完整** | 层级 1 → 层级 2 或直接输出 | 流程测试 |
| **选项数量** | ≤ 3 个 | 模板检查 |

---

## 三、引导类型 ④：决策类型引导（P2）

### 3.1 触发条件

**介入入口**：④ 完成/关闭 - 主动决策

**触发关键词**：
- "关闭项目"
- "暂停项目"
- "项目怎么办"
- "处理这个项目"

**判断逻辑**：

```python
def is_decision_intent(user_message):
    """判断是否为决策意图"""
    
    keywords = [
        "关闭项目", "暂停项目", "项目怎么办",
        "处理这个项目", "项目决策"
    ]
    
    for keyword in keywords:
        if keyword in user_message:
            # 判断决策类型是否明确
            if "关闭" in user_message or "暂停" in user_message:
                return False, "明确决策"
            return True, "不明确决策"
    
    return False, "非决策意图"
```

---

### 3.2 引导流程

**流程图**：

```
用户消息到达
    ↓
意图识别（decision）
    ↓
判断决策类型是否明确？
    ├─ 明确（用户说"关闭"/"暂停"） → 直接执行（不引导）
    └─ 不明确（"项目怎么办"） → 引导 ⭐
    ↓
引导：决策类型选择
    ├─ A. 暂停Project → 调用 governance-hierarchy.pause_project()
    ├─ B. 关闭Project → 调用 governance-hierarchy.close_project()
    ├─ C. 修改Project → 调用 governance-hierarchy.modify_project()
    └─ D. 查看状态后再决策 → 输出PROJECT-CHARTER
```

---

### 3.3 引导内容

**层级 1 引导模板**：

```
请确认决策类型：

A. 暂停Project（临时暂停，可恢复）
B. 关闭Project（正式关闭，不再恢复）
C. 修改Project（调整范围/目标）
D. 查看Project状态后再决策

回复 A/B/C/D 或描述具体需求。
```

**选项数量**：4 个（A/B/C/D）

---

### 3.4 用户选择后续动作

**用户选择 A → 暂停Project**：

```
请输入Project ID（例如：ZT-P015）：
```

**用户选择 B → 关闭Project**：

```
关闭Project需要Harold最终裁定。

请确认关闭原因：
```

**用户选择 C → 修改Project**：

```
请输入修改内容（范围/目标/优先级）：
```

**用户选择 D → 输出PROJECT-CHARTER**：

```
Project状态摘要：

Project ID：ZT-P015
状态：active
当前阶段：执行期
Harold参与度：巡航期

详细内容请查看 PROJECT-CHARTER.md
```

---

### 3.5 状态文件关联

**更新 dispatch-state.json**：

```json
{
  "decision_state": {
    "decision_type": "pause",
    "target_project": "ZT-P015",
    "decision_reason": "待填写",
    "decision_time": "2026-04-15T15:48:00+08:00"
  }
}
```

---

### 3.6 验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|----------|
| **决策类型判断** | 明确决策 → 不引导 | 逻辑测试 |
| **引导流程完整** | 4 种决策选项 | 流程测试 |
| **选项数量** | ≤ 4 个 | 模板检查 |

---

## 四、P3 引导细化

---

## 五、引导类型 ⑥：突发需求引导（P3）

### 5.1 触发条件

**介入入口**：⑥ 意外介入 - 突发需求

**触发关键词**：
- "我突然有个想法"
- "马上处理这个"
- "紧急需求"
- "现在就做"

**判断逻辑**：

```python
def is_emergency_intent(user_message):
    """判断是否为突发需求"""
    
    keywords = [
        "突然有个想法", "马上处理", "紧急需求",
        "现在就做", "立刻"
    ]
    
    for keyword in keywords:
        if keyword in user_message:
            return True, "突发需求"
    
    return False, "非突发需求"
```

---

### 5.2 引导流程

**流程图**：

```
用户消息到达
    ↓
意图识别（emergency）
    ↓
判断紧急程度？
    ├─ P0 紧急（"立刻"/"马上"） → 直接执行（不引导）
    └─ P1/P2 突发（"有个想法"） → 引导 ⭐
    ↓
引导：意图确认
    ├─ A. 需要创建新任务 → 进入创建Task引导
    ├─ B. 只需要查询/讨论 → 进入查询模式
    └─ C. 需要紧急处理 → 提升优先级为P0，立即执行
```

---

### 5.3 引导内容

**层级 1 引导模板**：

```
我理解您有新需求。请确认：

A. 需要创建新任务（会进入Task归属引导）
B. 只需要查询/讨论（不创建Task）
C. 需要紧急处理（优先级P0，立即执行）

回复 A/B/C 或描述具体需求。
```

**选项数量**：3 个（A/B/C）

---

### 5.4 用户选择后续动作

**用户选择 A → 进入创建Task引导**：

```
已确认：创建新任务。

请确认Task归属：
A. 选择已有Project + Topic（推荐）
B. 放入我的临时工作台（ZT-P-AGT-{agent}）
C. 放入NUCLEUS治理基础（ZT-P000）

回复 A/B/C 或描述具体需求。
```

**用户选择 B → 进入查询模式**：

```
已确认：查询/讨论模式。

请输入您的需求：
```

**用户选择 C → 提升优先级为P0**：

```
已确认：紧急处理（优先级P0）。

请输入紧急任务内容：
```

---

### 5.5 状态文件关联

**更新 dispatch-state.json**：

```json
{
  "emergency_state": {
    "emergency_type": "new_task",
    "priority": "P0",
    "emergency_time": "2026-04-15T15:48:00+08:00",
    "handled": false
  }
}
```

---

### 5.6 验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|----------|
| **紧急程度判断** | P0 紧急 → 不引导 | 逻辑测试 |
| **引导流程完整** | 3 种意图选项 | 流程测试 |
| **选项数量** | ≤ 3 个 | 模板检查 |

---

## 六、完整引导矩阵（6 种）

| 引导类型 | 介入入口 | 优先级 | 触发关键词数量 | 引导位置 | 选项数量 | 是否需要状态文件更新 |
|----------|----------|--------|---------------|----------|----------|---------------------|
| **① 创建Project引导** | ① 创建 - 主动创建 | **P0** ⭐ | 5 个 | 层级 1 | 3 个（A/B/C） | ✅ guidance_state + project_creation |
| **② 执行Task引导** | ② 执行 - 主动执行 | **P0** ⭐ | 5 个 | 层级 1 | 3 个（A/B/C） | ✅ session_state + user_preferences |
| **⑤ 阻塞处理引导** | ⑤ 被动介入 - Agent上报 | **P1** ⭐ | 5 个 | 阻塞上报 | 4 个（A/B/C/D） | ✅ blocked_handling |
| **③ 监控范围引导** | ③ 监控 - 主动监控 | **P2** | 4 个 | 范围确认 | 3 个（A/B/C） | ✅ monitoring_state |
| **④ 决策类型引导** | ④ 完成/关闭 - 主动决策 | **P2** | 5 个 | 决策选项 | 4 个（A/B/C/D） | ✅ decision_state |
| **⑥ 突发需求引导** | ⑥ 意外介入 - 突发需求 | **P3** | 3 个 | 意图确认 | 3 个（A/B/C） | ✅ emergency_state |

---

## 七、dispatch-state.json 完整字段（补充）

### 7.1 引导相关字段

```json
{
  "guidance_state": {
    "current_guidance_type": "create_project|execute_task|blocked_handling|monitoring|decision|emergency",
    "current_guidance_stage": "层级1|层级2|层级3",
    "last_guidance_time": "2026-04-15T15:48:00+08:00",
    "guidance_history": []
  },
  
  "project_creation": {
    "proposed_project_name": null,
    "approval_status": "pending|approved|rejected",
    "proposal_document_path": null
  },
  
  "blocked_handling": {
    "blocked_task_id": null,
    "blocked_reason": null,
    "blocked_severity": "P0|P1|P2",
    "harold_choice": "A|B|C|D",
    "blocked_time": null
  },
  
  "monitoring_state": {
    "query_scope": "global|single_project|single_task",
    "target_project": null,
    "target_task": null,
    "query_time": null
  },
  
  "decision_state": {
    "decision_type": "pause|close|modify",
    "target_project": null,
    "decision_reason": null,
    "decision_time": null
  },
  
  "emergency_state": {
    "emergency_type": "new_task|query_discussion|urgent_execute",
    "priority": "P0|P1|P2",
    "emergency_time": null,
    "handled": false
  }
}
```

---

## 八、下一步工作

**已完成**：
- ✅ 全部 6 种 Project 生命周期引导细化完成
- ✅ 引导流程、选项模板、状态文件关联完整

**待完成**：
- ⬜ 应用到 dispatch SKILL.md
- ⬜ 创建 dispatch-state.json 模板（完整版本）
- ⬜ 编写 dispatch 引导机制实现文档

---

*创建时间：2026-04-15 | 作者：张铁 (cqo) | 细化范围：P2 + P3*