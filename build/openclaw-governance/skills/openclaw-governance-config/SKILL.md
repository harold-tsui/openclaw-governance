---
name: managing-config
description: |
  Managing system configuration via config/*.yaml files with layered config operations.
  
  Activates when: System or user-level configuration needed, config management operations
  
  Capabilities:
  - Loading config/*.yaml files with layered config (defaults → system → user)
  - Config operations (read, update, validate)
  - Configuration template management (11 templates)
  - Runtime config loading for other skills
  
  Keywords: config, configuration, settings, yaml, system-config
  
author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "1.4.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L2"
  os: ["darwin", "linux"]
  tags: ["configuration", "yaml", "layered-config", "system-config", "user-config"]
---

# Governance Config - 系统配置管理

Tags: #governance, #config, #yaml, #system-config, #user-config

> 配置加载与管理的统一接口。
> **v1.4.0**: 补充 When to Use / Pitfalls 章节

## 何时使用

- **Session startup**: `load_core()` 加载 globals.yaml + duty-mapping.yaml
- **Agent routing**: `load_system("agents")` 获取 Agent 注册表
- **Skill layering**: `load_system("skills")` 获取 Skill 注册表
- **Project/Topic queries**: `load_system()` 或 `load_user()` 获取项目/Topic 数据
- **Do NOT use for**: 直接编辑 YAML — 配置变更应通过正规渠道

## 常见陷阱

1. **Core 配置是强制加载的**: `globals.yaml` 和 `duty-mapping.yaml` 在会话启动时无条件加载 — 它们永远不是"可选的"。
2. **System vs User 前缀很重要**: 系统文件用 `system-` 前缀，用户文件用 `user-` 前缀。混淆会导致数据过期/错误。
3. **新部署需要模板**: 首次部署时，从 `templates/` 复制模板到配置路径后再编辑。不要从头创建配置文件。
4. **用户配置是手动编辑的**: 与系统配置（由 Skill 自动管理）不同，用户配置（`user-projects.yaml`、`user-tasks.yaml` 等）必须由用户编辑 — Skill 只读取。

---

## 一、配置目录结构

```
config/
├── globals.yaml              # 核心配置（不分层，会话启动加载）
├── duty-mapping.yaml         # 核心配置（不分层，会话启动加载）
│
├── system/                   # 系统级配置（Skill 安装时创建）
│   ├── agents.yaml           # 系统级 Agent 配置
│   ├── skills.yaml           # Skill 注册表
│   ├── system-projects.yaml  # 系统级项目
│   ├── system-tasks.yaml     # 系统级任务（含 cron）
│   └── system-topics.yaml    # 系统级主题
│
└── user/                     # 用户级配置（手动编辑）
    ├── user-projects.yaml    # 用户项目
    ├── user-tasks.yaml       # 用户任务
    ├── user-topics.yaml      # 用户主题
    └── persons.yaml          # 人员数据
```

> **命名规则**：系统级文件使用 `system-` 前缀，用户级文件使用 `user-` 前缀，便于识别层级。
> **新部署引导**：首次部署时，将 `templates/` 下的模板文件复制到对应配置路径，按需修改后使用。

### 1.1 配置模板

| 模板文件 | 目标路径 | 说明 |
|----------|----------|------|
| `templates/TPL-globals.yaml` | `config/globals.yaml` | 全局变量、环境配置 |
| `templates/TPL-duty-mapping.yaml` | `config/duty-mapping.yaml` | Agent 职责映射表 |
| `templates/system/TPL-agents.yaml` | `config/system/agents.yaml` | Agent 注册表 |
| `templates/system/TPL-skills.yaml` | `config/system/skills.yaml` | Skill 注册表 |
| `templates/system/TPL-system-projects.yaml` | `config/system/system-projects.yaml` | 系统级项目 |
| `templates/system/TPL-system-tasks.yaml` | `config/system/system-tasks.yaml` | 系统级任务 |
| `templates/system/TPL-system-topics.yaml` | `config/system/system-topics.yaml` | 系统级主题 |
| `templates/user/TPL-user-projects.yaml` | `config/user/user-projects.yaml` | 用户项目 |
| `templates/user/TPL-user-tasks.yaml` | `config/user/user-tasks.yaml` | 用户任务 |
| `templates/user/TPL-user-topics.yaml` | `config/user/user-topics.yaml` | 用户主题 |
| `templates/user/TPL-persons.yaml` | `config/user/persons.yaml` | 人员信息 |

---

## 二、配置分层判定标准

### 系统级配置判定（满足任一）

1. 由 Skill 安装时自动创建
2. 长期运行，无明确结束日期
3. 支撑 OpenClaw 体系的基础运行
4. 由治理版本统一管理

### 用户级配置判定（满足任一）

1. 用户手动创建/编辑
2. 业务项目相关配置
3. 个性化定制配置
4. 可频繁变更的配置

---

## 三、加载机制

### 3.1 核心配置（会话启动加载）

```yaml
# 必须加载，不分层
files:
  - globals.yaml      # 全局变量、环境配置
  - duty-mapping.yaml # 职责映射表
```

**加载时机**：会话启动时，由 governance-core 调用 `load_core()`

### 3.2 系统级配置（按需加载）

```yaml
# 系统级，Skill 安装时创建
files:
  - system/agents.yaml    # Agent 配置
  - system/skills.yaml    # Skill 注册表
  - system/system-projects.yaml  # 系统项目
  - system/system-tasks.yaml     # 系统任务（含 cron）
  - system/system-topics.yaml    # 系统主题
```

**触发条件**：
- 需要查询系统级项目信息
- 需要处理系统任务或查看 cron 调度
- 需要查询系统主题
- 需要 Agent 路由信息
- 需要 Skill 分层依据

### 3.3 用户级配置（按需加载）

```yaml
# 用户级，手动编辑
files:
  - user/user-projects.yaml    # 用户项目
  - user/user-tasks.yaml       # 用户任务
  - user/user-topics.yaml      # 用户主题
  - user/persons.yaml          # 人员数据
```

**触发条件**：
- 需要查询用户级项目信息
- 需要处理用户任务
- 需要查询用户主题
- 需要人员信息

---

## 四、加载函数

### 4.1 load_core()

```python
def load_core():
    """加载核心配置（会话启动时调用）"""
    read config/globals.yaml
    read config/duty-mapping.yaml
```

**调用位置**：governance-core 会话启动流程

### 4.2 load_system()

```python
def load_system(subset=None):
    """加载系统级配置"""
    if subset == "agents":
        read config/system/agents.yaml
    elif subset == "skills":
        read config/system/skills.yaml
    elif subset == "projects":
        read config/system/system-projects.yaml
    elif subset == "tasks":
        read config/system/system-tasks.yaml
    elif subset == "topics":
        read config/system/system-topics.yaml
    else:
        # 加载全部系统级配置
        read config/system/agents.yaml
        read config/system/skills.yaml
        read config/system/system-projects.yaml
        read config/system/system-tasks.yaml
        read config/system/system-topics.yaml
```

### 4.3 load_user()

```python
def load_user(subset=None):
    """加载用户级配置"""
    if subset == "projects":
        read config/user/user-projects.yaml
    elif subset == "tasks":
        read config/user/user-tasks.yaml
    elif subset == "topics":
        read config/user/user-topics.yaml
    elif subset == "persons":
        read config/user/persons.yaml
    else:
        # 加载全部用户级配置
        read config/user/user-projects.yaml
        read config/user/user-tasks.yaml
        read config/user/user-topics.yaml
        read config/user/persons.yaml
```

---

## 五、配置操作函数

### 5.1 get_config(key)

```python
def get_config(key: str) -> any:
    """获取配置项（从已加载的配置中）"""
    # key 格式: "globals.environment.workspace"
    # 返回对应值
```

### 5.2 validate()

```python
def validate(config_type: str) -> bool:
    """配置校验"""
    # 检查必填字段
    # 检查格式合规
    # 返回校验结果
```

---

## 六、触发规则汇总

| 场景 | 加载内容 | 调用函数 |
|------|----------|----------|
| 会话启动 | globals + duty-mapping | `load_core()` |
| Agent 路由 | system/agents.yaml | `load_system("agents")` |
| Skill 分层 | system/skills.yaml | `load_system("skills")` |
| 系统项目查询 | system/system-projects.yaml | `load_system("projects")` |
| 系统任务/cron | system/system-tasks.yaml | `load_system("tasks")` |
| 系统主题查询 | system/system-topics.yaml | `load_system("topics")` |
| 用户项目查询 | user/user-projects.yaml | `load_user("projects")` |
| 用户任务处理 | user/user-tasks.yaml | `load_user("tasks")` |
| 用户主题查询 | user/user-topics.yaml | `load_user("topics")` |
| 人员信息查询 | user/persons.yaml | `load_user("persons")` |

---

## 七、与其他 Skill 的关系

| Skill | 调用方式 |
|-------|----------|
| governance-core | 会话启动时调用 `load_core()` |
| governance-task | 查询任务时调用 `load_system("tasks")` 或 `load_user("tasks")` |
| governance-heartbeat | 巡检时调用 `load_system("tasks")` 获取 cron |
| governance-hierarchy | 创建项目/主题时调用配置加载 |
| governance-dispatch | Agent 路由时调用 `load_system("agents")` |

---

## 八、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **1.3.0** | 2026-04-18 | 新增配置模板（globals/duty-mapping/system/user 全量模板），新部署可直接复制初始化 |
| **1.2.1** | 2026-04-11 | 修复：删除 tasks-extension.yaml（防止孤儿task）、删除 master-data.yaml（配置不存在） |
| **1.2.0** | 2026-04-03 | 对齐 governance-core v5.8.0：level 提升至 L2（启动触发） |
| **1.1.0** | 2026-03-30 | 配置文件重命名：system-projects/tasks/topics、user-projects/tasks/topics |
| 1.0.0 | 2026-03-30 | 初始版本：配置分层、加载函数、触发规则 |

---

*版本: 1.4.0 | 更新: 2026-04-23 | 变更: 补充 When to Use / Pitfalls 章节 + frontmatter 增强*

## Related Skills
- [[openclaw-governance-core]] - 核心运行机制，配置加载依赖
- [[openclaw-governance-data]] - 数据治理，配置文件路径管理
- [[openclaw-governance-hierarchy]] - 层级管理，Project/Topic配置