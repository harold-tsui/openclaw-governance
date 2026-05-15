# Dispatch 引导入口设计

> **版本**: v1.0
> **创建日期**: 2026-04-15
> **作者**: 张铁 (cqo)
> **用途**: 对比 BotLearn 引导机制 + 设计 dispatch 改进方案

---

## 一、BotLearn 引导机制分析

### 1.1 核心特性

| 特性 | BotLearn 实现 | 效果 |
|------|--------------|------|
| **引导式提问** | 不清楚用户需求时，提供选项让用户选择 | 避免猜测，提高准确性 |
| **状态感知路由** | state.json 记录用户状态，驱动路由决策 | 上下文连续性 |
| **Intent → Module Mapping** | 意图映射到模块，按需加载 | 减少冗余加载 |
| **Config-First 原则** | config.json 控制权限和能力 | 安全边界明确 |

### 1.2 引导式提问示例

**场景**: 用户说"帮我处理一下这个文档"

**BotLearn 引导**:
```
我理解您想处理文档，但需要确认具体操作：

请选择：
A. 创建新文档
B. 更新已有文档
C. 提取文档内容
D. 删除文档

回复 A/B/C/D 或描述具体需求。
```

---

## 二、当前 dispatch 对比分析

### 2.1 当前实现

| 功能 | 当前 dispatch v2.10.0 | BotLearn 对应 |
|------|----------------------|--------------|
| **意图识别** | §二.1 意图映射表（关键词匹配） | ✅ Intent → Module Mapping |
| **路由决策** | §三.1 标准流程 | ✅ 路由机制 |
| **缓存检查** | §三.2 缓存检查 | ⚠️ 缺少状态文件 |
| **异常处理** | §三.3 "询问澄清" | ❌ 无引导选项 |
| **状态感知** | 无 state.json | ❌ 缺少状态文件 |

### 2.2 关键差距

| 差距项 | 当前状态 | 改进方向 |
|--------|---------|----------|
| **引导式提问** | 只有"询问澄清"，无选项 | 增加 A/B/C 选项引导 |
| **状态感知路由** | 无状态文件 | 增加 dispatch-state.json |
| **意图歧义处理** | "取最高置信度，列出备选确认" | 改为引导选择 |

---

## 三、引导式提问设计

### 3.1 设计原则

| 原则 | 说明 |
|------|------|
| **不猜测** | 意图不清晰时，提供选项让用户选择 |
| **有限选项** | 选项数量不超过 5 个（避免认知负担） |
| **快速响应** | 引导选项预定义，无需计算 |
| **记忆上次选择** | state.json 记录用户偏好 |

### 3.2 引导流程设计

```
用户消息到达
    ↓
意图识别（关键词匹配）
    ↓
if 意图清晰:
    直接路由
elif 意图歧义（多个候选）:
    读取 dispatch-state.json（上次选择）
    ↓
    if 上次选择匹配候选:
        路由到上次选择
    else:
        引导选择（提供 A/B/C 选项）
        ↓
        用户回复 A/B/C
        ↓
        记录选择到 dispatch-state.json
        ↓
        路由到目标 Skill
else:
    引导澄清（提供通用选项）
```

### 3.3 引导选项模板

**模板 1：任务类型引导**

```
我理解您需要执行任务，但需要确认具体类型：

请选择：
A. 创建新任务（创建 Task-CARD）
B. 执行已有任务（继续未完成的 Task）
C. 查看任务状态（查看 MISSION_BOARD）
D. 修改任务（修改 Task-CARD）

回复 A/B/C/D 或描述具体需求。
```

**模板 2：项目操作引导**

```
我理解您需要进行项目操作，但需要确认具体动作：

请选择：
A. 创建新项目
B. 查看项目状态
C. 关闭已有项目
D. 项目归档

回复 A/B/C/D 或描述具体需求。
```

**模板 3：质量审核引导**

```
我理解您需要进行质量审核，但需要确认具体操作：

请选择：
A. 审核 Task-CARD（验证格式完整性）
B. 审核交付物（验证 DOD 达成）
C. 检查状态一致性（Task-CARD vs MISSION_BOARD）
D. PDCA 改进评估

回复 A/B/C/D 或描述具体需求。
```

---

## 四、dispatch-state.json 设计

### 4.1 状态文件结构

```json
{
  "version": "1.0.0",
  "updated_at": "2026-04-15",
  
  "user_preferences": {
    "last_intent_type": "create_task",
    "last_skill_loaded": "governance-task",
    "last_choice": "A",
    "choice_history": [
      {"intent": "create_task", "choice": "A", "timestamp": "2026-04-15T09:00:00+08:00"}
    ]
  },
  
  "session_state": {
    "loaded_skills": ["governance-core", "governance-dispatch"],
    "active_task": "N4-P1-T07-T02",
    "active_project": "ZT-P015"
  },
  
  "routing_cache": {
    "intent_to_skill": {
      "create_project": "governance-hierarchy",
      "create_task": "governance-task",
      "quality_review": "governance-quality"
    }
  },
  
  "guidance_templates": {
    "task_type": ["创建新任务", "执行已有任务", "查看任务状态", "修改任务"],
    "project_ops": ["创建新项目", "查看项目状态", "关闭已有项目", "项目归档"],
    "quality_ops": ["审核Task-CARD", "审核交付物", "检查状态一致性", "PDCA改进评估"]
  }
}
```

### 4.2 关键字段说明

| 字段 | 用途 | 更新时机 |
|------|------|----------|
| `user_preferences.last_intent_type` | 上次意图类型 | 每次路由成功 |
| `user_preferences.last_choice` | 上次引导选择 | 用户选择后 |
| `session_state.loaded_skills` | 已加载 Skill 列表 | Skill 加载时 |
| `session_state.active_task` | 当前活跃 Task | Task 开始时 |
| `routing_cache.intent_to_skill` | 意图→Skill 映射缓存 | 首次路由后 |

---

## 五、改进方案

### 5.1 改进点列表

| 改进点 | 优先级 | 预估工作量 | 影响范围 |
|--------|--------|-----------|----------|
| **§三.3.3 异常处理改为引导选择** | P0 | 2 小时 | dispatch SKILL.md |
| **dispatch-state.json 模板创建** | P1 | 1 小时 | templates 目录 |
| **引导选项预定义机制** | P2 | 1 小时 | dispatch SKILL.md |
| **用户偏好记忆机制** | P3 | 2 小时 | dispatch-state.json 更新逻辑 |

### 5.2 执行优先级

**Phase 1（立即执行）**：
- ✅ §三.3.3 异常处理改为引导选择（核心改进）
- ✅ 引导选项模板定义（3个模板）

**Phase 2（后续执行）**：
- ⬜ dispatch-state.json 模板创建
- ⬜ 用户偏好记忆机制实现

---

## 六、示例对比

### 6.1 当前 dispatch 行为

**用户**: "帮我处理一下文档"

**当前 dispatch（§三.3.3）**:
```
意图歧义：取最高置信度，列出备选确认
→ 可能是 create_project、create_task、quality_review
→ "请确认您的需求"
```

### 6.2 改进后 dispatch 行为

**用户**: "帮我处理一下文档"

**改进后 dispatch（引导式提问）**:
```
我理解您需要处理文档相关任务，请选择：

A. 创建新文档（创建 Task-CARD）
B. 更新已有文档（执行已有 Task）
C. 提取文档内容（查询操作）
D. 其他文档操作（描述具体需求）

回复 A/B/C/D 或描述具体需求。
```

---

## 七、验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|----------|
| **引导流程设计** | 流程完整、逻辑清晰 | 文档评审 |
| **引导选项模板** | 至少 3 个模板 | 文件检查 |
| **状态文件设计** | 字段定义完整 | JSON schema 验证 |
| **示例对比** | 改进效果明显 | 用户测试 |

---

*创建时间：2026-04-15 | 作者：张铁 (cqo) | 用途：dispatch 改进设计*