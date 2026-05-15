# Governance 模板索引

> **版本**：v1.1
> **更新**：2026-04-24
> **用途**：所有治理模板的中心化索引，方便查找和维护

---

## 模板层级体系

OpenClaw 模板分两层，治理层覆盖原生层：

```
原生层（openclaw/）          治理层（governance/templates/）
├── AGENTS.md     ──覆盖──→  TMPL-AGENTS-SUB.md
├── IDENTITY.md   ──覆盖──→  TMPL-IDENTITY-SUB.md / TMPL-IDENTITY-MAIN.md
├── SOUL.md       ──覆盖──→  TMPL-SOUL-SUB.md
├── TOOLS.md      ──覆盖──→  TMPL-TOOLS-SUB.md / TMPL-TOOLS.md
├── HEARTBEAT.md  ──覆盖──→  TMPL-HEARTBEAT-SUB.md / TMPL-HEARTBEAT.md
├── USER.md       ──覆盖──→  TMPL-USER-SUB.md
└── BOOTSTRAP.md  ──保留──→  （治理层无对应，由 ONBOARDING-SOP 替代）
```

**覆盖规则**：
- **启用治理的 Agent**：使用 governance TMPL-*.md 生成核心文件（含变量替换）
- **未启用治理的工作区**：使用 openclaw/ 原生模板（零配置通用版本）
- **BOOTSTRAP.md**：原生层独有，治理层用入职 SOP 替代引导流程

---

## 一、Agent 核心文件模板（governance-core）

子 Agent onboarding 时从这些模板生成 7 个核心文件。

| 模板 | 生成文件 | 用途 |
|------|----------|------|
| `governance-core/templates/TMPL-IDENTITY-MAIN.md` | 主 Agent `IDENTITY.md` | 主 Agent 身份定义 |
| `governance-core/templates/TMPL-IDENTITY-SUB.md` | 子 Agent `IDENTITY.md` | 子 Agent 身份定义 |
| `governance-core/templates/TMPL-AGENTS-SUB.md` | `AGENTS.md` | 工作方式声明（v6.3） |
| `governance-core/templates/TMPL-SOUL-SUB.md` | `SOUL.md` | 价值观与行为准则 |
| `governance-core/templates/TMPL-MISSION_BOARD.md` | `MISSION_BOARD.md` | 任务看板（v2.7） |
| `governance-core/templates/TMPL-TOOLS.md` | 主 Agent `TOOLS.md` | 工具使用指南 |
| `governance-core/templates/TMPL-TOOLS-SUB.md` | 子 Agent `TOOLS.md` | 子 Agent 工具使用 |
| `governance-core/templates/TMPL-HEARTBEAT-SUB.md` | 子 Agent `HEARTBEAT.md` | 子 Agent 心跳协议（v1.0） |
| `governance-core/templates/TMPL-USER-SUB.md` | `USER.md` | 用户定义 |
| `governance-core/templates/TMPL-SKILL.md` | `SKILL.md` | Skill 定义模板 |
| `governance-core/templates/TMPL-AGENT-MANUAL.md` | — | Agent 手册模板 |
| `governance-core/templates/TMPL-EMERGENCY-STOP.md` | — | 紧急停止模板 |

---

## 二、Agent 生命周期模板（governance-agent）

| 模板 | 用途 |
|------|------|
| `governance-agent/templates/TMPL-ONBOARDING-TASK-CARD.md` | 入职 Task Card |
| `governance-agent/templates/TMPL-TRAINING-REPORT.md` | 培训报告 |
| `governance-agent/templates/TMPL-PROMOTION-REPORT.md` | 升级报告 |
| `governance-agent/templates/TMPL-TRANSFER-REPORT.md` | 调岗报告 |
| `governance-agent/templates/TMPL-DEMOTION-REPORT.md` | 降级报告 |
| `governance-agent/templates/TMPL-RETIREMENT-REPORT.md` | 退役报告 |

---

## 三、任务管理模板（governance-task）

| 模板 | 用途 |
|------|------|
| `governance-task/templates/TMPL-TASK-CARD-任务卡片模板.md` | 标准 Task Card |
| `governance-task/templates/TMPL-ONBOARDING-TASK-CARD.md` | 入职专用 Task Card |
| `governance-task/templates/TMPL-TRAINING-TASK-CARD.md` | 培训专用 Task Card |
| `governance-task/templates/TMPL-RETIRE-TASK-CARD.md` | 退役专用 Task Card |

---

## 四、层级管理模板（governance-hierarchy）

| 模板 | 用途 |
|------|------|
| `governance-hierarchy/templates/TMPL-PROJECT-CHARTER-项目章程模板.md` | Project 章程（v1.2） |
| `governance-hierarchy/templates/TMPL-TOPIC-BRIEF-专题简报模板.md` | Topic 简报 |
| `governance-hierarchy/templates/TMPL-CLOSED-LOOP-TOPIC-v2.0.md` | 闭环治理 Topic（v2.0） |

---

## 五、质量管控模板（governance-quality）

| 模板 | 用途 |
|------|------|
| `governance-quality/templates/TMPL-DOD-验收标准.md` | Definition of Done |
| `governance-quality/templates/TMPL-REVIEW-审查报告.md` | 审查报告 |
| `governance-quality/templates/TMPL-PRIORITY-FRAMEWORK-多Project并行工作优先级框架.md` | 多 Project 优先级框架 |

---

## 六、心跳模板（governance-heartbeat / governance-core）

| 模板 | 用途 |
|------|------|
| `governance-heartbeat/templates/TMPL-HEARTBEAT.md` | 主 Agent 心跳协议 |
| `governance-core/templates/TMPL-HEARTBEAT-SUB.md` | 子 Agent 心跳协议（v1.0） |

---

## 七、风险管理模板（governance-risk）

| 模板 | 用途 |
|------|------|
| `governance-risk/templates/TMPL-RISK-REGISTER.md` | 风险登记册 |

---

## 八、知识管理模板（governance-knowledge）

| 模板 | 用途 |
|------|------|
| `governance-knowledge/templates/TMPL-LESSONS-LEARNED.md` | 经验教训登记册 |

---

## 九、告警模板（governance-alert）

| 模板 | 用途 |
|------|------|
| `governance-alert/templates/TMPL-ALERT-REPORT.md` | 告警报告 |
| `governance-alert/templates/TMPL-ALERT-ESCALATION.md` | 告警升级通知 |
| `governance-alert/templates/TMPL-ALERT-SUMMARY.md` | 告警汇总报告 |

---

## 十、故障管理模板（governance-incident）

| 模板 | 用途 |
|------|------|
| `governance-incident/templates/TMPL-INCIDENT-REPORT.md` | 故障报告 |
| `governance-incident/templates/TMPL-INCIDENT-TIMELINE.md` | 故障时间线 |
| `governance-incident/templates/TMPL-POSTMORTEM.md` | 故障复盘报告 |

---

## 系统级模板

| 位置 | 用途 |
|------|------|
| `.system/governance/current/templates/TMPL-DOD.md` | DOD 系统副本 |
| `.system/governance/current/templates/heartbeat-state-说明.md` | 心跳状态字段说明 |

---

**路径约定**：所有模板相对于 `skills/openclaw-governance/skills/` 目录。

**模板总数**：39 个

---

*Version: v1.1 - 2026-04-24*
