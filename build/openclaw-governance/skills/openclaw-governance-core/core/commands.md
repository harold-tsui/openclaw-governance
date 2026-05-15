> **Governance Core** · Entry: `skills/openclaw-governance/skills/openclaw-governance-core/SKILL.md`
> State: `.system/governance/current/.gov-state.json`
> Reference document — structured command definitions for governance core operations

# Governance Core Command Reference

This document defines every governance core operation as a **structured command**.
Each command has a fixed name, typed parameters, and expected output.

When executing governance operations, **use these command definitions** rather than manually
constructing file paths or state checks. This ensures correct parameters, proper error handling,
and consistent output.

---

## How to Execute

### Option A: Direct file operations (most commands)

Governance core commands are file-based operations. Read/write the appropriate files
per the command spec below. No helper script is needed.

### Command Spec Format

Each command below is defined as:

```
Command:     gov core <command> [--param value]
Required:    param1 (type), param2 (type)
Optional:    param3 (type, default)
Returns:     field1, field2
State:       what to update in .gov-state.json
Errors:      specific error handling
```

---

## Bootstrap Commands

### `gov core bootstrap-agent`

执行 Agent 启动序列（Phase 1 → 2A → 2B → 3 → 4）。

```
Required:    --agent-id (string)
Optional:    --skip-phase (string, none), --verbose (bool, false)
Returns:     phase_results[], warnings[], status (success/degraded/failed)
State:       bootstrap: { agent_id, last_boot_time, phase_results }
Errors:
  Phase 1 failed → TERMINATE（无法启动）
  Phase 2 failed → degraded 继续（记录警告）
  Phase 3 failed → WARN_AND_CONTINUE
```

### `gov core verify-phase`

验证 Phase 启动结果，检查屏障条件。

```
Required:    --phase (Phase1|Phase2A|Phase2B|Phase3|Phase4)
Returns:     passed (bool), failed_modules[], warnings[]
State:       phase_lock: { phase, locked_at, passed }
Errors:
  Phase 1 barrier failed → 终止启动
  Phase 2 barrier failed → degraded，记录警告
```

---

## Skill Loading Commands

### `gov core load-skill`

按依赖驱动加载协议加载指定 Skill。

```
Required:    --skill-name (string)
Optional:    --phase (string, auto), --force (bool, false)
Returns:     skill_version, load_status, dependencies_met (bool)
State:       loaded_skills: { skill_name, version, loaded_at, phase }
Errors:
  Skill 不存在 → 返回错误，记录警告
  依赖未满足 → 返回错误，不加载
  版本不兼容 → 返回错误，记录警告
```

### `gov core verify-skill-dependencies`

验证 Skill 依赖链是否完整。

```
Required:    --skill-name (string)
Returns:     all_met (bool), missing_deps[], degraded_deps[]
State:       无（只读操作）
Errors:
  循环依赖 → 返回错误
  缺失依赖 → 返回 missing_deps 列表
```

---

## State Management Commands

### `gov core read-state`

读取治理核心状态文件。

```
Required:    无（读取 .gov-state.json）
Optional:    --section (string, full)
Returns:     state object (完整或指定 section)
State:       无（只读操作）
Errors:
  状态文件不存在 → 返回空状态（使用 gov-state.json 模板初始化）
```

### `gov core write-state`

更新治理核心状态文件。

```
Required:    --section (string), --data (object)
Optional:    --merge (bool, true)
Returns:     write_status (success/failed), updated_at
State:       更新 .gov-state.json 对应 section
Errors:
  写失败 → 重试 1 次，仍失败则记录警告
  状态文件损坏 → 使用模板重新初始化，记录严重警告
```

---

## Probe Commands

### `gov core run-probe`

执行模块探针验证（阻塞型/咨询型/可选型）。

```
Required:    --module (string)
Optional:    --probe-type (blocking|advisory|optional, advisory)
Returns:     passed (bool), details[], failure_reason (optional)
State:       probe_results: { module, result, timestamp }
Errors:
  连续失败达到阈值 → 咨询型升级为阻塞型
```

### `gov core check-probe-escalation`

检查咨询型探针是否需要升级为阻塞型。

```
Required:    --module (string)
Returns:     escalated (bool), consecutive_failures (int), threshold (int)
State:       读取 .system/governance/current/probe-failures.yaml（如存在）
Errors:
  无
```

---

## Configuration Commands

### `gov core load-config`

加载治理配置文件（agents.yaml, projects.yaml, skills.yaml 等）。

```
Required:    --config-type (agents|projects|skills|topics|globals)
Optional:    --scope (system|user|both, both)
Returns:     config_data (object), load_status
State:       无（只读操作）
Errors:
  文件不存在 → 返回空配置，记录警告
  语法错误 → 返回错误，阻止加载
```

### `gov core verify-config`

验证配置文件完整性（用于探针和屏障检查）。

```
Required:    --config-type (agents|projects|skills|topics|globals)
Returns:     valid (bool), errors[], warnings[]
State:       无（只读操作）
Errors:
  无
```

---

## PDCA Integration Commands

### `gov core next-pdca-cycle`

为 PDCA 下一循环准备上下文（基于 Harold 修正的 PDCA-A 理解）。

```
Required:    --task-card-id (string)
Optional:    --last-act-summary (string), --escalation-required (bool, false)
Returns:     new_cycle_context (object), escalation_needed (bool)
State:       更新 .gov-state.json 的 pdca_context
Errors:
  连续 3 次 fail → 标记 escalation_required
```

### `gov core check-escalation`

检查任务是否需要上报 Harold（连续失败/阻塞超时）。

```
Required:    --task-card-id (string)
Returns:     needs_escalation (bool), reason (string), consecutive_fails (int)
State:       无（只读操作）
Errors:
  无
```

---

## Glossary

| 术语 | 定义 |
|------|------|
| **Phase** | 启动序列阶段（Phase 1-4），按依赖驱动加载 |
| **Barrier** | Phase 间的门控条件（硬屏障/软屏障/条件屏障） |
| **Probe** | 模块验证探针（阻塞型/咨询型/可选型） |
| **Degraded** | 模块部分功能降级，但不阻止继续执行 |
| **Escalation** | 问题上报 Harold 的触发条件 |

---

*Version: v1.0 | Created: 2026-04-18 | N4-P1-T07 T05*
