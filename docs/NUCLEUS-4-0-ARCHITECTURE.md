# NUCLEUS 4.0 — 架构与实施文档

> **文档编号**: NUCLEUS-4.0-ARCH-v1.1
> **创建日期**: 2026-04-18
> **修订日期**: 2026-05-06
> **权威性**: 本文件是 NUCLEUS 4.0 的唯一架构权威源（合并自 REQ-SPEC + ARCH + DESIGN + UPGRADE 四份 v2.0 文档）
> **评审状态**: 待 Harold 评审
> **引用格式**: `NUCLEUS-4.0-ARCH-v1.1 §{章节}`

---

## 一、项目概述

### 1.1 项目名称

**NUCLEUS** — **N**odes of **U**nified **C**ollaboration, **L**earning, **E**volution & **U**se **S**ystem
中文释义：灵枢计划（人体经络中枢，意为 AI 协作操作系统的核心引擎）

### 1.2 项目愿景

> **让 Harold 的认知与判断，通过 AI 团队被持续放大、沉淀、复用——构建一个自我进化的知识型财富引擎。**

### 1.3 核心飞轮

| 飞轮 | 链路 |
|------|------|
| **外飞轮**（Harold 时间解放） | Harold 判断 → Agent 执行 → 交付物沉淀 → 知识库丰富 → Agent 质量提升 → Harold 授权扩大 → Harold 时间释放 → 财富目标加速 |
| **内飞轮**（洞察驱动） | 洞察外部 → 洞察自我 → 洞察不足 → 洞察时机 → 产生新洞察 |

### 1.4 六大模块

| 模块 | 关注点 | 说明 |
|------|--------|------|
| MODULE 1 | WHO | 团队宪法 — Agent 身份、职责边界、路由规则 |
| MODULE 2 | HOW | 工作流程操作系统 — Task-CARD 生命周期、PDCA 闭环 |
| MODULE 3 | WHAT | 数据与知识治理 — DL/LL 条目管理、知识图谱 |
| MODULE 4 | TRUST | 人机协作与信任模型 — 决策自动化分级（L0-L5）、Review 级别（L0-L3） |
| MODULE 5 | GROW | 进化机制 — 自我感知、自我决策、自我学习 |
| MODULE 6 | WHY | 财富转化引擎 — Harold 时间解放的量化转化 |

### 1.5 项目 Lineage

| 项目 | 版本 | 日期 | 说明 |
|------|------|------|------|
| ZT-P000_NUCLEUS | v1.0 | 2026-02 | 灵枢计划原始项目，建立使命/飞轮/六大模块 |
| ZT-P009_NUCLEUS-2-0 | v3.0 | 2026-03 | Harness Engineering 实现，11 Skill 上线 |
| **ZT-P015_NUCLEUS-4-0** | **v4.0.0** | **2026-04** | **pdca.py 精简版架构，Phase 1-2 已实施** |

---

## 二、利益相关方分析

| 角色 | 身份 | 核心需求 | 痛点 |
|------|------|---------|------|
| **Harold** | 创始人/最终决策者 | 减少"解释任务"时间 < 30min/天；只在关键节点介入决策 | 模糊语言下任务导致反复沟通；知识未沉淀导致重复解释 |
| **银月** | PMO/Chief of Staff | 全局协调、任务分发、质量抽检、Harold 日报 | 跨 Agent 协调复杂；任务状态不一致；质量问题滞后发现 |
| **张铁 (CQO)** | 质量官/PM | 质量标准制定、自动化分级评估、PDCA 引擎维护 | 质量体系与执行脱节；审计缺乏自动化工具 |
| **菡云芝 (CTO)** | 技术官 | 代码质量、架构决策、技术调研 | 技术债积累；架构变更影响范围难以评估 |
| **辛如音 (CDO)** | 数据官 | 数据治理、知识归档、主数据管理 | 数据标准不统一；知识孤岛 |
| **其他 Agent** | 各领域专家 | 明确职责、减少上下文切换、专注领域工作 | 任务边界不清；被路由到非擅长领域 |

---

## 三、架构演进史

### 3.1 三代架构迭代

```
v1.0 (ZT-P000)          v3.0 (ZT-P009)           v4.0 (ZT-P015)
┌──────────────┐        ┌──────────────┐         ┌──────────────┐
│ 六大模块定义  │   →    │ 11 Skills    │    →    │ pdca.py      │
│ 双飞轮愿景    │        │ DOD+RG+Pipe  │         │ + SKILL.md   │
│ 灵枢计划      │        │ 闭环治理     │         │ + heartbeat  │
└──────────────┘        └──────────────┘         └──────────────┘
 定义"做什么"             实现"怎么做"              回归"做什么最小"
```

### 3.2 架构问题与修正

| 版本 | 问题 | 修正 |
|------|------|------|
| v4.0 Phase 1 | CycleUnit/CycleScheduler/CycleAggregator 过度工程化，Python 试图建模 LLM 判断逻辑 | v2.0.0：单文件 pdca.py 替代整个复杂系统 |
| v4.0 Phase 1 | 10 处逻辑不自洽 | v2.0.0：明确分工——Python 只做 I/O，LLM 负责推断 |
| v2.0.0 | c() 未校验 ADAS 规则 | v2.1.0：L0/L1 拒 pending，L3 首次必须 pending |
| v2.0.0 | p() 实现与文档冲突 | v2.0.0：修复 cycle 创建逻辑 |
| v2.0.0 | Step 0 缺少 pdca.py c 调用 | v2.1.0：Harold 回复后先 c() 再 Act |
| v2.1.0 | Act 阶段硬编码 LL/DL 触发 | v2.2.0：移除，属 governance-knowledge 关注点 |
| v2.x Phase 1 | 无层间传播机制 | Phase 2：pdca.py aggregate() 轻量聚合 |
| v2.x Phase 1 | 无并发控制 | Phase 2：pdca.py check_concurrency() 前置校验 |
| v2.x Phase 1 | 单粒度调度（仅 task） | Phase 2：scheduler_state.py 多粒度 |
| v4.0.0 | Path traversal 安全风险 | v4.0.0：三层防御（_validate_id + PDCA_DIR 前缀 + 拒绝路径遍历） |
| v4.0.0 | 数据完整性不可验证 | v4.0.0：SHA-256 checksum + verify-integrity 命令 |
| v4.0.0 | 配置硬编码 | v4.0.0：config/pdca_config.yaml 外部化 |

### 3.3 当前版本

| 组件 | 版本 | 说明 | 状态 |
|------|------|------|------|
| pdca.py | v4.0.0 | PDCA 状态记录器 + 安全加固 + 运维命令 | ✅ 已实施 |
| scheduler_state.py | v1.0.0 | 轻量多粒度调度计数器 | ✅ 已实施 |
| governance-nucleus SKILL.md | v4.0.0 | PDCA Harness 执行协议 | ✅ 已实施 |
| governance-delegation | v4.2.0 | Human-in-the-Loop A/B/C/D 协议 | ✅ 已实施 |
| governance-heartbeat | v5.7.0 | 分布式巡检协议 | ✅ 已实施 |
| governance-task | v6.0.4 | review_deliverable 与 PDCA Check 串联 | ✅ 已实施 |
| governance-quality | v3.2.0 | DOD + Review-Gate | ✅ 已实施 |

---

## 四、当前架构

### 4.1 总体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw 平台                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ dispatch     │    │ heartbeat    │    │ evolution    │   │
│  │ (任务分发)    │    │ (定时巡检)    │    │ (元治理)     │   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘   │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              governance-nucleus (L4)                  │   │
│  │  ┌────────────┐    ┌────────────┐    ┌────────────┐  │   │
│  │  │ Path A     │    │ Path B     │    │ 审计出口    │  │   │
│  │  │ 直接 PDCA  │    │ heartbeat  │    │ L0/L1 pass │  │   │
│  │  │ (同会话)    │    │ 定时触发   │    │ → audit    │  │   │
│  │  └─────┬──────┘    └─────┬──────┘    └─────┬──────┘  │   │
│  │        └─────────────────┼─────────────────┘          │   │
│  │                          ▼                            │   │
│  │  ┌────────────────────────────────────────────────┐   │   │
│  │  │          pdca.py (PDCA 状态记录器)               │   │   │
│  │  │  p/d/c/a + aggregate + check_concurrency       │   │   │
│  │  │  + verify-integrity + health-check + archive   │   │   │
│  │  └────────────────────┬───────────────────────────┘   │   │
│  │                       │                                │   │
│  │  ┌────────────────────┼────────────────────────────┐  │   │
│  │  │ scheduler_state.py │ (多粒度调度计数器)          │  │   │
│  │  └────────────────────┼────────────────────────────┘  │   │
│  │                       │                                │   │
│  └───────────────────────┼────────────────────────────────┘   │
│                          │                                     │
│  ┌───────────────────────▼────────────────────────────────┐   │
│  │              pdca/{task_id}.yaml (持久化状态)            │   │
│  │              config/pdca_config.yaml (外部化配置)        │   │
│  │              config/scheduler_state.yaml (调度计数器)    │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐  │
│  │ delegation │  │ knowledge  │  │   task     │  │ quality│  │
│  │ (HitL/A-D) │  │ (DL/LL)    │  │ (lifecycle)│  │ (DOD)  │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 组件关系

| 组件 | 职责 | 与 nucleus 的关系 |
|------|------|------------------|
| **pdca.py** | PDCA 状态记录（确定性 I/O）+ 层间传播 + 并发控制 + 安全校验 + 运维 | 唯一 Python 工具 |
| **scheduler_state.py** | 多粒度调度计数器（原子读写） | heartbeat 集成，决定各 scope 触发时机 |
| **governance-heartbeat** | 定时巡检协议 | 触发 Path B PDCA（Step 3a） |
| **governance-delegation** | 决策自动化分级 + HitL 协议 | L3 Review 引用 §10.2 A/B/C/D |
| **governance-knowledge** | DL/LL 管理 | 审计 <80 时 create_lesson_learned() |
| **governance-task** | Task 生命周期 | task-card 创建/状态派生 |
| **governance-quality** | DOD + Review-Gate | PDCA Check 在 L2/L3 场景触发 |
| **governance-evolution** | 元治理（L4） | 触发 Path A PDCA，决策"改什么" |

### 4.3 两条触发路径

| 路径 | 触发方 | 场景 | nucleus 的角色 |
|------|--------|------|----------------|
| **Path A** | governance-evolution / dispatch | 用户显式请求或紧急任务 | 由 evolution 按需启动，同会话立即执行 |
| **Path B** | governance-heartbeat cron | 后台自动 PDCA 循环 | 独立运行，scheduler_state.py 控制多粒度 |

---

## 五、数据流设计

### 5.1 PDCA 主数据流

```
task-card (§一/§三/§五)
    ↓ 读取
LLM Plan → pdca.py p() → pdca/{id}.yaml (p 段 + SHA-256 checksum)
    ↓
LLM Do   → pdca.py d() → pdca/{id}.yaml (d 段)
    ↓
CQO Review → sessions_spawn(cqo) → CQO-{TASK_ID}-{TIMESTAMP}.md
    ↓ (pass → 继续; revise/reject → 退回 Do)
LLM Check → pdca.py c() → pdca/{id}.yaml (c 段 + audit_eligible)
    ↓
LLM Act  → pdca.py a() → pdca/{id}.yaml (a 段 + completed)
    ↓
a() 自动触发 aggregate() → pdca/_state.yaml (层间传播)
    ↓
MISSION_BOARD 更新（写穿透规则 A2）
```

### 5.2 审计数据流

```
L0/L1 pass → audit_eligible=true (自动)
    ↓
审计 heartbeat → pdca.py audit-queue → 待审计队列
    ↓ (包含 dl_refs, p_summary, d_summary, evidence)
LLM 评分 → pdca.py mark-audit --score {0-100}
    ↓
score >= 80 → 记录通过
score < 80  → has_problem=true → governance-knowledge.create_lesson_learned()
    ↓ (质疑 dl_refs 中的 DL 条目)
DL 置信度降低 → 下次 LLM 使用该 DL 时无法自动化
```

### 5.3 Human-in-the-Loop 数据流

```
L3 Check → verdict=pending → pdca/{id}.yaml (phase=check)
    ↓
feishu_post → Harold DM (A/B/C/D 格式)
    ↓ (等待 7 天)
Harold 回复 A → LLM 解析为 pass
    ↓
pdca.py c() --verdict pass --level L3 → phase=act
    ↓
pdca.py a() → phase=completed
    ↓
知识沉淀 (delegation §10.5)
```

### 5.4 多粒度调度数据流

```
heartbeat 触发
    ↓
scheduler_state.py bump → 递增所有计数器
    ↓
scheduler_state.py check → 返回应触发的 scope 列表
    ↓
task(每1h), topic(每4h), project(每48h), system(每96h)
    ↓
各 scope 触发时 → pdca.py aggregate → 层间传播
```

---

## 六、功能性需求

### 6.1 PDCA 闭环引擎（核心需求）

| 需求 ID | 描述 | 优先级 | 实施状态 |
|---------|------|--------|---------|
| REQ-PDCA-001 | 系统必须支持 Plan → Do → Check → Act 四阶段循环 | P0 | ✅ |
| REQ-PDCA-002 | 每个 PDCA 循环必须持久化到文件（YAML），支持跨会话恢复 | P0 | ✅ |
| REQ-PDCA-003 | Python 只做确定性状态记录，LLM 负责所有推断、执行、判断、决策 | P0 | ✅ |
| REQ-PDCA-004 | 支持同一任务多轮 PDCA 迭代，直至 verdict=pass 且验收标准全部满足 | P0 | ✅ |
| REQ-PDCA-005 | 连续 3 次 verdict=fail 时自动上报 Harold 介入 | P1 | ✅ |

### 6.2 Review 级别体系（ADAS 分级）

| 需求 ID | 描述 | 优先级 | 实施状态 |
|---------|------|--------|---------|
| REQ-REVIEW-001 | L0：免审，自动通过 | P0 | ✅ |
| REQ-REVIEW-002 | L1：LLM 自验收，逐项自查验收标准 | P0 | ✅ |
| REQ-REVIEW-003 | L2：银月抽样核查（20-30%），抽中 pending，未抽中 pass | P0 | ✅ |
| REQ-REVIEW-004 | L3：Harold 全量审批，首次 Check 必须 verdict=pending | P0 | ✅ |
| REQ-REVIEW-005 | L0/L1 不允许 verdict=pending（自验收，无需人工介入） | P0 | ✅ |
| REQ-REVIEW-006 | L3 首次 Check 必须 pending，Harold 回复后再次调用 c() 记录最终结论 | P0 | ✅ |

### 6.3 Human-in-the-Loop（人工审批协议）

| 需求 ID | 描述 | 优先级 | 实施状态 |
|---------|------|--------|---------|
| REQ-HITL-001 | L3 Review 必须通过结构化格式（A/B/C/D）向 Harold 发出审批请求 | P0 | ✅ |
| REQ-HITL-002 | A = 批准，B = 有条件批准，C = 拒绝，D = 需要更多信息 | P0 | ✅ |
| REQ-HITL-003 | 7 天无回复自动升级为超时状态（is_overdue=true） | P0 | ✅ |
| REQ-HITL-004 | 超时后 MISSION_BOARD 对应条目升级为 [!]，重新通知 Harold | P0 | ✅ |
| REQ-HITL-005 | Harold 回复后自动解析 A/B/C/D 为 pass/partial/fail verdict | P0 | ✅ |

### 6.4 审计出口

| 需求 ID | 描述 | 优先级 | 实施状态 |
|---------|------|--------|---------|
| REQ-AUDIT-001 | L0/L1 pass 自动标记 audit_eligible=true | P0 | ✅ |
| REQ-AUDIT-002 | 外部审计 heartbeat 可通过 audit-queue 获取待审计交付物列表 | P0 | ✅ |
| REQ-AUDIT-003 | 审计评分 < 80 时自动标记 has_problem=true | P0 | ✅ |
| REQ-AUDIT-004 | 评分 < 80 时触发 governance-knowledge.create_lesson_learned() | P0 | ✅ |
| REQ-AUDIT-005 | 审计结果可追溯至 Plan 阶段引用的 dl_refs | P1 | ✅ |

### 6.5 层间传播（Phase 2）

| 需求 ID | 描述 | 优先级 | 实施状态 |
|---------|------|--------|---------|
| REQ-AGG-001 | a() 完成后自动触发 aggregate()，将 task verdict 聚合到 topic/project | P0 | ✅ |
| REQ-AGG-002 | 全 pass → pass，任一 fail → fail，混合 → partial | P0 | ✅ |
| REQ-AGG-003 | 父级 pdca yaml 由 aggregate() 自动派生，不由 LLM 填写 | P0 | ✅ |
| REQ-AGG-004 | 增量聚合：仅当子项 verdict 变化时更新父级 | P1 | ✅ |

### 6.6 并发控制（Phase 2）

| 需求 ID | 描述 | 优先级 | 实施状态 |
|---------|------|--------|---------|
| REQ-CONC-001 | task 级并发上限 ≤10，topic ≤5，project ≤3 | P0 | ✅ |
| REQ-CONC-002 | p() 调用前执行 check_concurrency() 前置校验 | P0 | ✅ |
| REQ-CONC-003 | 超限返回错误信息，阻止新建 cycle | P0 | ✅ |

### 6.7 安全与运维（v4.0.0）

| 需求 ID | 描述 | 优先级 | 实施状态 |
|---------|------|--------|---------|
| REQ-SEC-001 | Path traversal 三层防御（_validate_id + PDCA_DIR 前缀 + 拒绝遍历字符） | P0 | ✅ |
| REQ-SEC-002 | SHA-256 checksum：每次 _save() 计算并写入 yaml，verify-integrity 校验 | P0 | ✅ |
| REQ-SEC-003 | 配置外部化：config/pdca_config.yaml（限制/超时/聚合参数） | P1 | ✅ |
| REQ-OPS-001 | health-check 命令：files/pending/checksum/concurrency 概览 | P1 | ✅ |
| REQ-OPS-002 | verify-integrity 命令：校验单文件或全部 PDCA 文件 SHA-256 | P1 | ✅ |
| REQ-OPS-003 | archive 命令：归档已完成且 >30 天的 PDCA 文件 | P1 | ✅ |
| REQ-OPS-004 | pending 三级升级：正常 → 逾期 → 严重逾期 | P1 | ✅ |

---

## 七、非功能性需求

### 7.1 零数据库架构

| 需求 ID | 描述 | 约束 |
|---------|------|------|
| REQ-NF-001 | 所有数据以文件形式存储（.md / .yaml / .jsonl） | 不使用任何数据库 |
| REQ-NF-002 | 文件读写保证原子性（先写 .tmp 再 rename） | 防止并发损坏 |
| REQ-NF-003 | 人类和 LLM 可直接读写文件 | 无需专用工具解析 |
| REQ-NF-004 | 天然支持 git 版本控制 | 所有变更可追溯 |

### 7.2 性能指标

| 指标 | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|
| 自动化率 | ≥30% | ≥60% | ≥90% |
| 准确率 | ≥80% | ≥85% | ≥90% |
| 响应时间 | ≤5min | ≤2min | ≤30s |
| 知识覆盖率 | ≥50% | ≥70% | ≥90% |
| Heartbeat/Task 比例 | ≤1.5:1 | ≤1.2:1 | ≤1.1:1 |

### 7.3 安全边界

| 需求 ID | 描述 |
|---------|------|
| REQ-NF-008 | max_cycles 限制防止无限循环（默认 max_cycles_per_task=20，可配置） |
| REQ-NF-009 | 并发上限约束（task≤10, topic≤5, project≤3, system=1） |
| REQ-NF-010 | 操作白名单限制（Phase 3 自主决策仅在安全范围内） |

### 7.4 向后兼容

| 需求 ID | 描述 |
|---------|------|
| REQ-NF-005 | 架构升级不影响现有 Agent 功能 |
| REQ-NF-006 | Skill 接口升级必须保持向后兼容（废弃接口保留 1 个版本过渡期） |
| REQ-NF-007 | 历史 pdca YAML 文件可被新版本正确读取 |

---

## 八、接口契约

### 8.1 pdca.py CLI 接口

| 命令 | 必填参数 | 选填参数 | 输出 |
|------|---------|---------|------|
| `p` | --task-card-id, --summary | --criteria, --task-card-path, --dl-refs, --topic-id, --project-id | {ok, cycle_index, phase} |
| `d` | --task-card-id, --summary, --status | --blocker | {ok, cycle_index, phase, status} |
| `c` | --task-card-id, --verdict | --level, --evidence | {ok, cycle_index, phase, verdict, needs_act} |
| `a` | --task-card-id, --summary | --next-task, --lessons | {ok, cycle_index, phase, next_task} |
| `status` | --task-card-id | - | {task_card_id, cycles_total, current_phase, ...} |
| `history` | --task-card-id | - | {task_card_id, cycles: [...]} |
| `pending` | - | - | [{task_card_id, cycle_index, review_level, days_waiting, is_overdue, ...}] |
| `audit-queue` | - | - | [{task_card_id, cycle_index, dl_refs, p_summary, d_summary, ...}] |
| `mark-audit` | --task-card-id, --cycle-index, --score | --issues | {ok, score, has_problem, dl_refs, next_action} |
| `aggregate` | - | --triggered-by, --mode | {ok, scope, scope_id, verdict, children_count, child_verdicts} |
| `check-concurrency` | - | --scope, --scope-id | {ok, scope, active_count, limit} |
| `verify-integrity` | - | --task-card-id | {ok, checked, valid, invalid, details} |
| `health-check` | - | - | {ok, files, pending, checksum_ok, ...} |
| `archive` | - | --older-than-days, --dry-run | {ok, archived_count, ...} |

### 8.2 scheduler_state.py CLI 接口

| 命令 | 参数 | 输出 |
|------|------|------|
| `read` | - | {tick, task_tick, topic_tick, project_tick, system_tick} |
| `bump` | - | {tick, task_tick, topic_tick, project_tick, system_tick} |
| `check` | - | [{scope, threshold, current_tick, should_trigger}] |
| `reset` | scope_id | {ok, scope, tick_reset_to} |

### 8.3 YAML 存储格式

```yaml
# pdca/{task_card_id}.yaml
task_card_id: T1.1
task_card_path: /path/to/T1.1_TASK-CARD.md
topic_id: T06
project_id: ZT-P015
version: "1.0"
checksum: "sha256:abcdef..."        # v4.0.0 新增：完整性校验
cycles:
  - cycle_index: 1
    started_at: 2026-04-16T09:00:00Z
    completed_at: 2026-04-16T09:30:00Z
    phase: completed
    p:
      timestamp: 2026-04-16T09:00:00Z
      summary: "本轮目标：实现功能 X"
      acceptance_criteria: ["测试通过", "文档更新"]
      dl_refs: ["DL-2026-001", "DL-2026-002"]
    d:
      timestamp: 2026-04-16T09:10:00Z
      summary: "完成功能 X，修改了 foo.py"
      status: completed
      blocker: null
    cqo_review:                           # v8.1 新增：CQO 合规闸门
      timestamp: 2026-04-16T09:12:00Z
      result: pass                        # pass / revise / reject
      report_path: "10_Projects/ZT-P015/T01/deliverables/CQO-T1.1-20260416T091200Z.md"
      revise_count: 0                     # 同一 cycle 内 revise 次数
      issues: []                          # CQO-XX 不通过项列表
    c:
      timestamp: 2026-04-16T09:20:00Z
      verdict: pass
      review_level: L1
      evidence: ["标准A: 通过", "标准B: 通过"]
      audit_eligible: true
      audit_result:                    # mark_audit() 写入
        timestamp: null
        score: null
        issues: null
        has_problem: null
    a:
      timestamp: 2026-04-16T09:30:00Z
      summary: "功能 X 完成，下一任务 T1.2"
      next_task: T1.2
      lessons: ["标准B 需提前确认"]
```

### 8.4 Phase 推进规则

| 调用 | 前置条件 | phase 变化 |
|------|---------|-----------|
| `p()` | 无 cycle 或上一 cycle=completed/check(pending) | → plan（新建 cycle） |
| `p()` | 上一 cycle=plan/do/act | → plan（复用 cycle） |
| `d()` | cycle 存在 | → do |
| `cqo_review` | Do 完成，自动触发 | → cqo_review |
| `cqo_review` | pass | → check |
| `cqo_review` | revise/reject | → do（退回，同一 cycle） |
| `c(verdict=pass/fail/skip/partial)` | cycle 存在 | → act |
| `c(verdict=pending)` | L2/L3 级别 | → check（等待审批） |
| `a()` | cycle 在 act phase | → completed，写 completed_at，自动触发 aggregate() |

---

## 九、安全设计

### 9.1 ADAS 规则校验

| 规则 | 校验逻辑 | 错误返回 |
|------|---------|---------|
| L0/L1 拒 pending | `review_level in {L0,L1} AND verdict=pending` | "L0/L1 为自验收级别，不允许 verdict=pending" |
| L3 首次必须 pending | `review_level=L3 AND existing_c is None AND verdict!=pending` | "L3 首次 Check 必须 verdict=pending" |

### 9.2 Path Traversal 三层防御（v4.0.0）

| 层 | 防御 | 实现 |
|----|------|------|
| 1 | _validate_id() | 拒绝 `..`、`/`、`\`、空字符、超长 ID |
| 2 | PDCA_DIR 前缀 | os.path.realpath() 确保路径在 pdca/ 目录内 |
| 3 | 拒绝路径遍历 | 检测 realpath 后路径是否仍在预期目录 |

### 9.3 SHA-256 完整性校验（v4.0.0）

```python
# _save() 写入时计算 checksum
record['checksum'] = 'sha256:' + _compute_checksum(record)

# verify-integrity 读取时校验
stored = record.get('checksum', '')
expected = 'sha256:' + _compute_checksum(record)
valid = stored == expected
```

### 9.4 防无限循环

| 机制 | 说明 |
|------|------|
| max_cycles | config/pdca_config.yaml 可配置（默认 max_cycles_per_task=20） |
| p() 新 cycle 创建 | 只有上一 cycle=completed/check(pending) 时才新建 |
| 连续 3 次 fail | 上报 Harold 介入，不自动继续 |
| 连续 3 次 blocked | 标记 pdca_paused，移出候选队列 |

### 9.5 原子写入

```python
# pdca.py _save() 实现
def _save(record):
    path = _record_path(record['task_card_id'])
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        yaml.dump(record, f)
    os.replace(tmp, path)  # 原子替换
```

---

## 十、Harness 执行协议

### 10.1 两条触发路径

| 路径 | 触发时机 | 适用场景 |
|------|---------|---------|
| **A（直接入口）** | dispatch 创建 task-card 后，同会话立即执行 | 紧急/高优先级任务 |
| **B（heartbeat 入口）** | heartbeat 定时触发 Step 3a | 常规任务、后台推进 |

### 10.2 heartbeat 完整执行序列

```
前置: scheduler_state.py bump → check → pdca.py aggregate
Step 0: pdca.py pending → 处理 Harold 回复（A/B/C/D 解析）
Step 1: 选最高优先级 [P] 或 [V] 任务
Step 2: pdca.py status → 读取历史 PDCA 状态
Step 3-6: 完整 P→D→CQO Review→C→A 循环
```

### 10.3 单轮 PDCA 协议

| Step | Action | Key Rule |
|------|--------|----------|
| **Plan** | 明确本轮改进方向，基于上次根因 | P1: 必须说明与上次不同；P2: 必须回应上轮 Harold 条件 |
| **Do** | 实际执行，产出可见输出物 | D1: 必须描述实际变化 |
| **CQO Review** | 合规性检查（Do→Check 之间） | CQO-01~05 审核项，pass/revise/reject（§10.3.1） |
| **Check** | 按 Review 级别执行验收 | L3 → A/B/C/D 协议，7 天逾期升级 |
| **Act** | 基于 verdict 决定下一步 | A1: 必须包含下次 Plan 输入；A2: 写穿透；A3: 自动聚合 |

> **注意**：CQO Review 是 Do→Check 之间的过程性检查，不是 PDCA 的第 5 阶段。PDCA 本质仍是 Plan→Do→Check→Act 四阶段。

### 10.3.1 CQO 合规闸门（v8.1 新增）

**定位**：确保所有交付物在进入质量验收（Check）前符合 governance skill 规范。

**触发条件**：所有产出交付物的 Task，Do 完成后必须经过 CQO 审核。

**CQO Spawn 协议**：

```
sessions_spawn({
    agentId: "cqo",
    task: "CQO 合规审核",
    input: {
        task_card_id: "{TASK_ID}",
        deliverable_path: "10_Projects/{PROJECT_ID}/{TOPIC_ID}/deliverables/{FILENAME}",
        review_items: ["CQO-01", "CQO-02", "CQO-03", "CQO-04", "CQO-05"]
    }
})
```

**CQO 审核项**：

| 编号 | 审核项 | 检查内容 | 不通过处理 |
|------|--------|---------|-----------|
| CQO-01 | 模板匹配 | 交付物是否使用正确的 TMPL-* 模板 | revise，指定正确模板 |
| CQO-02 | 元数据完整 | frontmatter 必填字段齐全（title/id/status/owner/created/updated） | revise，列出缺失字段 |
| CQO-03 | 路径规范 | 存放路径符合 ZT-2026-007 | revise，指定正确路径 |
| CQO-04 | 结构完整 | 章节结构符合对应规范 | revise，列出缺失章节 |
| CQO-05 | 格式合规 | 标记、表格、引用格式符合 governance 规范 | 视严重程度 pass with note 或 revise |

**判定规则**：

| 结果 | 条件 | 后续 |
|------|------|------|
| **pass** | CQO-01~05 全部通过 | `pdca_current_phase = "check"`，进入 Check |
| **revise** | CQO-01~04 有 1-2 项不通过 | `pdca_current_phase = "do"`，退回原 Agent 修改 |
| **reject** | CQO-01~04 有 3+ 项不通过 | `pdca_current_phase = "do"`，退回原 Agent 重做 + 通知银月 |

**CQO 合规报告**：

- 存储路径：`10_Projects/{PROJECT_ID}/{TOPIC_ID}/deliverables/CQO-{TASK_ID}-{TIMESTAMP}.md`
- 模板：`TMPL-CQO-COMPLIANCE-REPORT.md`

**规则**：

- CQO 退回时 PDCA 仍在同一 cycle，不改 cycle_index
- CQO 审核不通过不影响 Task 状态标记（仍为 `[P]`）
- CQO 审核超时（5 分钟）：默认 pass，记录超时告警，CQO 合规报告中标记 `timeout: true`
- CQO revise 上限：同一 cycle 内 CQO revise 最多 3 次。第 4 次仍 revise → 自动升级为 reject，通知银月

**verdict → 状态映射**：pass → `[x]`，partial/fail/skip → `[P]`，pending → `[V]`

### 10.4 ADAS 分级规则表

| 级别 | Reviewer | 首次 Check | verdict 允许值 | audit_eligible |
|------|----------|-----------|---------------|----------------|
| **L0** | 无需 | 自动 pass | pass/fail/skip/partial | pass → true |
| **L1** | LLM 自身 | 自查通过 | pass/fail/skip/partial | pass → true |
| **L2** | 银月 | 抽样决定 | pass/pending | pass → false |
| **L3** | Harold | 必须 pending | pending → pass/fail/skip/partial | false |

### 10.5 Human-in-the-Loop 协议

**L3 Review 请求格式**：

```
【交付物审批】{task-card-id}
━━━━━━━━━━━━━━━━━━━━━━━━
📋 交付物: {name}
📊 验收标准:
  - {标准1}: {状态}
📝 执行摘要: {LLM 总结}
━━━━━━━━━━━━━━━━━━━━━━━━
请回复:
  A - 批准 | B - 有条件批准 | C - 拒绝 | D - 需要更多信息
```

**A/B/C/D 解析表**：

| 回复 | 映射 verdict | 后续动作 |
|------|-------------|---------|
| A | pass | c(verdict=pass) → Act → completed |
| B | partial | c(verdict=partial) → Act → 记录条件 |
| C | fail | c(verdict=fail) → Act → 记录根因 |
| D | partial | c(verdict=partial) → Act → 补充信息 |

**超时处理**：

| 等待时长 | 行为 |
|---------|------|
| ≤7 天 | 正常等待 |
| >7 天 | MISSION_BOARD 升级 [!]，feishu_post 重新通知 |
| >14 天 | 上报 Harold 队列，建议人工介入 |

### 10.6 持续迭代规则

**完成条件**：verdict=pass + task-card §五所有验收标准满足 + Task-CARD 状态更新 + MISSION_BOARD 标记完成

**迭代加速**：
- 连续 3 次 fail → Act 上报 MISSION_BOARD「需要 Harold 介入」
- 连续 partial 但有进展 → 正常继续
- 不允许连续 2 次 Do 内容完全相同（blocked 除外）

**特殊情况**：

| 情况 | 处理 |
|------|------|
| 任务 blocked | Do: `--status blocked`；Check: `--verdict fail` |
| 阻塞冷却（连续 3 次 blocked） | 标记 pdca_paused，移出候选队列，MISSION_BOARD `[~]` |
| L3 pending 审批 | feishu_post 通知 Harold；下次 Step 0 检查回填 |
| 连续 3 次 fail | Act 写明「需要 Harold 介入」，MISSION_BOARD `[!]` |
| CQO revise | 退回 Do，同一 cycle，revise_count+1 |
| CQO reject | 退回 Do，同一 cycle，通知银月 |
| CQO revise 3 次上限 | 第 4 次 revise → 自动升级为 reject |
| CQO 超时（5 分钟） | 默认 pass，记录超时告警 |

---

## 十一、层间传播与多粒度调度

### 11.1 轻量级层间传播

```
Task verdict (pdca/{task_id}.yaml)
    ↓ aggregate(scope='topic', scope_id='T06')
Topic verdict (pdca/_state.yaml) — 自动派生，不由 LLM 填写
    ↓ aggregate(scope='project', scope_id='ZT-P015')
Project verdict (pdca/_state.yaml) — 自动派生
```

**聚合模式**：

| 模式 | 说明 |
|------|------|
| `strict`（默认） | 向后兼容的严格规则 |
| `weighted` | 考虑比例和严重程度的权重模式 |

**strict 模式规则**：

| 子项组合 | 父项 verdict |
|---------|-------------|
| 全部 pass | pass |
| 任一 fail | fail |
| 部分 pass + 部分 partial | partial |
| 全部 skip | skip |
| 混合 | partial |

**weighted 模式规则**：

1. 比例阈值：≥80% pass → pass，≥20% fail → fail
2. 严重程度权重：pass=0, skip=1, partial=2, fail=3
3. 加权平均：<0.5 → pass，0.5-1.5 → partial，>1.5 → fail

可通过 `pdca.py aggregate --mode weighted` 或 config/pdca_config.yaml 切换模式。

**增量聚合**（v4.0.0）：仅当子项 verdict 变化时更新父级，使用 mtime 缓存避免全量扫描。

**触发**：a() 完成后自动调用聚合（task 级完成后聚合到 topic）。

### 11.2 并发上限约束

| Scope | 上限 | 校验时机 |
|-------|------|---------|
| task | ≤10 | p() 前置调用 check_concurrency('task') |
| topic | ≤5 | p() 前置调用 check_concurrency('topic') |
| project | ≤3 | p() 前置调用 check_concurrency('project') |

超限返回：`{ok: false, error: '{scope} 并发上限 {N}，当前活跃 {M}，请等待完成'}`

### 11.3 多粒度调度

> 1 tick = 1 heartbeat（约 30 分钟）。scheduler_state.py 每次 heartbeat 递增计数器，达到阈值时触发对应 scope 的 PDCA。

| Scope | 触发频率 | 阈值（tick 数） | 实际间隔 |
|-------|---------|----------------|---------|
| task | 每 1 heartbeat | 1 | ~30 分钟 |
| topic | 每 4 heartbeat | 4 | ~2 小时 |
| project | 每 48 heartbeat | 48 | ~1 天 |
| system | 每 96 heartbeat | 96 | ~2 天 |

**实现**：scheduler_state.py 持久化计数器 + 原子写入 config/scheduler_state.yaml。

**heartbeat 集成**：

```
heartbeat 触发:
  scheduler_state.py bump  → 递增所有计数器
  scheduler_state.py check → 返回应触发的 scope 列表
  for scope in triggered_scopes:
    process_scope(scope)    → 执行对应粒度的 PDCA
    scheduler_state.py reset {scope}  → 重置计数器
```

---

## 十二、运维命令

| 命令 | 用途 | 场景 |
|------|------|------|
| `verify-integrity` | 校验 PDCA 文件 SHA-256 完整性 | 检测篡改、数据损坏 |
| `health-check` | 系统健康状态概览 | heartbeat 运维巡检 |
| `archive` | 归档已完成的 PDCA 文件（>30 天） | 防止数据膨胀 |

```bash
python scripts/pdca.py verify-integrity [--task-card-id {id}]
python scripts/pdca.py health-check
python scripts/pdca.py archive [--older-than-days N] [--dry-run]
```

---

## 十三、已知限制

| 编号 | 限制 | 缓解措施 |
|------|------|---------|
| KL-1 | 无真正 cron 定时 | 外部调度：GitHub Actions cron / 独立守护进程 |
| KL-2 | 无 Feishu DM 读取机制 | LLM 自行调用 feishu_read 或手动标记 |
| KL-3 | probe-failures.yaml 不存在 | LLM 自行创建/更新 |
| KL-4 | bubble_up 不会自动触发 | close_task() 流程中显式调用 |
| KL-5 | aggregate() 依赖文件扫描 | mtime 缓存 + 增量检查优化性能 |
| KL-6 | 无跨 workspace 状态同步 | 各 workspace 独立 pdca/ 目录 |

---

## 十四、实施状态与里程碑

### 14.1 Phase 实施状态

| Phase | 目标 | 完成度 | 说明 |
|-------|------|--------|------|
| **Phase 0** | 接入边界定义 | ✅ 100% | T0.1 接入契约 + T0.2 PDCA Check 策略协议 |
| **Phase 1** | MVP 可进化 | ✅ 100% | pdca.py v2.2.0 + SKILL.md v2.5.0 + 99 测试通过 |
| **Phase 1.5** | 文档合并 + 安全加固 | ✅ 100% | 四文档合一 + SHA-256 + path traversal + 运维命令 |
| **Phase 2** | 层间传播 + 多粒度调度 | ✅ 100% | aggregate() + check_concurrency() + scheduler_state.py |
| **Phase 2.5** | 知识沉淀 | 🟡 进行中 | knowledge/lessons/ 结构已建，笔记数 <20 |
| **Phase 3** | 系统级自进化 | ⏸️ 待开始 | System 级 PDCA + 自主决策 + 预测性监控 |

### 14.2 里程碑

| 里程碑 | 计划日期 | 交付物 | 状态 |
|--------|----------|--------|------|
| M0: Phase 0 完成 | 2026-04-05 | T0.1/T0.2 签字确认 | ✅ 已完成 |
| M1: Phase 1 完成 | 2026-04-06 | pdca.py v2.2.0 + SKILL.md v2.5.0 | ✅ 已完成 |
| M2: 文档完整 | 2026-04-18 | 四文档 v2.0 | ✅ 已完成（已合并为本文件） |
| M3: Phase 2 完成 | 2026-07-11 | aggregate() + scheduler_state.py | ✅ 已完成 |
| M4: Phase 3 完成 | 2026-08-29 | 系统级自进化环 | ⏸️ 待开始 |

### 14.3 验收标准

| Phase | 门控条件 | 验收标准 | 状态 |
|-------|---------|---------|------|
| Phase 0 | T0.1/T0.2 签字确认 | 接入契约 + PDCA Check 策略协议 | ✅ |
| Phase 1 | pdca.py 稳定 + pdca/ ≥7天数据 | pdca.py v2.2.0 + SKILL.md v2.5.0 + 端到端验证 | ✅ |
| Phase 2 | aggregate() + scheduler_state 稳定 | 多粒度 PDCA + 层间传播 + 并发控制 | ✅ |
| Phase 3 | 系统级自进化环 + 完整递归 PDCA | System 粒度 + 自主决策 + 预测性监控 | ⏸️ |

### 14.4 Plan C 触发条件

| 条件 | 描述 |
|------|------|
| A | 12 项门控中有 ≥3 项失败 |
| B | 核心指标连续 2 个 Heartbeat 周期未达标 |
| C | 出现严重安全漏洞或数据丢失 |
| D | 知识笔记数超过 5000 |

---

## 十五、Phase 3 升级方案

### 15.1 系统级自进化环

**目标**：System 级别的 PDCA 自动执行，无需人工干预。

**能力**：
- 预测性监控：基于历史 logs/executions 识别趋势
- 自主决策：在操作白名单内自动调整配置
- 自适应执行：动态调整 heartbeat 频率、并发上限

**安全边界**：

```yaml
# config/act-whitelist.yaml (Phase 3)
allowed_operations:
  - type: "config_update"
    scope: "skill_parameters"
    max_change_ratio: 0.2
  - type: "task_retry"
    scope: "failed_tasks"
    max_retries: 3

blocked_operations:
  - "file_delete"
  - "skill_disable"
  - "config_schema_change"
```

### 15.2 预测性监控

**输入源**：logs/YYYY-MM-DD.jsonl + executions/YYYY-MM-DD.jsonl + pdca/*.yaml

**检测能力**：
- 异常模式识别（连续 fail 趋势）
- 性能退化（heartbeat 延迟增长）
- 资源耗尽预警（pdca 目录文件数增长）

### 15.3 知识沉淀

```
pdca/{id}.yaml (lessons)
    ↓ LLM 在 a() 时传入 lessons
knowledge/lessons/YYYY-MM-DD-{task_id}.md
    ↓ 老化机制（每周清理孤立笔记）
节点数上限：500（Phase 2 DoD），5000（Plan C 触发条件 D）
```

约束：不使用 Obsidian 外部工具，纯文件存储。

### 15.4 技能模块升级顺序

```
Week 15-16:  governance-delegation 自主决策
Week 17-18:  governance-nucleus System 级 PDCA
Week 19-20:  预测性监控 + 自适应执行
Week 21:     集成测试 + Phase 3 验收
```

---

## 十六、风险与缓解

### 16.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| aggregate() 聚合边界不清 | 中 | 低 | 先 Task→Topic 两层，验证后扩展 |
| 并发校验误判 | 高 | 低 | 单元测试覆盖所有边界条件 |
| scheduler_state 并发写入 | 中 | 低 | 原子写入 + heartbeat 单线程保证 |
| 文件 I/O 性能瓶颈 | 中 | 低 | 增量聚合 + mtime 缓存 |

### 16.2 业务风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| Harold 审批延迟导致 PDCA 停滞 | 中 | 高 | L3 超时升级机制已实现 |
| DL 条目置信度下降过快 | 中 | 中 | 审计阈值 80 分留有 20 分缓冲 |
| Agent 间职责重叠 | 低 | 低 | SKILL.md Activate 条件明确职责边界 |

---

## 十七、约束条件

### 17.1 OpenClaw 平台约束

| 约束 | 说明 |
|------|------|
| Heartbeat 频率 | 默认 30 分钟（可配置 1 分钟 - 24 小时） |
| isolatedSession | 各 Agent 会话隔离，无内存共享 |
| Skill 加载 | 按需加载，每次会话重新加载 |
| Subagent 通信 | sessions_spawn + sessions_send |

### 17.2 文件存储约束

| 约束 | 说明 |
|------|------|
| pdca 目录 | 位于 skill 根目录下 pdca/，每个 task 一个 YAML |
| MISSION_BOARD | 每个 Agent 独立维护，银月全局汇总 |
| task-card | 固定模板格式，§一/§三/§五 为 PDCA 关键输入 |

### 17.3 人力约束

| Agent | Phase 1 | Phase 2 | Phase 3 |
|-------|---------|---------|---------|
| 张铁 (PM/CQO) | 60% | 50% | 50% |
| 菡云芝 (CTO) | 60% | 60% | 60% |
| 银月 (PMO) | 20% | 20% | 20% |

---

## 十八、文件结构

### 18.1 Skill 目录（实现代码）

```
skills/openclaw-governance/skills/openclaw-governance-nucleus/
├── SKILL.md                   ← PDCA Harness 执行协议（v4.0.0）
├── scripts/
│   ├── pdca.py                ← PDCA 状态记录器（唯一 Python 工具）
│   └── scheduler_state.py     ← 调度计数器
├── pdca/                      ← pdca.py 数据存储（自动创建）
│   ├── {task_id}.yaml         # Task 级（LLM 填写）
│   ├── _state.yaml            # 聚合状态（aggregate 自动派生）
│   └── _archive/              # 归档已完成且 >30 天的文件
├── config/
│   ├── pdca_config.yaml       # 外部化配置（限制/超时/聚合参数）
│   └── scheduler_state.yaml   # 多粒度调度计数器
├── logs/
│   └── pdca.log               # 执行日志（JSON lines）
├── references/
│   └── pdca-harness.md        # 详细 Harness 执行协议 + CLI 参考
└── tests/                     # 单元测试
```

### 18.2 项目目录（ZT-P015）

```
10_Projects/ZT-P015_NUCLEUS-4-0/
├── docs/
│   ├── NUCLEUS-4-0-ARCHITECTURE.md  ← 本文件（唯一架构权威源）
│   └── archive/                      ← 历史文档归档
├── config/                           ← 配置文件（business_hours, escalation_policy 等）
├── cycles/                           ← Phase 1 遗留
├── logs/                             ← 观测日志
├── executions/                       ← 执行日志
├── topics/                           ← Topic 管理
├── tasks/                            ← Task 管理
├── scripts/                          ← 项目级可执行脚本
├── knowledge/                        ← 知识存储（Phase 2）
│   └── lessons/                      # 知识沉淀（轻量 .md 文件）
├── development/                      ← 开发过程记录
├── decisions/                        ← 架构决策
├── reviews/                          ← 评审记录
├── test/                             ← 测试文件
├── archived/                         ← Phase 1 归档
└── README.md                         ← 项目入口
```

---

*版本：v1.1 | 创建日期：2026-04-18 | 修订日期：2026-05-06 | 变更：新增 CQO 合规闸门（§10.3.1）+ 更新 phase 推进规则 + 更新 YAML 格式 | 架构师：张铁 (CQO) + 银月*
