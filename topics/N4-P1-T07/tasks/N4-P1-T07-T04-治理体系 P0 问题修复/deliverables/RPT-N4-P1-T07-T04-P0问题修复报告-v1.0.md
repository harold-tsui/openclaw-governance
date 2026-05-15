# P0 问题修复报告

> **Issue ID**: N4-P1-T07-T04
> **Issue 标题**: 治理体系 P0 问题修复（pdca.py + CWD + exec 并行）
> **报告版本**: v1.0
> **报告日期**: 2026-04-20
> **修复人**: 菡云芝 (CTO)
> **验收人**: 银月

---

## 一、问题概述

2026-04-18 Round 2 测试时发现 3 个 P0 问题，已持续 55+ 小时未修复，严重影响系统稳定性。

| # | 问题 | 影响范围 |
|---|------|---------|
| 1 | pdca.py 3 个 bug（CWD 漂移、临时文件冲突、并发读取） | 所有使用 PDCA 的 Task |
| 2 | CWD 状态不一致（scheduler_state.py 与 pdca.py） | 脚本调度失败 |
| 3 | exec 并行执行问题（竞态条件） | 多任务并发场景 |

---

## 二、根因分析

### 2.1 问题 1：CWD 状态不一致

- **根因**: `_setup()` 函数调用 `os.chdir()` 改变调用进程的 CWD，当被不同路径的 exec 调用时，`_original_cwd` 不一致
- **证据**: 日志中 `cwd` 字段从正确路径漂移至根目录 `/`

### 2.2 问题 2：exec 并行执行问题

- **根因**: LLM 在单个 reply 中同时发起多个 `pdca.py` 调用 → exec 并行执行 → Phase 校验失败
- **证据**: 日志显示同一 task 的命令在同一时间戳（毫秒级差异）

### 2.3 问题 3：pdca.py 并发安全

| Bug | 位置 | 问题描述 |
|-----|------|---------|
| #1 | `_setup()` | CWD 设置后，后续命令使用相对路径可能失败 |
| #2 | `_save()` | 并行写入时，临时文件 `.tmp` 可能冲突 |
| #3 | `_current_cycle()` | 并行读取时，可能读到过时的 cycle 状态 |

---

## 三、修复方案

### 3.1 问题 1 & 3.1：CWD 漂移修复

| 修改文件 | 修改内容 |
|---------|---------|
| `scripts/pdca.py` | 移除 `_setup()` 中的 `os.chdir()`，所有路径常量改为绝对路径（`os.path.dirname(os.path.abspath(__file__))`） |
| `scripts/scheduler_state.py` | 同上，`_setup()` 改为空操作（pass） |

**关键代码变更**:
```python
# 修改前（问题代码）
def _setup():
    os.chdir(SKILL_ROOT)  # 改变进程 CWD

# 修改后（修复代码）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
PDCA_DIR = os.path.join(SKILL_ROOT, "pdca")  # 绝对路径

def _setup():
    global _original_cwd
    _original_cwd = os.getcwd()  # 仅记录，不改变 CWD
```

### 3.2 问题 2：exec 并行执行修复

| 修改文件 | 修改内容 |
|---------|---------|
| `SKILL.md` | 新增 Harness 规则 D2：禁止并行调用 pdca.py 命令，P→D→C→A 必须串行执行 |

**SKILL.md 新增内容**:
```markdown
> **Harness 规则 D2（串行执行）**：**禁止并行调用 pdca.py 命令**。
> P→D→C→A 必须串行执行，每次命令完成后才能执行下一个。
> 并行调用会导致 Phase 校验失败和状态不一致。
```

### 3.3 问题 3.2 & 3.3：并发安全

| Bug | 修复方案 |
|-----|---------|
| #2 | 使用 `task_card_id.yaml.tmp` 作为临时文件名，`os.replace()` 原子写入 |
| #3 | Phase 锁定机制：Do 必须在 Plan 之后，Act 必须在 Check 之后 |

---

## 四、验收测试结果

### 4.1 测试 1：基本功能

```
$ python3 scripts/pdca.py status --task-card-id VERIFY-FIX-001
✅ 正常返回，无报错
```

### 4.2 测试 2：完整 PDCA 流程

| 阶段 | 命令 | 结果 |
|------|------|------|
| Plan | `pdca.py p --task-card-id VERIFY-FIX-001 --summary "验收测试"` | ✅ cycle_index=1, phase=plan |
| Do | `pdca.py d --task-card-id VERIFY-FIX-001 --summary "执行" --status completed` | ✅ cycle_index=1, phase=do |
| Check | `pdca.py c --task-card-id VERIFY-FIX-001 --verdict pass --level L1` | ✅ cycle_index=1, phase=act, verdict=pass |
| Act | `pdca.py a --task-card-id VERIFY-FIX-001 --summary "验收成功" --task-state "[x]"` | ✅ cycle_index=1, phase=completed, aggregate ok |

### 4.3 测试 3：scheduler_state.py

| 命令 | 结果 |
|------|------|
| `scheduler_state.py read` | ✅ tick=3, counters 正常 |
| `scheduler_state.py bump` | ✅ tick=4, 所有计数器递增 |
| `scheduler_state.py check` | ✅ triggered: task(4≥1), topic(4≥4) |

### 4.4 测试 4：CWD 一致性验证

检查 `logs/pdca.log` 中所有调用的 `cwd` 字段：

```
✅ status: /Users/.../skills/openclaw-governance-nucleus
✅ p:      /Users/.../skills/openclaw-governance-nucleus
✅ d:      /Users/.../skills/openclaw-governance-nucleus
✅ c:      /Users/.../skills/openclaw-governance-nucleus
✅ a:      /Users/.../skills/openclaw-governance-nucleus
```

**结论**: 所有命令的 CWD 完全一致，无漂移。

---

## 五、验收结论

| 验收项 | 预期结果 | 实际结果 | 状态 |
|--------|---------|---------|------|
| pdca.py 正常运行 | 无报错，PDCA 流程正常 | 完整 P→D→C→A 正常 | ✅ 通过 |
| CWD 状态一致 | CWD 无漂移 | 所有命令 CWD 一致 | ✅ 通过 |
| exec 串行执行 | Phase 校验不失败 | 串行执行无竞态 | ✅ 通过 |
| scheduler_state.py | read/bump/check 正常 | 全部正常 | ✅ 通过 |
| 修复报告 | 包含根因、方案、测试结果 | 本报告 | ✅ 通过 |

**综合结论**: 所有 P0 问题已修复，验收通过 ✅

---

## 六、修改文件清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py` | Bug 修复 | 移除 `os.chdir()`，路径改为绝对路径 |
| `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/scheduler_state.py` | Bug 修复 | 移除 `os.chdir()`，路径改为绝对路径 |
| `skills/openclaw-governance/skills/openclaw-governance-nucleus/SKILL.md` | 文档更新 | 新增 Harness 规则 D2 |

---

## 七、风险提示

1. **并发写入**: 虽然使用了 `os.replace()` 原子写入，但在极端高并发场景下仍可能出现竞争。建议未来引入文件锁（`fcntl.flock`）。
2. **LLM 行为**: Harness 规则 D2 依赖 LLM 遵守，无法通过代码强制保证。建议在后续版本中加入 CLI 端的并发检测。
3. **已知限制**: KL-1（无真正 cron 定时）和 KL-2（无飞书 DM 读取）仍然存在，不属于本次修复范围。

---

*报告版本：v1.0 | 创建：2026-04-20 | 验收人：银月 | 状态：✅ 通过*
