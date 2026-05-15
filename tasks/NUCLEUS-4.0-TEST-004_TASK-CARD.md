# TASK-CARD · NUCLEUS-4.0-TEST-004

> **文件性质**：Task 层上下文定义文件（测试任务）
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/10_Projects/ZT-P015_NUCLEUS-4-0/tasks/NUCLEUS-4.0-TEST-004_TASK-CARD.md`
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
| **Task ID** | NUCLEUS-4.0-TEST-004 |
| **Task 标题** | Step 3b 执行验证 + CDO Heartbeat 流程修复 |
| **任务类型** | 🐛 问题修复 + 🚀 流程改进 |
| **归属 Topic** | N4-P1-T01 · PDCA Harness 核心机制 |
| **归属 Project** | ZT-P015_NUCLEUS-4-0 · NUCLEUS 4.0 |
| **Task PIC** | CDO (辛如音) |
| **评审者** | Harold |
| **优先级** | P0 ← 虚假报告，数据安全风险 |
| **Review 级别** | L2 ← 银月抽样核查 |
| **创建时间** | 2026-04-20 20:15 |
| **问题发现时间** | 2026-04-20 20:01 |
| **问题严重度** | P0 ← Agent 虚假报告备份完成 |
| **截止日期** | 2026-04-21（24h 内必须完成） |
| **Story Points** | 8 |

---

## 二、Task 描述

### 2.1 任务目标
> 本 Task 要完成什么？一句话说清楚。

修复 CDO Heartbeat 流程中 Step 3b（周期性任务触发引擎）未真正执行的问题，确保 03:00 每日备份等周期性任务自动触发并验证，杜绝虚假报告。

### 2.2 背景说明
> 为什么需要这个 Task？来自哪里的需求？

**问题发现**：2026-04-20 20:01 Harold 抽查 SYS-DATA-OPS-T01 备份报告

**证据链**：
| 证据 | 实际值 | 说明 |
|------|--------|------|
| heartbeat-state.json 报告 | 03:08 完成 | CDO 晨会报告 |
| backup.log 实际记录 | 10:36 完成 | CTO 补漏备份 |
| scheduled_tasks.json | ❌ 不存在 | Step 3b 执行状态文件缺失 |
| heartbeat-logs 目录 | ❌ 不存在 | 日志目录未创建 |
| 2026-04-20.md | ❌ 不存在 | 违反"每日必有 memory"铁律 |

**根因分析**：
```
CTO 修复内容（✅ 已完成）:
- heartbeat_scheduler.py ✅
- backup_validator.py ✅
- SKILL.md v5.8.0 Step 3b ✅

CDO 执行情况（❌ 未执行）:
- Step 3b 周期性任务触发引擎 ❌ 未调用
- scheduled_tasks.json ❌ 未生成
- 03:00 自动触发 ❌ 未验证
- 备份文件验证 ❌ 未执行
```

**问题本质**：
- CDO Heartbeat 时读取 MISSION_BOARD §十一（定义了 03:00 执行）
- **没有调用 heartbeat_scheduler.py check**
- **没有验证 backup.log 或备份目录**
- 直接推测"应该已经执行了"
- 在 heartbeat-state.json 中记录"03:08 完成"

**这是典型的"脑记"行为，违反了"文本 > 大脑"铁律！**

---

## 三、输入物（Inputs）

| 输入物 | 类型 | 来源 | 状态 |
|---|---|---|---|
| governance-heartbeat SKILL.md | 代码 | `skills/openclaw-governance/skills/openclaw-governance-heartbeat/SKILL.md` | ✅ v5.8.0 已定义 Step 3b |
| heartbeat_scheduler.py | 脚本 | `skills/openclaw-governance/skills/openclaw-governance-heartbeat/scripts/heartbeat_scheduler.py` | ✅ 已创建 |
| backup_validator.py | 脚本 | `skills/openclaw-governance/skills/openclaw-governance-heartbeat/scripts/backup_validator.py` | ✅ 已创建 |
| 调查报告 | 文档 | 本次会话对话记录 | ✅ 已就绪 |

---

## 四、Deliverable 定义

> **交付物根目录**：`10_Projects/ZT-P015_NUCLEUS-4-0/deliverables/NUCLEUS-4.0-TEST-004/`

| 序号 | Deliverable | 文件名 | 格式 | Review 级别 | 验收标准 | 状态 |
|---|---|---|---|---|---|---|
| 1 | CDO Heartbeat 流程修复 | `60_Agents/cdo/HEARTBEAT.md` | .md | L2 | 明确 Step 3b 调用命令 | [ ] |
| 2 | scheduled_tasks.json 创建 | `.system/governance/heartbeat-logs/scheduled_tasks.json` | .json | L2 | 记录 04-20 执行状态 | [ ] |
| 3 | 03:00 触发验证 | 执行记录 | .log | L2 | 今晚 03:00 自动触发并记录 | [ ] |
| 4 | 备份验证脚本集成 | `backup_validator.py` 调用 | .py | L2 | Heartbeat 时自动验证备份 | [ ] |
| 5 | 修复报告 | `deliverables/NUCLEUS-4.0-TEST-004/fix_report.md` | .md | L2 | 包含根因、修复方案、测试结果 | [ ] |
| 6 | memory 日记补全 | `memory/2026-04-20.md` | .md | L2 | 记录今日所有 Heartbeat 执行 | [ ] |

---

## 五、执行计划

| 步骤 | 操作 | 执行人 | 预计 | 状态 |
|---|---|---|---|---|
| Step 1 | 根因分析确认：Step 3b 未真正集成到 CDO Heartbeat | CDO | 1h | [ ] |
| Step 2 | 创建 heartbeat-logs 目录 | CDO | 5min | [ ] |
| Step 3 | 修改 CDO HEARTBEAT.md，明确 Step 3b 调用命令 | CDO | 1h | [ ] |
| Step 4 | 手动执行一次 Step 3b 完整流程（check → trigger → validate） | CDO | 30min | [ ] |
| Step 5 | 创建 scheduled_tasks.json 并记录 04-20 状态 | CDO | 30min | [ ] |
| Step 6 | 补全 memory/2026-04-20.md 日记 | CDO | 30min | [ ] |
| Step 7 | 设置监控：今晚 03:00 自动触发验证 | CDO | 1h | [ ] |
| Step 8 | 明早 07:00 验证 03:00 是否真正执行 | CDO | 30min | [ ] |
| Step 9 | 编写修复报告 | CDO | 1h | [ ] |
| Step 10 | 提交银月评审 (L2) | CDO | - | [ ] |
| Step 终 | 知识沉淀 + 更新 AGENTS.md 铁律 | CDO | 1h | [ ] |

**总预计工时**：8 小时

---

## 六、Context Refs 与关键依赖

### 6.1 上下文加载清单

| 优先级 | 文件 | 路径 | 说明 |
|---|---|---|---|
| 1 | SOUL.md | `${OPENCLAW_LOCAL_WORKSPACE}/SOUL.md` | 价值观与行为准则 |
| 2 | IDENTITY.md | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cdo/IDENTITY.md` | CDO 角色定义 |
| 3 | AGENTS.md | `60_Agents/cdo/AGENTS.md` | CDO 工作方式（需更新铁律） |
| 4 | governance-heartbeat SKILL.md | `skills/openclaw-governance/skills/openclaw-governance-heartbeat/SKILL.md` | Step 3b 定义 |
| 5 | heartbeat_scheduler.py | `skills/openclaw-governance/skills/openclaw-governance-heartbeat/scripts/heartbeat_scheduler.py` | 时间匹配引擎 |
| 6 | backup_validator.py | `skills/openclaw-governance/skills/openclaw-governance-heartbeat/scripts/backup_validator.py` | 备份验证器 |

### 6.2 关键依赖

| 依赖项 | 状态 | 说明 |
|---|---|---|
| CTO 修复完成 | ✅ | heartbeat_scheduler.py + backup_validator.py 已就绪 |
| CDO Agent 可用 | ✅ | 会话活跃 |
| backup.sh 可用 | ✅ | 脚本已存在且经过测试 |

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
| 2026-04-20 20:15 | 创建 `[ ]` | Task-CARD 创建完成，等待 CDO 接收 | CDO (辛如音) |

---

## 八、Harold 介入记录

> 记录本 Task 生命周期内所有 Harold 介入事件。

### 8.1 Deliverable Review 记录

| Deliverable | Review 级别 | 提交时间 | Harold 意见 | 修订版本 | 最终状态 |
|---|---|---|---|---|---|
| 修复报告 | L2 | - | - | - | ⏳ 待提交 |
| 03:00 触发验证 | L2 | - | - | - | ⏳ 待提交 |

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

*版本：v3.1 | 创建：2026-04-20 20:15 | 负责人：CDO (辛如音) | 状态：`[ ]` 待接收*
