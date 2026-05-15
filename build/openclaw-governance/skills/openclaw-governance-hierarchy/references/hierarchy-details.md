# Hierarchy Management — Detailed Reference

> Moved from hierarchy SKILL.md to reduce main file size.

## §二 配置加载接口

### 2.0 获取项目配置
```python
def get_projects(level="user"):
    if level == "system":
        return governance_config.load_system("projects")
    elif level == "user":
        return governance_config.load_user("projects")
    else:
        return merge(governance_config.load_system("projects"), governance_config.load_user("projects"))
```

### 2.1 查询项目
```python
def query_project(project_id):
    projects = get_projects("all")
    return projects.find(p => p.id == project_id)
```

## §四 核心函数

### create_project()
- **Input**: `{action, name, alias, description, owner, members, tags, privacy_level, source}`
- **校验流程**：获取配置 → 校验 name/owner → 生成 ZT-P{序号} → 创建目录 → 更新配置 → 创建 CHARTER
- **错误码**: E_NAME_MISSING, E_NAME_DUPLICATE, E_OWNER_INVALID
- **Output**: `{status, project_id, dir_path, charter_path, review_level: L3}`

### create_topic()
- **Input**: `{action, project_id, name, description, topic_pm, source}`
- **校验流程**：获取项目配置 → 校验 name/topic_pm → 生成 T{序号}-{描述} → 创建目录 → 创建 TOPIC-BRIEF → 更新 topics_count
- **错误码**: E_PROJECT_NOT_FOUND, E_NAME_MISSING, E_PM_INVALID, E_OUT_OF_SCOPE
- **Output**: `{status, topic_id, dir_path, review_level: L2}`

### delegate_create_task()
委托给 governance-task，本 skill 不直接创建 Task。

## §五 状态冒泡

```
Task 完成 [x] → Topic 状态更新 → Project 状态更新 → MISSION_BOARD 同步
```

**bubble_up() Input**: `{action, task_id, task_status, project_id, topic_id}`

## §六 层级校验

| 操作 | 前置依赖 | 校验方式 |
|------|----------|----------|
| 创建 Project | 无 | 直接创建 |
| 创建 Topic | Project 必须存在 | governance-config 查项目配置 |
| 创建 Task | Project + Topic 必须存在 | 委托 governance-task 校验 |

## §八 错误码汇总

| 错误码 | 说明 |
|--------|------|
| E_PROJECT_NOT_FOUND | project_id 在项目配置中不存在 |
| E_NAME_MISSING | 未指定名称 |
| E_NAME_DUPLICATE | 名称已存在 |
| E_OWNER_INVALID | owner 不是有效 Agent |
| E_PM_INVALID | PM 不是有效 Agent |
| E_OUT_OF_SCOPE | 超出项目范围 |

## §十 目录结构验证

### Topic 目录格式规则
```
{project_dir}/T{序号}-{描述}/
```
- **正确**: `T03-governance-quality-skill/` (两位数字 + 描述)
- **错误**: `topics/T16-xxx/` (不应有 topics/ 子目录), `ZT-P008-T01/` (命名格式错误)

### 验证函数
```python
def validate_topic_dir(topic_path):
    pattern = r'^T\d{2}-[A-Za-z0-9_-]+$'
    dirname = os.path.basename(topic_path.rstrip('/'))
    if not re.match(pattern, dirname):
        return {"valid": False, "error": f"Topic目录名格式错误: {dirname}"}
    return {"valid": True}
```
