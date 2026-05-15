# NUCLEUS 详细设计文档

> **文档编号**: NUCLEUS-DESIGN-v2.0
> **创建日期**: 2026-04-16
> **修订日期**: 2026-04-18
> **上位引用**: NUCLEUS-ARCH-v2.0 · pdca.py (scripts/pdca.py)
> **评审状态**: 待 Harold 评审

---

## 一、pdca.py 函数级设计

### 1.1 p() — Plan 阶段记录

```python
def p(task_card_id, summary, acceptance_criteria=None, task_card_path=None, dl_refs=None) -> Dict
```

**职责**：记录 LLM 的 Plan 意图。

**新建 cycle 条件**（三选一）：
1. 首次调用（无历史 cycle）
2. 上一 cycle 已 completed
3. 上一 cycle 卡在 check/pending（LLM 放弃等待，重新规划）

**复用 cycle 条件**：
- 上一 cycle 处于 plan/do/act（正常迭代中途恢复）

**参数**：
- `summary`：本轮目标 + 相比上次的调整（Harness 规则 P1）
- `acceptance_criteria`：验收标准列表
- `dl_refs`：本轮 Plan 引用的 DL 条目列表（审计溯源用）

**输出**：`{ok: true, cycle_index: N, phase: 'plan'}`

### 1.2 d() — Do 阶段记录

```python
def d(task_card_id, summary, status, blocker=None) -> Dict
```

**职责**：记录 LLM 的实际执行结果。

**status 枚举**：
- `completed`：Do 阶段全部完成
- `blocked`：因外部依赖阻塞（必须填写 blocker）
- `partial`：部分完成

**参数**：
- `summary`：必须描述实际变化（Harness 规则 D1）

**输出**：`{ok: true, cycle_index: N, phase: 'do', status: '...'}`

### 1.3 c() — Check 阶段记录

```python
def c(task_card_id, verdict, review_level='L1', evidence=None) -> Dict
```

**职责**：记录验收结论。

**ADAS 规则校验**（自动执行）：
1. `L0/L1 + pending` → 拒绝（自验收无需人工介入）
2. `L3 首次 + 非 pending` → 拒绝（必须等待 Harold）

**verdict 与 phase 推进**：
- `pass/partial/fail/skip` → phase 自动推进到 act
- `pending` → phase 保持 check（等待审批）

**audit_eligible 标记**：
- `verdict=pass AND review_level in {L0, L1}` → `audit_eligible=true`
- 其他情况 → `audit_eligible=false`

**输出**：`{ok: true, cycle_index: N, phase: 'act'|'check', verdict: '...', needs_act: bool}`

### 1.4 a() — Act 阶段记录

```python
def a(task_card_id, summary, next_task=None, lessons=None) -> Dict
```

**职责**：记录本轮 PDCA 的行动决策。

**参数**：
- `summary`：必须包含「下次 Plan 的输入」（Harness 规则 A1）
- `next_task`：指向下一个任务或同一任务（重试时）
- `lessons`：经验教训列表

**输出**：`{ok: true, cycle_index: N, phase: 'completed', next_task: '...'}`

### 1.5 get_status() — 状态查询

```python
def get_status(task_card_id) -> Dict
```

**返回字段**：
- `cycles_total`：总循环数
- `current_phase`：当前阶段（None 表示无记录）
- `current_verdict`：最近一次 Check 的 verdict
- `last_p_summary` / `last_d_status`：最近 P/D 摘要

### 1.6 get_pending() — 待审批列表

```python
def get_pending() -> List[Dict]
```

**扫描逻辑**：遍历 `pdca/*.yaml`，筛选 `phase='check' AND verdict='pending'`。

**返回字段**：
- `days_waiting`：等待天数
- `is_overdue`：>7 天为 true
- `p_summary` / `review_level` / `cycle_index`

### 1.7 get_audit_queue() — 审计队列

```python
def get_audit_queue() -> List[Dict]
```

**筛选逻辑**：`audit_eligible=true AND audit_result=null`。

**返回字段**：
- `dl_refs`：Plan 阶段引用的 DL 条目（审计溯源）
- `p_summary` / `d_summary` / `evidence`
- `task_card_id` / `cycle_index` / `review_level`

### 1.8 mark_audit() — 审计记录

```python
def mark_audit(task_card_id, cycle_index, score, issues=None) -> Dict
```

**校验**：
- `cycle_index` 不存在 → `{ok: false, error: '...'}`
- `c` 段未记录 → `{ok: false, error: '...'}`
- 非 `audit_eligible` → `{ok: false, error: '...'}`

**评分逻辑**：
- `score >= 80` → `has_problem=false`，记录通过
- `score < 80` → `has_problem=true`，`next_action` 提示质疑 DL + popup

**输出**：`{ok: true, score, has_problem, dl_refs, next_action}`

### 1.9 aggregate() — 轻量级层间传播（Phase 2 新增）

```python
def aggregate(scope, scope_id) -> Dict
```

**职责**：扫描子项 pdca/*.yaml，聚合 verdict 到父级。

**参数**：
- `scope`：'topic' | 'project'
- `scope_id`：父级 ID（如 'T06' / 'ZT-P015'）

**扫描逻辑**：
- scope='topic'：扫描 pdca/ 下所有 task 级 yaml（task_card_id 以 scope_id 为前缀）
- scope='project'：扫描 pdca/ 下所有 topic 级 yaml

**聚合规则**：

| 子项组合 | 父项 verdict |
|---------|-------------|
| 全部 pass | pass |
| 任一 fail | fail |
| 部分 pass + 部分 partial | partial |
| 全部 skip | skip |
| 混合 | partial |

**触发**：a() 完成后自动调用（task 级 a() → 聚合到 topic）。

**存储**：父级也有 pdca/*.yaml，但不由 LLM 填写，由 aggregate() 自动派生。

**输出**：`{ok: true, scope, scope_id, verdict, children_count, child_verdicts}`

### 1.10 check_concurrency() — 并发上限校验（Phase 2 新增）

```python
def check_concurrency(scope) -> Dict
```

**职责**：p() 前置校验，防止超出并发上限。

**参数**：
- `scope`：'task' | 'topic' | 'project'

**校验逻辑**：扫描 pdca/*.yaml，统计各 scope 下 phase != completed 的数量。

**并发上限**：

| Scope | 上限 | 说明 |
|-------|------|------|
| task | 10 | 单 topic 下活跃 task 数 |
| topic | 5 | 单 project 下活跃 topic 数 |
| project | 3 | 全局活跃 project 数 |

**超限返回**：`{ok: false, error: '{scope} 并发上限 {N}，当前活跃 {M}，请等待完成'}`

**正常返回**：`{ok: true, scope, active_count, limit}`

---

## 二、scheduler_state.py 设计（Phase 2 新增）

### 2.1 职责

持久化调度计数器，实现多粒度调度（task/topic/project/system 不同频率）。

### 2.2 存储格式

```yaml
# config/scheduler_state.yaml
last_updated: "2026-04-18T09:00:00Z"
counters:
  task: 0       # 每 1 heartbeat 触发（30min）
  topic: 0      # 每 4 heartbeat 触发（2h）
  project: 0    # 每 48 heartbeat 触发（1d）
  system: 0     # 每 336 heartbeat 触发（1w）
thresholds:
  task: 1
  topic: 4
  project: 48
  system: 336
```

### 2.3 函数设计

```python
def load_scheduler_state() -> Dict
def tick_and_check(scope) -> bool  # 计数器+1，返回是否达到阈值
def reset_counter(scope) -> None
def save_scheduler_state() -> None  # 原子写入
```

### 2.4 心跳集成

```
heartbeat 触发:
  for scope in [task, topic, project, system]:
    if tick_and_check(scope):
      process_scope(scope)
      reset_counter(scope)
  save_scheduler_state()
```

---

## 三、YAML 存储格式规范

### 3.1 完整 Schema

```yaml
task_card_id: string           # 必填，唯一标识
task_card_path: string | null  # 首次 p() 时写入
cycles:                        # PDCA 循环历史
  - cycle_index: integer       # 从 1 递增
    started_at: ISO8601        # cycle 创建时间
    completed_at: ISO8601 | null  # a() 完成后写入
    phase: enum[plan, do, check, act, completed]
    p:                         # Plan 段
      timestamp: ISO8601
      summary: string          # 必须说明本轮目标和调整
      acceptance_criteria: [string]
      dl_refs: [string]        # 引用的 DL 条目
    d:                         # Do 段
      timestamp: ISO8601
      summary: string          # 必须描述实际变化
      status: enum[completed, blocked, partial]
      blocker: string | null
    c:                         # Check 段
      timestamp: ISO8601
      verdict: enum[pass, partial, fail, skip, pending]
      review_level: enum[L0, L1, L2, L3]
      evidence: [string]       # 验收证据
      audit_eligible: boolean  # L0/L1 pass 自动设置
      audit_result:            # 外部审计结果（mark_audit 写入）
        timestamp: ISO8601 | null
        score: integer | null
        issues: [string] | null
        has_problem: boolean | null
    a:                         # Act 段
      timestamp: ISO8601 | null
      summary: string | null
      next_task: string | null
      lessons: [string] | null
```

### 3.2 原子写入保证

```
写操作路径:
1. 读取现有 YAML → 内存修改
2. 写入 {path}.tmp
3. os.replace(tmp, path)  ← 原子替换
```

### 3.3 文件命名

- 目录：`pdca/`（相对于 skill 根目录）
- 文件名：`{task_card_id}.yaml`（task 级）/ `{scope_id}.yaml`（topic/project 级）
- 示例：`pdca/T1.1.yaml` / `pdca/T06.yaml` / `pdca/ZT-P015.yaml`

---

## 四、PDCA Harness 规则

### 4.1 规则总览

| 规则 ID | 阶段 | 规则内容 |
|---------|------|---------|
| **P1** | Plan | Plan summary 必须说明「本轮相比上次做了什么不同」；第一轮说明初始目标和方法 |
| **D1** | Do | Do summary 必须描述实际变化，不能是"检查了一下"之类的虚操作 |
| **C1** | Check | verdict=fail 时 evidence 必须说明「哪条验收标准失败、失败的具体表现」 |
| **C2** | Check | L3 pending 超时 >7 天，heartbeat Step 0 必须升级 MISSION_BOARD [!] |
| **A1** | Act | Act summary 必须包含「下次 Plan 的输入」；失败时必须有根因分析 |

### 4.2 收敛机制

| 条件 | 行为 |
|------|------|
| 同一任务连续 3 次 verdict=fail | Act 上报 MISSION_BOARD「需要 Harold 介入：{具体卡点}」 |
| 连续 verdict=partial 但有进展 | 正常，继续迭代 |
| 连续 2 次 Do 阶段内容完全相同 | 不允许（status=blocked 除外） |

---

## 五、ADAS 分级规则表

### 5.1 各级别行为约束

| 级别 | Reviewer | 首次 Check | verdict 允许值 | audit_eligible | 备注 |
|------|----------|-----------|---------------|----------------|------|
| **L0** | 无需 | 自动 pass | pass/fail/skip/partial | pass → true | 免审 |
| **L1** | LLM 自身 | 自查通过 | pass/fail/skip/partial | pass → true | 自验收 |
| **L2** | 银月 | 抽样决定 | pass/pending | pass → false（非自验收） | 抽检 20-30% |
| **L3** | Harold | 必须 pending | pending → pass/fail/skip/partial | false | 全量人工审批 |

### 5.2 ADAS 规则校验矩阵

| 输入组合 | 校验结果 | 错误信息 |
|---------|---------|---------|
| L0 + pending | 拒绝 | "L0/L1 为自验收级别，不允许 verdict=pending" |
| L1 + pending | 拒绝 | "L0/L1 为自验收级别，不允许 verdict=pending" |
| L3 首次 + 非 pending | 拒绝 | "L3 首次 Check 必须 verdict=pending" |
| L3 第二次 + 任意 | 通过 | Harold 回复后记录最终结论 |
| 任意 + invalid verdict | 拒绝 | "invalid verdict: '{verdict}'" |
| 任意 + invalid level | 拒绝 | "invalid level: '{level}'" |

---

## 六、Human-in-the-Loop 协议

### 6.1 L3 Review 请求格式

```
【交付物审批】{task-card-id}
━━━━━━━━━━━━━━━━━━━━━━━━

📋 交付物: {name}
📊 验收标准:
  - {标准1}: {状态}
  - {标准2}: {状态}

📝 执行摘要:
{LLM 总结}

━━━━━━━━━━━━━━━━━━━━━━━━
请回复:
  A - 批准（全部通过）
  B - 有条件批准（附带修改意见）
  C - 拒绝（不满足验收标准）
  D - 需要更多信息
```

### 6.2 A/B/C/D 解析表

| 回复 | 映射 verdict | 后续动作 |
|------|-------------|---------|
| **A** | pass | pdca.py c(verdict=pass) → Act → completed |
| **B** | partial | pdca.py c(verdict=partial) → Act → 记录有条件通过的要求 |
| **C** | fail | pdca.py c(verdict=fail) → Act → 记录失败根因 |
| **D** | partial | pdca.py c(verdict=partial) → Act → 补充信息后重试 |

### 6.3 超时处理

| 等待时长 | 行为 |
|---------|------|
| ≤7 天 | 正常等待，heartbeat 记录状态 |
| >7 天 | MISSION_BOARD 对应条目升级为 [!]，feishu_post 重新通知（标注"已逾期 {days} 天"） |
| >14 天 | 上报 Harold 队列，建议人工介入 |

---

## 七、审计出口设计

### 7.1 audit_eligible 标记规则

```python
audit_eligible = (verdict == 'pass' and review_level in {'L0', 'L1'})
```

| Check 结果 | audit_eligible |
|-----------|---------------|
| L0 + pass | true |
| L1 + pass | true |
| L1 + fail | false |
| L2 + pass | false（非自验收，银月已在 L2 做了抽检） |
| L3 + pass | false（Harold 已审批，无需再审计） |

### 7.2 get_audit_queue 扫描逻辑

```
遍历 pdca/*.yaml:
  for each cycle in record['cycles']:
    if cycle['c']['audit_eligible'] and cycle['c']['audit_result'] is None:
      加入队列
```

### 7.3 mark_audit 评分阈值

| 分数 | has_problem | 后续动作 |
|------|-------------|---------|
| >= 80 | false | 记录通过，无需额外操作 |
| < 80 | true | governance-knowledge.create_lesson_learned() 质疑 dl_refs 中的 DL |

---

## 八、两条触发路径

### 8.1 Path A — 直接入口（同会话）

```
dispatch 路由
  → task.create_task()
  → task.accept_task()（状态 [P]）
  → LLM 直接执行完整 PDCA（p→d→c→a）
  → 更新 MISSION_BOARD
```

**适用场景**：紧急/高优先级任务，Harold 明确要求立即执行。

### 8.2 Path B — heartbeat 入口（定时触发）

```
heartbeat cron (每 30 分钟)
  → Step 0: pdca.py pending（检查 L3 等待中审批）
  → Step 1: 选 [P] 状态最高优先级任务
  → Step 2: pdca.py status（读取历史 PDCA 状态）
  → Step 3-6: 完整 PDCA（p→d→c→a）
  → 更新 MISSION_BOARD
```

**适用场景**：常规任务、后台推进、跨会话任务。

### 8.3 等价性保证

两条路径产生的 PDCA 历史记录完全等价——都通过相同的 pdca.py 函数写入相同的 YAML 格式。差异仅在于触发时机和执行上下文。

---

## 九、错误处理

### 9.1 参数校验错误

| 错误场景 | 返回 |
|---------|------|
| status 不在 {completed, blocked, partial} | `{ok: false, error: 'invalid status: ...'}` |
| verdict 不在 {pass, partial, fail, skip, pending} | `{ok: false, error: 'invalid verdict: ...'}` |
| level 不在 {L0, L1, L2, L3} | `{ok: false, error: 'invalid level: ...'}` |
| ADAS 规则校验失败 | `{ok: false, error: '...'}` |

### 9.2 审计错误

| 错误场景 | 返回 |
|---------|------|
| cycle_index 不存在 | `{ok: false, error: 'cycle_index=N 不存在'}` |
| Check 阶段未记录 | `{ok: false, error: 'Check 阶段尚未记录'}` |
| 非 audit_eligible 状态 | `{ok: false, error: '该 cycle 不是 audit_eligible 状态'}` |

### 9.3 文件 I/O 错误

- `yaml.safe_load` 失败：Python 会抛出异常，由调用方处理
- 临时文件写入失败：不会触发 `os.replace`，原文件保持不变

---

## 十、测试用例设计

### 10.1 Simulation 测试（7 场景）

| 场景 | 覆盖内容 | 状态 |
|------|---------|------|
| S1 | L1 自验收完整循环（P→D→C→A） | ✅ |
| S2 | L3 HitL 完整循环（P→D→C(pending)→回复→C→A） | ✅ |
| S3 | fail → 新 cycle → pass（持续收敛） | ✅ |
| S4 | p() 放弃 pending 重新规划 | ✅ |
| S5 | 超时检测（days_waiting + is_overdue） | ✅ |
| S6 | ADAS 规则守卫 | ✅ |
| S7 | status/pending CLI 输出格式 | ✅ |

### 10.2 Audit & Routing 测试（17 场景）

| 场景 | 覆盖内容 | 状态 |
|------|---------|------|
| A1 | audit_eligible 标记规则（5 种组合） | ✅ |
| A2 | get_audit_queue() 只返回未审计的 eligible 条目 | ✅ |
| A3 | mark_audit() 评分 >= 80（通过） | ✅ |
| A4 | mark_audit() 评分 < 80（有问题） | ✅ |
| A5 | mark_audit() 同一条目不可重复审计 | ✅ |
| A6 | mark_audit() 错误参数（cycle_index 不存在 / 非 eligible） | ✅ |
| A7 | dl_refs 在 audit_queue 中可追溯 | ✅ |
| G1 | Step 1 任务过滤规则（cycles_total=0 新任务） | ✅ |
| G2 | Path A vs Path B 产生等价 PDCA 历史 | ✅ |
| CLI | audit-queue / mark-audit CLI 命令输出格式 | ✅ |

---

*版本：v2.0 | 创建日期：2026-04-16 | 修订日期：2026-04-18 | 作者：张铁 (CQO) + 银月*
