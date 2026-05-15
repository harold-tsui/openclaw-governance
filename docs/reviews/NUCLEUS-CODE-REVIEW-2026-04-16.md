# NUCLEUS 4.0 代码审查报告

> **审查日期**：2026-04-16
> **审查范围**：`skills/openclaw-governance/skills/openclaw-governance-nucleus/`
> **审查人**：银月（会话内 review）
> **状态**：✅ P0 修复已完成，P1 协议已补充

---

## 一、审查结论

### 1.1 整体判断

**实现比预期更完整，但存在一个核心架构错位。**

`skills/.../openclaw-governance-nucleus/` 已有完整的 Python 骨架（`core/` + `modules/` + `scripts/`），unit test 126 个、通过率 100%。但 `modules/` 层存在设计错误——部分函数试图用 Python stub 替代 LLM 的判断职责，导致系统在 heartbeat 触发后无法实际执行 PDCA 循环。

### 1.2 各层状态

| 层 | 目录 | 状态 | 说明 |
|----|------|------|------|
| 基础设施层 | `core/` | ✅ 正确 | 纯文件 I/O，符合"Python 只做确定性计算"原则 |
| 调度入口 | `scripts/` | ✅ 正确 | heartbeat Step 3a 调用正常 |
| PDCA 模块层 | `modules/` | ⚠️ 混杂 | 部分函数正确，部分是 stub 或架构错误 |
| LLM 协议层 | `SKILL.md` | 🔴 缺失 | 无任何 LLM 执行指令，scheduler 创建的 cycles 无人处理 |
| 原型代码 | `code/nucleus-4.0/` | 🗑️ 废弃 | 错误领域（FMEA 汽车故障），与治理系统无关 |

---

## 二、发现的问题（按优先级）

### P0 — 系统无法正常运行

#### BUG-001 `check.py` stub 导致 review_level 恒为 L2

**位置**：`modules/check.py:305`

```python
# 修复前（stub）
def _get_review_level_from_task_card(task_card_id: str) -> str:
    return 'L2'  # 永远返回 L2，根本没有解析 task-card
```

**影响**：所有 Check 阶段都按 L2 处理。L3 任务不会触发 Harold 审批；L0 任务不会免审。

---

#### BUG-002 `check.py` L2 用随机数模拟"银月抽样"

**位置**：`modules/check.py:158`

```python
# 修复前（语义错误）
import random
if random.random() < 0.8:
    result['verdict'] = 'pass'
else:
    result['verdict'] = 'partial'
```

**影响**：L2 的语义是"银月人工抽样 20-30% 审核"，Python 用随机数模拟是错误的。该决策属于 LLM 职责，不应在 Python 中实现。

---

#### BUG-003 `act.py` 硬编码 agent_dir 路径

**位置**：`modules/act.py:227`

```python
# 修复前（硬编码）
agent_dir = os.path.expanduser("~/Workspaces/openclaw/main/60_Agents/cqo")
```

**影响**：state_sync 只能用于 cqo agent，其他 agent 调用时写入错误目录，导致 MISSION_BOARD 更新错误。

---

#### BUG-004 `monitor.py` `_find_child_cycles` 忽略 parent_id 参数

**位置**：`modules/monitor.py:319`

```python
# 修复前（参数被忽略）
def _find_child_cycles(parent_id: str) -> List[Dict]:
    child_files = glob.glob("cycles/task/*.yaml")  # parent_id 从未被用到
    for file_path in child_files:
        cycle_data = yaml.safe_load(f)
        if cycle_data and cycle_data.get('id'):
            child_cycles.append(cycle_data)  # 全量返回，无过滤
```

**影响**：`aggregate_child_results()` 返回所有 task cycles 的聚合，而非指定父环的子环。父环的 Check 阶段证据收集完全错误。

---

#### BUG-005 `state_sync.py` hardcoded topic ID 映射

**位置**：`modules/state_sync.py:248`

```python
# 修复前（ZT-P015 专属，不通用）
if task_id.startswith('T1.'):
    return 'N4-P1-T01'
elif task_id.startswith('T2.'):
    return 'N4-P1-T02'
...
```

**影响**：仅适用于 ZT-P015_NUCLEUS-4-0 项目的任务 ID 格式，任何其他项目的 task 调用 state_sync 都会找不到 topic，TOPIC-BRIEF 更新失效。

---

### P1 — 核心功能缺失

#### GAP-001 SKILL.md 缺少 LLM 执行协议（最关键）

**位置**：`SKILL.md` 整体

`nucleus_scheduler.py` 在 heartbeat 触发后创建 CycleUnit YAML，并返回：
```json
{"created_cycles": ["task/task-20260411T034357Z"], "triggered_scopes": ["task"]}
```

但 SKILL.md（v1.3.0）只有架构说明和文件结构，**没有任何指令告诉 LLM 收到 `created_cycles` 后应该做什么**。

这是 `task-20260411T034357Z.yaml` 中 `actions_executed: 0`、`children_created: 0` 的根本原因：调度器创建了 YAML shell，但没有后续的 LLM 处理协议，整个 PDCA 循环在 Plan 阶段就停止了。

---

### P2 — 架构错误（待清理）

#### ARCH-001 `code/nucleus-4.0/` 为废弃原型，使用错误领域模型

**位置**：`10_Projects/ZT-P015_NUCLEUS-4-0/code/nucleus-4.0/`

| 文件 | 问题 |
|------|------|
| `interfaces/decide.py` | `ActionType.emergency` / `auto` / `monitor`，FMEA 故障分析领域 |
| `models/event.py` | `AnomalyEvent: severity×occurrence×detection_difficulty`，汽车故障模式分析 |
| `models/rpn.py` | `RPN`（Risk Priority Number），完全属于 FMEA 方法论 |
| `interfaces/event_bus.py` | 内存 pub/sub，与 `isolatedSession:true` 根本不兼容 |

这套代码和实际 skill 实现（`skills/.../openclaw-governance-nucleus/`）完全独立，不被任何生产代码引用。

---

## 三、修复方案

### 3.1 架构原则（修复的基础）

```
Python 负责（确定性操作）:
  - 文件 I/O：读写 YAML、Markdown
  - 计数器：scheduler 触发阈值判断
  - 规则计算：adjust_automation_level() 的升降级逻辑
  - 文本解析：parse_review_level_from_task_card() 正则匹配

LLM 负责（智能判断）:
  - Do 阶段：实际推进任务、检查进度
  - Check 阶段：对照 acceptance_criteria 给出 verdict（L0/L1）
  - L2：判断抽样范围，银月主动审核
  - L3：确认 Harold 审批结果
```

### 3.2 BUG-001 修复方案

```python
# 修复后：复用 plan.py 的解析器
def _get_review_level_from_task_card(task_card_id: str) -> str:
    from plan import parse_review_level_from_task_card
    if task_card_id and os.path.exists(task_card_id):
        with open(task_card_id, 'r', encoding='utf-8') as f:
            return parse_review_level_from_task_card(f.read())
    return 'L3'  # 回退到最安全级别
```

### 3.3 BUG-002 修复方案

```python
# 修复后：L2 返回 pending_sampling，交由 LLM 处理
elif review_level == 'L2':
    evidence = collect_evidence(cycle_id)
    result['evidence'] = evidence
    result['verdict'] = 'pending_sampling'  # LLM 协议处理
```

### 3.4 BUG-003 修复方案

```python
# 修复后：agent_dir 作为可选参数，未提供时跳过 state_sync
def apply_adjustments(
    cycle_path: str,
    adjustments: List[Dict[str, Any]],
    agent_dir: Optional[str] = None,
    project_dir: Optional[str] = None
) -> bool:
    ...
    if agent_dir is None:
        cycle_data['act']['state_sync_skipped'] = 'agent_dir not provided'
        return True
```

### 3.5 BUG-004 修复方案

```python
# 修复后：按 parent_cycle_id 字段过滤
def _find_child_cycles(parent_id: str) -> List[Dict]:
    for scope in ['task', 'topic', 'project', 'system']:
        for file_path in glob.glob(f"cycles/{scope}/*.yaml"):
            cycle_data = yaml.safe_load(open(file_path))
            if cycle_data.get('parent_cycle_id') == parent_id:
                child_cycles.append(cycle_data)
```

### 3.6 BUG-005 修复方案

```python
# 修复后：优先从 CycleUnit metadata 读取，其次用通用正则
def extract_topic_id(task_id: str) -> Optional[str]:
    # 通用规则：T{n}.{m} → T0{n}
    m = re.match(r'^T(\d+)\.\d+$', task_id)
    if m:
        return f"T{m.group(1).zfill(2)}"
    # ZT-PXXX-T{n}-{seq} 格式
    m = re.match(r'^(ZT-P\d+)-T(\d+)-', task_id)
    if m:
        return f"{m.group(1)}-T{m.group(2).zfill(2)}"
    return None
```

调用方注入优先：
```python
topic_id = cycle_unit.get('metadata', {}).get('topic_id') or extract_topic_id(task_id)
```

### 3.7 GAP-001 修复方案：补充 SKILL.md §四 LLM 执行协议

核心内容：

```
当 nucleus_scheduler.py 返回 created_cycles 时：

for each cycle_id in created_cycles:
  Step 1: 读取 CycleUnit YAML 和对应 Task-CARD
  Step 2 (Plan): 调用 plan.determine_review() 获取 review_level
  Step 3 (Do): LLM 推进任务，更新 MISSION_BOARD
  Step 4 (Check):
    L0 → skip
    L1 → LLM 自查 acceptance_criteria
    L2 → pending_sampling，MISSION_BOARD 标注，等待银月
    L3 → 触发飞书通知，写 pending，等待 Harold
  Step 5 (Act):
    pending/pending_sampling → 跳过，下次 heartbeat §4.4 轮询
    pass/fail/partial/skip → 计算 adjustments，触发 state_sync
```

---

## 四、修复计划

### 4.1 P0 修复（已完成）

| 任务 | 文件 | 状态 | 完成时间 |
|------|------|------|----------|
| BUG-001 修复 check.py stub | `modules/check.py` | ✅ 已完成 | 2026-04-16 |
| BUG-002 移除 random 采样 | `modules/check.py` | ✅ 已完成 | 2026-04-16 |
| BUG-003 去除 act.py 硬编码 | `modules/act.py` | ✅ 已完成 | 2026-04-16 |
| BUG-004 修复 monitor.py 过滤 | `modules/monitor.py` | ✅ 已完成 | 2026-04-16 |
| BUG-005 state_sync 通用化 | `modules/state_sync.py` | ✅ 已完成 | 2026-04-16 |

### 4.2 P1 修复（已完成）

| 任务 | 文件 | 状态 | 完成时间 |
|------|------|------|----------|
| GAP-001 补充 LLM 执行协议 | `SKILL.md §四` | ✅ 已完成 | 2026-04-16 |

### 4.3 P2 待完成

| 任务 | 文件 | 优先级 | 说明 |
|------|------|--------|------|
| 归档废弃原型代码 | `code/nucleus-4.0/interfaces/`、`models/` | P2 | 移至 `docs/archive/`，避免混淆 |
| `send_feishu_notification()` 真实实现 | `modules/check.py` | P2 | 当前是 print stub，需接入 governance-alert |
| `check-pending` 子命令 | `scripts/nucleus_scheduler.py` | P2 | §4.4 轮询协议需要此入口 |
| `do.py` `execute_actions()` 真实实现 | `modules/do.py` | P2 | 当前是 stub，Do 阶段实际执行由 LLM 协议驱动 |
| CycleUnit schema 增加 `parent_cycle_id` | `cycles/cycle_unit.schema.yaml` | P2 | BUG-004 修复依赖此字段，需确认 schema 已包含 |

### 4.4 后续建议

1. **端到端集成测试**：从 heartbeat 触发 → `nucleus_scheduler.py` → LLM 读取 SKILL.md §四协议 → 写入 cycle verdict，跑一遍完整路径
2. **`do.py` 与 LLM 的边界再梳理**：`execute_cycle()` 目前仍是 Python 实现，但 Do 阶段的核心工作是 LLM 推进任务，建议将 `do.py` 简化为纯写入工具（不再试图"执行 actions"）
3. **parent_cycle_id 字段补全**：创建子环时由 `scheduler.py` 写入 `parent_cycle_id`，确保 BUG-004 修复生效

---

## 五、变更记录

### 2026-04-16

#### `modules/check.py`

**变更 1**：`_get_review_level_from_task_card()` stub → 真实解析

```diff
 def _get_review_level_from_task_card(task_card_id: str) -> str:
-    # 简化实现：返回 L2
-    return 'L2'
+    from plan import parse_review_level_from_task_card
+    if task_card_id and os.path.exists(task_card_id):
+        with open(task_card_id, 'r', encoding='utf-8') as f:
+            return parse_review_level_from_task_card(f.read())
+    return 'L3'
```

**变更 2**：L2 随机数采样 → `pending_sampling`

```diff
 elif review_level == 'L2':
-    import random
-    if random.random() < 0.8:
-        result['verdict'] = 'pass'
-    else:
-        result['verdict'] = 'partial'
+    evidence = collect_evidence(cycle_id)
+    result['evidence'] = evidence
+    result['verdict'] = 'pending_sampling'
```

**变更 3**：`check_cycle()` 返回值 docstring 更新

```diff
-    'verdict': 'pass|partial|fail|skip',
+    'verdict': 'pass|partial|fail|skip|pending|pending_sampling',
+    Note:
+        L2 返回 pending_sampling，由 LLM（银月）在 SKILL.md 协议中决定最终 verdict
+        L3 返回 pending，等待 Harold 飞书审批后回写 verdict
```

#### `modules/act.py`

**变更 4**：`apply_adjustments()` 增加 `agent_dir` / `project_dir` 参数

```diff
-def apply_adjustments(cycle_path: str, adjustments: List[Dict[str, Any]]) -> bool:
+def apply_adjustments(
+    cycle_path: str,
+    adjustments: List[Dict[str, Any]],
+    agent_dir: Optional[str] = None,
+    project_dir: Optional[str] = None
+) -> bool:
```

**变更 5**：移除硬编码 `agent_dir`，改为参数传入 + 跳过保护

```diff
-    agent_dir = os.path.expanduser("~/Workspaces/openclaw/main/60_Agents/cqo")
-    sync_result = on_act_complete(cycle_data, project_dir, agent_dir)
+    if agent_dir is None:
+        cycle_data['act']['state_sync_skipped'] = 'agent_dir not provided'
+        # 写回后正常返回，不影响主流程
+        return True
+    sync_result = on_act_complete(cycle_data, project_dir, agent_dir)
```

#### `modules/monitor.py`

**变更 6**：`_find_child_cycles()` 实现 parent_id 过滤

```diff
 def _find_child_cycles(parent_id: str) -> List[Dict]:
-    child_files = glob.glob("cycles/task/*.yaml")
-    for file_path in child_files:
-        if cycle_data and cycle_data.get('id'):
-            child_cycles.append(cycle_data)
+    for scope in ['task', 'topic', 'project', 'system']:
+        child_files.extend(glob.glob(f"cycles/{scope}/*.yaml"))
+    for file_path in child_files:
+        if cycle_data.get('parent_cycle_id') == parent_id:
+            child_cycles.append(cycle_data)
```

#### `modules/state_sync.py`

**变更 7**：`on_act_complete()` 优先读 `CycleUnit.metadata.topic_id`

```diff
-    topic_id = extract_topic_id(task_id)
+    topic_id = cycle_unit.get('metadata', {}).get('topic_id') or extract_topic_id(task_id)
```

**变更 8**：`extract_topic_id()` 替换为通用正则，去除 ZT-P015 硬编码

```diff
-    if task_id.startswith('T0.'):
-        return 'N4-P0-T01'
-    elif task_id.startswith('T1.'):
-        return 'N4-P1-T01'
-    ...（7 条硬编码）
+    m = re.match(r'^T(\d+)\.\d+$', task_id)
+    if m:
+        return f"T{m.group(1).zfill(2)}"
+    m = re.match(r'^(ZT-P\d+)-T(\d+)-', task_id)
+    if m:
+        return f"{m.group(1)}-T{m.group(2).zfill(2)}"
+    return None
```

#### `SKILL.md`

**变更 9**：新增 §四 LLM 执行协议（原 §四～§六 顺延为 §五～§七）

新增内容覆盖：
- §4.1 触发后处理流程（scheduler 输出 → 单环处理入口）
- §4.2 单环 PDCA 协议（Step 1～5，含各 review_level 分支）
- §4.3 特殊情况处理（task_card 缺失、阻塞、pending 等）
- §4.4 pending 状态跨 heartbeat 轮询机制

---

*生成时间：2026-04-16 | 审查会话：银月*
