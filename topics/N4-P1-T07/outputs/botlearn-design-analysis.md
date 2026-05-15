# BotLearn 设计理念提炼报告

> **Topic**: N4-P1-T07
> **Task**: N4-P1-T07-T01
> **作者**: 张铁 (cqo)
> **日期**: 2026-04-15
> **版本**: v1.1
> **项目**: ZT-P015 NUCLEUS 4.0

---

## 一、产品设计层面观察（Harold 视角）⭐

### 1.1 引导式提问机制

**Harold 观察**：BotLearn 在不清楚用户需求时，会引导用户选择。

**BotLearn 实现示例**：
```markdown
### State-Aware Routing

5. **Has pending tasks?** → After completing any action, check `tasks` for the next pending task and suggest it.
Example: after benchmark, if `subscribe_channel` is pending, say:
"Want to check out the community? Subscribing to a channel is a great next step."
```

**关键特点**：
- Agent 主动引导用户（"Want to check out the community?"）
- 提供清晰的选项（"say 'subscribe'"）
- 不清楚时不会盲猜，而是明确询问

**可应用到 governance-core**：

| 场景 | 当前行为 | 改进行为（引导式提问） |
|------|----------|----------------------|
| **任务创建模糊** | Agent 自行判断 | "是否创建新任务？还是合并到之前的任务中？" |
| **任务类型不明确** | 默认创建 | "这是交付物类任务还是方法论建设类任务？" |
| **Review 级别不明确** | 默认 L2 | "这个交付物需要 L1 全量检查还是 L2 抽样检查？" |
| **下一步不明确** | 无主动建议 | "Task 已完成，下一步：更新 TOPIC-BRIEF 还是直接归档？" |

**产品设计改进方向**：
```markdown
## 引导式提问机制

当以下条件满足时，Agent 应主动提问引导用户：

1. **任务意图模糊** → "是否创建新任务？还是合并到之前的任务中？"
2. **任务类型不明确** → "这是交付物类任务还是方法论建设类任务？"
3. **Review 级别不明确** → "需要 L1 全量检查还是 L2 抽样检查？"
4. **下一步不明确** → "Task 已完成，下一步建议：更新 TOPIC-BRIEF"

Config gate: `auto_guide_questions` (default: true)
```

---

### 1.2 流程清晰度 + 复测功能（PDCA-A）

**Harold 观察**：BotLearn 的流程足够清晰，包括复测功能，相当于 PDCA 中的 A（Act）过程。

**BotLearn 流程清晰度体现**：

#### 1. Benchmark 流程（完整的闭环）
```markdown
### Full Benchmark Flow
botlearn scan
  → botlearn exam start
  → (for each question: write answer to file → botlearn answer)
  → botlearn exam submit
  → botlearn summary-poll
  → botlearn report
```

#### 2. Install & Recheck 流程（PDCA-A）
```markdown
### Install & Recheck Flow
botlearn recommendations → botlearn install {name} → botlearn scan → botlearn exam start → botlearn exam submit
```

**关键特点**：
- **Recheck = PDCA-A**：安装改进方案后，立即复测验证效果
- **流程图清晰**：每个命令用 `→` 连接，一目了然
- **闭环完整**：Benchmark → Report → Install → Recheck → 新 Report

**对比 governance-core**：

| 维度 | BotLearn | governance-core（当前） |
|------|----------|------------------------|
| **流程图清晰度** | 用 `→` 连接，一目了然 | 协议描述式，不够直观 |
| **PDCA-A 定义** | Recheck 流程清晰定义 | PDCA 提过但无明确流程 |
| **Task-CARD 生命周期** | Task → Report → Done | Task → Task → Task（闭环不够清晰） |
| **Project 生命周期** | 未涉及（专注 Skill） | 有但不够清晰 |

**产品设计改进方向**：

#### Task-CARD 生命周期流程图
```markdown
### Task-CARD Full Lifecycle Flow
Task 创建
  → Task 执行
  → Deliverable 交付
  → Review 检查
  → 问题发现？
    → Yes → 修复 → Recheck（PDCA-A）
    → No → 状态更新
  → TOPIC-BRIEF 同步
  → 归档
```

#### Project 生命周期流程图
```markdown
### Project Full Lifecycle Flow
Project 创建
  → Topic 规划
  → Task 创建
  → Task 执行（循环）
  → Phase 完成
  → 验收
  → 问题发现？
    → Yes → 改进 → Recheck（PDCA-A）
    → No → Project 归档
```

#### Recheck 机制定义
```markdown
### Recheck 机制（PDCA-A）

**触发条件**：
- Task 完成后发现问题
- 改进方案实施后
- Harold 要求验证效果

**Recheck 流程**：
1. 读取原 Task-CARD
2. 识别改进点
3. 执行改进
4. 重新验收
5. 对比前后效果
6. 更新 Task-CARD（新增 Recheck 章节）
```

---

### 1.3 产品设计层面总结

| 产品设计理念 | BotLearn 实现 | governance-core 改进方向 |
|--------------|--------------|--------------------------|
| **引导式提问** | State-Aware Routing + 主动建议 | 建立引导式提问机制 |
| **流程清晰度** | 用 `→` 连接的流程图 | Task-CARD/Project 生命周期流程图 |
| **复测功能** | Install & Recheck Flow | 建立 Recheck 机制（PDCA-A） |
| **闭环完整** | Benchmark → Report → Install → Recheck | Task → Review → Fix → Recheck |

---

## 二、技术设计层面理念

### 2.1 CLI-via-markdown（Agent IS the Runtime）

**定义**：SKILL.md 直接让 Agent 成为 CLI，无需 MCP server 或独立进程。

**BotLearn 实现**：
```markdown
> **YOU ARE THE CLI.** This document turns you into BotLearn's command-line interface.
Every operation is a structured command defined in `core/commands.md`.
Parse user intent → match command → execute with correct parameters → update state → show result.
Do NOT load all modules at once.
```

**关键特点**：
- SKILL.md 是"命令行接口定义文档"
- Agent 解析用户意图 → 匹配命令 → 执行
- 不需要额外的 runtime（Agent 自己就是 runtime）

**对比 governance-core**：
| 维度 | BotLearn | governance-core |
|------|----------|-----------------|
| Runtime | Agent IS the runtime | Agent IS the runtime ✅ |
| 命令定义 | SKILL.md 定义命令路由 | SKILL.md 定义协议流程 |
| 执行方式 | Parse intent → match command → execute | Read protocol → follow steps |

**改进方向**：
- governance-core 可以借鉴"命令路由器"设计
- 建立 Intent → Module Mapping
- 让 Agent 可以"按需加载"而不是"一次性读取全部"

---

### 2.2 懒加载机制（Lazy Loading）

**定义**：只加载需要的模块，不一次性加载所有。

**BotLearn 实现**：
```markdown
## Command Router

Parse your human's intent and load **only** the matching module.

### Intent → Module Mapping

| Intent | Trigger Words | Load Module | Description |
|--------|--------------|-------------|-------------|
| **Setup** | install botlearn, setup, register, claim | `core/setup.md` | First-time setup & registration |
| **Benchmark** | benchmark, score, evaluate | `benchmark/README.md` | Run capability assessment |
```

**关键特点**：
- 建立 Intent → Module Mapping 表
- 用户意图匹配触发词 → 加载对应模块
- 避免一次性加载所有内容

**对比 governance-core**：
| 维度 | BotLearn | governance-core |
|------|----------|-----------------|
| 加载方式 | Intent → Module Mapping | 一次性加载全部 SKILL.md |
| Trigger Words | 明确的触发词列表 | 无明确触发词定义 |
| 模块化 | 按功能拆分多个文件 | 单一大文件 |

**改进方向**：
- governance-core 可以拆分为：
  - `core/commands.md`（命令规范）
  - `core/api-patterns.md`（API 调用模式）
  - `governance/protocol-flow.md`（协议流程）
- 建立 Intent → Module Mapping 表

---

### 2.3 状态感知路由（State-Aware Routing）

**定义**：根据 state.json 决定下一步，而不是每次都问用户。

**BotLearn 实现**：
```markdown
### State-Aware Routing

Before routing, read `<WORKSPACE>/.botlearn/state.json`:

1. **No credentials?** → Route to `core/setup.md` (first-time setup)
2. **No profile?** → Route to `onboarding/onboarding.md`
3. **No benchmark?** → When user mentions benchmark, start benchmark flow
4. **Has benchmark, no solutions?** → Mention skillhunt recommendation
5. **Normal state** → Route based on intent table above
```

**关键特点**：
- 状态文件驱动路由决策
- 不每次都问用户"你想做什么"
- Agent 可以根据状态主动建议下一步

**对比 governance-core**：
| 维度 | BotLearn | governance-core |
|------|----------|-----------------|
| 状态文件 | 统一 state.json | 状态散落在多个文件 |
| 路由决策 | 状态驱动 | 协议驱动 |
| 主动建议 | 根据状态主动建议 | 无 |

**改进方向**：
- governance-core 可以建立统一状态模板：
  - `templates/state.json`（状态模板）
  - 状态字段：`onboarding.completed`、`benchmark.lastScore`、`tasks.*`
- 根据状态驱动路由（如：Task 未完成 → 建议继续执行）

---

### 2.4 Config-First 原则

**定义**：敏感操作前先检查 config.json 权限，而不是直接执行。

**BotLearn 实现**：
```markdown
## Operational Principles

1. **Config-first** — Always check `<WORKSPACE>/.botlearn/config.json` before sensitive operations.
If a permission is disabled, ask your human for confirmation.
```

**Config 结构**：
```json
{
  "auto_post": false,
  "auto_install_solutions": false,
  "auto_update": false
}
```

**关键特点**：
- 权限配置文件控制敏感操作
- `false` → 必须询问用户
- `true` → 可以自动执行

**对比 governance-core**：
| 维度 | BotLearn | governance-core |
|------|----------|-----------------|
| 权限配置 | templates/config.json | 无统一配置 |
| 敏感操作检查 | Config-first 原则 | 依赖 Agent 自主判断 |
| 用户授权 | 配置文件控制 | 口头确认 |

**改进方向**：
- governance-core 可以建立权限配置模板：
  - `templates/config.json`
  - 权限字段：`auto_heartbeat`、`auto_quality_check`、`auto_task_creation`
- 建立 Config-First 原则

---

### 2.5 命令规范格式（Command Spec）

**定义**：每个命令有固定的定义结构，而不是自由描述。

**BotLearn 实现**：
```markdown
### Command Spec Format

Each command below is defined as:

```
Command:     botlearn <command> [--param value]
Script:      botlearn.sh <command> (if available)
API:         METHOD /path
Required:    param1 (type), param2 (type)
Optional:    param3 (type, default)
Returns:     field1, field2
State:       what to update in state.json
Display:     how to show result to user
Errors:      specific error handling
```
```

**示例**：
```markdown
### `botlearn scan`

```
API:         POST https://www.botlearn.ai/api/v2/benchmark/config
Required:    --platform (auto-detect)
Auto-collect:
  installedSkills → ls <WORKSPACE>/skills/
Returns:     configId, skillCount, automationScore
State:       benchmark.lastConfigId = configId
Display:     Tree-format scan summary + "Config uploaded."
Timeout:     Individual commands 5-15s, API upload 30s
```
```

**关键特点**：
- 固定的 9 个字段（Command/Script/API/Required/Optional/Returns/State/Display/Errors）
- 结构化定义，便于 Agent 解析和执行
- 类型安全（每个参数有类型）

**对比 governance-core**：
| 维度 | BotLearn | governance-core |
|------|----------|-----------------|
| 命令定义 | Command Spec（结构化） | 协议描述（自由文本） |
| 参数类型 | 明确类型定义 | 无类型定义 |
| 状态更新 | 明确 state.json 更新字段 | 无明确定义 |
| 错误处理 | 明确错误码和处理动作 | 散落在各处 |

**改进方向**：
- governance-core 可以建立 Command Spec 格式：
  - Command: `heartbeat`
  - Required: 无（自动触发）
  - Returns: `status`, `issues_found`, `recommendations`
  - State: `heartbeat.lastCheck`, `heartbeat.issues[]`
  - Display: Tree-format progress + result box
  - Errors: 统一错误码映射表

---

### 2.6 模板文件机制（Templates）

**定义**：标准化的初始配置模板，而不是手工创建。

**BotLearn 实现**：
```
templates/
├── config.json      ← 权限配置模板
├── credentials.json ← API 凭证模板
└── state.json       ← 状态模板
```

**state.json 模板**：
```json
{
  "version": "0.4.3",
  "agentName": null,
  "onboarding": {
    "completed": false
  },
  "benchmark": {
    "lastSessionId": null,
    "lastScore": null,
    "totalBenchmarks": 0
  },
  "tasks": {
    "onboarding": "pending",
    "run_benchmark": "pending",
    "view_report": "pending"
  }
}
```

**关键特点**：
- 模板文件定义初始结构
- Agent 从模板复制，而不是手工创建
- 版本号字段便于升级管理

**对比 governance-core**：
| 维度 | BotLearn | governance-core |
|------|----------|-----------------|
| 配置文件 | templates/ 目录 | 无模板机制 |
| 初始状态 | 从模板复制 | 手工创建或不存在 |
| 版本管理 | version 字段 | 无 |

**改进方向**：
- governance-core 可以建立模板目录：
  - `templates/state.json`（状态模板）
  - `templates/config.json`（权限配置模板）
  - `templates/heartbeat-state.json`（heartbeat 状态模板）

---

## 三、技术层面对比总结

| 设计理念 | BotLearn 实现 | governance-core 当前 | 改进方向 |
|----------|--------------|---------------------|----------|
| **CLI-via-markdown** | SKILL.md = CLI 定义 | SKILL.md = 协议定义 | 建立命令路由器 |
| **懒加载机制** | Intent → Module Mapping | 一次性加载全部 | 建立模块拆分 + Mapping |
| **状态感知路由** | state.json 驱动路由 | 无状态驱动 | 建立状态模板 |
| **Config-First 原则** | config.json 权限控制 | 无权限配置 | 建立权限模板 |
| **命令规范格式** | Command Spec（9字段） | 协议描述（自由文本） | 建立命令规范格式 |
| **模板文件机制** | templates/ 目录 | 无模板机制 | 建立模板目录 |

---

## 四、可复用的技术设计模式

### 4.1 命令路由器模式（Command Router）

**模式定义**：
```
用户输入
    ↓
Parse intent（解析意图）
    ↓
Match trigger words（匹配触发词）
    ↓
Load only matching module（只加载匹配模块）
    ↓
Execute command（执行命令）
    ↓
Update state（更新状态）
    ↓
Show result（显示结果）
```

**可应用到 governance-core**：
- 用户说"heartbeat"、"巡检" → 加载 `governance/heartbeat-flow.md`
- 用户说"创建任务"、"新建任务" → 加载 `governance/task-create-flow.md`
- 用户说"审核"、"验收" → 加载 `governance/quality-check-flow.md`

---

### 4.2 状态驱动决策模式（State-Driven Decision）

**模式定义**：
```
Agent 启动
    ↓
Read state.json（读取状态文件）
    ↓
if (状态字段 == null):
    → 路由到初始化流程
elif (状态字段 == "pending"):
    → 路径到执行流程
elif (状态字段 == "completed"):
    → 路由到下一步流程
```

**可应用到 governance-heartbeat**：
```json
{
  "heartbeat": {
    "lastCheck": null,
    "issues": [],
    "tasks": {
      "scan_mission_board": "pending",
      "check_quality_tasks": "pending"
    }
  }
}
```

---

### 4.3 权限配置门控模式（Config Gate）

**模式定义**：
```
敏感操作触发
    ↓
Read config.json（读取权限配置）
    ↓
if (权限字段 == false):
    → 询问用户确认
elif (权限字段 == true):
    → 自动执行
```

**可应用到 governance-core**：
```json
{
  "auto_heartbeat": false,     // 心跳巡检需要用户确认
  "auto_quality_check": true,  // 质量审核可自动执行
  "auto_task_creation": false  // 创建任务需要用户确认
}
```

---

## 五、下一步行动建议

### Phase 2：设计改进方案（优先级排序）

| 优先级 | 改进项 | 理由 | 预计工作量 |
|--------|--------|------|-----------|
| **P0** | 建立命令规范格式 | 最核心改进，直接影响流程清晰度 | 2 天 |
| **P0** | 建立状态模板 | 状态驱动路由的基础 | 1 天 |
| **P1** | 建立 Intent → Module Mapping | 实现懒加载的基础 | 2 天 |
| **P1** | 建立 Config-First 原则 | 权限控制的基础 | 1 天 |
| **P2** | 模板目录机制 | 便于版本管理和初始化 | 1 天 |

### Phase 3：试点应用建议

**首选 Skill**：`governance-heartbeat`

**理由**：
- heartbeat 是最简单的 Skill（周期性检查任务）
- 流程清晰（Step 1-7）
- 易于验证效果（是否更流畅清晰）

**改进点**：
1. 建立 heartbeat 命令规范（Command Spec）
2. 建立 heartbeat-state.json 模板
3. 建立 heartbeat Intent → Module Mapping
4. 建立 heartbeat config.json 权限控制

---

## 六、总结

BotLearn 的流程化设计精髓在于（产品设计 + 技术设计）：

### 产品设计层面：
1. **引导式提问机制** → Agent 不清楚时主动询问，引导用户明确需求
2. **流程清晰度** → 用 `→` 连接的流程图，一目了然
3. **复测功能（PDCA-A）** → Install & Recheck Flow，验证改进效果
4. **闭环完整** → Benchmark → Report → Install → Recheck

### 技术设计层面：
1. **结构化命令定义**（Command Spec）→ Agent 知道“怎么执行”
2. **状态驱动路由**（State-Aware Routing）→ Agent 知道“下一步做什么”
3. **懒加载机制**→ 减少 context 开销
4. **权限门控**（Config-First）→ Agent 知道“什么时候需要问用户”

这些设计理念可以逐步应用到 governance skills，让我们的流程也能如 BotLearn 一样流畅清晰。

---

*Version: v1.0 | 创建日期: 2026-04-15 | 作者: 张铁 (cqo)*
---

## 七、新增：Dispatch 引导入口设计（Harold 建议）⭐

### 7.1 当前 dispatch 设计（v2.10.0）

```markdown
## 核心职责
理解用户意图 → 判断是否需要 Task → 路由到正确的 Agent/Skill
```

**当前问题**：
- 只做分发，不做引导
- 用户需求不明确时，降级到闲聊或猜测意图
- 无主动提问机制

### 7.2 改进后 dispatch（引导式 Routing）

| 维度 | 当前 dispatch | 改进后 dispatch（引导式）|
|------|--------------|-------------------------|
| **职责定位** | 意图识别 + 路由分发 | 意图识别 + 引导澄清 + 路由分发 |
| **用户需求不明确时** | 降级到闲聊或猜测意图 | 主动提问引导用户 |
| **置信度阈值** | 无明确阈值 | 置信度 < 70% → 提问引导 |
| **示例** | 无明确引导 | "是否创建新任务？还是合并到之前的任务中？" |

### 7.3 引导式 Routing 流程

```markdown
用户消息
    ↓
意图识别（计算置信度）
    ↓
if 置信度 < 70%:
    → 提问引导用户明确意图
    → 等待用户回复
    → 重新识别意图
elif 置信度 >= 70%:
    → 正常路由流程
```

### 7.4 引导式提问示例

| 场景 | 当前行为 | 改进后行为（引导式提问） |
|------|----------|-------------------------|
| **任务意图模糊** | Agent 自行判断 | "是否创建新任务？还是合并到之前的任务中？" |
| **任务类型不明确** | 默认创建 | "这是交付物类任务还是方法论建设类任务？" |
| **Review 级别不明确** | 默认 L2 | "需要 L1 全量检查还是 L2 抽样检查？" |
| **下一步不明确** | 无主动建议 | "Task 已完成，下一步建议：更新 TOPIC-BRIEF" |
| **多个意图冲突** | 取最高置信度 | "你是想要 A 还是 B？请明确一下" |

### 7.5 dispatch 改进优先级

**优先级**：P0（核心入口改进）

**预计工作量**：2-3 天

**改进要点**：
1. 新增"引导式 Routing"章节
2. 定义置信度阈值（< 70% → 提问）
3. 建立引导式提问示例表
4. 新增 `auto_guide_questions` 配置项

---

## 八、新增：PDCA-A 正确理解（Harold 修正）⭐

### 8.1 BotLearn 的 Recheck 设计

```markdown
### Install & Recheck Flow
botlearn recommendations → botlearn install {name} → botlearn scan → botlearn exam start → botlearn exam submit
```

**BotLearn 的理解**：Recheck = A（Act），复测验证效果

### 8.2 Harold 的正确理解

**Harold 观察点**：A 之后进入下一个 PDCA 循环，不只是 recheck。根据提升要求，P、D、C 的要求都可能不一样了。

| PDCA 阶段 | BotLearn Recheck | 正确的 PDCA-A |
|-----------|------------------|---------------|
| **A (Act)** | Recheck（复测验证） | ✅ 复测 + 进入下一循环 |
| **下一循环的 P** | 无变化（同样的 benchmark） | ⚠️ 根据提升要求重新 Plan |
| **下一循环的 D** | 无变化（同样的 exam） | ⚠️ 根据新 Plan 调整 Do |
| **下一循环的 C** | 无变化（同样的 report） | ⚠️ 根据新 D 调整 Check |

### 8.3 举例说明

假设 Benchmark 发现"Memory" 维度得分低（10/20）：

**当前 PDCA 循环**：
- P：测试 Memory 能力
- D：回答 Memory 相关问题
- C：得分 10/20，发现问题
- A：安装 memory-enhancement skill

**下一 PDCA 循环**（Harold 观点）：
- P：重新定义测试目标（可能不只是 Memory，还要测试"Memory + Reasoning" 结合能力）
- D：根据新 P 调整执行方式
- C：新的验收标准（不只看分数，还要看实际应用效果）
- A：根据新 C 决定下一步

### 8.4 governance-core 应用

```
Task 完成后发现问题（PDCA-C）
    ↓
A (Act)：执行改进
    ↓
下一 PDCA 循环：
    P：重新定义验收标准（根据提升后的要求）
    D：执行新标准下的工作
    C：用新标准验收
    A：根据新 C 决定下一步
```

### 8.5 PDCA Full Cycle Flow（含下一循环）

```markdown
**当前循环**：
Plan → Do → Check →发现问题？
    → Yes → Act（改进）
    → No → 状态更新 → 归档

**下一循环**（Act 之后）：
新 Plan（根据提升要求重新定义）→ 新 Do → 新 Check → 新 Act

**关键点**：
- A 之后不只是 Recheck，而是进入全新的 PDCA 循环
- 新循环的 P/D/C 根据提升后的要求重新定义
- 不假设"同样的标准再测一次"
```

### 8.6 改进优先级

**优先级**：P0（核心理论修正）

**预计工作量**：1 天（更新 governance-core SKILL.md）

---

## 九、总结（更新版）

BotLearn 的流程化设计精髓（产品设计 + 技术设计 + Harold 修正）：

### 产品设计层面：
1. **引导式提问机制** → Agent 不清楚时主动询问，引导用户明确需求
2. **流程清晰度** → 用 `→` 连接的流程图，一目了然
3. **复测功能（PDCA-A）** → Install & Recheck Flow，验证改进效果
4. **闭环完整** → Benchmark → Report → Install → Recheck

### Harold 修正（产品设计）：
1. **Dispatch 引导入口** → 不只是分发，而是引导用户明确需求
2. **PDCA-A 正确理解** → A 之后进入下一循环，P/D/C 根据提升要求重新定义

### 技术设计层面：
1. **结构化命令定义**（Command Spec）→ Agent 知道"怎么执行"
2. **状态驱动路由**（State-Aware Routing）→ Agent 知道"下一步做什么"
3. **懒加载机制**→ 减少 context 开销
4. **权限门控**（Config-First）→ Agent 知道"什么时候需要问用户"

---

*Version: v1.1 | 更新日期: 2026-04-15 | 更新人: 张铁 (cqo) | 更新内容: 新增 Dispatch 引导入口 + PDCA-A 正确理解*
