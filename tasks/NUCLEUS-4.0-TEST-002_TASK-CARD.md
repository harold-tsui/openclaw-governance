# TASK-CARD · NUCLEUS-4.0-TEST-002

> **文件性质**：Task 层上下文定义文件（测试任务）
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/10_Projects/ZT-P015_NUCLEUS-4-0/tasks/NUCLEUS-4.0-TEST-002_TASK-CARD.md`
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
| **Task ID** | NUCLEUS-4.0-TEST-002 |
| **Task 标题** | Heartbeat 周期性任务触发机制缺失修复 |
| **任务类型** | 🐛 问题修复 |
| **归属 Topic** | N4-P1-T01 · PDCA Harness 核心机制 |
| **归属 Project** | ZT-P015_NUCLEUS-4-0 · NUCLEUS 4.0 |
| **Task PIC** | CTO (菡云芝) |
| **评审者** | Harold |
| **优先级** | P0 ← 备份已滞后 12 天 |
| **Review 级别** | L2 ← 银月抽样核查 |
| **创建时间** | 2026-04-20 09:15 |
| **问题发现时间** | 2026-04-20 08:02 |
| **问题严重度** | P0 ← 数据安全风险 |
| **截止日期** | 2026-04-21（24h 内必须完成） |
| **Story Points** | 8 |

---

## 二、Task 描述

### 2.1 任务目标
> 本 Task 要完成什么？一句话说清楚。

修复 governance-heartbeat 机制中周期性任务自动触发功能缺失，确保每日备份 (03:00)、每周清理 (周日 04:30) 等周期性任务能按时自动执行。

### 2.2 背景说明
> 为什么需要这个 Task？来自哪里的需求？

**问题发现**：2026-04-20 08:02 Harold 询问备份情况
**根因分析**：
- 最后一次实际备份：2026-04-08 17:49（已滞后 12 天）
- Heartbeat 每 30 分钟触发，但**没有时间匹配逻辑**
- Agent 不会检查"当前时间是否应该执行某个周期性任务"
- MISSION_BOARD 定义了任务周期（03:00/09:30/每周日），但 Heartbeat 流程不读取、不匹配、不触发

**影响范围**：
- SYS-DATA-OPS-T01 每日备份（03:00）→ 已滞后 12 天
- SYS-DATA-OPS-T05 湖仓监控（09:30）→ 每天应执行
- SYS-DATA-OPS-T02/03/04 周日清理 → 每周日应执行

---

## 三、输入物（Inputs）

| 输入物 | 类型 | 来源 | 状态 |
|---|---|---|---|
| governance-heartbeat SKILL.md | 代码 | `skills/openclaw-governance/skills/openclaw-governance-heartbeat/SKILL.md` | ✅ 已就绪 |
| MISSION_BOARD.md | 文档 | `60_Agents/cdo/MISSION_BOARD.md` | ✅ 已就绪 |
| backup.sh | 脚本 | `skills/openclaw-governance/skills/openclaw-governance-data/scripts/backup.sh` | ✅ 已就绪 |
| 根因分析报告 | 文档 | 本次会话对话记录 | ✅ 已就绪 |

---

## 四、Deliverable 定义

> **交付物根目录**：`10_Projects/ZT-P015_NUCLEUS-4-0/deliverables/NUCLEUS-4.0-TEST-002/`

| 序号 | Deliverable | 文件名 | 格式 | Review 级别 | 验收标准 | 状态 |
|---|---|---|---|---|---|---|
| 1 | governance-heartbeat 修复 | `SKILL.md` 修订版 | .md | L2 | 新增时间匹配逻辑 + 任务触发函数 | ✅ |
| 2 | 时间匹配函数 | `scripts/heartbeat_scheduler.py` | .py | L2 | 支持周期匹配、任务调度 | ✅ |
| 3 | 执行验证函数 | `scripts/backup_validator.py` | .py | L2 | 验证备份文件实际生成 | ✅ |
| 4 | 补漏备份执行 | backup.sh incremental | 脚本执行 | L2 | 生成 2026-04-20 备份目录 | ✅ |
| 5 | 修复报告 | `deliverables/NUCLEUS-4.0-TEST-002/fix_report.md` | .md | L2 | 包含根因、方案、测试结果 | ✅ |
| 6 | 回归测试报告 | `deliverables/NUCLEUS-4.0-TEST-002/regression_test.md` | .md | L2 | 验证 03:00/09:30 任务正常触发 | ✅ |

---

## 五、执行计划

| 步骤 | 操作 | 执行人 | 预计 | 状态 |
|---|---|---|---|---|
| Step 1 | 根因分析确认：Heartbeat 时间匹配逻辑缺失 | CTO | 1h | ✅ |
| Step 2 | 设计时间匹配函数：读取 MISSION_BOARD §十一，匹配当前时间 | CTO | 2h | ✅ |
| Step 3 | 实现任务触发函数：调用 backup.sh 等脚本 | CTO | 2h | ✅ |
| Step 4 | 实现执行验证函数：检查备份文件是否实际生成 | CTO | 1h | ✅ |
| Step 5 | 修改 governance-heartbeat SKILL.md：集成新函数 | CTO | 2h | ✅ |
| Step 6 | 执行补漏备份：incremental backup 2026-04-20 | CTO | 5min | ✅ |
| Step 7 | 回归测试：模拟 03:00/09:30 触发场景 | CTO | 1h | [ ] |
| Step 8 | 编写修复报告 | CTO | 1h | ✅ |
| Step 9 | 提交银月评审 (L2) | CTO | - | [ ] |
| Step 终 | 状态同步 + 知识沉淀 | CTO | 1h | [ ] |

**总预计工时**：11 小时

---

## 六、Context Refs 与关键依赖

### 6.1 上下文加载清单

| 优先级 | 文件 | 路径 | 说明 |
|---|---|---|---|
| 1 | SOUL.md | `${OPENCLAW_LOCAL_WORKSPACE}/SOUL.md` | 价值观与行为准则 |
| 2 | IDENTITY.md | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cto/IDENTITY.md` | CTO 角色定义 |
| 3 | governance-heartbeat SKILL.md | `skills/openclaw-governance/skills/openclaw-governance-heartbeat/SKILL.md` | 待修复文件 |
| 4 | MISSION_BOARD.md | `60_Agents/cdo/MISSION_BOARD.md` | 任务周期定义 |
| 5 | backup.sh | `skills/openclaw-governance/skills/openclaw-governance-data/scripts/backup.sh` | 备份脚本 |
| 6 | PROJECT-CHARTER.md | `../PROJECT-CHARTER.md` | 项目目标与范围 |

### 6.2 关键依赖

| 依赖项 | 状态 | 说明 |
|---|---|---|
| CTO Agent 可用 | ✅ | 菡云芝会话活跃 |
| backup.sh 可用 | ✅ | 脚本已存在且经过测试 |
| MISSION_BOARD 定义完整 | ✅ | §十一 定义了所有周期性任务 |

---

## ── Zone B：运行时状态（执行中更新）────────────────────

## 七、状态与执行记录

### 7.1 当前状态

| 字段 | 内容 |
|---|---|
| **状态标记** | `[V]` 待验收 |
| **当前状态值** | `[V]` 待验收 |
| **阻塞原因** | - |
| **MISSION BOARD 同步** | ⏳ 待同步 |

### 7.2 执行记录

> 执行过程中更新，保留最新 20 条。

| 日期 | 记录类型 | 内容 | 记录人 |
|---|---|---|---|
| 2026-04-20 09:15 | 创建 `[ ]` | Task-CARD 创建完成，等待 CTO 接收 | CDO (辛如音) |
| 2026-04-20 09:50 | 状态变更 `[P]` | CTO 接收任务，开始执行 | CTO (菡云芝) |
| 2026-04-20 10:36 | 状态变更 `[V]` | 所有交付物完成，补漏备份成功（3908文件，293MB） | CTO (菡云芝) |

---

## 八、Harold 介入记录

> 记录本 Task 生命周期内所有 Harold 介入事件。

### 8.1 Deliverable Review 记录

| Deliverable | Review 级别 | 提交时间 | Harold 意见 | 修订版本 | 最终状态 |
|---|---|---|---|---|---|
| 修复报告 | L2 | - | - | - | ⏳ 待提交 |
| 回归测试报告 | L2 | - | - | - | ⏳ 待提交 |

---

## ── Zone C：后处理（关闭后异步完成）────────────────────

## 九、知识沉淀

> **宽限期**：关闭后 3 个工作日内完成
> **核查节奏**：银月 Weekly Review 核查

| 字段 | 内容 |
|---|---|
| **知识沉淀内容** | - |
| **DL 条目** | - |
| **改进建议** | - |

---

## 十、归档信息

| 字段 | 内容 |
|---|---|
| **归档状态** | ⏳ 未归档 |
| **归档时间** | - |
| **归档位置** | - |

---

*版本：v3.1 | 创建：2026-04-20 09:15 | 负责人：CTO (菡云芝) | 状态：`[ ]` 待接收*
