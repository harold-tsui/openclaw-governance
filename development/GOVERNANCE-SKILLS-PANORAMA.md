# Governance Skills 全景图

> **生成日期**: 2026-04-18
> **维护规则**: 每次 skill 新增/删除/版本变更时更新此文件。
> **数据来源**: `skills/openclaw-governance/skills/*/SKILL.md` frontmatter + 完整文件扫描

---

## 一、Skills 总览

| # | Skill ID | 简称 | 版本 | Level | 定位 | 触发方式 |
|---|----------|------|------|-------|------|---------|
| 1 | governance-core | core | 6.1.8 | L1 | 会话运行时基座 | 会话启动 |
| 2 | governance-dispatch | dispatch | 2.12.0 | L1 | 消息分拣与路由 | 会话启动 |
| 3 | governance-data | data | 4.0 | L1 | 数据治理与备份 | 按需加载 |
| 4 | governance-config | config | 1.3.0 | L2 | 配置加载与管理 | 会话启动 |
| 5 | governance-task | task | 6.0.4 | L2 | Task 生命周期 | 意图触发 |
| 6 | governance-hierarchy | hierarchy | 2.5.0 | L2 | Project/Topic/Task 层级 | 意图触发 |
| 7 | governance-heartbeat | heartbeat | 5.7.0 | L2 | 分布式定时巡检 | 定时触发 |
| 8 | governance-quality | quality | 3.2.0 | L3 | DOD + Review-Gate 质量门控 | 按需加载 |
| 9 | governance-delegation | delegation | 1.6.0 | L1 | 授权/降级/Review 等级 | 按需加载 |
| 10 | governance-risk | risk | 1.0.0 | L2 | 风险管理 | 按需加载 |
| 11 | governance-knowledge | knowledge | 1.1.0 | L2 | 知识增强与经验沉淀 | 按需加载 |
| 12 | governance-agent | agent | 1.1.0 | L3 | Agent 生命周期管理 | 按需加载 |
| 13 | governance-alert | alert | 1.0.0 | L3 | 告警接收与升级 | 按需加载 |
| 14 | governance-incident | incident | 1.0.0 | L3 | 事件响应与复盘 | 按需加载 |
| 15 | governance-nucleus | nucleus | **2.7.1** | L3 | PDCA 持续迭代执行引擎 | heartbeat 触发 |
| 16 | governance-pipeline | pipeline | 1.0.0 | L2 | 阀点管理管道 | 惰性加载 |
| 17 | governance-evolution | evolution | 1.2.0 | L4 | 元治理层，系统级自进化 | 惰性加载 |
| 18 | governance-infrastructure | infrastructure | 1.1.0 | L3 | 基础设施管理（仅 CTO） | CTO 内部 |
| 19 | ~~governance-intelligence~~ | ~~intelligence~~ | 1.0.0 | L3* | ~~情报收集~~ | **待移出 gov 家族** |
| 20 | ~~governance-content~~ | ~~content~~ | 1.0.0 | L3* | ~~内容创作~~ | **待移出 gov 家族** |
| 21 | ~~governance-visual~~ | ~~visual~~ | 1.0.0 | L3* | ~~视觉设计~~ | **待移出 gov 家族** |

> L3* = 骨架文件，待实现。#19~21 不属于治理范畴，计划移入其他 skill 家族。

---

## 二、依赖关系图

```
L1  core ─────────────────────────────────────────────────────────┐
    dispatch ─────────────────────────────────────────────────────┤
    data ─────────────────────────────────────────────────────────┤
                                                                  │
    delegation ──────┐                                            │
                     ▼                                            │
L2  config ──▶  nucleus ◀──────────────── heartbeat ─────────────┘
    task ───┐            ▲           (依赖: core + nucleus)
            │            │
    hierarchy ──▶ evolution ───┘
            │          ▲
    heartbeat ─┘       │
                       │
L3  quality ───────────┘
    nucleus (PDCA)
    risk
    risk
    knowledge
    agent
    alert
    incident
    infrastructure (仅CTO)

L4  pipeline
    evolution (元治理)

待移出  intelligence / content / visual → 非治理类，统一规划
```

### 显式依赖链（SKILL.md frontmatter）

| Skill | 依赖 |
|-------|------|
| nucleus | core, heartbeat, delegation |
| heartbeat | core, nucleus |
| delegation | nucleus |
| evolution | core, hierarchy, quality, config |

> **循环依赖注意**: nucleus ↔ heartbeat 互为依赖。这是协议层的互指引用，不是运行时循环调用：heartbeat 通过 Step 3a 触发 nucleus PDCA，nucleus 通过 SKILL.md 协议被 heartbeat 调用。

---

## 三、版本一致性

| Skill | Frontmatter | Footer | INDEX.md | 状态 |
|-------|-------------|--------|----------|------|
| core | 6.1.8 | 6.1.8 | — | ✅ |
| nucleus | 2.7.1 | (无) | v2.7.1 | ✅ |
| heartbeat | 5.7.0 | 5.7.0 | v5.7.0 | ✅ |
| dispatch | 2.13.0 | (无) | — | ✅ |
| delegation | 1.6.0 | (无) | v1.6.0 | ✅ |
| task | 6.0.4 | (无) | v6.0.4 | ✅ |
| quality | 3.2.0 | (无) | v3.2.0 | ✅ |
| hierarchy | 2.5.0 | (无) | — | ✅ |
| config | 1.3.0 | (无) | — | ✅ |
| evolution | 1.2.0 | (无) | — | ✅ |
| knowledge | 1.1.0 | 1.1.0 | — | ✅ |
| data | 4.0 | (无) | — | ✅ |
| risk | 1.0.0 | 1.0.0 | — | ✅ |
| pipeline | 1.0.0 | 1.0.0 | — | ✅ |
| agent | 1.1.0 | 1.1.0 | — | ✅ |
| alert | 1.0.0 | 1.0.0 | — | ✅ |
| incident | 1.0.0 | 1.0.0 | — | ✅ |

---

## 四、文件目录明细

### governance-core (L1 · 会话运行时基座 · v6.1.8)

> 所有 Agent 共享的会话启动基座，定义路径变量、Phase 启动序列、屏障规则。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 核心协议：Agent 启动引导、Skill 加载协议、失败处理 |
| `DESIGN.md` | 架构设计文档，供开发者理解复杂边界情况 |
| `INDEX.md` | 文档索引单一入口，Agent 不确定找信息时查询 |
| `README.md` | 开发者快速上手文档（常规执行用 SKILL.md） |
| `_meta.json` | 元数据 |
| `core/commands.md` | 治理命令规范 + gov-state.json 状态模板定义 |
| `frameworks/ADR-001_Agent文件分层架构.md` | 架构决策记录：Agent 文件分层方案 |
| `policies/ZT-2026-000_SOUL.md` | 灵魂规范：所有 Agent 共享的价值观与行为准则 |
| `policies/ZT-2026-006_组织架构规范.md` | 组织架构规范：角色/权限/层级定义 |
| `templates/gov-state.json` | 治理状态 JSON 模板（状态机持久化） |
| `templates/TMPL-AGENT-MANUAL.md` | Agent 管理手册模板 |
| `templates/TMPL-AGENTS-SUB.md` | Sub Agent 工作方式声明模板（AGENTS.md） |
| `templates/TMPL-EMERGENCY-STOP.md` | Agent 紧急停用协议模板 |
| `templates/TMPL-IDENTITY-MAIN.md` | Main Agent 身份定义模板（IDENTITY.md） |
| `templates/TMPL-IDENTITY-SUB.md` | Sub Agent 身份定义模板 |
| `templates/TMPL-MISSION_BOARD.md` | 任务看板模板（MISSION_BOARD.md） |
| `templates/TMPL-SKILL.md` | Skill 文件模板 |
| `templates/TMPL-SOUL-SUB.md` | Sub Agent 灵魂模板（SOUL.md） |
| `templates/TMPL-TOOLS-SUB.md` | Sub Agent 工具清单模板（TOOLS.md） |
| `templates/TMPL-TOOLS.md` | 工具清单通用模板 |
| `templates/TMPL-USER-SUB.md` | Sub Agent 用户定义模板（USER.md） |

### governance-dispatch (L1 · 消息分拣与路由 · v2.12.0)

> 意图理解、类型分类、Skill/Agent 路由、分层引导机制。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 路由协议：意图映射表 + 引导机制 + 模糊意图处理 |
| `_meta.json` | 元数据 |
| `frameworks/ZT-2026-009_消息分拣与任务清洗规范.md` | 消息分拣与任务清洗规范 |
| `standards/ZT-2026-005_Agent会话通信规范.md` | Agent 会话通信协议规范 |

### governance-data (L1 · 数据治理与备份 · v4.0)

> 存储架构、数据备份、工作空间整理标准。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 数据治理协议：存储、备份、归档、删除规范 |
| `_meta.json` | 元数据 |
| `scripts/backup.sh` | 本地备份脚本 |
| `scripts/cloud_backup.sh` | 云端（OneDrive）备份脚本 |
| `scripts/github_backup.sh` | GitHub 备份脚本 |
| `scripts/heartbeat_task_scanner.sh` | Heartbeat 任务扫描器 |
| `scripts/restore_deleted.sh` | 恢复已删除文件脚本 |
| `scripts/safe_delete.sh` | 安全删除脚本 |
| `scripts/.env.example` | 环境变量示例 |
| `validate.sh` | 数据治理验证脚本 |
| `standards/ZT-2026-001_存储架构规范.md` | 存储架构规范 |
| `standards/ZT-2026-003_数据备份与归档规范.md` | 数据备份与归档规范 |
| `standards/ZT-2026-004_数据治理体系规范.md` | 数据治理体系规范 |
| `standards/ZT-2026-007_工作空间整理标准.md` | 工作空间整理与熵管理标准 |
| `standards/ZT-2026-009_YAML-Frontmatter规范.md` | YAML Frontmatter 规范 |

### governance-config (L2 · 配置加载 · v1.3.0)

> 配置加载与管理的统一接口，提供系统/用户级配置模板。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 配置协议：配置文件路径、加载顺序、模板注册 |
| `_meta.json` | 元数据 |
| `core/config.py` | 配置加载 Python 实现 |
| `templates/system/TPL-agents.yaml` | 系统 Agent 注册表模板 |
| `templates/system/TPL-skills.yaml` | 系统 Skill 注册表模板 |
| `templates/system/TPL-system-projects.yaml` | 系统项目注册表模板 |
| `templates/system/TPL-system-tasks.yaml` | 系统任务注册表模板 |
| `templates/system/TPL-system-topics.yaml` | 系统专题注册表模板 |
| `templates/TPL-duty-mapping.yaml` | 职责-角色映射模板 |
| `templates/TPL-globals.yaml` | 全局配置模板 |
| `templates/user/TPL-persons.yaml` | 人员配置模板 |
| `templates/user/TPL-user-projects.yaml` | 用户项目配置模板 |
| `templates/user/TPL-user-tasks.yaml` | 用户任务配置模板 |
| `templates/user/TPL-user-topics.yaml` | 用户专题配置模板 |

### governance-task (L2 · Task 生命周期 · v6.0.4)

> 任务创建、分发、验收、退休全生命周期管理。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | Task 协议：创建/接收/执行/验收/退休生命周期 |
| `_meta.json` | 元数据 |
| `core/task.py` | Task 生命周期 Python 实现 |
| `procedures/ZT-2026-005_工作流程与约束规则.md` | 工作流程与约束规则 |
| `templates/TMPL-ONBOARDING-TASK-CARD.md` | Sub Agent 入职 Task Card 模板 |
| `templates/TMPL-RETIRE-TASK-CARD.md` | Sub Agent 退休 Task Card 模板 |
| `templates/TMPL-TASK-CARD-任务卡片模板.md` | 通用 Task Card 模板 |
| `templates/TMPL-TRAINING-TASK-CARD.md` | 培训 Task Card 模板 |
| `tests/test_task.py` | Task 核心实现单元测试 |

### governance-hierarchy (L2 · 层级管理 · v2.5.0)

> Project/Topic/Task 层级结构、交付物路径、创建流程。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 层级协议：Project→Topic→Task 结构、交付物路径、冒泡规则 |
| `_meta.json` | 元数据 |
| `core/hierarchy.py` | 层级管理 Python 实现 |
| `policies/ZT-2026-007_交付物路径规范.md` | 交付物路径规范 |
| `procedures/PROJECT-CREATION-SOP.md` | 项目创建标准流程 |
| `standards/ZT-2026-002_数据治理系统目录规范.md` | 目录结构规范 |
| `templates/TMPL-CLOSED-LOOP-TOPIC-v2.0.md` | 闭环治理 Topic 模板 |
| `templates/TMPL-PROJECT-CHARTER-项目章程模板.md` | 项目章程模板 |
| `templates/TMPL-REGISTRY-PROJECT.yaml` | 项目注册表模板 |
| `templates/TMPL-REGISTRY-TASK.yaml` | 任务注册表模板 |
| `templates/TMPL-REGISTRY-TOPIC.yaml` | 专题注册表模板 |
| `templates/TMPL-TOPIC-BRIEF-专题简报模板.md` | Topic 简报模板 |
| `tests/test_hierarchy.py` | 层级核心实现单元测试 |

### governance-heartbeat (L2 · 定时巡检 · v5.7.0)

> 分布式定时巡检协议，8 步工作流 + MISSION_BOARD 更新。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 巡检协议：8 步工作流 + PDCA 集成（Step 3a） + 报告格式 |
| `_meta.json` | 元数据 |
| `core/commands.md` | Heartbeat 命令规范 + heartbeat-state.json 模板 |
| `templates/heartbeat-state.json` | Heartbeat 状态 JSON 模板 |
| `templates/TMPL-HEARTBEAT.md` | Heartbeat 报告模板（Main Agent） |
| `templates/TMPL-HEARTBEAT-SUB.md` | Heartbeat 报告模板（Sub Agent） |

### governance-quality (L3 · 质量门控 · v3.2.0)

> DOD（Definition of Done）+ Review-Gate 质量门控验证。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 质量协议：DOD 定义、Review-Gate 流程、优先级框架 |
| `_meta.json` | 元数据 |
| `docs/dod-guide.md` | DOD 使用指南 |
| `docs/review-gate-guide.md` | Review-Gate 使用指南 |
| `frameworks/ZT-2026-011_工作优先级框架.md` | 多 Project 并行优先级框架 |
| `schemas/dod.schema.json` | DOD JSON Schema |
| `scripts/validate-reviews.sh` | Review 合规性验证脚本 |
| `scripts/verify-dod.sh` | DOD 合规性验证脚本 |
| `templates/TMPL-DOD-EXAMPLE.json` | DOD 示例 JSON |
| `templates/TMPL-DOD-验收标准.md` | DOD 验收标准模板 |
| `templates/TMPL-PRIORITY-FRAMEWORK-多Project并行工作优先级框架.md` | 优先级决策模板 |
| `templates/TMPL-REVIEW-审查报告.md` | 审查报告模板 |
| `tests/fixtures/*.json` | DOD 测试 fixture（valid/invalid/unmet） |
| `tests/fixtures/reviews/*/review.md` | Review 测试用例 |
| `tests/test-validate-reviews.sh` | Review 验证脚本测试 |
| `tests/test-verify-dod.sh` | DOD 验证脚本测试 |

### governance-delegation (L1 · 授权与等级 · v1.6.0)

> 授权/降级/Review 等级判定，Human-in-the-Loop 协议。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 授权协议：Review 级别判定、授权检查、决策自动化分级 |
| `_meta.json` | 元数据 |
| `core/delegation.py` | 授权/Review 等级 Python 实现 |
| `determine.sh` | 等级判定 Shell 脚本 |
| `frameworks/HUMAN-DELEGATION.md` | Harold 授权记录（Review 级别人工判定） |
| `tests/test_delegation.py` | 授权核心实现单元测试 |

### governance-risk (L2 · 风险管理 · v1.0.0)

> 风险登记册与评估框架。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 风险管理协议：风险识别、评估、跟踪 |
| `_meta.json` | 元数据 |
| `templates/TMPL-RISK-REGISTER.md` | 风险登记册模板 |

### governance-knowledge (L2 · 知识沉淀 · v1.1.0)

> 知识增强与经验沉淀。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 知识协议：经验沉淀、DL 条目管理 |
| `_meta.json` | 元数据 |
| `frameworks/ZT-2026-008_知识增强路径.md` | 知识增强路径规范 |
| `templates/TMPL-LESSONS-LEARNED.md` | 经验教训模板 |

### governance-agent (L3 · Agent 生命周期 · v1.1.0)

> Agent 入职、培训、晋升、调动、降级、退休全流程。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | Agent 生命周期协议：6 个阶段 SOP |
| `_meta.json` | 元数据 |
| `procedures/DEMOTION-SOP.md` | 降级标准流程（连续失败/能力不匹配） |
| `procedures/ONBOARDING-SOP.md` | 入职标准流程 |
| `procedures/PROMOTION-SOP.md` | 晋升标准流程 |
| `procedures/RETIREMENT-SOP.md` | 退休标准流程 |
| `procedures/TRAINING-SOP.md` | 培训标准流程 |
| `procedures/TRANSFER-SOP.md` | 调动标准流程 |
| `standards/AGENT-LIFECYCLE.md` | Agent 生命周期总规范 |
| `templates/TMPL-DEMOTION-REPORT.md` | 降级报告模板 |
| `templates/TMPL-ONBOARDING-TASK-CARD.md` | 入职 Task Card 模板 |
| `templates/TMPL-PROMOTION-REPORT.md` | 晋升报告模板 |
| `templates/TMPL-RETIREMENT-REPORT.md` | 退休报告模板 |
| `templates/TMPL-TRAINING-REPORT.md` | 培训报告模板 |
| `templates/TMPL-TRANSFER-REPORT.md` | 调动报告模板 |

### governance-alert (L3 · 告警管理 · v1.0.0)

> 告警接收、升级、摘要生成。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 告警协议：接收、处理、升级、摘要 |
| `_meta.json` | 元数据 |
| `procedures/ALERT-ESCALATION-SOP.md` | 告警升级标准流程 |
| `procedures/ALERT-RECEIVE-SOP.md` | 告警接收标准流程 |
| `procedures/ALERT-SUMMARY-SOP.md` | 告警摘要生成标准流程 |
| `templates/TMPL-ALERT-ESCALATION.md` | 告警升级模板 |
| `templates/TMPL-ALERT-REPORT.md` | 告警报告模板 |
| `templates/TMPL-ALERT-SUMMARY.md` | 告警摘要模板 |

### governance-incident (L3 · 事件响应 · v1.0.0)

> 故障检测、恢复、复盘。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 事件协议：检测、恢复、复盘 |
| `_meta.json` | 元数据 |
| `procedures/INCIDENT-DETECT-SOP.md` | 事件检测标准流程 |
| `procedures/INCIDENT-RECOVER-SOP.md` | 事件恢复标准流程 |
| `procedures/INCIDENT-POSTMORTEM-SOP.md` | 事件复盘标准流程 |
| `templates/TMPL-INCIDENT-REPORT.md` | 故障报告模板 |
| `templates/TMPL-INCIDENT-TIMELINE.md` | 故障时间线模板 |
| `templates/TMPL-POSTMORTEM.md` | 复盘报告模板 |

### governance-nucleus (L3 · PDCA 引擎 · v2.7.1)

> PDCA 持续迭代执行引擎，驱动每个 task 持续收敛到交付标准。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | PDCA Harness 协议：P→D→C→A 全流程 + 状态机防护 guardrails |
| `_meta.json` | 元数据 |
| `scripts/pdca.py` | PDCA 状态记录器（唯一 Python 工具），含 phase-locking/幂等性/并发控制/日志 |
| `scripts/scheduler_state.py` | 轻量多粒度调度计数器（task/topic/project/system） |
| `config/scheduler_state.yaml` | 调度计数器持久化状态 |
| `pdca/_state.yaml` | 聚合状态文件（topic/project verdict 派生） |
| `logs/pdca.log` | 执行日志（JSON lines，每次 CLI 调用一行，含原始 CWD） |

### governance-pipeline (L2 · 阀点管理 · v1.0.0)

> 管道状态机与阶段流转。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 管道协议：阶段定义、状态流转、触发条件 |
| `_meta.json` | 元数据 |
| `docs/pipeline-guide.md` | 管道使用指南 |
| `schemas/pipeline.schema.json` | 管道状态 JSON Schema |
| `templates/TMPL-PIPELINE-STATE.json` | 管道状态模板 |

### governance-evolution (L4 · 元治理 · v1.2.0)

> 系统级自进化，评估、升级、淘汰 Skill。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 元治理协议：Skill 生命周期评估、升级决策、依赖链验证 |
| `_meta.json` | 元数据 |
| `policies/ZT-2026-010_治理流程微调建议.md` | 治理流程微调建议记录 |

### governance-infrastructure (L3 · 基础设施 · v1.1.0)

> 基础设施管理，仅 CTO 角色可调用。

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 基础设施协议：仅 CTO 内部调用，不接受 dispatch 路由 |
| `_meta.json` | 元数据 |

---

### ~~待移出 gov 家族的 Skill~~

> 以下 3 个 skill 不属于治理范畴，骨架已建但待统一规划迁移。

### ~~governance-intelligence (L3* · 情报收集 · v1.0.0)~~

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 骨架文件，待实现 — 情报收集与分析 |
| `_meta.json` | 元数据 |

### ~~governance-content (L3* · 内容创作 · v1.0.0)~~

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 骨架文件，待实现 — 内容创作与编辑 |
| `_meta.json` | 元数据 |

### ~~governance-visual (L3* · 视觉设计 · v1.0.0)~~

| 文件 | 一句话 |
|------|--------|
| `SKILL.md` | 骨架文件，待实现 — 视觉设计与 UI |
| `_meta.json` | 元数据 |

---

## 五、待决策问题

### ~~5.1 nucleus 应该降为 L3 吗？~~

**状态**：✅ 已执行（2026-04-18）。nucleus L4 → L3。dispatch v2.13.0 已同步。

### 5.2 ~~intelligence / content / visual~~ 移出 gov 家族（已确认，待执行）

**当前**：在 `skills/openclaw-governance/skills/` 下

**建议**：
- 移出 `skills/openclaw-governance/skills/`
- 统一到其他 skill 家族，如 `skills/openclaw-intelligence/`、`skills/openclaw-creative/`
- 这 3 个 skill 是**能力型**（情报/内容/视觉），不是**治理型**（流程/质量/授权）

**需要改**：
1. 移动文件到目标目录
2. 更新 dispatch §3.4 路由层，去掉 3 个 skill 的引用
3. 更新 core 的 Skill 注册表
4. 更新本全景图（标记已移出）

---

## 六、测试报告

测试报告存放在 `10_Projects/ZT-P015_NUCLEUS-4-0/test_reports/`。

| 文件 | 一句话 |
|------|--------|
| `README.md` | 测试流程说明 + 执行日志使用方法 |
| `TEMPLATE.md` | 测试报告模板（复制后填写） |
| `CQO-TEST-REPORT-2026-04-18.md` | 首次 CQO 测试报告 |
| `REVIEW-2026-04-18.md` | 开发人复核报告（3 个 bug 无法复现） |
| `fixtures/` | 测试用 YAML fixture |

---

## 七、CLI 命令汇总

### 7.1 pdca.py (nucleus)

| 子命令 | 用途 |
|--------|------|
| `p --task-card-id ID --summary "..."` | 记录 Plan 阶段 |
| `d --task-card-id ID --summary "..." --status completed\|blocked\|partial` | 记录 Do 阶段 |
| `c --task-card-id ID --verdict pass\|partial\|fail\|skip\|pending --level L0\|L1\|L2\|L3` | 记录 Check 阶段 |
| `a --task-card-id ID --summary "..." [--task-state "[x]"]` | 记录 Act 阶段 |
| `status --task-card-id ID` | 查看当前 PDCA 状态 |
| `history --task-card-id ID` | 查看完整 PDCA 历史 |
| `pending [--review-level L2\|L3]` | 列出待审批任务 |
| `audit-queue` | 列出待审计队列 |
| `mark-audit --task-card-id ID --cycle-index N --score 0-100` | 记录审计结果 |
| `aggregate` | 聚合 task verdict 到 topic/project 级 |
| `check-concurrency [--scope task\|topic\|project]` | 检查并发上限 |

### 7.2 scheduler_state.py (nucleus)

| 子命令 | 用途 |
|--------|------|
| `read` | 读取当前调度计数器 |
| `bump` | 递增所有计数器（heartbeat 每轮调用） |
| `check` | 返回应触发的 scope 列表 |
| `reset task` | 重置 task 计数器 |

### 7.3 Shell 脚本

| 脚本 | Skill | 用途 |
|------|-------|------|
| `core/delegation.py` + `determine.sh` | delegation | Review 等级判定 |
| `scripts/validate-reviews.sh` | quality | 验证 Review 合规性 |
| `scripts/verify-dod.sh` | quality | 验证 DOD 合规性 |
| `scripts/backup.sh` | data | 本地数据备份 |
| `scripts/cloud_backup.sh` | data | 云端备份 |
| `scripts/github_backup.sh` | data | GitHub 备份 |
| `scripts/restore_deleted.sh` | data | 恢复已删除文件 |
| `scripts/safe_delete.sh` | data | 安全删除 |
| `scripts/heartbeat_task_scanner.sh` | data | Heartbeat 任务扫描 |
| `validate.sh` | data | 数据治理验证 |

---

*生成于 2026-04-18 | 下次更新: 任意 skill 版本/结构变更时*
