# TASK-CARD · N4-P3-T13-T01 PMBOK×Agent场景适配分析

> **Task ID**: N4-P3-T13-T01
> **上位 Topic**: N4-P3-T13-PMBOK×Agent场景适配
> **上位 Project**: ZT-P015_NUCLEUS-4-0
> **Owner**: CQO 张铁
> **Review 级别**: L2（银月抽样）
> **创建时间**: 2026-04-19
> **迁移来源**: ZT-P009 NUCLEUS-2.0-T13-T01
> **状态**: [P] 已接收

---

## §一、项目上下文

| 字段 | 内容 |
|------|------|
| **Project ID** | ZT-P015 |
| **Project 名称** | NUCLEUS 4.0（自动进化内核） |
| **Topic ID** | N4-P3-T13 |
| **Topic 名称** | PMBOK×Agent场景适配 |
| **workspace** | `/Users/haroldtsui/Workspaces/openclaw/main` |
| **task_card_path** | `10_Projects/ZT-P015_NUCLEUS-4-0/topics/N4-P3-T13/TASK-CARD-T01.md` |
| **deliverable_path** | `10_Projects/ZT-P015_NUCLEUS-4-0/topics/N4-P3-T13/deliverables/` |

---

## §二、任务定义

### 2.1 任务名称

**PMBOK×Agent场景适配分析** - 识别PMBOK方法论在Agent协作中的适配场景

### 2.2 任务目标

将PMBOK项目管理方法论适配到Agent协作场景：
1. **PMBOK核心流程识别** - 启动/规划/执行/监控/收尾五大过程组
2. **Agent协作场景映射** - PMBOK流程与Agent角色对应
3. **适配场景清单** - 哪些PMBOK流程可直接适配、哪些需改造
4. **改造方案初步设计** - 不适配场景的Agent化改造思路

### 2.3 任务类型

| 类型 | 说明 |
|------|------|
| **方法论建设** | PMBOK与Agent协作适配分析 |

### 2.4 优先级

**P1** - Phase 3规划，系统级自进化基础

---

## §三、执行计划

### 3.1 前置条件

- ✅ NUCLEUS 4.0 Phase 2核心功能完成
- ⚪ 决策自动化分级完成（N4-P2-T09）

### 3.2 工作步骤

| Step | 内容 | 预计时间 | 状态 |
|------|------|----------|------|
| **Step 1** | PMBOK五大过程组调研 | 1h | ⚪ 待开始 |
| **Step 2** | Agent角色与职责清单 | 30min | ⚪ 待开始 |
| **Step 3** | PMBOK→Agent场景映射 | 2h | ⚪ 待开始 |
| **Step 4** | 适配场景分类（直接/改造/不适用） | 1h | ⚪ 待开始 |
| **Step 5** | 编写PMBOK×Agent适配文档 | 2h | ⚪ 待开始 |
| **Step 6** | 验证适配可行性（样例场景） | 1h | ⚪ 待开始 |

### 3.3 阻塞风险

| 风险 | 影响程度 | 应对措施 |
|------|----------|----------|
| PMBOK方法论复杂度高 | 中 | 先聚焦核心流程，逐步扩展 |

---

## §四、交付物清单

### Zone A: 任务定义（创建时填写）

| 交付物 | 类型 | 路径 | 验收标准 |
|--------|------|------|----------|
| **PMBOK×Agent适配文档** | doc | `deliverables/PMBOK-AGENT-ADAPTATION-v1.0.md` | 五大过程组映射清晰、场景分类合理 |
| **样例场景验证报告** | doc | `deliverables/SAMPLE-SCENARIO-REPORT.md` | 3个样例场景适配结果 |

### Zone B: 运行时（执行时更新）

| 字段 | 内容 |
|------|------|
| **实际开始时间** | - |
| **实际完成时间** | - |
| **执行日志路径** | `logs/N4-P3-T13-T01-execution.log` |

### Zone C: 后处理（完成后填写）

| 字段 | 内容 |
|------|------|
| **知识沉淀** | 待填写（经验教训） |
| **归档位置** | `topics/N4-P3-T13/archive/` |

---

## §五、验收标准

| 序号 | 验收标准 | 衡量方式 |
|------|----------|----------|
| **1** | PMBOK五大过程组映射清晰 | 每过程组有Agent角色对应 |
| **2** | 适配场景分类合理 | 直接适配≥3、改造适配≥3、不适用明确 |
| **3** | 样例场景验证可行 | 3个样例场景适配结果符合预期 |
| **4** | 文档格式正确 | 符合TMPL-ADAPTATION模板 |

---

## §六、相关资源

### 6.1 参考文档

| 文档 | 路径 |
|------|------|
| PMBOK指南 | 外部资料（Harold提供） |
| Agent角色清单 | `docs/NUCLEUS-4-0-ARCHITECTURE.md §一` |
| 项目命名规范 | `skills/openclaw-governance/skills/openclaw-governance-hierarchy/SKILL.md` |

### 6.2 迁移来源

| 来源 | 说明 |
|------|------|
| ZT-P009 NUCLEUS-2.0 | 原T13-T01定义在归档文档中 |

---

## §七、状态历史

| 时间 | 状态变更 | 变更原因 | 记录人 |
|------|----------|----------|--------|
| 2026-04-19 21:47 | 创建 → [P] | Harold决策迁移ZT-P009-T13到ZT-P015 | CQO |

---

## §八、PDCA 记录（首次）

| Cycle | Phase | Summary | verdict |
|-------|-------|---------|---------|
| Cycle 1 | Plan | PMBOK×Agent场景适配分析启动，需先调研PMBOK五大过程组 | - |

---

*版本: TASK-CARD v3.0 | 创建: 2026-04-19 | Owner: CQO 张铁*