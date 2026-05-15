---
name: governing-openclaw
description: |
  Loading and coordinating governance skills at agent startup.
  
  Activates when: Agent session starts (L1 core skill)
  
  Capabilities:
  - Loading skills in dependency-driven phases
  - Enforcing phase barriers between loading stages
  - Handling failures with degradation strategies
  - Broadcasting module states across phases
  
  Keywords: startup, bootstrap, phase, barrier, failure-handling, skill-loading
  
  For detailed documentation, see:
  - references/barrier-design.md
  - references/failure-matrix.md
  - references/phase-sequence.md
  
author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "7.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L1"
  os: ["darwin", "linux"]
  lastRefactor: "2026-04-23"
  tags: ["bootstrap", "phase-loading", "skill-loading", "core-runtime"]
prerequisites:
  commands: ["python3"]
---

# Governance Core - 核心运行机制

Tags: #governance, #core, #agent, #skill-loading, #bootstrap

> Agent 启动时必须加载的核心治理能力。
> **v7.1.0**: 补充 When to Use / Pitfalls 章节

## 何时使用

- **Always**: 每次 Agent 会话启动时（L1 强制技能）
- **Explicitly**: 排查 Skill 加载失败、Phase 屏障问题
- **Do NOT load manually**: 由运行时自动加载，无需手动调用

## 常见陷阱

1. **Phase 1 失败 = 致命**: core 或 dispatch 失败会终止整个启动流程。Phase 1 稳定前不要尝试加载其他 Skill。
2. **Hierarchy + delegation 是硬阻塞**: 任一失败都会阻塞 Phase 3（任务加载）。这是设计决策 — 安全性优于可用性。
3. **降级不是静默的**: 模块降级时会记录警告。查看 `references/failure-matrix.md` 对比预期行为与实际行为。
4. **Barrier lock 不可重入**: `PhaseBarrierLock` 不能嵌套使用。并发执行 Phase 会导致死锁。
5. **项目发现是强制的**: 每个 Agent 在会话启动时必须读取 `user-projects.yaml` 和 `system-projects.yaml` — 跳过这是治理违规。

---

## 一、核心路径变量

| 变量 | 值 | 说明 |
|------|-----|------|
| `$OPENCLAW_GOVERNANCE_DIR` | `.system/governance/current` | 治理文件运行目录（openclaw.json env 定义） |
| `$OPENCLAW_LOCAL_WORKSPACE` | 工作空间根目录 | Agent 工作区（openclaw.json env 定义） |

> **注意**：旧版使用的 `$OPENCLAW_GOV_PATH` 和 `$OPENCLAW_WORKSPACE_SYSTEM` 已废弃，统一替换为 `$OPENCLAW_GOVERNANCE_DIR`。

---

## 二、Phase 启动序列

> **详细说明**：[references/phase-sequence.md]({baseDir}/references/phase-sequence.md)

### Phase 结构概览

| Phase | 层级 | 加载方式 | 模块 |
|-------|------|----------|------|
| **Phase 1** | 基础层 | 串行 | core, config, dispatch |
| **Phase 2A** | 依赖第一批 | 并行 | hierarchy, data |
| **Phase 2B** | 依赖第二批 | 并行 | quality, delegation |
| **Phase 3** | 执行层 | 串行 | task, heartbeat, knowledge |
| **Phase 4** | 增强层 | 惰性 | evolution |

### 核心约束

- **Phase 1 失败** → 终止启动（致命）
- **hierarchy/delegation 失败** → 阻塞 Phase 3
- **其他模块失败** → 降级继续（带警告）

---

## 三、Phase 屏障规则

> **详细设计**：[references/barrier-design.md]({baseDir}/references/barrier-design.md)
> **Python 实现**：[scripts/barrier_lock.py]({baseDir}/scripts/barrier_lock.py)

### 屏障类型

| 屏障 | 类型 | 触发条件 |
|------|------|----------|
| **Phase 1→2A** | 硬屏障 | 所有 Phase 1 模块完成 |
| **Phase 2A→2B** | 状态广播 | 所有 2A 模块完成 + 广播快照 |
| **Phase 2B→3** | 条件屏障 | hierarchy/delegation 非 failed |
| **Phase 3→4** | 软屏障 | Phase 3 完成 |

### 状态锁定

使用 `PhaseBarrierLock` 锁定状态快照，Phase 执行期间状态冻结。

```python
# Python 实现见 scripts/barrier_lock.py
with PhaseBarrierLock() as barrier:
    barrier.lock_snapshot(current_module_states)
    execute_phase()
```

---

## 四、失败处理规范

> **详细矩阵**：[references/failure-matrix.md]({baseDir}/references/failure-matrix.md)
> **决策树实现**：[scripts/decision_tree.py]({baseDir}/scripts/decision_tree.py)

### 单点失败处理规则

| 失败节点 | 降级策略 | 是否阻塞 Phase 3 |
|----------|----------|------------------|
| **core** | 终止启动 | ✅ 是（致命） |
| **dispatch** | 终止启动 | ✅ 是（无法路由） |
| **hierarchy** | 严重降级 | ✅ 是 |
| **delegation** | 阻止 task 加载 | ✅ 是（安全风险） |
| **config/data/quality** | 降级继续 | ❌ 否（带警告） |

### 组合失败决策树

使用 `scripts/decision_tree.py` 处理组合失败：
- Rule 1: delegation 失败 → 阻塞 Phase 3（安全优先）
- Rule 2: hierarchy 失败 → 阻塞 Phase 3（架构优先）
- Rule 3: data + quality 失败 → 双降级（数据传播）

---

## 五、Skill 注册表

| Skill | 层级 | 触发类型 | 依赖 |
|-------|------|----------|------|
| governance-core | L1 | 启动触发 | 无 |
| governance-dispatch | L1 | 启动触发 | core |
| governance-config | L2 | 启动触发 | core |
| governance-hierarchy | L2 | 意图触发 | core |
| governance-data | L2 | 意图触发 | core, config |
| governance-quality | L3 | 事件触发 | core, data |
| governance-delegation | L3 | 意图触发 | core, hierarchy |
| governance-task | L2 | 意图触发 | core, hierarchy, quality, data, delegation |
| governance-heartbeat | L2 | 定时触发 | core, hierarchy, task |
| governance-knowledge | L2 | 事件触发 | core, task |
| governance-nucleus | L3 | heartbeat 触发 | core, heartbeat |
| governance-agent | L2 | 意图触发 | core, hierarchy |
| governance-alert | L3 | 事件触发 | core, config |
| governance-incident | L3 | 事件触发 | core, quality, alert |
| governance-pipeline | L3 | 意图触发 | core, task, config |
| governance-risk | L3 | 意图触发 | core, quality, data |
| governance-evolution | L4 | 显式触发 | core, hierarchy, quality |

---

## 六、就绪探针机制

> **详细实现**：[scripts/probe_checker.py]({baseDir}/scripts/probe_checker.py)

| 探针角色 | 阻塞行为 | 失败处理 |
|----------|----------|----------|
| **阻塞型** | 阻止 Phase 进入 | 记录错误，终止 |
| **咨询型** | 不阻塞 | 降级继续，记录警告 |
| **可选型** | 不阻塞 | 静默记录，忽略 |

---

## 七、项目发现与 Agent 职责边界

### 7.1 项目发现协议

**强制规则**：每个 Agent 在每次对话开始时必须执行：

```
Step 1: read .system/governance/current/config/user/user-projects.yaml
Step 2: read .system/governance/current/config/system-projects.yaml
```

### 7.2 Agent 职责边界

**核心原则**：Agent 只能对自己拥有的项目开展项目工作。

| 行为 | 对自己的项目 | 对他人的项目 |
|------|-------------|-------------|
| 提供技术建议 | ✅ 允许 | ✅ 允许 |
| 创建 Task-CARD | ✅ 允许 | ❌ 禁止 |
| 更新 MISSION_BOARD | ✅ 允许 | ❌ 禁止 |
| 启动 PDCA 循环 | ✅ 允许 | ❌ 禁止 |

---

## 八、扩展文档引用

> **关键**：按需读取，避免一次性加载所有文档

| 场景 | 读取文档 |
|------|----------|
| 需要理解屏障设计 | [references/barrier-design.md]({baseDir}/references/barrier-design.md) |
| 需要处理组合失败 | [references/failure-matrix.md]({baseDir}/references/failure-matrix.md) |
| 需要理解 Phase 序列 | [references/phase-sequence.md]({baseDir}/references/phase-sequence.md) |
| 需要理解 PDCA-A | [references/pdca-workflow.md]({baseDir}/references/pdca-workflow.md) |
| 需要执行探针验证 | [scripts/probe_checker.py]({baseDir}/scripts/probe_checker.py) |
| 需要使用屏障锁 | [scripts/barrier_lock.py]({baseDir}/scripts/barrier_lock.py) |

---

## 九、版本历史

| 版本 | 日期 | 叱更 |
|------|------|------|
| **7.1.0** | 2026-04-23 | 补充 When to Use / Pitfalls 章节 + frontmatter 增强（author/tags/prerequisites）|
| **7.0.0** | 2026-04-22 | Skills 最佳实践重构：代码分离(scripts/)、文档分离(references/)、SKILL.md 精简（816→~380 行）|
| **6.2.0** | 2026-04-22 | 新增 §七 项目发现与 Agent 职责边界 |
| **6.1.0** | 2026-04-04 | P0 改进：Phase 屏障完成语义、就绪探针、组合失败传播矩阵 |
| **6.0.0** | 2026-04-03 | 分离设计与执行，保留运行时必需内容 |

---

*版本: 7.1.0 | 更新: 2026-04-23 | 变更: 补充 When to Use / Pitfalls 章节*

## Related Skills
- [[openclaw-governance-config]] - 配置管理技能
- [[openclaw-governance-dispatch]] - 消息分拣与路由