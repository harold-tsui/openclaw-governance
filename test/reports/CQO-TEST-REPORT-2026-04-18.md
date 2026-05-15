# CQO 测试报告 · NUCLEUS 4.0 guardrails

> **测试日期**：2026-04-18
> **测试人**：张铁 (CQO)
> **测试范围**：scheduler_state.py + pdca.py guardrails
> **测试结论**：scheduler_state.py ✅ 正常，pdca.py ❌ 有 3 个 bug

---

## 一、测试环境

| 项目 | 信息 |
|------|------|
| **测试 Agent** | cqo (张铁) |
| **测试目录** | `/Users/haroldtsui/Workspaces/openclaw/main/skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/` |
| **Python 版本** | python3 |
| **测试方法** | CLI 命令调用 |

---

## 二、scheduler_state.py 测试结果 ✅

### 2.1 read 命令

**命令**：
```bash
python3 scheduler_state.py read
```

**输出**：
```json
{
  "ok": true,
  "tick": 0,
  "counters": {
    "task": 0,
    "topic": 0,
    "project": 0,
    "system": 0
  },
  "thresholds": {
    "task": 1,
    "topic": 4,
    "project": 48,
    "system": 96
  }
}
```

**结论**：✅ 正常

---

### 2.2 bump 命令

**命令**：
```bash
python3 scheduler_state.py bump
```

**输出**：
```json
{
  "ok": true,
  "tick": 1,
  "counters": {
    "task": 1,
    "topic": 1,
    "project": 1,
    "system": 1
  }
}
```

**结论**：✅ 正常

---

### 2.3 check 命令

**命令**：
```bash
python3 scheduler_state.py check
```

**输出**：
```json
{
  "ok": true,
  "tick": 0,
  "triggered": [],
  "scopes_needing_action": []
}
```

**结论**：✅ 正常

---

## 三、pdca.py 测试结果 ❌

### 3.1 测试流程

**完整 PDCA 流程测试**：

| 步骤 | 命令 | 预期 | 实际 | 状态 |
|------|------|------|------|------|
| **P** | `pdca.py p --task-card-id TEST-FULL-001 --summary "测试"` | phase=plan | phase=plan | ✅ |
| **D** | `pdca.py d --task-card-id TEST-FULL-001 --summary "执行" --status completed` | phase=do, status=completed | phase=do, status=completed | ✅ |
| **C** | `pdca.py c --task-card-id TEST-FULL-001 --verdict pass --level L1` | phase=act, verdict=pass | FileNotFoundError | ❌ |
| **A** | `pdca.py a --task-card-id TEST-FULL-001 --summary "完成"` | phase=completed | "Act 阶段不能在没有 PDCA 历史的情况下调用" | ❌ |
| **status** | `pdca.py status --task-card-id TEST-FULL-001` | current_phase=act | current_phase=plan | ❌ |

---

### 3.2 Bug 详情

#### Bug #1：c() _save() FileNotFoundError ⭐ P0

**错误信息**：
```
FileNotFoundError: [Errno 2] No such file or directory: 
'pdca/TEST-FULL-001.yaml.tmp' -> 'pdca/TEST-FULL-001.yaml'
```

**根因分析**：
- `_save()` 中 `os.replace()` 使用相对路径
- .tmp 文件在 CWD（60_Agents/cqo）创建
- 目标文件在 skill_root/pdca/
- 路径不一致导致 replace 失败

**修复建议**：
```python
def _save(record: Dict[str, Any]) -> None:
    path = _record_path(record['task_card_id'])
    tmp = path + '.tmp'
    # 使用绝对路径
    abs_path = os.path.abspath(path)
    abs_tmp = os.path.abspath(tmp)
    with open(abs_tmp, 'w', encoding='utf-8') as f:
        yaml.dump(record, f, allow_unicode=True, default_flow_style=False)
    os.replace(abs_tmp, abs_path)
```

---

#### Bug #2：status 输出与 YAML 不一致 ⭐ P1

**现象**：
- `status` 输出：`current_phase=plan`
- YAML 文件实际：`phase=act`

**根因分析**：
- `_load()` 可能读取缓存而非最新文件
- 或 `_current_cycle()` 判断逻辑有误

**验证**：
```yaml
# pdca/TEST-FULL-001.yaml 实际内容
cycles:
- phase: act        ← YAML 显示 act
  c:
    verdict: pass
```

**修复建议**：
- 检查 `_load()` 是否每次重新读取文件
- 检查 `_current_cycle()` 是否正确判断最新 cycle

---

#### Bug #3：d 段丢失 ⭐ P1

**现象**：
- YAML 文件：`d: null`（没有 d 段）
- 但 `d()` 命令返回成功：`{"ok": true, "phase": "do", "status": "completed"}`

**根因分析**：
- `d()` 函数可能未正确写入 d 段到 record
- 或 `_save()` 在 d() 后未调用

**验证**：
```yaml
# pdca/TEST-FULL-001.yaml 实际内容
cycles:
- d: null           ← Bug：d 段丢失
  p:
    summary: 完整 PDCA 流程测试
```

**修复建议**：
- 检查 `d()` 函数是否正确调用 `_save(record)`
- 检查 d 段写入逻辑

---

### 3.3 YAML 文件实际内容

```yaml
cycles:
- a: null
  c:
    audit_eligible: true
    audit_result: null
    evidence:
    - 测试成功
    review_level: L1
    timestamp: '2026-04-18T12:43:32.065391+00:00'
    verdict: pass
  completed_at: null
  cycle_index: 1
  d: null                    ← Bug #3：d 段丢失
  p:
    acceptance_criteria:
    - a
    - b
    dl_refs: []
    summary: 完整 PDCA 流程测试
    timestamp: '2026-04-18T12:43:32.062534+00:00'
  phase: act                 ← Bug #2：status 显示 phase=plan
  started_at: '2026-04-18T12:43:32.062397+00:00'
project_id: null
task_card_id: TEST-FULL-001
task_card_path: null
task_state: null
task_state_updated_at: null
topic_id: null
```

---

## 四、测试结论

| 组件 | 状态 | Bug 数量 |
|------|------|---------|
| **scheduler_state.py** | ✅ 正常 | 0 |
| **pdca.py** | ❌ 有 bug | 3 |

---

## 五、Bug 优先级评估

| Bug ID | 严重程度 | 优先级 | 影响 |
|--------|---------|--------|------|
| **#1** | 阻塞 | P0 | c() 完全失败，PDCA 无法完成 |
| **#2** | 数据不一致 | P1 | status 输出误导，影响判断 |
| **#3** | 数据丢失 | P1 | d 段历史丢失，影响追溯 |

---

## 六、建议修复顺序

1. **P0**：修复 Bug #1（c() _save() 路径问题）
2. **P1**：修复 Bug #3（d 段写入逻辑）
3. **P1**：修复 Bug #2（status 输出逻辑）

---

## 七、相关文件

| 文件 | 路径 |
|------|------|
| pdca.py | `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py` |
| scheduler_state.py | `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/scheduler_state.py` |
| 测试 YAML | `skills/openclaw-governance/skills/openclaw-governance-nucleus/pdca/TEST-FULL-001.yaml` |

---

## 八、附录：完整测试日志

### 8.1 scheduler_state.py 测试日志

```
$ python3 scheduler_state.py read
{
  "ok": true,
  "tick": 0,
  "counters": {"task": 0, "topic": 0, "project": 0, "system": 0},
  "thresholds": {"task": 1, "topic": 4, "project": 48, "system": 96}
}

$ python3 scheduler_state.py bump
{
  "ok": true,
  "tick": 1,
  "counters": {"task": 1, "topic": 1, "project": 1, "system": 1}
}

$ python3 scheduler_state.py check
{
  "ok": true,
  "tick": 0,
  "triggered": [],
  "scopes_needing_action": []
}
```

---

### 8.2 pdca.py 测试日志

```
$ python3 pdca.py p --task-card-id TEST-FULL-001 --summary "完整 PDCA 流程测试" --criteria "a|b"
{
  "ok": true,
  "cycle_index": 1,
  "phase": "plan"
}

$ python3 pdca.py d --task-card-id TEST-FULL-001 --summary "执行 Do 阶段" --status completed
{
  "ok": true,
  "cycle_index": 1,
  "phase": "do",
  "status": "completed"
}

$ python3 pdca.py c --task-card-id TEST-FULL-001 --verdict pass --level L1 --evidence "测试成功"
Traceback (most recent call last):
  File ".../pdca.py", line 1058, in <module>
    main()
  File ".../pdca.py", line 1018, in main
    result = c(...)
  File ".../pdca.py", line 328, in c
    _save(record)
  File ".../pdca.py", line 95, in _save
    os.replace(tmp, path)
FileNotFoundError: [Errno 2] No such file or directory: 
'pdca/TEST-FULL-001.yaml.tmp' -> 'pdca/TEST-FULL-001.yaml'

$ python3 pdca.py a --task-card-id TEST-FULL-001 --summary "测试完成" --task-state "[x]"
{
  "ok": false,
  "error": "Act 阶段不能在没有 PDCA 历史的情况下调用。请先执行完整的 P→D→C 流程"
}

$ python3 pdca.py status --task-card-id TEST-FULL-001
{
  "task_card_id": "TEST-FULL-001",
  "cycles_total": 1,
  "current_cycle_index": 1,
  "current_phase": "plan",          ← Bug：YAML 显示 phase=act
  "current_verdict": null,
  "last_p_summary": "完整 PDCA 流程测试",
  "last_d_status": null             ← Bug：d 段丢失
}
```

---

*测试报告结束*

*报告人：张铁 (CQO)*
*报告日期：2026-04-18 20:46*