---
name: managing-agents
description: |
  Managing agent lifecycle — onboarding, training, promotion, transfer, demotion, and retirement.
  
  Activates when: Agent lifecycle events (onboarding, training, promotion, transfer, demotion, retirement)
  
  Capabilities:
  - Agent onboarding with task cards and SOPs
  - Training program management and tracking
  - Promotion/demotion evaluation and reporting
  - Transfer between projects/roles
  - Retirement procedures and knowledge capture
  
  Keywords: agent, lifecycle, onboarding, training, promotion, demotion, retirement
  
  For detailed documentation, see:
  - standards/AGENT-LIFECYCLE.md
  - procedures/ (SOPs for each lifecycle stage)
  - templates/ (report templates for each stage)
  
author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "2.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L3"
  os: ["darwin", "linux"]
  tags: ["agent-lifecycle", "onboarding", "training", "promotion", "retirement"]
---

# Agent 生命周期管理 - Skill

> **职责**：标准化管理 Agent 从入职到退役的全生命周期
> **触发**：生命周期事件（入职/培训/升级/调岗/降级/退役）
> **负责 Agent**：main（银月）

## 何时使用

- **New Agent creation**: 向系统引入新 Agent 的入职
- **Skill changes**: Agent 获得/失去技能 → 触发培训
- **Automation level changes**: 基于绩效的升级或降级
- **Role transfer**: Agent 在项目/角色间调岗
- **Agent retirement**: 不再需要的 Agent 退役
- **Do NOT use for**: 日常 Agent 任务执行 — 通过 MISSION_BOARD 管理

## 常见陷阱

1. **入职/退役需要 Harold 审批（L3）**: 这些是关键生命周期事件 — 没有 Harold 的明确授权不能执行。
2. **集中式 vs 分散式管理**: 入职、退役和权限变更是集中式的（SYS-AGENT 项目）。培训记录、能力列表和角色微调是分散式的（每个 Agent 的 MISSION_BOARD）。
3. **培训在 Skill 变更时触发**: Agent 的技能增加/删除时，必须执行培训 SOP — 不要跳过培训步骤。
4. **降级不只是绩效问题**: 能力下降也可能是由系统变更引起的（如 Skill 废弃、协议变更）— 降级前检查根本原因。

---

## 一、生命周期阶段

```
入职 → 培训 → 在岗 → 升级/调岗/降级 → 退役
```

| 阶段 | 触发条件 | 审批级别 | SOP |
|------|----------|----------|-----|
| **入职** | 新 Agent 创建 | L3 (Harold) | `procedures/ONBOARDING-SOP.md` |
| **培训** | Skill 变更/能力升级 | L1/L2 | `procedures/TRAINING-SOP.md` |
| **升级** | 自动化级别提升 | L2/L3 | `procedures/PROMOTION-SOP.md` |
| **调岗** | 职责变更 | L2 | `procedures/TRANSFER-SOP.md` |
| **降级** | 能力下降 | L2/L3 | `procedures/DEMOTION-SOP.md` |
| **退役** | Agent 废弃 | L3 (Harold) | `procedures/RETIREMENT-SOP.md` |

---

## 二、规范文件

| 文件 | 说明 |
|------|------|
| `standards/AGENT-LIFECYCLE.md` | 生命周期管理规范（完整定义） |

**包含章节**：
- §十 自动化级别定义（L0-L4）
- §十一 agents.yaml 字段定义
- §十二 触发机制说明

---

## 三、流程文件

| 文件 | 说明 |
|------|------|
| `procedures/ONBOARDING-SOP.md` | 入职流程 |
| `procedures/TRAINING-SOP.md` | 培训流程 |
| `procedures/PROMOTION-SOP.md` | 升级流程 |
| `procedures/TRANSFER-SOP.md` | 调岗流程 |
| `procedures/DEMOTION-SOP.md` | 降级流程 |
| `procedures/RETIREMENT-SOP.md` | 退役流程 |

---

## 四、模板文件

| 模板 | 用途 |
|------|------|
| `templates/TMPL-ONBOARDING-TASK-CARD.md` | 入职培训任务卡 |
| `templates/TMPL-TRAINING-REPORT.md` | 培训报告 |
| `templates/TMPL-PROMOTION-REPORT.md` | 升级报告 |
| `templates/TMPL-TRANSFER-REPORT.md` | 调岗报告 |
| `templates/TMPL-DEMOTION-REPORT.md` | 降级报告 |
| `templates/TMPL-RETIREMENT-REPORT.md` | 退役报告 |

### 模板变量替换

入职时从 `governance-core/templates/` 生成核心文件（IDENTITY.md, AGENTS.md, SOUL.md, TOOLS.md, MISSION_BOARD.md, HEARTBEAT.md, USER.md），必须替换所有变量占位符。

**替换规则**：
- `${VARIABLE}` — 必须替换，缺失视为错误
- `{variable}` — 必须替换，运行时上下文填充
- `[variable]` — 可选替换，无值则移除整段

**完整变量清单**：见 `procedures/ONBOARDING-SOP.md` §Step 4 > 模板变量替换

---

## 五、集中 vs 分散管理

### 集中管理（SYS-AGENT 项目）
- 入职、退役 → 关键事件，Harold 审批
- 权限变更 → 安全相关
- 自动化级别升降 → 系统级配置

### 分散跟踪（各 Agent MISSION_BOARD）
- 培训记录 → 个人成长档案
- 能力清单变更 → Skill 变更历史
- 职责微调 → 日常调整

---

## 六、触发关键词

- 入职、onboard、新 Agent
- 培训、training、Skill 学习
- 升级、promotion、自动化级别
- 调岗、transfer、职责变更
- 降级、demotion、能力下降
- 退役、retire、Agent 废弃

---

## 七、与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| governance-core | 核心运行机制，引用本 Skill |
| governance-delegation | 授权管理，与升级/降级联动 |
| governance-task | 任务管理，入职培训使用 |

---

*版本: 2.2.0 | 更新: 2026-04-24 | 变更: §四增加模板变量替换规则和变量清单索引*