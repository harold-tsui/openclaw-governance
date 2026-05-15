---
name: dispatching-intents
description: |
  Routing user intents to appropriate governance skills and agents.
  
  Activates when: User message matches intent keywords
  
  Capabilities:
  - Intent recognition and classification
  - Task judgment (when to create task-card)
  - Guiding users with layered architecture
  - Routing to correct skill/agent
  
  Keywords: intent, routing, dispatch, task-judgment, guidance
  
  For detailed design, see:
  - references/dispatch-design.md
  
author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "3.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L1"
  os: ["darwin", "linux"]
  lastRefactor: "2026-04-23"
  tags: ["intent-routing", "dispatch", "task-judgment", "guidance"]
---

# OpenClaw Dispatch - 意图理解与路由

Tags: #governance, #dispatch, #routing, #intent

> **核心职责**：理解用户意图 → 判断是否需要 Task → 路由到正确的 Agent/Skill
> **v3.2.0**: 补充复合意图与优先级判定（§五）

## 何时使用

- **Always**: 每次用户消息到达时，首个评估意图路由的 Skill
- **Explicitly**: 排查消息被路由到错误 Skill 的原因
- **Do NOT use for**: 直接执行任务 — dispatch 仅负责路由，不负责执行

## 常见陷阱

1. **创建项目/任务前必须验证层级**: Harold 的三个"不能"约束 — 不能有未知项目、不能有孤儿 Task-CARD、不能有孤儿 Topic。行动前必须先验证。
2. **聊天消息不应加载 Skill**: 简单问候/对话不需要加载 Skill。路由到"不加载 Skill"以避免消耗上下文。
3. **引导 ≠ 执行**: 用户意图不明确时，提供分层引导（A/B/C/D 选项），而非直接执行可能错误的操作。
4. **显式声明是强制的**: 执行前必须声明 `正在执行：{完整对象名称}（{补充信息}）` — 让用户立即发现理解偏差。

---

## 一、核心定义

### 1.1 Task 判断标准

| 条件 | 是否创建 Task |
|------|--------------|
| 需要 Harold 审批/Review | ✅ 必须创建 |
| 需要跨 Agent 协作 | ✅ 必须创建 |
| 工作量 > 30 分钟 | ✅ 必须创建 |
| 会产生交付物 | ✅ 必须创建 |
| 只是简单问答/聊天 | ❌ 不创建 |

### 1.2 Harold 三个"不能"约束

| 约束 | 规则 |
|------|------|
| **❌ 不能有未知 Project** | 所有 Project 必须在 projects.yaml 注册 |
| **❌ 不能有孤儿 Task-CARD** | Task 必须归属某个 Topic |
| **❌ 不能有孤儿 Topic** | Topic 必须归属某个 Project |

---

## 二、意图分类与路由表

> **详细实现**：[scripts/dispatch_decision_tree.py]({baseDir}/scripts/dispatch_decision_tree.py)

| 意图类型 | 关键词示例 | 路由目标 Skill |
|----------|------------|----------------|
| `create_project` | 创建项目 | governance-hierarchy |
| `create_task` | 创建任务 | governance-task |
| `create_topic` | 创建 Topic | governance-hierarchy |
| `quality_review` | 审核 | governance-quality |
| `data_classify` | 数据分级 | governance-data |
| `delegation_check` | 授权检查 | governance-delegation |
| `execute_task` | 推进、执行任务 | governance-heartbeat |
| `task_complete` | 做完了、任务完成 | governance-heartbeat |
| `task_blocked` | 卡住了、阻塞了 | governance-heartbeat |
| `heartbeat_check` | heartbeat | governance-heartbeat |
| `risk_assess` | 风险评估 | governance-risk |
| `pipeline_run` | 执行流水线 | governance-pipeline |
| `evolution_eval` | 系统评估 | governance-evolution |
| `core_ops` | 启动、加载、配置 | governance-core |
| `config_manage` | 配置修改、参数调整 | governance-config |
| `agent_manage` | Agent 生命周期、创建、权限 | governance-agent |
| `alert_handle` | 告警、通知、提醒 | governance-alert |
| `incident_handle` | 事故、异常、应急 | governance-incident |
| `knowledge_manage` | 知识沉淀、归档、Wiki | governance-knowledge |
| `nucleus_ops` | PDCA 状态、聚合、传播 | governance-nucleus |
| `chat` | 你好、谢谢 | 不加载 Skill |

---

## 三、分层引导架构

> **详细设计**：[references/dispatch-design.md]({baseDir}/references/dispatch-design.md)

```
层级 1：顶层引导（Project/Task 归属验证）
层级 2：已有 Project/Topic 选择引导
层级 3：任务类型引导（如果需要）
```

### 引导触发条件

- 不明确归属 → 引导（提供 A/B/C/D 选项）
- 明确归属 → 不引导，显式声明后执行

### 11 种引导类型

| 引导类型 | 优先级 | 触发关键词 |
|----------|--------|-----------|
| 创建 Project 引导 | **P0** | 创建项目/新建项目 |
| 执行 Task 引导 | **P0** | 帮我完成任务/推进/执行任务 |
| 推进 Task PDCA | **P0** | 推进/执行/继续任务 |
| 创建 Topic 引导 | **P0** | 创建专题 |
| 通用意图引导 | **P1** | 帮我处理 |
| 任务完成→下一步 | **P1** | 做完了 |
| Project 选择引导 | **P1** | 在已有项目上创建 |
| Topic 选择引导 | **P1** | 选择 Topic |
| 检查范围引导 | **P2** | 检查状态 |
| 任务类型引导 | **P2** | 归属明确但类型不清 |
| 任务阻塞→处理 | **P3** | 卡住了 |
| 归档位置引导 | **P3** | 归档这个任务 |

---

## 四、显式声明规范

**显式声明格式**：
```
正在执行：{完整对象名称}（{补充信息}）
```

**核心价值**：
- 用户看到完整信息 → 发现说错了 → 立即纠正
- 避免 Agent 理解偏差

---

## 五、复合意图与优先级判定

当单条意图匹配多个 Skill 时，按以下规则解决冲突：

### 5.1 优先级规则（按顺序判定）

| 优先级 | 规则 | 示例 |
|--------|------|------|
| **1** | L1 > L2 > L3 > L4 | 同意图命中不同层级 Skill，高优先 |
| **2** | 具体意图 > 通用意图 | "审核数据分级" → data（具体） > quality（通用） |
| **3** | 动作词 > 名词词 | "创建项目" → hierarchy（动作匹配） > task（名词匹配） |
| **4** | skills.yaml 触发词精确度 | 触发词越长越精确，优先匹配 |
| **5** | 多 Skill 并行加载 | 以上规则无法判定时，并行加载所有匹配 Skill |

### 5.2 复合意图拆分

当意图包含多个独立子意图时，拆分为独立路由：

```
输入: "创建任务并审核数据分级"
拆分:
  - 意图1: create_task → governance-task
  - 意图2: data_classify → governance-data
  - 意图3: quality_review → governance-quality
执行: 先 task 后 data+quality（task 交付物是审核对象）
```

### 5.3 降级策略

匹配到 3 个以上 Skill 时，仅加载优先级最高的 2 个，其余按需延迟加载。

---

## 六、Skill 加载层级

| 层级 | 代表 Skill | 加载方式 |
|------|-----------|----------|
| **L1** | core | 启动触发 |
| **L2** | dispatch, config | 启动触发 |
| **L2** | task, hierarchy | 意图触发 |
| **L2** | heartbeat | 定时触发 |
| **L3** | quality, data, delegation, risk, nucleus | 按需加载 |
| **L4** | pipeline, evolution | 惰性加载 |

---

## 六、版本历史

| 版本 | 日期 | 叱更 |
|------|------|------|
| **3.0.0** | 2026-04-22 | Skills 最佳实践重构：引导分离(references/)、决策树分离(scripts/)、SKILL.md 精简（631→~200 行）|
| **2.14.0** | 2026-04-19 | N4-P1-T07 T02 补完 — 生命周期引导模板 |
| **2.12.0** | 2026-04-18 | 分层引导架构 |

---

*版本: 3.2.0 | 更新: 2026-04-24 | 变更: 新增 §五 复合意图与优先级判定（5 条优先级规则 + 拆分机制 + 降级策略）*

## Related Skills
- [[openclaw-governance-core]] - 核心运行机制
- [[openclaw-governance-task]] - 任务管理