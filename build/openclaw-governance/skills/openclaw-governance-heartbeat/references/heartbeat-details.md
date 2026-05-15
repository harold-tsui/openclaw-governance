# Heartbeat Operation Details — Detailed Reference

> Moved from heartbeat SKILL.md §三–§十一 to reduce main file size.

## §三 银月 heartbeat 职责

### 七-Step Process

```
Step 0  Scope Declaration    上下文加载与声明
Step 1  MISSION_BOARD Triage  任务板巡检与分类
Step 2  Review 级别判断        新增任务确认 Review 级别
Step 3  执行推进 & 状态冒泡   推进阻塞、核查完成、向上同步状态
Step 4  知识沉淀后处理核查   Weekly Review 核查，3 工作日宽限期
Step 5  授权降级评估         评估是否满足阶段升级或授权降级条件
Step 6  质量管控核查         核查张铁审核状态、质量指标、PDCA 审计队列
Step 7  用户 日报            汇总今日情况，提交 Harold
```

### Step 6 内部子步骤

```
Step 6a  PDCA 审计队列巡检
  - 调用 pdca.py audit-queue 获取待审计列表
  - 对每个待审计 cycle 进行质量评分（0-100）
  - 评分 < 80 → 触发 governance-knowledge.create_lesson_learned()
  - 调用 pdca.py mark-audit 回写审计结果

Step 6b  质量指标核查
  - 核查张铁审核状态
  - 检查交付物质量趋势
```

### MISSION_BOARD Read Strategy

**Normal path**: Direct read of each Agent's MISSION_BOARD:
```python
agents = ["ceo", "cto", "cdo", "cco", "cvo", "cio", "cfo", "cqo", "ld", "ec-ceo"]
for agent in agents:
    read(f"60_Agents/{agent}/MISSION_BOARD.md")
```

**Recovery path** (only when):
- MISSION_BOARD > 24h stale
- Inconsistency with Task-CARD state
- New Agent initialization

### Agent Maintenance Checklist

```
[ ] Scan responsible Projects → confirm status (🟢/🟡/🔴) and role (PIC/participant/observer)
[ ] Scan responsible/participating Topics → update status, record task progress
[ ] Scan responsible/participating Tasks → update state ([ ]/[P]/[V]/[x]/[?]), identify blockers
[ ] Scan pending Deliverables → check for own deliverables awaiting acceptance
```

## §四 实时进展上报机制

### Trigger Conditions

| Trigger | Report Content |
|---------|---------------|
| Harold message starts analysis | "正在分析消息" |
| Determined as formal task | "判定为任务，正在整理" |
| Task creation complete | "任务已创建，准备分发" |
| Sub-Agent report received | "收到汇报，正在向 Harold 汇报" |
| Blocked | "遇到阻塞，需要 Harold 决策" |

### Report Format
```
[进展] Task-XXX: 正在[当前动作]
状态：分析中→整理中→已创建→分发中→完成
```

### Blocker Handling

| Blocker Type | Handling | Time Limit |
|-------------|----------|------------|
| Missing input | Contact source, urge delivery | Immediate |
| Waiting Harold decision | Confirm moved to §四 | 24h reminder |
| Inter-Agent dependency | Contact predecessor PM | 2 hours |
| External dependency | Record external status | 2 hours |

## §五 巡检频率与汇报规则

### Report Types

| Type | Time | Content | Condition |
|------|------|---------|-----------|
| **Morning Report** | 07:00 | Full status (progress, blockers, today's plan) | Daily fixed |
| **Evening Report** | 21:00 | Full status (today's done, tomorrow's plan) | Daily fixed |
| **Exception/Change** | Real-time | Only changed/exception parts | State change or blocker |

### Silent Execution Rule
Other times (non 7:00/21:00):
- Execute full heartbeat process (Step 1-7)
- Update MISSION_BOARD
- **No Feishu message** (unless exception or state change)
- Local record to `heartbeat-state.json`

### Original Frequency (Adjusted)

| Type | Frequency | Participants | Reporting |
|------|-----------|-------------|-----------|
| Morning heartbeat | 07:00 | All Agents | Feishu report |
| Evening heartbeat | 21:00 | All Agents | Feishu report |
| Intermediate heartbeat | Every 30 min | All Agents | Silent, no message |
| P0 task period | Every 4 hours | All Agents | Silent, message on exception |
| Weekly summary | Friday | 银月 | Full Feishu report |

## §六 各 Agent heartbeat 检查清单

### Execution Steps

```
[Step 1] Read own MISSION_BOARD.md
[Step 2] Scan four-layer tracking (Project/Topic/Task/Deliverable)
[Step 3] Update state ⭐ MUST include file editing
    3.1 Edit MISSION_BOARD.md §一 status overview
    3.2 Edit MISSION_BOARD.md §九 "last updated" time
    3.3 Update heartbeat-state.json
    3.4 Create/update memory/YYYY-MM-DD.md
    3.5 Verify: re-read MISSION_BOARD.md to confirm update

    **Prohibited**:
    - ❌ Send Feishu message without editing MISSION_BOARD.md
    - ❌ Only update heartbeat-state.json without editing MISSION_BOARD.md
    - ❌ Heartbeat >24h without MISSION_BOARD.md update

[Step 3a] NUCLEUS PDCA Harness — see nucleus SKILL.md §四
[Step 4] Identify blockers (>2 days mark [?])
[Step 5] Check pending deliverables
[Step 6] Quality control check + PDCA audit queue
  6.1 Check 张铁 review status
  6.2 Run pdca.py audit-queue, score each eligible cycle
  6.3 Call pdca.py mark-audit to record results
[Step 7] Prepare report
[Step 8] Send to 银月
```

## §七 银月发起 heartbeat

```python
sessions_spawn(
    agentId="cto",
    task="## 分布式 Heartbeat 检查\n\n请读取并更新你的 MISSION_BOARD",
    timeoutSeconds=120,
    mode="run",
    runtime="subagent"
)
```

**Timeout**: >120s → mark "未响应", continue scanning, note in Harold daily report.

## §八 Task-CARD 作为 AI 总线

```
Agent A (银月) → writes decisions, progress, issues → Task-CARD
    ↓ reads context
Agent B (张铁) → writes execution results → Task-CARD
    ↓ reads results
Agent C (菡云芝)
```

### Context Transfer Rules

| Scenario | Write Content | Read Timing |
|----------|--------------|-------------|
| Task assignment | Goal, inputs, acceptance criteria | When receiving task |
| Progress update | Completion, blockers, risks | During heartbeat |
| Delivery acceptance | Deliverables, execution summary | When submitting for review |
| Issue escalation | Description, impact scope | When discovering problem |

## §九 模板清单

| Template | Purpose | Version |
|----------|---------|---------|
| `templates/TMPL-HEARTBEAT.md` | Main Agent heartbeat protocol | v3.2 |
| `templates/TMPL-HEARTBEAT-SUB.md` | Sub Agent heartbeat protocol | v3.2 |
| `templates/heartbeat-state.json` | State record template | v1.1.0 |

## §十 状态模板机制与权限说明

**State file**: `60_Agents/{agent_id}/memory/heartbeat-state.json`

**Key fields**:

| Field | Purpose | Update Timing |
|-------|---------|---------------|
| `heartbeat.lastCheck` | Last check date | Each heartbeat |
| `heartbeat.checkCount` | Cumulative checks | Each heartbeat +1 |
| `heartbeat.issues[]` | Discovered issues | When found |
| `heartbeat.stats.heartbeatTaskRatio` | Heartbeat/Task ratio | Each heartbeat complete |
| `reporting.morningReport.lastSent` | Morning report time | 07:00 |
| `reporting.eveningReport.lastSent` | Evening report time | 21:00 |

## §十一 命令规范

**Core commands**:
- `gov heartbeat scan-mission-board --agent-id <id>` — Scan mission board
- `gov heartbeat track-responsibilities --agent-id <id>` — Responsibility tracking
- `gov heartbeat update-mission-board` — Update board state
- `gov heartbeat run-pdca-cycle --task-card-id <id>` — PDCA cycle
- `gov heartbeat check-pending` — Check pending queue
- `gov heartbeat generate-report` — Generate report
- `gov heartbeat read-state` / `write-state` — State read/write
