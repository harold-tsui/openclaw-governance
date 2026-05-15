# TASK-CARD · NUCLEUS-4.0-FIX-001

> **文件性质**：Task 层上下文定义文件（P0 紧急修复）
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/10_Projects/ZT-P015_NUCLEUS-4-0/tasks/NUCLEUS-4.0-FIX-001_TASK-CARD.md`
> **上位文件**：`../PROJECT-CHARTER.md`
> **版本**：v3.1

---

## 声明

> **状态标记含义**：详细定义见 HEARTBEAT.md 附录 A
> **通用状态**：`[ ]` 待接收 / `[P]` 执行中 / `[V]` 待验收 / `[x]` 已完成 / `[?]` 阻塞 / `[!]` Harold 待决
> **Review 级别规则**：L0=免审 / L1=异常上报 / L2=抽样核查 / L3=全量人工

---

## ── Zone A：任务定义（创建时填写，基本不变）──────────────

## 一、Task 基本信息

| 字段 | 内容 |
|---|---|
| **Task ID** | NUCLEUS-4.0-FIX-001 |
| **Task 标题** | pdca.py + CWD + exec 并行 3 个 P0 问题修复 |
| **任务类型** | 🐛 问题修复 |
| **归属 Topic** | N4-P1-T07 · 治理体系 P0 问题修复 |
| **归属 Project** | ZT-P015_NUCLEUS-4-0 · NUCLEUS 4.0 |
| **Task PIC** | CTO (菡云芝) |
| **评审者** | Harold |
| **优先级** | P0 ← 已超时 55+ 小时 |
| **Review 级别** | L3 ← Harold 全量审批 |
| **创建时间** | 2026-04-20 |
| **问题发现时间** | 2026-04-18 20:46 ~ 22:15 |
| **超时时长** | 55+ 小时 |
| **截止日期** | 2026-04-21（24h 内必须完成） |
| **Story Points** | 13 |

---

## 二、Task 描述

### 2.1 任务目标
> 本 Task 要完成什么？一句话说清楚。

修复 2026-04-18 发现的 3 个 P0 问题（pdca.py 3 个 bug、CWD 状态不一致、exec 并行执行问题），恢复系统正常运行。

### 2.2 背景说明
> 为什么需要这个 Task？来自哪里的需求？

2026-04-18 20:46~22:15 期间进行 Round 2 测试时发现 3 个严重问题，已持续 55+ 小时未处理，严重影响系统稳定性和可信度。

---

## 三、输入物（Inputs）

| 输入物 | 类型 | 来源 | 状态 |
|---|---|---|---|
| pdca.py 源码 | 代码 | `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py` | ✅ 已就绪 |
| 问题发现记录 | 文档 | `60_Agents/cqo/memory/2026-04-18.md` | ✅ 已就绪 |
| 测试报告 | 文档 | `60_Agents/cqo/memory/heartbeat-state.json` | ✅ 已就绪 |

---

## 四、Deliverable 定义

> **交付物根目录**：`10_Projects/ZT-P015_NUCLEUS-4-0/deliverables/NUCLEUS-4.0-FIX-001/`

| 序号 | Deliverable | 文件名 | 格式 | Review 级别 | 验收标准 | 状态 |
|---|---|---|---|---|---|---|
| 1 | 问题 1 修复：pdca.py 3 个 bug | `scripts/pdca.py` | .py | L3 | 所有 bug 修复，测试通过 | [ ] |
| 2 | 问题 2 修复：CWD 状态不一致 | `scripts/scheduler_state.py` | .py | L3 | CWD 状态一致，测试通过 | [ ] |
| 3 | 问题 3 修复：exec 并行执行 | `skills/` 相关配置 | .yaml/.py | L3 | 并行执行正常，无竞态 | [ ] |
| 4 | 修复报告 | `deliverables/NUCLEUS-4.0-FIX-001/fix_report.md` | .md | L3 | 包含问题根因、修复方案、测试结果 | [ ] |
| 5 | 回归测试报告 | `deliverables/NUCLEUS-4.0-FIX-001/regression_test.md` | .md | L3 | Round 3 测试通过 | [ ] |

---

## 五、执行计划

| 步骤 | 操作 | 执行人 | 预计 | 状态 |
|---|---|---|---|---|
| Step 1 | 问题 1 根因分析：pdca.py 3 个 bug | CTO | 2h | [ ] |
| Step 2 | 问题 1 修复：pdca.py bug 修复 + 单元测试 | CTO | 4h | [ ] |
| Step 3 | 问题 2 根因分析：CWD 状态不一致 | CTO | 2h | [ ] |
| Step 4 | 问题 2 修复：CWD 状态管理修复 | CTO | 3h | [ ] |
| Step 5 | 问题 3 根因分析：exec 并行执行问题 | CTO | 2h | [ ] |
| Step 6 | 问题 3 修复：exec 并行控制修复 | CTO | 3h | [ ] |
| Step 7 | 集成测试：Round 3 回归测试 | CTO | 2h | [ ] |
| Step 8 | 编写修复报告 | CTO | 1h | [ ] |
| Step 9 | 提交 Harold 评审 | CTO | - | [ ] |
| Step 终 | 状态同步 + 知识沉淀 | CTO | 1h | [ ] |

**总预计工时**：20 小时

---

## 六、Context Refs 与关键依赖

### 6.1 上下文加载清单

| 优先级 | 文件 | 路径 | 说明 |
|---|---|---|---|
| 1 | SOUL.md | `${OPENCLAW_LOCAL_WORKSPACE}/SOUL.md` | 价值观与行为准则 |
| 2 | IDENTITY.md | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cto/IDENTITY.md` | CTO 角色定义 |
| 3 | pdca.py | `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py` | 问题源码 |
| 4 | 问题记录 | `60_Agents/cqo/memory/2026-04-18.md` | 问题发现记录 |
| 5 | PROJECT-CHARTER.md | `../PROJECT-CHARTER.md` | 项目目标与范围 |

---

## ── Zone B：运行时状态（执行中更新）────────────────────

## 七、状态与执行记录

### 7.1 当前状态

| 字段 | 内容 |
|---|---|
| **状态标记** | `[ ]` 待接收 |
| **当前状态值** | `[ ]` 待接收 |
| **阻塞原因** | - |
| **MISSION BOARD 同步** | ⏳ 待同步 |

### 7.2 执行记录

> 执行过程中更新，保留最新 20 条。

| 日期 | 记录类型 | 内容 | 记录人 |
|---|---|---|---|
| 2026-04-20 08:15 | 创建 `[ ]` | Task-CARD 创建完成，等待 CTO 接收 | 张铁 |

---

## 八、Harold 介入记录

> 记录本 Task 生命周期内所有 Harold 介入事件。

### 8.1 Deliverable Review 记录

| Deliverable | Review 级别 | 提交时间 | Harold 意见 | 修订版本 | 最终状态 |
|---|---|---|---|---|---|
| 修复报告 | L3 | - | - | - | ⏳ 待提交 |
| 回归测试报告 | L3 | - | - | - | ⏳ 待提交 |

---

## ── Zone C：后处理（关闭后异步完成）────────────────────

## 九、知识沉淀

> **宽限期**：关闭后 3 个工作日内完成
> **核查节奏**：银月 Weekly Review 核查

| 字段 | 内容 |
|---|---|
| **知识沉淀内容** | - |
| **LL 条目** | - |
| **改进建议** | - |

---

## 十、归档信息

| 字段 | 内容 |
|---|---|
| **归档状态** | ⏳ 未归档 |
| **归档时间** | - |
| **归档位置** | - |

---

*版本：v3.1 | 创建：2026-04-20 08:15 | 负责人：CTO (菡云芝) | 状态：`[ ]` 待接收*
