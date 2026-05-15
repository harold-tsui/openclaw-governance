---
name: driving-pdca
description: |
  Driving continuous PDCA iteration for every task until delivery.
  
  Activates when: Triggered by governance-heartbeat Step 3a or governance-evolution
  
  NOT Activates when: Direct dispatch routing or user direct invocation
  
  Capabilities:
  - PDCA cycle execution (Plan → Do → CQO Review → Check → Act)
  - Persistent state management via pdca.py (YAML storage)
  - Human-in-the-Loop protocol (L3 review with A/B/C/D)
  - Audit queue management (L0/L1 pass auto-eligible)
  - CQO 合规闸门 (Do→Check 间合规审核，pass/revise/reject)
  - Cross-session recovery and iteration tracking
  - Lightweight verdict aggregation (task → topic → project)
  - Data integrity verification (SHA-256 checksums)
  - System health monitoring
  - Expired data archiving
  
  Keywords: pdca, iteration, continuous-improvement, harness, execution, pdca-cycle
  
  Core tool: scripts/pdca.py (Python only does state recording, LLM handles all inference)
  
  For detailed documentation, see:
  - references/pdca-harness.md
  - docs/archive/nucleus-v1/ (legacy v1 system)

author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "4.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L4"
  os: ["darwin", "linux"]
  tags: ["pdca", "iteration", "continuous-improvement", "harness", "execution"]
  dependencies:
    - openclaw-governance-core
    - openclaw-governance-heartbeat
    - openclaw-governance-delegation  # Human-in-the-Loop Check protocol (§10)
---

# NUCLEUS 4.0 - PDCA Harness

> **定位**：驱动 LLM 对每个 task 持续 PDCA 迭代直至交付的执行 harness
> **层级**：L4，不可被 dispatch 独立路由
> **调用方**：governance-heartbeat（Step 3a）
> **核心原则**：Python 只做确定性状态记录；LLM 负责所有推断、执行、判断、优化
> **v3.1.0**: 补充 When to Use / Pitfalls 章节

## 何时使用

- **PDCA cycle execution**: 任务需要 Plan→Do→Check→Act 迭代
- **Cross-session recovery**: 上一会话中任务在进行中，需要恢复
- **Harold reply processing**: Step 0 检查 Harold 的 A/B/C/D 回复
- **Escalation**: 连续 3 次失败需要 Harold 介入
- **Do NOT use for**: 直接 dispatch 路由 — nucleus 由 heartbeat 或 evolution 触发，不接受用户直接调用

## 常见陷阱

1. **Python 只记录状态**: `pdca.py` 不是推理引擎。所有规划、执行、判断必须来自 LLM。不要期望脚本来"决策"。
2. **没有真正的 cron 调度**: Nucleus 依赖 heartbeat 触发或外部调度（GitHub Actions cron），不会自己按计划运行。
3. **阻塞任务冷却**: 连续 3 次"blocked" verdict 后，任务标记为 `pdca_paused` 并从候选队列移除。不要继续重试 — 应该升级。
4. **Bubble-up 不是自动的**: `bubble_up()` 函数必须在 `close_task()` 中显式调用 — PDCA 完成不会自动同步到项目/MISSION_BOARD。
5. **没有飞书 DM 读取机制**: 没有自动读取 Harold 回复的机制。LLM 必须手动调用 `feishu_read` 或在 Step 0 中检查回复。

---

## 一、定位与架构关系

### 1.1 在体系中的位置

```
L1  governance-core          会话运行时（每次会话必须加载）
L4  governance-evolution     元治理层（跨会话系统级，惰性加载）
└── governance-nucleus       PDCA 执行引擎（L4，由 evolution 或 heartbeat 触发）
        ├── scripts/pdca.py    PDCA 状态记录器（唯一 Python 工具）
        ├── pdca/              每个 task 的 PDCA 历史（YAML）
        └── references/        详细 Harness 执行协议
```

### 1.2 职责边界

| | governance-evolution（父） | governance-nucleus（本模块） |
|---|---|---|
| **职责** | 决策"改什么"，输出改进方案 | 自动执行 PDCA 循环，持久化调度 |
| **形态** | SKILL.md 框架描述 | SKILL.md + Python 可执行代码 |
| **触发** | heartbeat 定时 + 用户显式 | evolution 加载 或 heartbeat cron |
| **输出** | Skill 版本升级决策、架构改进报告 | cycles/ 运行时数据、执行日志 |

### 1.3 两条触发路径

| 路径 | 触发方 | 场景 | nucleus 的角色 |
|------|--------|------|----------------|
| **路径 A** | governance-evolution | 用户显式请求系统评估 | 由 evolution 按需启动 |
| **路径 B** | governance-heartbeat cron | 后台自动 PDCA 循环 | 独立运行，evolution 不在场 |

---

## 二、核心架构

### 2.1 核心组件（v2.6+ 单文件方案）

| 组件 | 功能 | 文件路径 |
|------|------|----------|
| **pdca.py** | PDCA 状态记录器（唯一 Python 工具） | `scripts/pdca.py` |
| **scheduler_state.py** | 轻量多粒度调度计数器 | `scripts/scheduler_state.py` |
| **PDCA Harness** | LLM 执行的 P→D→CQO→C→A 协议 | references/pdca-harness.md |
| **pdca/{task_id}.yaml** | 每个 task 的 PDCA 历史（自动创建） | `pdca/` 目录 |
| **pdca/_state.yaml** | 聚合状态（topic/project verdict 派生） | `pdca/_state.yaml` |
| **config/pdca_config.yaml** | 外部化配置（限制/超时/聚合参数） | `config/pdca_config.yaml` |
| **pdca/_archive/** | 归档已完成的 PDCA 文件（>30 天） | `pdca/_archive/` |

### 2.2 执行流程

```
[触发条件] → [Plan] → [Do] → [CQO Review] → [Check] → [Act]
    ↑                                          ↓
    └────────────── 改进 ←──────────────────────┘
                              ↓
                   汇报 governance-evolution（决策层）
```

### 2.3 触发条件

| 触发源 | 路径 | 说明 |
|--------|------|------|
| **governance-heartbeat** | 路径 B | 定时触发（Step 3a），最主要触发方式 |
| **governance-evolution** | 路径 A | 用户请求系统评估时，evolution 主动加载 |
| **Agent 会话** | 路径 A | Task-CARD 创建/更新时 |
| **外部事件** | 路径 B | 系统异常、阈值超限 |

---

## 三、集成方式

### 3.1 Heartbeat 集成（路径 B）

**调用位置**：governance-heartbeat Step 3a

```
heartbeat 触发
    ↓
Step 0 — bump: scheduler_state.py bump → check → pdca.py aggregate
    ↓
Step 1: 读取 MISSION_BOARD，选最高优先级 [P] 任务
    ↓
Step 2: pdca.py status → 读取历史 PDCA 状态 + escalation 信号
    ↓
Step 3-6: 执行完整 P→D→CQO→C→A 循环
    ↓
结果写入 pdca/{task_id}.yaml，a() 完成后自动触发 aggregate()
```

> **多粒度调度**：task 级每 heartbeat 执行；topic 级每 4 heartbeat；project 级每 48 heartbeat。

### 3.2 evolution 集成（路径 A）

直接读取 pdca/*.yaml 文件获取 PDCA 执行历史，无需独立触发。

---

## 四、Harness 执行协议（摘要）

> **核心目标**：驱动 LLM 对每个 task 持续 PDCA 迭代，直到 verdict=pass 且验收标准全部满足。
> **分工原则**：Python 只做状态记录；LLM 负责所有推断、执行、判断。

### 4.0 两条触发路径

| 路径 | 触发时机 | 适用场景 |
|------|---------|---------|
| **A（直接入口）** | dispatch 创建 task-card 后，同会话立即执行 | 紧急/高优先级任务 |
| **B（heartbeat 入口）** | heartbeat 定时触发 Step 3a | 常规任务、后台推进 |

### 4.1 heartbeat 执行序列

```
前置: scheduler_state.py bump → check → pdca.py aggregate
Step 0: pdca.py pending → 处理 Harold 回复（A/B/C/D 解析）
Step 1: 选最高优先级 [P] 或 [V] 任务
Step 2: pdca.py status → 读取历史 PDCA 状态
Step 3-6: 完整 P→D→CQO→C→A 循环
```

### 4.2 单轮 PDCA 摘要

| Step | Action | Key Rule |
|------|--------|----------|
| **Plan** | 明确本轮改进方向，基于上次根因 | P2: 必须回应上轮 Harold 条件 |
| **Do** | 实际执行，产出可见输出物 | D1: 必须描述实际变化；completed→进入 CQO Review |
| **CQO Review** | CQO (张铁) 合规审核交付物 | pass→Check，revise→回 Do，reject→回 Do + 通知银月 |
| **Check** | 按 Review 级别执行验收 | L3 → A/B/C/D 协议，7 天逾期升级 |
| **Act** | 基于 verdict 决定下一步 | A2: 写穿透 — 必须更新 Task-CARD + MISSION_BOARD |

**verdict → 状态映射**：pass → `[x]`，partial/fail/skip → `[P]`，pending → `[V]`

### 4.3 持续迭代

**完成条件**：verdict=pass + task-card §五所有验收标准满足

**迭代加速**：连续 3 次 fail → 上报 MISSION_BOARD「需要 Harold 介入」

### 4.4 特殊情况

| 情况 | 处理 |
|------|------|
| 任务 blocked | Do: `--status blocked`；phase 保持 do，不进入 CQO Review |
| 阻塞冷却（连续 3 次 blocked） | 标记 pdca_paused，移出候选队列，`[~]` |
| L3 pending 审批 | feishu_post 通知 Harold；下次 Step 0 检查回填 |
| 连续 3 次 fail | Act 写明「需要 Harold 介入」，MISSION_BOARD `[!]` |
| CQO revise | 回到 Do 阶段重新执行；连续 3 次 revise 自动升级为 reject |
| CQO reject | 回到 Do + 通知银月；需重做后再次 CQO Review |
| 跳过 CQO（向后兼容） | 旧流程 Do→Check 直接跳过 CQO，cqo_review_status=None |

### 4.5 CQO 合规闸门

| 命令 | 用途 | 场景 |
|------|------|------|
| `cqo-review` | CQO 审核交付物合规性 | Do 完成后、Check 之前 |

```bash
python scripts/pdca.py cqo-review --task-card-id {id} --result pass|revise|reject [--report-path PATH] [--issues "CQO-01|CQO-02"]
```

**CQO 审核项** (CQO-01~05)：
- CQO-01: 模板合规（是否使用规定模板）
- CQO-02: 元数据完整性（frontmatter 必填字段）
- CQO-03: 路径合规（文件存放位置）
- CQO-04: 内容完整性（章节/字段齐备）
- CQO-05: 引用一致性（交叉引用有效）

**结果处理**：
- `pass` → 进入 Check 阶段
- `revise` → 回到 Do 阶段（同一 cycle），revise_count +1
- `reject` → 回到 Do 阶段 + 通知银月，revise_count +1
- 连续 3 次 revise → 第 4 次自动升级为 reject

> 详细 CQO 协议：NUCLEUS-4-0-ARCHITECTURE.md §10.3.1

### 4.6 运维命令

| 命令 | 用途 | 场景 |
|------|------|------|
| `verify-integrity` | 校验 PDCA 文件 SHA-256 完整性 | 检测篡改、数据损坏 |
| `health-check` | 系统健康状态概览 | heartbeat 运维巡检 |
| `archive` | 归档已完成的 PDCA 文件（>30 天） | 防止数据膨胀 |

```bash
python scripts/pdca.py verify-integrity [--task-card-id {id}]  # 校验单个或全部文件
python scripts/pdca.py health-check                             # 返回 files/pending/checksum/concurrency 概览
python scripts/pdca.py archive [--older-than-days N] [--dry-run]  # 归档过期数据
```

### 4.7 已知限制

| 编号 | 限制 | 缓解措施 |
|------|------|---------|
| **KL-1** | 无真正 cron 定时 | 外部调度：GitHub Actions cron / 独立守护进程 |
| **KL-2** | 无 Feishu DM 读取机制 | LLM 自行调用 feishu_read 或手动标记 |
| **KL-3** | probe-failures.yaml 不存在 | LLM 自行创建/更新 |
| **KL-4** | bubble_up 不会自动触发 | close_task() 流程中显式调用 |

> 详细 Harness 执行协议、单轮 PDCA 规则、CLI 参考、文件结构：[references/pdca-harness.md]({baseDir}/references/pdca-harness.md)

---

## 五、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **4.1.0** | 2026-05-06 | CQO 合规闸门：cqo-review CLI 命令、Do→CQO→Check 阶段流转、revise 上限(3)自动升级、向后兼容跳过 CQO 流程 |
| **4.0.0** | 2026-04-23 | 安全加固 + 运维命令：path traversal 三层防御、SHA-256 checksum、config 外部化、health-check/verify-integrity/archive 命令、pending 三级升级、增量聚合 |
| **3.0.0** | 2026-04-22 | SKILL.md 瘦身至 <300 行，详细 Harness 协议移至 references/pdca-harness.md |
| **2.7.1** | 2026-04-18 | 可维护性：logs/pdca.log 自动执行日志 + _save() 绝对路径防御 |
| **2.7.0** | 2026-04-18 | PDCA 状态机防护：Phase 锁定 + 幂等性 + 陈旧 verdict 过滤 |
| **2.6.0** | 2026-04-18 | 层间传播 aggregate() + 并发上限 check_concurrency() + scheduler_state.py |
| **2.5.0** | 2026-04-18 | 逻辑修复：Act --task-state + [V] 任务选择 + 阻塞冷却 + P2 条件强制 |
| **2.0.0** | 2026-04-16 | 架构重写：单文件 pdca.py 替代旧 modules/+core/ 系统 |

---

*版本: 4.1.0 | 更新: 2026-05-06 | 变更: CQO 合规闸门*

## Related Skills
- [[openclaw-governance-heartbeat]] - 分布式巡检，Step 3a 触发入口
- [[openclaw-governance-evolution]] - 治理演进，路径 A 触发方
- [[openclaw-governance-delegation]] - 授权与等级判定，L3 Human-in-the-Loop 协议
- [[openclaw-governance-config]] - 配置管理，scheduler_state 持久化
