# NUCLEUS 需求规格说明书

> **文档编号**: NUCLEUS-REQ-SPEC-v2.0
> **创建日期**: 2026-04-16
> **修订日期**: 2026-04-18
> **上位引用**: ZT-P000 PROJECT-CHARTER v1.1 · ZT-P009 PROJECT-CHARTER v3.1 · ZT-P015 PROJECT-CHARTER v3.2
> **评审状态**: 待 Harold 评审

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

## 三、功能性需求

### 3.1 PDCA 闭环引擎（核心需求）

| 需求 ID | 描述 | 优先级 |
|---------|------|--------|
| **REQ-PDCA-001** | 系统必须支持 Plan → Do → Check → Act 四阶段循环 | P0 |
| **REQ-PDCA-002** | 每个 PDCA 循环必须持久化到文件（YAML），支持跨会话恢复 | P0 |
| **REQ-PDCA-003** | Python 只做确定性状态记录，LLM 负责所有推断、执行、判断、决策 | P0 |
| **REQ-PDCA-004** | 支持同一任务多轮 PDCA 迭代，直至 verdict=pass 且验收标准全部满足 | P0 |
| **REQ-PDCA-005** | 连续 3 次 verdict=fail 时自动上报 Harold 介入 | P1 |

### 3.2 Review 级别体系（ADAS 分级）

| 需求 ID | 描述 | 优先级 |
|---------|------|--------|
| **REQ-REVIEW-001** | L0：免审，自动通过 | P0 |
| **REQ-REVIEW-002** | L1：LLM 自验收，逐项自查验收标准 | P0 |
| **REQ-REVIEW-003** | L2：银月抽样核查（20-30%），抽中 pending，未抽中 pass | P0 |
| **REQ-REVIEW-004** | L3：Harold 全量审批，首次 Check 必须 verdict=pending | P0 |
| **REQ-REVIEW-005** | L0/L1 不允许 verdict=pending（自验收，无需人工介入） | P0 |
| **REQ-REVIEW-006** | L3 首次 Check 必须 pending，Harold 回复后再次调用 c() 记录最终结论 | P0 |

### 3.3 Human-in-the-Loop（人工审批协议）

| 需求 ID | 描述 | 优先级 |
|---------|------|--------|
| **REQ-HITL-001** | L3 Review 必须通过结构化格式（A/B/C/D）向 Harold 发出审批请求 | P0 |
| **REQ-HITL-002** | A = 批准，B = 有条件批准，C = 拒绝，D = 需要更多信息 | P0 |
| **REQ-HITL-003** | 7 天无回复自动升级为超时状态（is_overdue=true） | P0 |
| **REQ-HITL-004** | 超时后 MISSION_BOARD 对应条目升级为 [!]，重新通知 Harold | P0 |
| **REQ-HITL-005** | Harold 回复后自动解析 A/B/C/D 为 pass/partial/fail verdict | P0 |

### 3.4 审计出口（L0/L1 自动通过后质量监督）

| 需求 ID | 描述 | 优先级 |
|---------|------|--------|
| **REQ-AUDIT-001** | L0/L1 pass 自动标记 audit_eligible=true | P0 |
| **REQ-AUDIT-002** | 外部审计 heartbeat 可通过 audit-queue 获取待审计交付物列表 | P0 |
| **REQ-AUDIT-003** | 审计评分 < 80 时自动标记 has_problem=true | P0 |
| **REQ-AUDIT-004** | 评分 < 80 时触发 governance-knowledge.create_lesson_learned() 质疑对应 DL 条目 | P0 |
| **REQ-AUDIT-005** | 审计结果可追溯至 Plan 阶段引用的 dl_refs（DL 条目列表） | P1 |

### 3.5 知识沉淀

| 需求 ID | 描述 | 优先级 |
|---------|------|--------|
| **REQ-KNOWLEDGE-001** | Act 阶段可记录经验教训（lessons），持久化到 pdca YAML | P0 |
| **REQ-KNOWLEDGE-002** | verdict=fail 时强制触发知识沉淀（失败经验） | P1 |
| **REQ-KNOWLEDGE-003** | 审计发现问题时自动创建 Lessons Learned，降低对应 DL 置信度 | P1 |
| **REQ-KNOWLEDGE-004** | 支持 Obsidian 知识图谱存储（Phase 2） | P2 |

### 3.6 任务分发与选择

| 需求 ID | 描述 | 优先级 |
|---------|------|--------|
| **REQ-DISPATCH-001** | heartbeat Step 1 只选择 [P] 状态任务（已接收/执行中） | P0 |
| **REQ-DISPATCH-002** | 优先选择上次 verdict=fail/partial 的同一任务（持续收敛） | P0 |
| **REQ-DISPATCH-003** | 无 [P] 任务时做系统健康检查，verdict=skip | P1 |
| **REQ-DISPATCH-004** | 支持两条触发路径：Path A（同会话直接 PDCA）、Path B（heartbeat 定时触发） | P0 |

---

## 四、非功能性需求

### 4.1 零数据库架构

| 需求 ID | 描述 | 约束 |
|---------|------|------|
| **REQ-NF-001** | 所有数据以文件形式存储（.md / .yaml / .jsonl） | 不使用任何数据库 |
| **REQ-NF-002** | 文件读写保证原子性（先写 .tmp 再 rename） | 防止并发损坏 |
| **REQ-NF-003** | 人类和 LLM 可直接读写文件 | 无需专用工具解析 |
| **REQ-NF-004** | 天然支持 git 版本控制 | 所有变更可追溯 |

### 4.2 性能指标

| 指标 | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|
| 自动化率 | ≥30% | ≥60% | ≥90% |
| 准确率 | ≥80% | ≥85% | ≥90% |
| 响应时间 | ≤5min | ≤2min | ≤30s |
| 知识覆盖率 | ≥50% | ≥70% | ≥90% |
| Heartbeat/Task 比例 | ≤1.5:1 | ≤1.2:1 | ≤1.1:1 |

### 4.3 向后兼容

| 需求 ID | 描述 |
|---------|------|
| **REQ-NF-005** | 架构升级不影响现有 Agent 功能 |
| **REQ-NF-006** | Skill 接口升级必须保持向后兼容（废弃接口保留 1 个版本过渡期） |
| **REQ-NF-007** | 历史 pdca YAML 文件可被新版本正确读取 |

### 4.4 安全边界

| 需求 ID | 描述 |
|---------|------|
| **REQ-NF-008** | max_cycles 限制防止无限循环（默认值：task=3, topic=5, project=10） |
| **REQ-NF-009** | 并发上限约束（Phase 1：task≤10, topic≤5, project≤3, system=1） |
| **REQ-NF-010** | 操作白名单限制（Phase 3 自主决策仅在安全范围内） |

---

## 五、约束条件

### 5.1 OpenClaw 平台约束

| 约束 | 说明 |
|------|------|
| Heartbeat 频率 | 默认 30 分钟（可配置为 1 分钟 - 24 小时） |
| isolatedSession | 各 Agent 会话隔离，无内存共享 |
| Skill 加载 | 按需加载，每次会话重新加载 |
| Subagent 通信 | sessions_spawn + sessions_send |

### 5.2 文件存储约束

| 约束 | 说明 |
|------|------|
| pdca 目录 | 位于 skill 根目录下 pdca/，每个 task 一个 YAML |
| MISSION_BOARD | 每个 Agent 独立维护，银月全局汇总 |
| task-card | 固定模板格式，§一/§三/§五 为 PDCA 关键输入 |

### 5.3 人力约束

| Agent | Phase 1 | Phase 2 | Phase 3 |
|-------|---------|---------|---------|
| 张铁 (PM/CQO) | 60% | 50% | 50% |
| 菡云芝 (CTO) | 60% | 60% | 60% |
| 银月 (PMO) | 20% | 20% | 20% |

---

## 六、验收标准

### 6.1 Phase 门控条件

| Phase | 门控条件 | 验收标准 |
|-------|---------|---------|
| **Phase 0** | T0.1/T0.2 签字确认 | 接入契约 + PDCA Check 策略协议 |
| **Phase 1** | pdca.py 稳定 + pdca/ ≥7天数据 | pdca.py v2.2.0 + SKILL.md v2.5.0 + 端到端验证 |
| **Phase 2** | aggregate() + scheduler_state 稳定 + knowledge/ ≥20笔记 | 多粒度 PDCA + 层间传播 + 知识沉淀 |
| **Phase 3** | 系统级自进化环 + 完整递归 PDCA | System 粒度 + 自主决策 |

### 6.2 质量门控

| 门控 | 要求 |
|------|------|
| **F1** | 语法检查通过（无数据库相关代码） |
| **F2** | 单元测试通过（≥90% 覆盖率） |
| **F3** | 集成测试通过（端到端流程验证） |
| **F4** | 文档完整性（VISION/ARCH/PLAN 三文档） |

### 6.3 Plan C 触发条件

| 条件 | 描述 |
|------|------|
| **A** | 12 项门控中有 ≥3 项失败 |
| **B** | 核心指标连续 2 个 Heartbeat 周期未达标 |
| **C** | 出现严重安全漏洞或数据丢失 |
| **D** | 知识笔记数超过 5000 |

---

## 七、用户故事

### 7.1 Dispatch 入口（Path A）

> **作为** 银月（PMO）
> **当** dispatch 路由创建 task-card 后
> **我希望** Agent 立即 accept 并执行完整 PDCA 循环
> **以便** 高优先级任务在同会话内推进

### 7.2 Heartbeat 入口（Path B）

> **作为** 系统
> **当** heartbeat 定时触发（每 30 分钟）
> **我希望** 自动选出最高优先级 [P] 任务并推进一轮 PDCA
> **以便** 跨会话持续收敛任务

### 7.3 Harold 审批（L3）

> **作为** Harold（创始人）
> **当** 收到 A/B/C/D 结构化审批请求
> **我希望** 只需回复一个字母即可完成审批
> **以便** 最低摩擦参与决策

### 7.4 审计抽查

> **作为** 张铁（CQO）
> **当** 审计 heartbeat 触发
> **我希望** 自动获取 L0/L1 通过的交付物队列并评分
> **以便** 发现质量问题时自动质疑对应 DL，防止错误知识传播

### 7.5 超时升级

> **作为** 银月（PMO）
> **当** Harold 7 天未回复 L3 审批请求
> **我希望** 自动升级 MISSION_BOARD 并重新通知
> **以便** 不遗忘待审批事项

---

*版本：v2.0 | 创建日期：2026-04-16 | 修订日期：2026-04-18 | PM：张铁 | PMO：银月*
