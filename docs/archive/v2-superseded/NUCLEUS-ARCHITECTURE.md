# NUCLEUS 系统架构书

> **文档编号**: NUCLEUS-ARCH-v2.0
> **创建日期**: 2026-04-16
> **修订日期**: 2026-04-18
> **上位引用**: NUCLEUS-REQ-SPEC-v2.0
> **评审状态**: 待 Harold 评审

---

## 一、架构演进史

### 1.1 三代架构迭代

```
v1.0 (ZT-P000)          v3.0 (ZT-P009)           v2.0+ (v4.0 精简版)
┌──────────────┐        ┌──────────────┐         ┌──────────────┐
│ 六大模块定义  │   →    │ 11 Skills    │    →    │ pdca.py      │
│ 双飞轮愿景    │        │ DOD+RG+Pipe  │         │ + SKILL.md   │
│ 灵枢计划      │        │ 闭环治理     │         │ + heartbeat  │
└──────────────┘        └──────────────┘         └──────────────┘
 定义"做什么"             实现"怎么做"              回归"做什么最小"
```

### 1.2 架构问题与修正

| 版本 | 问题 | 修正 |
|------|------|------|
| v4.0 Phase 1 | CycleUnit/CycleScheduler/CycleAggregator 过度工程化，Python 试图建模 LLM 判断逻辑 | v2.0.0：单文件 pdca.py 替代整个复杂系统 |
| v4.0 Phase 1 | 10 处逻辑不自洽 | v2.0.0：明确分工——Python 只做 I/O，LLM 负责推断 |
| v2.0.0 | c() 未校验 ADAS 规则 | v2.1.0：L0/L1 拒 pending，L3 首次必须 pending |
| v2.0.0 | p() 实现与文档冲突 | v2.0.0：修复 cycle 创建逻辑（completed/pending → new，plan/do/act → reuse） |
| v2.0.0 | Step 0 缺少 pdca.py c 调用 | v2.1.0：Harold 回复后先 c() 再 Act |
| v2.0.0 | Heartbeat Step 0 缺少 Harold 回复分支 | v2.1.0：三分支（有回复/超时/等待中） |
| v2.1.0 | Act 阶段硬编码 LL/DL 触发 | v2.2.0：移除，属 governance-knowledge 关注点 |
| v2.x Phase 1 | 无层间传播机制 | v2.x Phase 2：pdca.py aggregate() 轻量聚合 |
| v2.x Phase 1 | 无并发控制 | v2.x Phase 2：pdca.py check_concurrency() 前置校验 |
| v2.x Phase 1 | 单粒度调度（仅 task） | v2.x Phase 2：scheduler_state.py 多粒度 |

### 1.3 当前版本

| 组件 | 版本 | 说明 |
|------|------|------|
| pdca.py | v2.2.0（随 nucleus SKILL.md v2.5.0） | PDCA 状态记录器（唯一 Python 工具） |
| scheduler_state.py | 待开发（Phase 2） | 多粒度调度计数器 |
| governance-delegation | v4.2.0 | Human-in-the-Loop A/B/C/D 协议 |
| governance-heartbeat | v5.7.0 | 分布式巡检协议 |
| governance-task | v6.0.4 | review_deliverable 与 PDCA Check 串联 |
| governance-quality | v3.2.0 | DOD + Review-Gate |

---

## 二、当前架构

### 2.1 总体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw 平台                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ dispatch     │    │ heartbeat    │    │ evolution    │   │
│  │ (任务分发)    │    │ (定时巡检)    │    │ (元治理)     │   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘   │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              governance-nucleus (L4)                  │   │
│  │  ┌────────────┐    ┌────────────┐    ┌────────────┐  │   │
│  │  │ Path A     │    │ Path B     │    │ 审计出口    │  │   │
│  │  │ 直接 PDCA  │    │ heartbeat  │    │ L0/L1 pass │  │   │
│  │  │ (同会话)    │    │ 定时触发   │    │ → audit    │  │   │
│  │  └─────┬──────┘    └─────┬──────┘    └─────┬──────┘  │   │
│  │        └─────────────────┼─────────────────┘          │   │
│  │                          ▼                            │   │
│  │  ┌────────────────────────────────────────────────┐   │   │
│  │  │          pdca.py (PDCA 状态记录器)               │   │   │
│  │  │  p() / d() / c() / a() / status / pending      │   │   │
│  │  │  audit-queue / mark-audit                       │   │   │
│  │  └────────────────────┬───────────────────────────┘   │   │
│  │                       │                                │   │
│  └───────────────────────┼────────────────────────────────┘   │
│                          │                                     │
│  ┌───────────────────────▼────────────────────────────────┐   │
│  │              pdca/{task_id}.yaml (持久化状态)            │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐  │
│  │ delegation │  │ knowledge  │  │   task     │  │ quality│  │
│  │ (HitL/A-D) │  │ (DL/LL)    │  │ (lifecycle)│  │ (DOD)  │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 组件关系

| 组件 | 职责 | 与 nucleus 的关系 |
|------|------|------------------|
| **pdca.py** | PDCA 状态记录（确定性 I/O） | 唯一 Python 工具 |
| **governance-heartbeat** | 定时巡检协议 | 触发 Path B PDCA（Step 3a） |
| **governance-delegation** | 决策自动化分级 + HitL 协议 | L3 Review 引用 §10.2 A/B/C/D |
| **governance-knowledge** | DL/LL 管理 | 审计 <80 时 create_lesson_learned() |
| **governance-task** | Task 生命周期 | task-card 创建/状态派生 |
| **governance-quality** | DOD + Review-Gate | PDCA Check 在 L2/L3 场景触发 |
| **governance-evolution** | 元治理（L4） | 触发 Path A PDCA，决策"改什么" |

---

## 三、数据流设计

### 3.1 PDCA 主数据流

```
task-card (§一/§三/§五)
    ↓ 读取
LLM Plan → pdca.py p() → pdca/{id}.yaml (p 段)
    ↓
LLM Do   → pdca.py d() → pdca/{id}.yaml (d 段)
    ↓
LLM Check → pdca.py c() → pdca/{id}.yaml (c 段 + audit_eligible)
    ↓
LLM Act  → pdca.py a() → pdca/{id}.yaml (a 段 + completed)
    ↓
MISSION_BOARD 更新
```

### 3.2 审计数据流

```
L0/L1 pass → audit_eligible=true (自动)
    ↓
审计 heartbeat → pdca.py audit-queue → 待审计队列
    ↓ (包含 dl_refs, p_summary, d_summary, evidence)
LLM 评分 → pdca.py mark-audit --score {0-100}
    ↓
score >= 80 → 记录通过
score < 80  → has_problem=true → governance-knowledge.create_lesson_learned()
    ↓ (质疑 dl_refs 中的 DL 条目)
DL 置信度降低 → 下次 LLM 使用该 DL 时无法自动化
```

### 3.3 Human-in-the-Loop 数据流

```
L3 Check → verdict=pending → pdca/{id}.yaml (phase=check)
    ↓
feishu_post → Harold DM (A/B/C/D 格式)
    ↓ (等待 7 天)
Harold 回复 A → LLM 解析为 pass
    ↓
pdca.py c() --verdict pass --level L3 → phase=act
    ↓
pdca.py a() → phase=completed
    ↓
知识沉淀 (delegation §10.5)
```

---

## 四、接口契约

### 4.1 pdca.py CLI 接口

| 命令 | 必填参数 | 选填参数 | 输出 |
|------|---------|---------|------|
| `p` | --task-card-id, --summary | --criteria, --task-card-path, --dl-refs | {ok, cycle_index, phase} |
| `d` | --task-card-id, --summary, --status | --blocker | {ok, cycle_index, phase, status} |
| `c` | --task-card-id, --verdict | --level, --evidence | {ok, cycle_index, phase, verdict, needs_act} |
| `a` | --task-card-id, --summary | --next-task, --lessons | {ok, cycle_index, phase, next_task} |
| `status` | --task-card-id | - | {task_card_id, cycles_total, current_phase, ...} |
| `pending` | - | - | [{task_card_id, cycle_index, review_level, days_waiting, is_overdue, ...}] |
| `audit-queue` | - | - | [{task_card_id, cycle_index, dl_refs, p_summary, d_summary, ...}] |
| `mark-audit` | --task-card-id, --cycle-index, --score | --issues | {ok, score, has_problem, dl_refs, next_action} |

### 4.2 YAML 存储格式

```yaml
task_card_id: T1.1
task_card_path: /path/to/T1.1_TASK-CARD.md  # 首次 p() 时写入
cycles:
  - cycle_index: 1
    started_at: 2026-04-16T09:00:00Z
    completed_at: 2026-04-16T09:30:00Z
    phase: completed
    p:
      timestamp: 2026-04-16T09:00:00Z
      summary: "本轮目标：实现功能 X"
      acceptance_criteria: ["测试通过", "文档更新"]
      dl_refs: ["DL-2026-001", "DL-2026-002"]  # Plan 引用的 DL 条目
    d:
      timestamp: 2026-04-16T09:10:00Z
      summary: "完成功能 X，修改了 foo.py"
      status: completed
      blocker: null
    c:
      timestamp: 2026-04-16T09:20:00Z
      verdict: pass
      review_level: L1
      evidence: ["标准A: 通过", "标准B: 通过"]
      audit_eligible: true          # L0/L1 pass 自动设置
      audit_result: null            # 外部审计通过 mark_audit() 填写
    a:
      timestamp: 2026-04-16T09:30:00Z
      summary: "功能 X 完成，下一任务 T1.2"
      next_task: T1.2
      lessons: ["标准B 需提前确认"]
```

### 4.3 Phase 推进规则

| 调用 | 前置条件 | phase 变化 |
|------|---------|-----------|
| `p()` | 无 cycle 或上一 cycle=completed/check(pending) | → plan（新建 cycle） |
| `p()` | 上一 cycle=plan/do/act | → plan（复用 cycle） |
| `d()` | cycle 存在 | → do |
| `c(verdict=pass/fail/skip/partial)` | cycle 存在 | → act |
| `c(verdict=pending)` | L2/L3 级别 | → check（等待审批） |
| `a()` | cycle 在 act phase | → completed，写 completed_at |

---

## 五、安全边界

### 5.1 ADAS 规则校验

| 规则 | 校验逻辑 | 错误返回 |
|------|---------|---------|
| L0/L1 拒 pending | `review_level in {L0,L1} AND verdict=pending` | "L0/L1 为自验收级别，不允许 verdict=pending" |
| L3 首次必须 pending | `review_level=L3 AND existing_c is None AND verdict!=pending` | "L3 首次 Check 必须 verdict=pending" |

### 5.2 防无限循环

| 机制 | 说明 |
|------|------|
| max_cycles | 在 CycleUnit schema 中定义（task=3, topic=5, project=10, system=无限） |
| p() 新 cycle 创建 | 只有上一 cycle=completed/check(pending) 时才新建，防止重复规划 |
| 连续 3 次 fail | 上报 Harold 介入，不自动继续 |

### 5.3 原子写入

```python
# pdca.py _save() 实现
def _save(record):
    path = _record_path(record['task_card_id'])
    tmp = path + '.tmp'                    # 先写入临时文件
    with open(tmp, 'w') as f:
        yaml.dump(record, f)
    os.replace(tmp, path)                  # 原子替换
```

---

## 六、Phase 2-3 架构规划

### 6.1 轻量级层间传播（Phase 2）

**原则**：不引入 CycleAggregator 类，使用 pdca.py aggregate() 轻量函数。

```
Task verdict (pdca/{task_id}.yaml)
    ↓ aggregate(scope='topic', scope_id='T06')
Topic verdict (pdca/{topic_id}.yaml) — 自动派生，不由 LLM 填写
    ↓ aggregate(scope='project', scope_id='ZT-P015')
Project verdict (pdca/{project_id}.yaml) — 自动派生
```

**聚合规则**：

| 子项组合 | 父项 verdict |
|---------|-------------|
| 全部 pass | pass |
| 任一 fail | fail |
| 部分 pass + 部分 partial | partial |
| 全部 skip | skip |
| 混合 | partial |

**触发时机**：a() 完成后自动调用聚合（task 级完成后聚合到 topic）。

### 6.2 并发上限约束（Phase 2）

| Scope | 上限 | 校验时机 |
|-------|------|---------|
| task | ≤10 | p() 前置调用 check_concurrency('task') |
| topic | ≤5 | p() 前置调用 check_concurrency('topic') |
| project | ≤3 | p() 前置调用 check_concurrency('project') |
| system | 1 | 全局互斥 |

**超限行为**：返回 `{ok: false, error: '{scope} 并发上限 {N}，当前活跃 {M}，请等待完成'}`。

### 6.3 多粒度调度（Phase 2）

| Scope | 触发频率 | 对应 Heartbeat 数 |
|-------|---------|------------------|
| task | 每 30 分钟 | 1 |
| topic | 每 2 小时 | 4 |
| project | 每 1 天 | 48 |
| system | 每 1 周 | 336 |

**实现**：轻量 `scripts/scheduler_state.py`（只做计数器读写 + 原子写入）。

### 6.4 知识沉淀（Phase 2）

```
pdca/{id}.yaml (lessons)
    ↓ LLM 在 a() 时传入 lessons
knowledge/lessons/YYYY-MM-DD-{task_id}.md — 轻量 .md 文件
    ↓ 老化机制（每周清理孤立笔记）
节点数上限：500（Phase 2 DoD），5000（Plan C 触发条件 D）
```

**约束**：不使用 Obsidian 外部工具，纯文件存储。

### 6.5 Phase 3 展望

| 能力 | 说明 | 安全边界 |
|------|------|---------|
| 预测性监控 | 基于 logs/executions 识别趋势 | 只读，不自动执行 |
| 自主决策（白名单） | 在操作白名单内自动调整配置 | 严格白名单 + 操作审计日志 |
| 完整递归 PDCA | System 级自进化环 | L3 Review 不可绕过 |

### 6.6 Phase 2-3 文件结构

```
workspace/
├── pdca/                      # pdca.py 存储（多粒度）
│   ├── {task_id}.yaml         # Task 级（LLM 填写）
│   ├── {topic_id}.yaml        # Topic 级（aggregate() 自动派生）
│   └── {project_id}.yaml      # Project 级（aggregate() 自动派生）
├── config/
│   └── scheduler_state.yaml   # 多粒度调度计数器
├── knowledge/
│   └── lessons/               # 知识沉淀（轻量 .md 文件）
├── logs/                      # 观测日志
│   └── YYYY-MM-DD.jsonl
├── executions/                # 执行日志
│   └── YYYY-MM-DD.jsonl
└── scripts/
    ├── pdca.py                # PDCA 状态记录器
    └── scheduler_state.py     # 调度计数器（Phase 2 新增）
```

---

*版本：v2.0 | 创建日期：2026-04-16 | 修订日期：2026-04-18 | 架构师：张铁 + 银月*
