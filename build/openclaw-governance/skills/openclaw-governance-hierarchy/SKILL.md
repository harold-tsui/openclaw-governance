---
name: managing-hierarchy
description: |
  Managing project and topic hierarchy, creation, and state bubbling.
  
  Activates when: Project or topic creation requested, hierarchy management needed
  
  Capabilities:
  - Project creation with charter and ID generation (ZT-PXXX format)
  - Topic creation under projects with proper directory structure
  - Hierarchy validation and dependency checking
  - State bubbling (task → topic → project → MISSION_BOARD)
  - Directory structure validation for topic naming
  
  Keywords: project, topic, hierarchy, create-project, create-topic, bubble-up
  
  For detailed documentation, see:
  - references/hierarchy-details.md

author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "3.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L2"
  os: ["darwin", "linux"]
  tags: ["hierarchy", "project", "topic", "state-bubbling", "charter"]
---

# Governance Hierarchy - 层级管理

Tags: #governance, #hierarchy, #project, #topic, #structure

> **触发模式**：描述匹配触发 + 模型主动 read()
> **v3.1.0**: 补充 When to Use / Pitfalls 章节

## 何时使用

- **Project creation**: 用户要求创建新项目（总是从 dispatch 路由到这里）
- **Topic creation**: 在现有项目下创建新 Topic
- **Hierarchy validation**: 创建依赖项前检查项目/Topic 是否存在
- **State bubbling**: 任务完成需要向上冒泡到项目和 MISSION_BOARD
- **Do NOT use for**: 任务创建 — 委托给 `governance-task.create_task()`

## 常见陷阱

1. **Topic 目录格式是严格的**: 必须是 `{project_dir}/T{序号}-{描述}/` — 不能有 `topics/` 子目录包装。`T03-governance-quality-skill/` 正确；`topics/T16-xxx/` 错误。
2. **项目名称必须唯一**: 重复的项目名会触发 E_NAME_DUPLICATE。创建前检查 `user-projects.yaml` 和 `system-projects.yaml`。
3. **Owner/PM 必须是有效 Agent**: 用无效 owner 创建项目或用无效 PM 创建 Topic 会触发 E_OWNER_INVALID / E_PM_INVALID。
4. **Bubble-up 不是自动的**: `bubble_up()` 函数必须在 `close_task()` 流程中显式调用 — 不会自己触发。

---

## 一、规范引用

| 规范/配置 | 路径 | 用途 |
|------|------|------|
| **ZT-2026-007** | policies/ZT-2026-007_交付物路径规范.md | Topic 目录命名规范 |
| **system-projects.yaml** | config/system/system-projects.yaml | 系统级项目主数据 |
| **user-projects.yaml** | config/user/user-projects.yaml | 用户级项目主数据 |
| **agents.yaml** | .system/governance/current/config/system/agents.yaml | Agent 注册表 |
| **persons.yaml** | config/user/persons.yaml | 人员信息表 |

---

## 二、职责边界

| 本 Skill 负责 | 委托给 governance-task |
|---------------|------------------------|
| Project 创建 | Task 创建 |
| Topic 创建 | Task 生命周期管理 |
| 层级关系维护 | Task 状态流转 |
| 状态冒泡（向上） | Task 验收流程 |

---

## 三、核心函数（摘要）

### create_project()
- **输入**：`{name, alias, description, owner, members, tags, privacy_level, source}`
- **约束**：name/owner 必填，项目名不重复
- **输出**：`{project_id: ZT-P{序号}, dir_path, charter_path, review_level: L3}`

### create_topic()
- **输入**：`{project_id, name, description, topic_pm, source}`
- **约束**：project_id/name/topic_pm 必填，目录格式 `T{序号}-{描述}/`
- **输出**：`{topic_id, dir_path, review_level: L2}`

### delegate_create_task()
委托给 governance-task.create_task()。

> 详细校验流程、错误码、目录验证规则：[references/hierarchy-details.md]({baseDir}/references/hierarchy-details.md)

---

## 四、状态冒泡（摘要）

```
Task 完成 [x] → Topic 状态更新 → Project 状态更新 → MISSION_BOARD 同步
```

**bubble_up()**：`{task_id, task_status, project_id, topic_id}` → 更新 topic tasks_count → project topics_count → MISSION_BOARD

> 详细冒泡规则、更新逻辑：[references/hierarchy-details.md]({baseDir}/references/hierarchy-details.md)

---

## 五、层级校验

| 操作 | 前置依赖 | 校验方式 |
|------|----------|----------|
| 创建 Project | 无 | 直接创建 |
| 创建 Topic | Project 必须存在 | governance-config 查项目配置 |
| 创建 Task | Project + Topic 必须存在 | 委托 governance-task 校验 |

### 错误码

| 错误码 | 说明 |
|--------|------|
| E_PROJECT_NOT_FOUND | project_id 不存在 |
| E_NAME_MISSING | 未指定名称 |
| E_NAME_DUPLICATE | 名称已存在 |
| E_OWNER_INVALID | owner 不是有效 Agent |
| E_PM_INVALID | PM 不是有效 Agent |
| E_OUT_OF_SCOPE | 超出项目范围 |

---

## 六、目录结构验证（摘要）

**Topic 目录格式**：`{project_dir}/T{序号}-{描述}/`
- **正确**：`T03-governance-quality-skill/`
- **错误**：`topics/T16-xxx/`（不应有 topics/ 子目录）

> 详细验证函数、规则：[references/hierarchy-details.md]({baseDir}/references/hierarchy-details.md)

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **3.0.0** | 2026-04-22 | SKILL.md 瘦身至 <300 行，详细内容移至 references/hierarchy-details.md |
| **v2.5.0** | 2026-04-07 | 对齐 governance-config v1.2.0，改用按需加载 |

---

*版本: 3.1.0 | 更新: 2026-04-23 | 变更: 补充 When to Use / Pitfalls 章节*

## Related Skills
- [[openclaw-governance-task]] - 任务管理，Topic 下的 Task 执行
- [[openclaw-governance-core]] - 核心运行机制，层级注册表管理
- [[openclaw-governance-config]] - 配置管理，Project/Topic 配置加载
