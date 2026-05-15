# T06 实施计划 — pdca.py 精简版 + 轻量级层间传播

> **原 Topic**: N4-P2-T06 通过 BotLearn 优化 OpenClaw Governance（已废弃）
> **新 Topic**: N4-P2-T06 NUCLEUS 新准则实施（Phase 2）
> **上位引用**: NUCLEUS-REQ-SPEC-v1.0 · NUCLEUS-ARCH-v1.0 · NUCLEUS-DESIGN-v1.0 · NUCLEUS-UPGRADE-v1.0
> **架构原则**: pdca.py 精简版 + 轻量级层间传播（不引入 CycleUnit schema）
> **状态**: 规划完成

---

## 一、架构确认

### 1.1 核心原则

**pdca.py 是唯一 Python 工具**，职责：确定性 I/O（读写 pdca/*.yaml）。
**LLM 负责所有推断、执行、判断、决策。**

```
┌─ dispatch ─┐      ┌─ heartbeat ─┐      ┌─ evolution ─┐
│ (任务分发)  │      │ (定时巡检)   │      │ (元治理)     │
└─────┬──────┘      └─────┬───────┘      └─────┬───────┘
      │                   │                   │
      ▼                   ▼                   ▼
    ┌─────────────────────────────────────────┐
    │    governance-nucleus (L4 Skill)         │
    │    SKILL.md 定义 PDCA Harness 规则       │
    │    pdca.py 做确定性状态记录               │
    └──────────────────┬──────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    pdca/*.yaml    pdca/*.yaml    pdca/*.yaml
    (Task级)       (Topic级)      (Project级)
        │              │              │
        ▼              ▼              ▼
    轻量级聚合：扫描同级 yaml 的 verdict → 父级 verdict 自动派生
```

### 1.2 已完成（Phase 0-1）

| 功能 | 状态 | 实现 |
|------|------|------|
| PDCA 状态记录器 | ✅ | pdca.py v2.2.0（p/d/c/a/status/pending/history） |
| ADAS L0-L3 Review | ✅ | c() 内置规则校验 |
| Human-in-the-Loop | ✅ | delegation §10.2 A/B/C/D + 7天超时 |
| 审计出口 | ✅ | audit_eligible + audit-queue + mark-audit |
| 两条触发路径 | ✅ | Path A（直接）+ Path B（heartbeat） |
| Harness 规则 | ✅ | P1/D1/C1/C2/A1 在 SKILL.md |
| consecutive_fails 熔断 | ✅ | get_status() → needs_escalation |
| 原子写入 | ✅ | _save() 先 .tmp 再 os.replace |

### 1.3 Phase 2 新增（本计划范围）

| 功能 | 类型 | 说明 |
|------|------|------|
| **层间传播** | Phase 2 新增 | task verdict 聚合到 topic/project，不引入 CycleUnit |
| **并发上限** | Phase 2 新增 | p() 前置校验，防止超出并发上限 |
| **多粒度调度** | Phase 2 新增 | topic/project/system 级不同触发频率 |
| **知识图谱** | Phase 2 新增 | lessons → knowledge/ 轻量存储 |
| **escalation 集成** | Phase 1 差距 | heartbeat 消费 needs_escalation 信号 |
| **审计集成** | Phase 1 差距 | 审计 heartbeat 完整流程 |

---

## 二、T06 Task 清单

### T06.1 — pdca.py 差距修复（P0）

| # | 内容 | 改动 |
|---|------|------|
| **#1** | escalation 集成：heartbeat 消费 needs_escalation 信号 | nucleus SKILL.md Step 1 增加"consecutive_fails≥3 → 上报 Harold" |
| **#2** | 无 [P] 任务时系统健康检查（REQ-DISPATCH-003） | nucleus SKILL.md Step 1 增加"无 [P] 任务 → 健康检查 → verdict=skip" |
| **#3** | 向后兼容验证（REQ-NF-007） | 编写测试：现有 pdca/*.yaml 能否被 pdca.py 正确读取 |

### T06.2 — 轻量级层间传播（P0）⭐

| 内容 | 说明 |
|------|------|
| **目标** | task verdict 自动聚合到 topic/project 级 |
| **方案** | pdca.py 新增 `aggregate(scope, scope_id)` 函数 |
| **规则** | 所有子项 pass → 父 pass；任一 fail → 父 fail；其余 → partial |
| **存储** | topic/project 级也有 pdca/*.yaml，但不由 LLM 填写，由 aggregate() 自动派生 |
| **触发** | a() 完成后自动调用聚合（scope=task 完成后聚合到 topic） |
| **文件** | pdca.py 新增 aggregate() + a() 末尾调用 |

**聚合规则**：

| 子项组合 | 父项 verdict |
|---------|-------------|
| 全部 pass | pass |
| 任一 fail | fail |
| 部分 pass + 部分 partial | partial |
| 全部 skip | skip |
| 混合 | partial |

### T06.3 — 并发上限约束（P0）

| 内容 | 说明 |
|------|------|
| **目标** | REQ-NF-009 并发上限（Phase 1：task≤10, topic≤5, project≤3） |
| **方案** | pdca.py 新增 `check_concurrency(scope)` 函数 |
| **校验** | p() 调用前执行，扫描 pdca/*.yaml 统计各 scope 下 phase != completed 的数量 |
| **超限** | 返回 `{ok: false, error: '{scope} 并发上限 {N}，当前活跃 {M}，请等待完成'}` |
| **文件** | pdca.py 新增函数 + p() 前置调用 |

### T06.4 — 多粒度调度（P0）

| 内容 | 说明 |
|------|------|
| **目标** | UPGRADE §2.2 多粒度调度 |
| **方案** | 持久化计数器 `config/scheduler_state.yaml` |
| **频率** | task: 每 1 heartbeat (30m)；topic: 每 4 (2h)；project: 每 48 (1d) |
| **实现** | 轻量 `scripts/scheduler_state.py`（只做计数器读写 + 原子写入） |
| **触发** | heartbeat 中读取计数器，判断 scope 是否达到阈值 |

### T06.5 — 知识沉淀（P1）

| 内容 | 说明 |
|------|------|
| **目标** | REQ-KNOWLEDGE-001 + REQ-KNOWLEDGE-004 |
| **方案** | Phase 2 MVP：`knowledge/lessons/` 目录，每份 lesson 一个 .md 文件 |
| **触发** | LLM 在 a() 时传入 lessons，nucleus SKILL.md 指导 LLM 沉淀到 knowledge/ |
| **约束** | Phase 2 笔记 ≤ 500，5000 触发 Plan C 条件 D |
| **老化** | 每周清理孤立笔记（无反向链接） |

### T06.6 — 审计出口集成（P1）

| 内容 | 说明 |
|------|------|
| **目标** | 审计 heartbeat 完整流程 |
| **流程** | `pdca.py audit-queue → LLM 评分 → pdca.py mark-audit → score<80 → LLM 创建 lesson_learned` |
| **文件** | nucleus SKILL.md 新增审计 Step 指引 |

### T06.7 — 集成测试 + 验收（P0）

| 内容 | 说明 |
|------|------|
| **目标** | 端到端验证 |
| **覆盖** | 并发上限 → PDCA 循环 → 层间传播 → 多粒度调度 → 审计出口 → 知识沉淀 |

---

## 三、执行顺序

```
T06.1（差距修复）→ T06.2（层间传播）→ T06.3（并发上限）→ T06.4（多粒度调度）→ T06.5（知识沉淀）→ T06.6（审计集成）→ T06.7（集成测试）
```

---

## 四、与旧架构的区别

| 维度 | 旧架构（已废弃） | 新架构（本计划） |
|------|-----------------|-----------------|
| **核心引擎** | CycleUnit/CycleScheduler/CycleAggregator 三模块 | pdca.py 单文件 |
| **层间传播** | CycleAggregator 类，完整聚合逻辑 | pdca.py aggregate() 轻量函数 |
| **调度** | CycleScheduler，持久化计数器 | 轻量 scheduler_state.py |
| **Python 职责** | 试图建模 LLM 判断逻辑 | 只做确定性 I/O |
| **复杂度** | 10+ Python 文件，~3000 行 | pdca.py ~700 行 + 2 个轻量脚本 |

---

*创建时间：2026-04-18 | 创建人：银月 | 架构确认：pdca.py 精简版 + 轻量级层间传播*
