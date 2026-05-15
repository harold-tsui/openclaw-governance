# NUCLEUS-4-0 Version History

> **维护规则**: 每次 git 提交涉及 NUCLEUS 架构变更时更新此文件。
> **版本格式**: `major.minor.patch` — major=架构变更, minor=功能增强, patch=修复

---

## Phase 1: MVP 建立（2026-04-05 ~ 2026-04-08）

| 版本 | 日期 | Commit | 变更 |
|------|------|--------|------|
| **1.0.0** | 2026-04-06 | `dc64e08` | 初始版本，Phase 1 MVP 完成。建立 NUCLEUS docs/（ARCH-002, BENCHMARK 等）、config/、cycles/ 基础目录 |
| **1.1.0** | 2026-04-08 | `08ff645` | metadata `level: L3` → `L1-meta-sub`；新增 `standalone: false` + `parent_skill: governance-evolution`；`dependencies` 补充 governance-evolution；description Activate 条件修正 |
| **1.2.0** | 2026-04-08 | `b886748` | level 统一为 L4（移除自造层级 L1-meta-sub）；移除 standalone/parent_skill 字段 |
| **1.3.0** | 2026-04-08 | `352eb15` | Python 文件迁移至 Skill 目录；文件结构从项目目录更新为 Skill 标准结构；`nucleus_scheduler_integration.py` 创建 |
| **1.4.0** | 2026-04-08 | `08ff645` | pdca-check-protocol.md 更新至 v1.2；nucleus SKILL.md 创建（`352eb15`）；core/ 和 modules/ 目录 populated — CycleUnit/CycleScheduler 完整实现 |
| **1.4.2** | 2026-04-07 | `08ff645` | ARCH-v1.4.2 发布（CycleUnit 架构） |
| **1.4.3** | 2026-04-08 | `08ff645` | ARCH-v1.4.3 发布（最终 Phase 1 架构） |

---

## Phase 1 → Phase 2 过渡（2026-04-09 ~ 2026-04-13）

| 版本 | 日期 | Commit | 变更 |
|------|------|--------|------|
| **1.5.0** | 2026-04-09 | `9b82c7f` | ZT-2026-003 v4.0 备份规范获批 — 优化排除规则，节省 92% 空间 |
| **1.5.1** | 2026-04-13 | `1f85650` | N4-P2-T01 TASK-CARD 创建；scheduler_state.yaml 初始化；CycleUnit 文件更新；test/pdca-heartbeat-test reports 创建 |
| **1.5.2** | 2026-04-13 | `ba0943b` | tasks/ TASK-CARDs（T1.2, T2.1-T2.3, T3.1）创建 |
| **1.6.0** | 2026-04-16 | `63328ad` | docs/ 四文档发布（NUCLEUS-REQ-SPEC-v1.0 / ARCH-v1.0 / DESIGN-v1.0 / UPGRADE-v1.0）— **新准则确立**；code/nucleus-4.0 interfaces and models 创建 |
| **1.6.1** | 2026-04-17 | `1967e52` | 120 files 同步 — governance-delegation / heartbeat templates / nucleus modules / docs/archive/nucleus-v1 归档建立 |

---

## Phase 2: 架构精简（2026-04-18）

| 版本 | 日期 | Commit | 变更 |
|------|------|--------|------|
| **2.0.0** | 2026-04-18 | `bc578ed` | **架构修正** — 全面审查 21 个 SKILL.md 可实现性问题并修复。nucleus SKILL.md 精简（61 行变更，移除过时架构描述）。确认 pdca.py 为唯一 Python 工具，LLM 负责所有推断/判断/决策 |
| **2.0.1** | 2026-04-18 | `a839f9b` | governance-core 第二轮 review 修复 — 重复分隔符/章节号/过期引用/孤儿文件 |
| **2.0.2** | 2026-04-18 | `fdcd082` | governance-config 第二轮 review 修复 — 幽灵配置/缺失 return/缓存清理 |
| **2.0.3** | 2026-04-18 | `d03cafb` | governance-data 第二轮 review 修复 — 规范路径错误/版本不一致 |
| **2.0.4** | 2026-04-18 | `d6305af` | governance-dispatch _meta.json 版本号修正 2.2.0 → 2.11.0 + 时间戳修正 |
| **2.0.5** | 2026-04-18 | `f239433` | governance-hierarchy 第二轮 review 修复 — 章节号重排/版本不一致/缓存清理 |
| **2.0.6** | 2026-04-18 | `55b8a67` | governance-quality _meta.json 版本号 3.0.0 → 3.2.0 + 补充版本历史 |
| **2.0.7** | 2026-04-18 | `a7d1856` | 批量修复 4 个 skill _meta.json 版本不一致 |
| **2.0.8** | 2026-04-18 | `9c5707c` | 清理 skills 目录下的 __pycache__ 和 .pytest_cache 缓存文件 |
| **2.0.9** | 2026-04-18 | `4191956` | governance-config 环境变量名修正 WORKSPACE_DIR → OPENCLAW_LOCAL_WORKSPACE |
| **2.0.10** | 2026-04-18 | `9581686` | governance-config 新增配置模板体系，新部署可复制初始化 |

---

## Phase 2: 目录重组 + T06 重新规划（2026-04-18，本地未提交）

| 版本 | 日期 | 类型 | 变更 |
|------|------|------|------|
| **2.1.0** | 2026-04-18 | 本地变更 | NUCLEUS-4-0 目录重组 — 60+ 散乱根文件归档至 archived/（phase1/, phase1-core/, phase1-modules/, phase1-artifacts/, phase1-reports/, v1-docs/）；新建 README.md 定义目录结构 |
| **2.1.1** | 2026-04-18 | 本地变更 | N4-P2-T01 ~ T05 归档至 topics/archive/（旧架构不符合新准则） |
| **2.1.2** | 2026-04-18 | 本地变更 | N4-P2-T06 重新规划 — 从 "BotLearn 优化" 改为 "NUCLEUS 新准则实施（Phase 2）"；T06-PLAN.md 创建（pdca.py 精简版 + 轻量级层间传播）；TOPIC-BRIEF.md v2.0 |
| **2.1.3** | 2026-04-18 | 本地变更 | development/N4-P1-T07-dev-log.md 创建（记录 T02-T06 完成 + N4-P2-T06 重组）；VERSION_HISTORY.md 初始化 |
| **2.2.0** | ✅ 2026-04-18 | 实施完成 | T06.1 — pdca.py 差距修复（escalation 集成、健康检查已存在于 SKILL.md） |
| **2.3.0** | ✅ 2026-04-18 | 实施完成 | T06.2 — 轻量级层间传播（pdca.py aggregate() + pdca/_state.yaml 单文件方案） |
| **2.4.0** | ✅ 2026-04-18 | 实施完成 | T06.3 — 并发上限约束（pdca.py check_concurrency()） |
| **2.5.0** | ✅ 2026-04-18 | 实施完成 | T06.4 — 多粒度调度（scripts/scheduler_state.py 轻量计数器） |
| **2.6.0** | 待提交 | 计划 | T06.5 — 知识沉淀（knowledge/lessons/） |
| **2.7.0** | 待提交 | 计划 | T06.6 — 审计出口集成 |
| **3.0.0** | 待提交 | 计划 | T06.7 — 集成测试 + 验收，Phase 2 完成 |

---

## 关键架构变更对照

| 维度 | v1.x（Phase 1，已废弃） | v2.x（Phase 2，当前） |
|------|------------------------|---------------------|
| **核心引擎** | CycleUnit + CycleScheduler + CycleAggregator（10+ 文件，~3000 行） | pdca.py 单文件（~700 行） |
| **Python 职责** | 建模 LLM 判断逻辑（过度工程化） | 只做确定性 I/O（读写 pdca/*.yaml） |
| **LLM 职责** | 辅助 Python 判断 | 所有推断、执行、判断、决策 |
| **层间传播** | CycleAggregator 类，完整聚合逻辑 | pdca.py aggregate() 轻量函数 |
| **调度** | CycleScheduler，持久化计数器 | 轻量 scheduler_state.py |
| **需求规格** | 无正式文档 | NUCLEUS-REQ-SPEC-v1.0（6 功能模块 + 非功能需求） |
| **架构文档** | ARCH-v1.4.3（过时） | ARCH-v1.0（精简版） |
| **数据持久化** | cycle_unit.state.yaml + scheduler_state.yaml | pdca/*.yaml（多粒度：task/topic/project/system） |
| **审计出口** | 不完整 | audit_eligible + audit-queue + mark-audit 完整 pipeline |
| **并发控制** | 无 | 并发上限（task≤10, topic≤5, project≤3） |
| **知识沉淀** | 无 | knowledge/lessons/ 轻量存储 |
| **Human-in-the-Loop** | 无 | delegation §10.2 A/B/C/D + 7天超时 |
| **escalation** | consecutive_fails 计数器 | consecutive_fails≥3 → needs_escalation → heartbeat 消费 |

---

## Skill 版本对照表

| Skill | 当前版本 | 最后更新 Commit | 备注 |
|-------|---------|----------------|------|
| governance-nucleus | **v2.6.0** | 本地 | Phase 2: aggregate() + check_concurrency() + scheduler_state.py |
| governance-core | v6.1.8 | `a839f9b` + 本地 | PDCA-A 修正 + 命令规范 |
| governance-heartbeat | v5.7.0 | `bc578ed` + 本地 | 命令规范索引 |
| governance-dispatch | v2.12.0 | `d6305af` + 本地 | 分层引导 |
| governance-task | v6.0.4 | `bc578ed` | P0 修复 |
| governance-delegation | v4.2.0 | `bc578ed` | A/B/C/D 协议 |
| governance-data | v2.1.0 | `d03cafb` | 规范路径修正 |
| governance-config | v1.1.0 | `9581686` | 配置模板体系 |
| governance-quality | v3.2.0 | `55b8a67` | 版本号修正 |
| governance-hierarchy | v3.1.0 | `f239433` | 章节号重排 |

---

*最后更新：2026-04-18 18:00 | 维护人：银月 | 基于 git log + 本地变更记录*
