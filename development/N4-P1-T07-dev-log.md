# N4-P1-T07 开发日志 — Skill 流程化设计

## 开发概览

| 字段 | 值 |
|------|------|
| **Topic** | N4-P1-T07 Skill 流程化设计研究 |
| **Project** | ZT-P015 NUCLEUS 4.0 |
| **执行者** | 银月（Claude Code） |
| **开始日期** | 2026-04-18 |
| **完成日期** | 2026-04-18 |
| **参考文档** | `topics/N4-P1-T07/TOPIC-BRIEF.md` |

---

## Task 完成情况

### T02 — Dispatch 引导入口设计 ✅

**变更文件**: `skills/openclaw-governance/skills/openclaw-governance-dispatch/SKILL.md` (v2.12.0)

**变更内容**:
- 新增 §1.4 Harold 三个"不能"约束（未知 Project、孤儿 Task、孤儿 Topic）
- 新增 §1.5 分层引导架构（L1 归属验证 → L2 Project 选择 → L3 任务类型）
- 新增 §1.6 dispatch-state.json 状态模板（支持状态感知路由）
- 新增 §三.4.1/.2/.3 引导模板（创建 Project/Task/通用意图）
- 更新 §四.1 fallback 引用分层引导

**设计理念来源**: `topics/N4-P1-T07/outputs/dispatch-guidance-design-v2.md`

---

### T03 — PDCA-A 正确理解修正 ✅

**变更文件**: `skills/openclaw-governance/skills/openclaw-governance-core/SKILL.md` (v6.1.7)

**变更内容**:
- 新增 §3.5 PDCA-A 正确理解（Harold 修正）
- 核心：A 之后不仅是复测，而是进入下一个 PDCA 循环
- 下一循环的 P/D/C 必须根据提升要求重新定义，不能简单重复
- 包含两轮 PDCA 对比示例

**理论来源**: `topics/N4-P1-T07/outputs/botlearn-design-analysis.md` §八

---

### T04 — 治理体系P0问题修复 ✅

**变更文件**: `topics/N4-P1-T07/tasks/N4-P1-T07-T04-治理体系P0问题修复/TASK-CARD.md`

**修复记录**: 19 项修复（CRITICAL 4 + HIGH 5 + MEDIUM 6 + LOW 1 + 已知限制 4）

**涉及文件**:
- `pdca.py` — 新增 consecutive_fails 计数器、history API、review_level 过滤
- `nucleus SKILL.md` (v2.5.0) — 幽灵引用修复、Step 1 [V] 状态、阻塞冷却、已知限制
- `governance-core SKILL.md` (v6.1.6) — knowledge 注册表、PDCA-A
- `governance-task SKILL.md` (v6.0.4) — 权威源统一、Issue severity 分级
- `governance-dispatch SKILL.md` (v2.12.0) — 分层引导

---

### T05 — governance-core 命令规范设计 ✅

**新建文件**:
- `skills/openclaw-governance/skills/openclaw-governance-core/core/commands.md` — Command Spec 定义
- `skills/openclaw-governance/skills/openclaw-governance-core/templates/gov-state.json` — 状态模板

**变更文件**: `skills/openclaw-governance/skills/openclaw-governance-core/SKILL.md` (v6.1.8)
- 新增 §八 命令规范索引（引用 core/commands.md）
- 版本历史从 6.1.7 → 6.1.8

**命令类别**: Bootstrap、Skill Loading、State Management、Probe、Configuration、PDCA Integration

**设计参考**: BotLearn `core/commands.md` Command Spec 格式

---

### T06 — heartbeat 试点应用 ✅

**新建文件**:
- `skills/openclaw-governance/skills/openclaw-governance-heartbeat/core/commands.md` — Command Spec 定义

**变更文件**: `skills/openclaw-governance/skills/openclaw-governance-heartbeat/SKILL.md` (v5.7.0)
- 新增 §十一 命令规范索引（引用 core/commands.md）
- 版本从 5.6.0 → 5.7.0

**命令类别**: Scan、Track、Report、NUCLEUS Integration、State、Escalation

---

## 架构决策记录

### ADR-T07-001: Command Spec 格式采用 BotLearn 模式

**决策**: governance skills 的命令规范采用 BotLearn 的 Command Spec 格式（Command/Required/Optional/Returns/State/Errors），而非自定义格式。

**理由**:
1. BotLearn 的格式简洁明了，适合 LLM 理解
2. 不依赖脚本文件（governance 是文件驱动，非脚本驱动）
3. 保持跨 skill 的一致性

### ADR-T07-002: 分层引导优于置信度阈值

**决策**: dispatch 使用分层引导架构（§1.5）替代简单的置信度阈值判断。

**理由**:
1. Harold 明确要求"三个不能"约束，引导是强制性的
2. 置信度阈值（<70% 引导）无法处理"意图明确但归属不明确"的场景
3. 分层引导给了用户结构化的选择路径

### ADR-T07-003: PDCA-A 承上启下而非简单复测

**决策**: PDCA-A 阶段不只是复测验证，而是进入下一个 PDCA 循环的转折点。

**理由**:
1. Harold 明确修正了 BotLearn 的 Recheck 理解
2. 复测只是下一循环中 Check 的一部分
3. 这要求 nucleus 的 a() 必须包含 --next-task 参数

---

## 版本变更汇总

| Skill | 旧版本 | 新版本 | 变更类型 |
|-------|--------|--------|---------|
| governance-dispatch | 2.11.0 | 2.12.0 | 功能增强 |
| governance-core | 6.1.5 | 6.1.8 | 功能增强（3 次递增） |
| governance-nucleus | 2.3.0 | 2.5.0 | 修复增强 |
| governance-task | 6.0.2 | 6.0.4 | 修复增强 |
| governance-heartbeat | 5.6.0 | 5.7.0 | 功能增强 |

---

*创建时间: 2026-04-18 | 创建人: 银月*

---

# N4-P2-T06 开发日志 — 新准则实施

## 架构重构

### 2026-04-18 决策

| 决策 | 内容 |
|------|------|
| **旧架构废弃** | N4-P2-T01 至 T05（基于 CycleUnit/CycleScheduler/CycleAggregator）归档 |
| **新准则** | docs/ 下四文档为唯一真相源（REQ-SPEC + ARCH + DESIGN + UPGRADE-PLAN） |
| **T06 重新规划** | 从 BotLearn 优化改为 NUCLEUS 新准则实施（Phase 2） |
| **CycleAggregator 废弃** | 用户确认不需要，新架构中已大幅简化 |

### 新 Task 清单

| Task | 内容 | 优先级 |
|------|------|--------|
| T06.1 | pdca.py 差距修复（escalation/健康检查/兼容） | P0 |
| T06.2 | 并发上限约束（REQ-NF-009） | P0 |
| T06.3 | 多粒度调度（UPGRADE §2.2） | P0 |
| T06.4 | Obsidian 知识图谱（UPGRADE §2.3） | P1 |
| T06.5 | 审计出口集成 | P1 |
| T06.6 | 集成测试 + 验收 | P0 |

---

*创建时间: 2026-04-18 | 创建人: 银月*
