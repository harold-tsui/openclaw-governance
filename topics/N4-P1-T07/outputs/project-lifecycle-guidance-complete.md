# Project 生命周期引导方案（完整版）

> **版本**: v3.0
> **创建日期**: 2026-04-15
> **作者**: 张铁 (cqo)
> **Harold 审查**: 待确认
> **用途**: 整体方案审查 → 应用到 dispatch SKILL.md

---

## 一、方案概述

**核心思想**：
1. **Project 生命周期驱动**：从 Project 生命周期出发，定义介入入口
2. **显式声明原则**：所有执行动作必须显式声明完整对象名（Harold 修正）
3. **引导触发条件**：不明确归属/意图时引导，明确时显式声明后执行

---

## 二、Project 生命周期（5 阶段）

```
① 创建 → ② 执行 → ③ 监控 → ④ 完成/关闭 → ⑤ 归档
```

| 阶段 | 核心动作 | 典型文件 | 状态标记 |
|------|----------|----------|----------|
| **① 创建** | Harold 提议 → 银月整理 → Harold 审批 → 创建 PROJECT-CHARTER | PROJECT-CHARTER.md | `pending` → `in_review` → `approved` |
| **② 执行** | Topic 分解 → Task 创建 → Task 执行 → 交付物提交 | TOPIC-BRIEF.md, TASK-CARD.md | `active` |
| **③ 监控** | MISSION_BOARD 跟踪 → Heartbeat 巡检 → 状态冒泡 | MISSION_BOARD.md | `running` / `blocked` |
| **④ 完成/关闭** | Topic 关闭 → Project 关闭 → Harold 裁定 | PROJECT-CHARTER.md §状态字段 | `completed` / `closed` |
| **⑤ 归档** | 文件归档 → MISSION_BOARD 移除 → archive 目录 | archive/ | `archived` |

---

## 三、人类介入入口（6 种）

| 介入入口 | 介入时机 | 典型场景 |
|----------|----------|----------|
| **① 创建 - 主动创建** | Harold 有新想法 | "我想做一个新项目" |
| **② 执行 - 主动执行** | Harold 想参与 Task | "继续 T07-T02 的工作" |
| **③ 监控 - 主动监控** | Harold 想查看状态 | "项目进展怎么样" |
| **④ 完成/关闭 - 主动决策** | Harold 想关闭 Project | "关闭 P015" |
| **⑤ 被动介入 - Agent 上报** | Agent 无法决策 | "任务阻塞，需要 Harold 决策" |
| **⑥ 意外介入 - 突发需求** | Harold 突然介入 | "我突然有个想法" |

---

## 四、引导类型（6 种）

### 4.1 引导矩阵

| 引导类型 | 介入入口 | 优先级 | 触发关键词 | 选项数量 | 是否需要显式声明 |
|----------|----------|--------|-----------|----------|-----------------|
| **① 创建 Project 引导** | ① 创建 - 主动创建 | **P0** ⭐ | 5 个 | 3 个（A/B/C） | ✅ 所有执行动作 |
| **② 执行 Task 引导** | ② 执行 - 主动执行 | **P0** ⭐ | 5 个 | 3 个（A/B/C） | ✅ 所有执行动作 |
| **⑤ 阻塞处理引导** | ⑤ 被动介入 - Agent 上报 | **P1** ⭐ | 5 个 | 4 个（A/B/C/D） | ✅ 所有执行动作 |
| **③ 监控范围引导** | ③ 监控 - 主动监控 | **P2** | 4 个 | 3 个（A/B/C） | ✅ 所有执行动作 |
| **④ 决策类型引导** | ④ 完成/关闭 - 主动决策 | **P2** | 5 个 | 4 个（A/B/C/D） | ✅ 所有执行动作 |
| **⑥ 突发需求引导** | ⑥ 意外介入 - 突发需求 | **P3** | 3 个 | 3 个（A/B/C） | ✅ 所有执行动作 |

---

### 4.2 引导类型 ①：创建 Project 引导（P0）

**触发关键词**：
- "创建项目"、"新建项目"、"立项"、"新项目"、"我想做一个项目"

**触发条件**：用户说"创建项目"，归属不明确

**引导流程**：
```
用户："创建项目"
    ↓
Agent（引导）：
我理解您想创建新项目。请确认：

A. 在已有项目基础上创建新 Task/Topic（推荐，避免重复）
B. 确实需要创建新 Project（需要 Harold 审批）
C. 只是查询/讨论，不需要创建

回复 A/B/C 或描述具体需求。
    ↓
用户选择 B
    ↓
Agent（显式声明）：
已确认：创建新 Project（需要 Harold 审批）

正在准备提案文档：PROJECT-PROPOSAL-{项目名}.md
请描述项目提议内容：
```

**状态文件更新**：
```json
{
  "guidance_state": {
    "current_guidance_type": "create_project",
    "current_guidance_stage": "层级 1",
    "last_user_choice": "B"
  },
  "project_creation": {
    "proposed_project_name": null,
    "approval_status": "pending",
    "proposal_document_path": null
  }
}
```

---

### 4.3 引导类型 ②：执行 Task 引导（P0）

**触发关键词**：
- "帮我完成任务"、"继续工作"、"执行任务"、"处理这个任务"

**触发条件**：用户说"帮我完成任务"，归属不明确

**判断逻辑**：
- 明确归属（用户指定 Task ID 或 state 有记录） → ❌ 不引导，✅ 显式声明
- 不明确归属 → ✅ 需要引导

**引导流程**：
```
用户："帮我完成任务"（无 Task ID）
    ↓
Agent（引导）：
我理解您想执行任务，但需要确认具体 Task：

A. 继续上次未完成的 Task
B. 选择已有 Project 下的 Task
C. 创建新 Task

回复 A/B/C 或描述具体需求。
    ↓
用户选择 A
    ↓
Agent（显式声明）：
正在查询：您的未完成 Task 列表（来源：MISSION_BOARD §三）

您的未完成 Task 列表：

1. N4-P1-T07-T02 Dispatch 引导入口设计（状态：执行中）
2. ZT-P015-T001 某个任务（状态：阻塞）

请选择 Task 编号：
```

**状态文件更新**：
```json
{
  "session_state": {
    "intent_type": "execute_task",
    "active_task": "N4-P1-T07-T02",
    "active_project": "ZT-P015"
  }
}
```

---

### 4.4 引导类型 ⑤：阻塞处理引导（P1）

**触发关键词**：
- "任务阻塞"、"需要 Harold 决策"、"无法继续执行"、"阻塞上报"

**触发条件**：Agent 上报阻塞

**引导流程**：
```
Agent 上报："任务阻塞，需要 Harold 决策"
    ↓
Agent（引导）：
任务已阻塞。阻塞原因：需要 Harold 审批

请选择处理方式：

A. 取消阻塞条件（修改阻塞原因）
B. 暂停任务（标记为阻塞，稍后处理）
C. 创建替代任务（绕过阻塞）
D. 等待外部条件（等待阻塞解除）

回复 A/B/C/D 或描述具体需求。
    ↓
用户选择 B
    ↓
Agent（显式声明）：
已确认：暂停任务（等待 Harold 决策）

正在更新：N4-P1-T07-T02 状态 → 阻塞
阻塞原因：需要 Harold 审批

任务状态已更新。稍后可在 MISSION_BOARD §二 阻塞区 查看此任务。
```

**状态文件更新**：
```json
{
  "blocked_handling": {
    "blocked_task_id": "N4-P1-T07-T02",
    "blocked_reason": "需要 Harold 审批",
    "blocked_severity": "P1",
    "harold_choice": "B",
    "blocked_time": "2026-04-15T16:00:00+08:00"
  }
}
```

---

### 4.5 引导类型 ③：监控范围引导（P2）

**触发关键词**：
- "查看状态"、"项目进展"、"任务状态"、"最近进展"

**触发条件**：用户询问状态，范围不明确

**判断逻辑**：
- 明确范围（用户指定 Project/Task） → ❌ 不引导，✅ 显式声明
- 不明确范围 → ✅ 需要引导

**引导流程**：
```
用户："项目进展怎么样"（不明确）
    ↓
Agent（引导）：
请确认查询范围：

A. 全局状态（所有 Project）
B. 单项目状态（指定 Project）
C. 单 Task 状态（指定 Task）

回复 A/B/C 或描述具体需求。
    ↓
用户选择 B
    ↓
Agent（引导层级 2）：
请选择 Project：

1. ZT-P015 NUCLEUS 4.0
2. ZT-P009 NUCLEUS 2.0
3. ZT-P-AGT-cqo

回复数字或 Project 名称。
    ↓
用户选择 1
    ↓
Agent（显式声明）：
正在查询：ZT-P015 NUCLEUS 4.0 项目状态

Project 状态摘要：

Project ID：ZT-P015
状态：active
当前阶段：执行期
Harold 参与度：巡航期

详细内容请查看 PROJECT-CHARTER.md
```

**状态文件更新**：
```json
{
  "monitoring_state": {
    "query_scope": "single_project",
    "target_project": "ZT-P015",
    "query_time": "2026-04-15T16:00:00+08:00"
  }
}
```

---

### 4.6 引导类型 ④：决策类型引导（P2）

**触发关键词**：
- "关闭项目"、"暂停项目"、"项目怎么办"、"处理这个项目"

**触发条件**：用户想关闭/暂停 Project，决策类型不明确

**判断逻辑**：
- 明确决策（用户说"关闭"/"暂停"） → ❌ 不引导，✅ 显式声明
- 不明确决策（"项目怎么办"） → ✅ 需要引导

**引导流程**：
```
用户："项目怎么办"（不明确）
    ↓
Agent（引导）：
请确认决策类型：

A. 暂停 Project（临时暂停，可恢复）
B. 关闭 Project（正式关闭，不再恢复）
C. 修改 Project（调整范围/目标）
D. 查看 Project 状态后再决策

回复 A/B/C/D 或描述具体需求。
    ↓
用户选择 A
    ↓
Agent（显式声明）：
已确认：暂停 Project（临时暂停，可恢复）

请输入 Project ID：
```

**明确决策场景**：
```
用户："关闭 P015"（明确）
    ↓
Agent（显式声明）：
正在关闭：ZT-P015 NUCLEUS 4.0 项目

关闭原因：待填写
请确认关闭原因：
```

**状态文件更新**：
```json
{
  "decision_state": {
    "decision_type": "pause",
    "target_project": "ZT-P015",
    "decision_reason": "待填写",
    "decision_time": "2026-04-15T16:00:00+08:00"
  }
}
```

---

### 4.7 引导类型 ⑥：突发需求引导（P3）

**触发关键词**：
- "我突然有个想法"、"马上处理这个"、"紧急需求"、"现在就做"

**触发条件**：Harold 突然介入，临时想法

**判断逻辑**：
- 紧急程度 P0（"立刻"/"马上"） → ❌ 不引导，✅ 显式声明
- 突发需求（"有个想法"） → ✅ 需要引导

**引导流程**：
```
用户："突然有个想法"（突发）
    ↓
Agent（引导）：
我理解您有新需求。请确认：

A. 需要创建新任务（会进入 Task 归属引导）
B. 只需要查询/讨论（不创建 Task）
C. 需要紧急处理（优先级 P0，立即执行）

回复 A/B/C 或描述具体需求。
    ↓
用户选择 A
    ↓
Agent（显式声明）：
已确认：创建新任务（会进入 Task 归属引导）

请确认 Task 归属：
A. 选择已有 Project + Topic（推荐）
B. 放入我的临时工作台（ZT-P-AGT-cqo）
C. 放入 NUCLEUS 治理基础（ZT-P000）

回复 A/B/C 或描述具体需求。
```

**状态文件更新**：
```json
{
  "emergency_state": {
    "emergency_type": "new_task",
    "priority": "P1",
    "emergency_time": "2026-04-15T16:00:00+08:00",
    "handled": false
  }
}
```

---

## 五、显式声明原则（Harold 修正） ⭐

### 5.1 核心原则

**Harold 原话**：**对于任何明确的、紧急的情况，都需要显式声明你的选择，让用户知道你的选择是什么。这就是"显式声明"。**

**显式声明格式**：
```
正在执行：{完整对象名称}（{补充信息}）

示例：
正在关闭：ZT-P015 NUCLEUS 4.0 项目（Harold 审批流程）
正在执行：N4-P1-T07-T02 Dispatch 引导入口设计（状态：执行中）
正在查询：ZT-P015/N4-P1-T07 的 Task 列表（共 3 个 Task）
```

---

### 5.2 显式声明触发场景

| 场景 | 是否显式声明 | 显式声明内容 | 时机 |
|------|-------------|-------------|------|
| **① 用户明确归属（关闭 P015）** | ✅ 必须显式声明 | 完整项目名 + 执行动作 | 执行前 |
| **② 用户明确 Task ID（继续 T07-T02）** | ✅ 必须显式声明 | 完整 Task 名 + Task ID + 执行动作 | 执行前 |
| **③ 用户紧急处理（立刻处理）** | ✅ 必须显式声明 | 紧急标记（P0） + 执行动作 + 确认信息 | 执行前 |
| **④ Agent 理解意图后（引导选择后）** | ✅ 必须显式声明 | 完整对象名 + 执行动作 | 执行前 |
| **⑤ Agent 上报阻塞** | ✅ 必须显式声明 | 阻塞 Task ID + 阻塞原因 + 处理选项 | 上报时 |

---

### 5.3 显式声明核心价值

**用户纠正机会**：

```
用户："关闭 P015"

Agent（显式声明）：
正在关闭：ZT-P015 NUCLEUS 4.0 项目

用户纠正："不对，我说的是 P009"

Agent（重新显式声明）：
已纠正：正在关闭 ZT-P009 NUCLEUS 2.0 项目（纠正原因：用户纠正）
```

**效果**：
- 用户看到完整项目名 → 发现说错了 → 立即纠正
- 避免 Agent 理解偏差 → 避免"关闭了错误的项目"

---

## 六、dispatch-state.json 完整设计

### 6.1 引导相关字段

```json
{
  "guidance_state": {
    "current_guidance_type": "create_project|execute_task|blocked_handling|monitoring|decision|emergency",
    "current_guidance_stage": "层级 1|层级 2|层级 3",
    "last_guidance_time": "2026-04-15T16:00:00+08:00",
    "guidance_history": []
  },
  
  "explicit_declaration": {
    "last_user_declaration": "关闭 P015",
    "parsed_object_type": "project",
    "parsed_object_id": "ZT-P015",
    "parsed_object_full_name": "ZT-P015 NUCLEUS 4.0",
    "parsed_action": "close",
    "declaration_time": "2026-04-15T16:00:00+08:00",
    
    "agent_response": "正在关闭：ZT-P015 NUCLEUS 4.0 项目",
    "agent_response_time": "2026-04-15T16:00:05+08:00",
    
    "user_correction": null,
    "user_correction_time": null
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

## 七、应用到 dispatch SKILL.md

### 7.1 修改位置

**文件**：`skills/openclaw-governance/skills/openclaw-governance-dispatch/SKILL.md`

**修改章节**：
- §三.3 异常处理 → 改为引导选择（显式声明版本）
- 新增 §三.4 引导机制（6 种引导类型）
- 新增 §三.5 显式声明规范
- 新增 §一.4 输出字段（dispatch-state.json）

---

### 7.2 修改示例

**原 §三.3 异常处理**：
```markdown
### 3.3 异常处理

| 场景 | 处理 |
|------|------|
| Skill 加载失败 | 返回友好提示，降级到 main 处理 |
| 意图歧义 | 取最高置信度，列出备选确认 |
| 完全无法识别 | 降级到闲聊模式 |
```

**修改后 §三.3 异常处理（引导选择 + 显式声明）**：
```markdown
### 3.3 异常处理（引导选择 + 显式声明） ⭐ v2.11.0

> **核心改进**: 意图不清晰时，提供 A/B/C/D 选项引导用户选择；意图明确时，显式声明执行动作

| 场景 | 处理 |
|------|------|
| Skill 加载失败 | 返回友好提示，降级到 main 处理 |
| **意图歧义** | **引导选择（提供 A/B/C/D 选项 + 记录到 dispatch-state.json）** |
| **明确归属** | **显式声明执行动作（完整对象名 + 执行动作）** |
| 完全无法识别 | **引导澄清（提供通用选项模板）** |

### 3.3.1 引导选择流程 ⭐ v2.11.0

[引导流程图]

### 3.3.2 显式声明规范 ⭐ v2.11.0

[显式声明格式模板]
```

---

## 八、验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|----------|
| **引导类型完整** | 6 种引导类型完整定义 | 文档审查 |
| **显式声明触发** | 所有执行动作都必须显式声明 | 流程测试 |
| **显式声明内容** | 完整对象名 + 执行动作 + 补充信息 | 模板检查 |
| **用户纠正机会** | 用户看到完整信息后可纠正 | 用户测试 |
| **状态文件更新** | guidance_state + explicit_declaration | JSON 验证 |

---

## 九、文件清单

| 文件 | 路径 | 用途 |
|------|------|------|
| **Project 生命周期研究** | `outputs/project-lifecycle-entry-points.md` | 5 阶段 + 6 介入入口 |
| **引导规范文档** | `outputs/dispatch-guidance-specification.md` | 11 种引导类型（旧版） |
| **P0+P1 引导细化** | `outputs/project-lifecycle-guidance-refined.md` | P0+P1 细化（显式声明前） |
| **P2+P3 引导细化** | `outputs/project-lifecycle-guidance-p2-p3.md` | P2+P3 细化（显式声明前） |
| **显式声明设计** | `outputs/explicit-declaration-design.md` | Harold 修正原则 |
| **完整方案（本文件）** | `outputs/project-lifecycle-guidance-complete.md` | 整体方案审查 ⭐ |

---

## 十、下一步工作

**待 Harold 审查**：
- ✅ 整体方案审查（本文件）
- ⬜ 审查通过后应用到 dispatch SKILL.md

**执行计划**：
1. Harold 审查本文件 → 确认无问题
2. 修改 dispatch SKILL.md（§三.3 + 新增 §三.4/3.5）
3. 创建 dispatch-state.json 模板
4. 测试验证（P0 引导试点）

---

*创建时间：2026-04-15 | 作者：张铁 (cqo) | Harold 审查：待确认*