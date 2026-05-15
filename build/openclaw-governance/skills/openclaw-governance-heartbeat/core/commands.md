> **Governance Heartbeat** · Entry: `skills/openclaw-governance/skills/openclaw-governance-heartbeat/SKILL.md`
> State: `60_Agents/{agent_id}/memory/heartbeat-state.json`
> Reference document — structured command definitions for heartbeat operations

# Governance Heartbeat Command Reference

This document defines every heartbeat operation as a **structured command**.
Each command has a fixed name, typed parameters, and expected output.

---

## How to Execute

### Option A: Direct file operations

Heartbeat commands are file-based operations. Read/write the appropriate files
per the command spec below. No helper script is needed.

### Command Spec Format

```
Command:     gov heartbeat <command> [--param value]
Required:    param1 (type)
Optional:    param3 (type, default)
Returns:     field1, field2
State:       what to update in heartbeat-state.json
Errors:      specific error handling
```

---

## Scan Commands

### `gov heartbeat scan-mission-board`

扫描 Agent 的 MISSION_BOARD，读取四层跟踪状态。

```
Required:    --agent-id (string)
Optional:    --scope (self|all, self)
Returns:     projects[], topics[], tasks[], deliverables[]
State:       无（只读操作）
Errors:
  MISSION_BOARD 不存在 → 返回空看板，记录警告
```

### `gov heartbeat scan-all-agents`

银月扫描所有 Agent 的 MISSION_BOARD。

```
Required:    无
Optional:    --agent-list (array, from agents.yaml)
Returns:     agent_states[], healthy_count, unhealthy_count
State:       无（只读操作）
Errors:
  Agent MISSION_BOARD 不可读 → 标记为 unresponsive，继续扫描下一个
```

---

## Track Commands

### `gov heartbeat track-responsibilities`

判断哪些项目/Topic/Task 需要跟踪（基于 agent_id 和 pic）。

```
Required:    --agent-id (string)
Returns:     tracked_items[], ownership_map
State:       无（只读操作）
Errors:
  无
```

### `gov heartbeat update-mission-board`

更新 MISSION_BOARD 状态（编辑 §一 状态总览 + §九 最后更新时间）。

```
Required:    --agent-id (string), --updates (object)
Optional:    --section (string, full)
Returns:     write_status (success/failed), updated_at
State:       编辑 MISSION_BOARD.md 文件
Errors:
  文件不可写 → 重试 1 次，仍失败则记录严重警告
```

---

## Report Commands

### `gov heartbeat generate-report`

生成 heartbeat 报告（晨会/夕会/异常）。

```
Required:    --agent-id (string), --report-type (morning|evening|exception)
Optional:    --scope (self|all, self)
Returns:     report_text, feishu_payload
State:       更新 heartbeat-state.json 的 reporting 部分
Errors:
  无
```

### `gov heartbeat post-feishu`

发送飞书报告。

```
Required:    --channel-id (string), --report-text (string)
Optional:    --priority (P0|P1|P2|P3, P2)
Returns:     post_status (success/failed), message_id
State:       更新 heartbeat-state.json 的 reporting.lastSent
Errors:
  飞书 API 失败 → 重试 1 次，记录错误
```

---

## NUCLEUS Integration Commands

### `gov heartbeat run-pdca-cycle`

通过 pdca.py 驱动单个 task 的 PDCA 循环。

```
Required:    --task-card-id (string)
Optional:    --step (p|d|c|a|full, full)
Returns:     pdca_result, next_action
State:       更新 heartbeat-state.json 的 heartbeat.tasks
Errors:
  Task-CARD 不存在 → 返回错误
  PDCA 脚本执行失败 → 记录错误，继续下一个 task
```

### `gov heartbeat check-pending`

检查 PDCA pending 队列（等待 Harold review 的任务）。

```
Required:    无
Optional:    --task-card-id (string, 单个任务检查)
Returns:     pending_items[], overdue_count
State:       无（只读操作）
Errors:
  无
```

---

## PDCA Audit Commands

### `gov heartbeat check-audit-queue`

获取 L0/L1 自通过待审计 PDCA 周期队列。

```
Required:    无
Returns:     audit_queue[] (task_card_id, cycle_index, review_level, dl_refs, evidence)
State:       无（只读操作，调用 pdca.py audit-queue）
Errors:
  pdca.py 执行失败 → 记录错误，跳过本轮审计
```

### `gov heartbeat mark-audit-result`

回写单个 PDCA 周期的外部审计结果。

```
Required:    --task-card-id (string), --cycle-index (int), --score (int, 0-100)
Optional:    --issues (string, 问题描述)
Returns:     audit_status (success/failed)
State:       调用 pdca.py mark-audit，更新 pdca/*.yaml 的 audit_result 字段
Errors:
  score 超出范围 → 拒绝
  cycle 不存在 → 拒绝
  非 audit_eligible 状态 → 拒绝

---

## State Commands

### `gov heartbeat read-state`

读取 heartbeat 状态文件。

```
Required:    --agent-id (string)
Returns:     heartbeat-state.json (完整对象)
State:       无（只读操作）
Errors:
  状态文件不存在 → 从 templates/heartbeat-state.json 初始化
```

### `gov heartbeat write-state`

更新 heartbeat 状态文件。

```
Required:    --agent-id (string), --section (string), --data (object)
Optional:    --merge (bool, true)
Returns:     write_status (success/failed), updated_at
State:       更新 60_Agents/{agent_id}/memory/heartbeat-state.json
Errors:
  写失败 → 重试 1 次，仍失败则记录警告
```

---

## Escalation Commands

### `gov heartbeat check-escalation`

检查是否需要触发故障升级（heartbeat 连续失败）。

```
Required:    --agent-id (string)
Returns:     needs_escalation (bool), reason, failure_count
State:       读取 failureEscalation 部分
Errors:
  无
```

---

## Glossary

| 术语 | 定义 |
|------|------|
| **MISSION_BOARD** | Agent 任务看板，四层跟踪（Project → Topic → Task → Deliverable） |
| **Pending** | PDCA 循环中等待 Harold review 的状态 |
| **Overdue** | Pending 超过 7 天的任务 |
| **Unresponsive** | Agent 120s 未响应 heartbeat 扫描 |
| **1:1 Target** | 每个 heartbeat 周期推进或关闭至少一个 Task |

---

*Version: v1.0 | Created: 2026-04-18 | N4-P1-T07 T06*
