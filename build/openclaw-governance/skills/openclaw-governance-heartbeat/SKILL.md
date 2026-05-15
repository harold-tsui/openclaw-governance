---
name: pdca-executor
description: |
  PDCA execution entry point — every heartbeat drives one Task-CARD through a full PDCA cycle.
  Also handles human-driven task execution in session (same PDCA rules apply).

  Activates when: Heartbeat trigger, periodic check, or human directly asks to work on a task

  Capabilities:
  - PDCA cycle execution for Task-CARDs (Plan → Do → Check → Act)
  - Task selection with priority ordering
  - Human review gate management (Plan review, Check review)
  - Review level routing (L0-L3) with LLM escalation
  - MISSION_BOARD derived metrics refresh
  - Morning/evening reporting (byproduct, not purpose)
  - Cross-agent coordination
  - Breakpoint resume (pdca_current_phase in Task-CARD Zone B)
  - Experience feedback via governance-knowledge (create_lesson_learned + enhance_knowledge)
  - Next-task recommendation on Act completion
  - Feishu step-level execution logging

  Keywords: heartbeat, pdca, execution, task-progress, mission-board, review, closed-loop, learning

  For detailed documentation, see:
  - references/heartbeat-details.md

author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "9.0.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L2"
  os: ["darwin", "linux"]
  tags: ["heartbeat", "pdca", "execution", "mission-board", "task-progress", "closed-loop", "learning"]
  dependencies:
    - openclaw-governance-core
    - openclaw-governance-task
    - openclaw-governance-nucleus  # pdca.py state recording
---

# HEARTBEAT - PDCA 闭环执行器

Tags: #governance, #heartbeat, #pdca, #execution, #task-progress, #closed-loop

> **定位**：PDCA 闭环执行入口，每次 heartbeat 推进一个 Task-CARD 完成一轮 PDCA，并通过 Learn 步骤实现闭环
> **v9.0.0**: PDCA 执行模型强约束重构 — 7 段式 checklist（必读/必做/必调/必写/必发/必验/闸门），Do 逐步骤追踪，Check 逐交付物验收，Act 严格顺序副作用

## 何时使用

- **Heartbeat trigger**: OpenClaw Gateway 定时触发 → 选一个 Task-CARD → 执行 PDCA
- **Human-driven task**: Harold 在会话中直接要求推进某任务 → 同一 PDCA 流程
- **PDCA execution**: 任何需要 Plan→Do→Check→Act 推进的任务
- **Do NOT use for**: 纯状态查询（直接读 MISSION_BOARD 即可）

## 常见陷阱

1. **Heartbeat 不是巡检**: 每次 heartbeat 必须推进至少一个 Task-CARD 的 PDCA，除非所有 Task 都在等人类 Review。没有"无变化"的 heartbeat。
2. **MISSION_BOARD 是派生视图**: §一 状态总览的数字从 §二/§三/§五/§六 计数得出，不是手写。Act 步骤自动刷新。
3. **PDCA 不可跳步**: Plan→Do→CQO Review→Check→Act 必须顺序执行。不能只 Do 不 Check，不能只 Check 不 Act。断点续传不算跳步（见 §3.6）。
4. **Review 阻塞是唯一停顿**: PDCA 自动推进，唯一的断点是"需要人类决策"。人类介入时机取决于 Review 级别和 LLM 判断。
5. **人类驱动 = 同一规则**: Harold 在会话中主动推进任务，和 heartbeat 自动推进，走的是同一个 PDCA 流程。

---

## 一、核心理念

### 1.0 闭环增强：断点续传 + 经验回流

我们的多级 PDCA 环已是闭环：Task PDCA → aggregate() → Topic verdict → Project verdict，bubble_up() 层间传播。v8.0 不是外挂新步骤，而是丰富已有闭环的两个薄弱点：

**薄弱点 1 — 断点续传**：heartbeat 可能中途中断（超时、token 耗尽），当前逻辑假设每次 heartbeat 走完一整轮 PDCA，但断点后下次 Plan 无法识别"上次断在哪一步"。

**薄弱点 2 — 经验回流**：aggregate() 只传播 verdict（pass/fail/partial），不传播经验。Task A 走完后，同类 Task B 并没有因此更高效。已有 `governance-knowledge` Skill 处理 lessons learned，但 Act 步骤没有调用它。

v8.0 增强：
1. **断点续传**：Task-CARD Zone B 记录当前 PDCA phase，下次 heartbeat 从断点继续而非重新开始
2. **经验回流**：Act(verdict=pass) 时触发 `governance-knowledge` 的 `create_lesson_learned()` + `enhance_knowledge()` 在下次 Plan 时检索历史经验
3. **完成即推荐**：Act 完成后主动推荐下一个 Task，保持推进惯性

### 1.1 两种入口，同一流程

| 入口 | 触发方式 | 场景 | 区别 |
|------|---------|------|------|
| **系统触发** | OpenClaw Gateway heartbeat | 定时自动推进 | Agent 自主选 Task |
| **人类驱动** | Harold 在会话中直接推进 | 人工指定 Task | Harold 指定 Task |

**核心原则**：无论哪种入口，Task-CARD 都必须跑完一轮完整 PDCA。不存在"跳过 Check 直接交付"。

### 1.2 PDCA 执行模型

> **v9.0 核心变化**：每个 PDCA 步骤采用 7 段式 checklist（必读输入→必做动作→必调命令→必写更新→必发日志→必验结果→闸门条件），LLM 必须机械执行，不可跳步。步骤之间的闸门条件不通过则不可进入下一步骤。

```
Heartbeat 触发 或 Harold 直接推进
    ↓
选取 Task-CARD（优先级排序）
    ↓
断点检查：读取 Task-CARD Zone B §7.1 的 pdca_current_phase ────┐
    │                                                             │
    ├─ 无断点（新Task/新一轮）→ 进入 Plan                          │
    └─ 有断点（上次中断）→ 从断点 phase 继续（§3.6 断点续传）──────┘
    ↓
Plan  ─ 必读: Zone B §7.1 + Zone A §2/§3/§4/§5/§6
    │    必做: 确认目标 + 确认输入就绪 + 确认交付物清单 + 确认执行步骤
    │    必调: pdca.py p --task-card-id ... --criteria "{§4验收标准}"
    │    必发: P: {目标重述}; {N} steps, {M} deliverables [done]
    ↓  ╳ 闸门: §4有交付物 AND §5有步骤 AND §3输入物全部就绪 AND pdca.py ok:true
Do    ─ 必读: Zone A §5(执行步骤) + §4(交付物) + §3(输入物)
    │    必做: 按§5逐步执行，每步 ⬜→🟡→✅；完成后 ls 校验§4交付物文件存在
    │    必调: pdca.py d --task-card-id ... --status completed|blocked|partial
    │    必写: §5步骤状态列 + §7.2逐条执行记录 + §4交付物状态
    │    必发: D: {N}/{M} deliverables ready [{status}]
    ↓  ╳ 闸门: status=completed AND 交付物文件存在 AND pdca.py phase="cqo_review"
CQO Review ─ 必读: Zone A §4(交付物路径) + 交付物文件内容
    │         必做: 验证交付物文件存在 → spawn CQO → CQO-01~05 逐项审核
    │         必调: pdca.py cqo-review --task-card-id ... --result pass|revise|reject
    │         必发: Q: CQO合规审核 [{result}] {— 不通过项}
    ↓  ╳ 闸门: cqo_result=pass AND Zone B pdca_current_phase="check"
    │  (revise/reject → 回到 Do，同 cycle，不改 cycle_index)
Check ─ 必读: Zone A §4(逐项验收标准) + §1(review_level) + 交付物文件
    │    必做: 对§4每个 Deliverable 逐项 pass/fail；按 Review 级别路由
    │    必调: pdca.py c --task-card-id ... --verdict ... --level ... --evidence "§4.1:pass|§4.2:fail|..."
    │    必发: C: {N}/{M} deliverables pass; verdict={verdict} [{status}]
    ↓  ╳ 闸门: verdict 是 final（非 pending）AND evidence 行数=§4行数 AND pdca.py ok:true
    │  (pending → 暂停等 Review，标记 [V]，通知 Review 人)
Act   ─ 必读: Check verdict + Zone A §4 + §1 + MISSION_BOARD
    │    必做（严格顺序）: ①pdca.py a ②更新Task-CARD状态 ③更新Zone B ④audit_eligible ⑤lesson_learned ⑥刷新MISSION_BOARD ⑦heartbeat-state.json ⑧推荐下一Task
    │    必调: pdca.py a --task-card-id ... --summary "..." --next-task ... --lessons "..."
    │    必发: A: verdict={verdict} → [{status}]; next: {TASK_ID} [{verdict}]
    ↓  ╳ 闸门: pdca.py phase="completed" AND MISSION_BOARD已刷新 AND Zone B pdca_current_phase=null
Cycle Complete → 推荐下一个 Task
```

### 1.3 MISSION_BOARD 是派生视图

**MISSION_BOARD §一 状态总览** 的数字从各 section 计数得出，每次 Act 步骤自动刷新：

| 指标 | 派生算法 |
|------|---------|
| 活跃任务数 | §三 进行中区 的 Task ID 数（含 Task ID 的表格行） |
| 待处理任务数 | §五 待处理队列 的 Task ID 数（含 Task ID 的表格行） |
| 阻塞任务数 | §二 阻塞区 的 Task ID 数（含 Task ID 的表格行） |
| 本周完成任务数 | §六 已完成区 中 `close_date` 在本周范围内的 Task ID 数 |
| 今日 Harold Review | §四 待响应评审区 中 Harold 为待审批人的 Task ID 数 |

**"本周"定义**：周一 00:00 ~ 周日 23:59。每周一首次 heartbeat 时，§六 已完成区 自动清零（上周记录归档）。

---

## 二、Task-CARD 选取规则

### 2.1 选取优先级

```
1. [!] Harold 待决 / [V] 待验收 follow-up  — 优先处理等待人类 Review 的任务
2. [?] 阻塞任务                              — 尝试解除阻塞（P0 优先）
3. [P] 进行中任务                            — 推进 PDCA（P0 优先）
4. [ ] 待启动任务                            — 启动 PDCA（P0 优先）
```

### 2.2 Task-CARD 文件定位

从 MISSION_BOARD 选取 Task 后，需要定位到 Task-CARD 文件才能执行 PDCA。定位方式：

1. **优先**：MISSION_BOARD §一.2 Task 跟踪表中的 `Task-CARD 路径` 列
2. **兜底**：按约定路径推导：`10_Projects/{project_dir}/topics/{topic_dir}/tasks/TASK-CARD-{task_id}.md`

### 2.3 选取约束

- 每次 heartbeat 只选一个 Task-CARD 推进
- 如果选中的 Task 是 `[!]` 或 `[V]` 且 Review 人已回复 → 处理回复，推进状态
- 如果选中的 Task 是 `[ ]` → 先执行 accept（`[ ]` → `[P]`），再执行 Plan
- 如果所有 Task 都在等人类 Review 且无新 Review → heartbeat 产出"全队等待"报告

### 2.4 人类驱动时

Harold 指定 Task-CARD → 跳过选取，直接进入 PDCA。如果指定的是 `[ ]` 任务，先 accept 再 Plan。

---

## 三、PDCA 详细步骤

### 3.1 Plan

#### 3.1.1 必读输入

按顺序读取 Task-CARD 以下章节，缺一不可：

| 顺序 | 读取内容 | 来源 | 未满足时 |
|------|---------|------|---------|
| 1 | 当前状态 + PDCA 断点 | Zone B §7.1 | null → 新 cycle；有值 → 断点续传（§3.6） |
| 2 | 任务目标 + 背景 | Zone A §二 | 目标模糊 → 标记 `[?]`，停止 |
| 3 | 输入物就绪状态 | Zone A §三 | 任何输入 ⚠️待准备 → 标记 `[?]`，记录阻塞原因，跳到 Act(verdict=fail) |
| 4 | 交付物清单 + 验收标准 | Zone A §四 | 必须至少 1 个交付物，否则 Plan 不可通过 |
| 5 | 执行步骤 | Zone A §五 | 必须至少 1 步，否则 Plan 不可通过 |
| 6 | 基本信息（优先级/Review级别/类型） | Zone A §一 | 用于闸门判断和后续路由 |
| 7 | Context Refs | Zone A §六 | 至少加载 SOUL.md + IDENTITY.md + HAROLD-DECISION-LIBRARY.md |

如果是断点续传（§7.1 pdca_current_phase 非空），还需读取：
```bash
python scripts/pdca.py status --task-card-id {TASK_ID}
```

#### 3.1.2 必做动作

按序执行，不可跳步：

```
[ ] 1. 读取 Zone B §7.1 → 判断新 cycle 还是断点续传
[ ] 2. 读取 Zone A §二 → 用一句话重述任务目标
[ ] 3. 读取 Zone A §三 → 逐项检查输入物状态，全部 ✅ 才继续
[ ] 4. 读取 Zone A §四 → 列出所有交付物及其验收标准；确认文件名和路径已指定
[ ] 5. 读取 Zone A §五 → 列出所有执行步骤；确认每步有操作和执行人
[ ] 6. 读取 Zone A §一 → 确认优先级、Review 级别、任务类型
[ ] 7. 加载 §六 必要上下文文件
[ ] 8. 调用 enhance_knowledge() 检索历史经验（如有）
[ ] 9. 状态分支判断：
       [V] + Review 已 approve → 跳到 Act(verdict=pass)
       [V] + Review 已 reject  → Plan 方向 = "基于 reject 反馈修改"
       [V] + Review 待回复     → 跳过此 Task，选下一个
       [!] Harold 待决        → 读取 Harold 决策，确定动作
[ ] 10. 若 plan_review_required: true → 暂停等 Harold 审批后再 Do
[ ] 11. 构造 plan summary（格式: "Goal: {目标重述}; Steps: {N}; Deliverables: {M}; Risk: {none/low/high}"）
```

#### 3.1.3 必调命令

```bash
python scripts/pdca.py p \
  --task-card-id {TASK_ID} \
  --summary "Goal: {目标重述}; Steps: {N}; Deliverables: {M}; Risk: {risk}" \
  --criteria "{§4.1验收标准}|{§4.2验收标准}|..." \
  --task-card-path "{Task-CARD绝对路径}" \
  --topic-id {TOPIC_ID} \
  --project-id {PROJECT_ID}
```

- `--criteria`：从 §四 每个交付物的验收标准列提取，用 `|` 连接
- `--task-card-path`：Task-CARD 文件绝对路径
- `--topic-id`、`--project-id`：从 §一 读取

#### 3.1.4 必写更新

| 位置 | 字段 | 更新为 |
|------|------|--------|
| Zone B §7.1 | `pdca_current_phase` | `"do"` |
| Zone B §7.1 | `当前状态值` | `[P]`（如原来是 `[ ]`） |

#### 3.1.5 必发日志

```
P: {目标重述}; {N} steps, {M} deliverables [done]
```

示例：`P: 重构PDCA执行模型; 5 steps, 3 deliverables [done]`

#### 3.1.6 必验结果

- pdca.py 返回 `ok: true` 且 `phase: "plan"`
- Zone B §7.1 `pdca_current_phase = "do"`
- §三 所有输入物状态为 ✅
- §四 至少 1 个交付物
- §五 至少 1 个执行步骤

#### 3.1.7 闸门条件

**全部**满足才可进入 Do：
1. pdca.py p() 返回成功
2. Zone B pdca_current_phase = "do"
3. §三 输入物全部就绪
4. §四 有交付物定义
5. §五 有执行步骤定义
6. 若 plan_review_required=true，Harold 已审批

### 3.2 Do

#### 3.2.1 必读输入

| 顺序 | 读取内容 | 来源 | 用途 |
|------|---------|------|------|
| 1 | 执行步骤（按序） | Zone A §五 | Do 的执行蓝图，必须逐步执行 |
| 2 | 交付物清单 | Zone A §四 | 确认需要产出什么 |
| 3 | 输入物 | Zone A §三 | 执行所需材料 |
| 4 | Plan summary | 上一步 3.1.2 产出 | 方向确认 |
| 5 | 历史执行记录 | Zone B §7.2 | 续传时了解上次做到哪里 |

#### 3.2.2 必做动作

**逐步执行 §五 的每个步骤**，每步按以下子动作执行：

```
对于 §五 中的 Step {N}:
  [ ] Read:  读取本步需要的文件/资源
  [ ] Execute: 执行本步操作
  [ ] Produce: 产出本步输出物（如有）
  [ ] Update §五 状态列: ⬜ → 🟡（开始）→ ✅（完成）或 ❌（失败）
  [ ] Update §7.2 执行记录: 追加一行 "{DATE} | Do Step {N} | {具体做了什么} | {PIC}"
```

**全部步骤执行后**：
```
[ ] 交付物校验: 对 §四 每个交付物，ls 确认文件存在于声明路径
    - 文件存在 → §四 该交付物状态 ⬜ → ✅
    - 文件不存在 → §四 该交付物状态 ⬜ → 🟡，Do status = partial
[ ] 确定整体 Do status:
    - 全部步骤 ✅ 且所有交付物文件存在 → completed
    - 部分步骤失败或交付物缺失 → partial
    - 被阻塞无法继续 → blocked（记录 --blocker 原因）
```

**§五 逐步状态追踪格式**（实时更新 Zone A §五 状态列）：

| Step | 操作 | 状态 |
|------|------|------|
| Step 1 | {action_1} | ✅ |
| Step 2 | {action_2} | 🟡 |
| Step 3 | {action_3} | ⬜ |

#### 3.2.3 必调命令

```bash
python scripts/pdca.py d \
  --task-card-id {TASK_ID} \
  --summary "Completed: Step {N1},{N2}; Deliverables: {已存在的交付物列表}; Issues: {none或描述}" \
  --status completed|blocked|partial \
  --blocker "{阻塞原因}"  # 仅 status=blocked 时
```

#### 3.2.4 必写更新

| 位置 | 字段 | 更新为 |
|------|------|--------|
| Zone B §7.1 | `pdca_current_phase` | `"cqo_review"`（completed）或 `"do"`（blocked/partial） |
| Zone B §7.1 | `阻塞原因` | （如 blocked，填写原因） |
| Zone B §7.1 | `阻塞于` | （如 blocked，填写依赖） |
| Zone A §五 | 各步骤状态列 | ✅ / ❌ / 🟡 |
| Zone A §四 | 各交付物状态 | ✅（文件存在）/ 🟡（文件缺失） |
| Zone B §7.2 | 执行记录 | 每步一行 + Do 完成汇总行 |

§7.2 汇总行格式：
```
| {DATE} | Do 完成 | status={completed/blocked/partial}; deliverables={N}/{M} ready | {PIC} |
```

#### 3.2.5 必发日志

```
D: {N}/{M} deliverables ready [{status}]
```

示例：
- `D: 3/3 deliverables ready [completed]`
- `D: 1/3 deliverables ready [partial]`

#### 3.2.6 必验结果

- pdca.py 返回 `ok: true`
- 若 completed：`phase: "cqo_review"`
- 若 blocked：Zone B §7.1 阻塞原因已填写
- §五 状态列与实际执行一致
- §四 每个标记 ✅ 的交付物，文件确实存在于声明路径

#### 3.2.7 闸门条件

**全部**满足才可进入 CQO Review：
1. pdca.py d() 返回 `status: "completed"` 且 `phase: "cqo_review"`
2. 至少 1 个交付物文件存在于 §四 声明路径
3. Zone B pdca_current_phase = "cqo_review"

**若 status=blocked/partial**：不进入 CQO Review。
- blocked：记录阻塞原因，尝试解除；无法解除 → 进入 Act(verdict=fail)
- partial：可重试 Do 或以已有交付物继续 CQO Review

### 3.3 CQO 合规闸门

> **定位**：CQO 合规闸门是 Do→Check 之间的**过程性检查**，不是 PDCA 的第 5 阶段。PDCA 仍是 Plan→Do→Check→Act 四阶段。

#### 3.3.1 必读输入

| 顺序 | 读取内容 | 来源 | 用途 |
|------|---------|------|------|
| 1 | 交付物清单 + 文件路径 | Zone A §四 | 确定要审核哪些文件 |
| 2 | 交付物文件内容 | §四 声明路径 | CQO-01~05 审核对象 |
| 3 | 对应 TMPL-* 模板 | governance-quality/templates/ | CQO-01 模板匹配的对照基准 |

#### 3.3.2 必做动作

```
[ ] 1. 从 §四 提取所有交付物的文件路径
[ ] 2. 逐个 ls 验证文件存在于声明路径；缺失的文件记录为 CQO-03 不通过
[ ] 3. Spawn CQO Agent 审核（见下方 Spawn 协议）
[ ] 4. 等待 CQO 结果（超时 5 分钟 → 默认 pass，记录 timeout: true）
[ ] 5. 处理 CQO 结果:
       pass   → 进入 Check
       revise → 回到 Do（同 cycle），按 issues 修改后重新 Do
       reject → 回到 Do（同 cycle），重做 + 通知银月
[ ] 6. 追踪 revise_count；>3 次 → 自动升级为 reject
```

**CQO Spawn 协议**（必须逐个列出 §四 交付物）：
```
sessions_spawn({
    agentId: "cqo",
    task: "CQO 合规审核",
    input: {
        task_card_id: "{TASK_ID}",
        deliverables: [
            { name: "{§四.1交付物名}", path: "{完整路径}", format: "{格式}", template: "{TMPL名}" },
            { name: "{§四.2交付物名}", path: "{完整路径}", format: "{格式}", template: "{TMPL名}" }
        ],
        review_items: ["CQO-01", "CQO-02", "CQO-03", "CQO-04", "CQO-05"]
    }
})
```

**CQO 审核项**：

| 编号 | 审核项 | 检查内容 | 不通过处理 |
|------|--------|---------|-----------|
| CQO-01 | 模板匹配 | 交付物是否使用正确的 TMPL-* 模板 | revise，指定正确模板 |
| CQO-02 | 元数据完整 | frontmatter 必填字段齐全（title/id/status/owner/created/updated） | revise，列出缺失字段 |
| CQO-03 | 路径规范 | 文件存放路径符合 §四 声明路径 + ZT-2026-007 | revise，指定正确路径 |
| CQO-04 | 结构完整 | 章节结构符合对应规范 | revise，列出缺失章节 |
| CQO-05 | 格式合规 | 标记、表格、引用格式符合 governance 规范 | 视严重程度 pass with note 或 revise |

**判定规则**：

| 结果 | 条件 | 后续 |
|------|------|------|
| **pass** | CQO-01~05 全部通过 | 进入 Check |
| **revise** | CQO-01~04 有 1-2 项不通过 | 回到 Do，按 issues 修改（同 cycle） |
| **reject** | CQO-01~04 有 3+ 项不通过 | 回到 Do，重做 + 通知银月（同 cycle） |

#### 3.3.3 必调命令

```bash
python scripts/pdca.py cqo-review \
  --task-card-id {TASK_ID} \
  --result pass|revise|reject \
  --report-path "10_Projects/{PROJECT_ID}/{TOPIC_ID}/deliverables/CQO-{TASK_ID}-{TIMESTAMP}.md" \
  --issues "CQO-01|CQO-03"  # 仅 revise/reject 时，列出未通过项
```

#### 3.3.4 必写更新

| 位置 | 字段 | 更新为 |
|------|------|--------|
| Zone B §7.1 | `pdca_current_phase` | `"check"`（pass）或 `"do"`（revise/reject） |
| Zone B §7.1 | `CQO 审核状态` | pass / revise / reject |
| Zone B §7.2 | 执行记录 | 追加 `"{DATE} \| CQO Review \| result={result}; issues={list} \| CQO"` |

revise/reject 时还需：
- Zone A §四：不通过交付物状态 ✅ → 🟡（需修改）
- 通知银月（仅 reject）

#### 3.3.5 必发日志

```
Q: CQO合规审核 [{result}] {— 不通过项（如有）}
```

示例：
- `Q: CQO合规审核 [pass]`
- `Q: CQO合规审核 [revise] — CQO-01,CQO-03`

#### 3.3.6 必验结果

- pdca.py 返回 `ok: true`
- pass：Zone B pdca_current_phase = "check"
- revise/reject：Zone B pdca_current_phase = "do"
- CQO 合规报告文件存在于 --report-path 路径（如有）
- revise_count 未超限（≤3）

#### 3.3.7 闸门条件

**全部**满足才可进入 Check：
1. pdca.py 返回 `cqo_result: "pass"`
2. Zone B pdca_current_phase = "check"
3. Zone B CQO 审核状态 = "pass"

**若 revise/reject**：回到 Do（§3.2），cycle_index 不变，从 CQO issues 指出的失败步骤重新执行。

### 3.4 Check

#### 3.4.1 必读输入

| 顺序 | 读取内容 | 来源 | 用途 |
|------|---------|------|------|
| 1 | 交付物清单 + 验收标准 | Zone A §四 | **逐项验收的基准**，每个 Deliverable 必须对照其验收标准 |
| 2 | Review 级别 | Zone A §一 | 决定谁 Review |
| 3 | 交付物文件内容 | §四 声明路径 | 验证实际内容是否满足验收标准 |
| 4 | CQO 合规报告 | deliverables/ | 已通过合规闸门的证据 |

#### 3.4.2 必做动作

**步骤 A：逐交付物验收（必须生成以下表格）**

对 §四 每个交付物，逐项判定：

| §四序号 | 交付物名称 | 验收标准 | 文件存在? | 标准满足? | 判定 |
|---------|-----------|---------|----------|----------|------|
| 1 | {name} | {criteria text} | yes/no | yes/no | pass/fail |
| 2 | {name} | {criteria text} | yes/no | yes/no | pass/fail |

**整体 verdict 推导**：
- 全部 pass → verdict = pass
- 有 fail → verdict = fail
- 非关键项 fail但关键项 pass → verdict = partial

**步骤 B：Review 级别路由**

| Review 级别 | LLM 动作 | pdca.py verdict |
|------------|---------|----------------|
| L0 | 自验收，直接出结论 | pass 或 fail（不可 pending） |
| L1 | LLM 自审，质量不确定可升级 L2 | pass/fail/partial（不可 pending） |
| L2 | LLM 自审；被抽样时 → pending | pass/fail/partial 或 pending |
| L3 | **必须** pending，等 Harold | pending（仅此一个值） |

LLM 可主动升级 Review 级别：质量存疑/发现风险/超出判断能力时。

**步骤 C：verdict=pending 时的处理**
```
[ ] Task 标记 [V] → Zone B §7.1
[ ] 录入 MISSION_BOARD §四（待响应评审区）
[ ] 飞书通知 Review 人
[ ] PDCA 暂停；下次 heartbeat 在 Plan 步骤检查 Review 人回复
```

#### 3.4.3 必调命令

```bash
python scripts/pdca.py c \
  --task-card-id {TASK_ID} \
  --verdict pass|partial|fail|pending \
  --level {REVIEW_LEVEL} \
  --evidence "§4.1:{pass/fail}|§4.2:{pass/fail}|...|§4.N:{pass/fail}"
```

- `--evidence` **必须**逐项对应 §四 的每个交付物，格式 `§4.{序号}:{判定}`
- evidence 行数必须 = §四 交付物行数

#### 3.4.4 必写更新

| 位置 | 字段 | 更新为 |
|------|------|--------|
| Zone B §7.1 | `pdca_current_phase` | `"act"`（final verdict）或 `"check"`（pending） |
| Zone B §7.1 | `当前状态值` | `[V]`（pending）或 `[P]`（partial/fail） |
| Zone B §7.2 | 执行记录 | 追加 `"{DATE} \| Check \| verdict={verdict}; §4 items: {N}/{M} pass; level={Lx} \| {PIC}"` |

若 pending，还需更新 §八.1 Harold Review 记录。

#### 3.4.5 必发日志

```
C: {N}/{M} deliverables pass; verdict={verdict} [{status}]
```

示例：
- `C: 3/3 deliverables pass; verdict=pass [pass]`
- `C: 1/3 deliverables pass; verdict=partial [partial]`
- `C: awaiting Harold review; verdict=pending [pending]`

#### 3.4.6 必验结果

- pdca.py 返回 `ok: true`
- 非 pending：Zone B pdca_current_phase = "act"
- pending：Zone B pdca_current_phase = "check"（保持）
- L0/L1：verdict 不是 pending
- L3：verdict 是 pending
- `--evidence` 中的项数 = §四 交付物行数

#### 3.4.7 闸门条件

**全部**满足才可进入 Act：
1. pdca.py c() 返回 **final** verdict（非 pending）
2. Zone B pdca_current_phase = "act"
3. 逐交付物验收表格完整（§四 每行都有判定）

**若 verdict=pending**：PDCA 暂停。下次 heartbeat 在 Plan（§3.1.2 步骤 9）检查 Review 人回复。

### 3.5 Act

#### 3.5.1 必读输入

| 顺序 | 读取内容 | 来源 | 用途 |
|------|---------|------|------|
| 1 | Check verdict | pdca.py status 或 Zone B | 决定 Act 动作 |
| 2 | 交付物清单 | Zone A §四 | 最终状态更新 |
| 3 | 基本信息 | Zone A §一 | audit_eligible 判断 |
| 4 | MISSION_BOARD | MISSION_BOARD.md | 派生刷新 |

#### 3.5.2 必做动作

**严格按以下顺序执行，每步依赖前步完成**：

```
[ ] 1. 调用 pdca.py a（见 3.5.3）
[ ] 2. 更新 Task-CARD Zone B §7.1 状态标记:
       verdict=pass    → [x]
       verdict=partial → [P]
       verdict=fail    → [P]
[ ] 3. 更新 Zone B §7.1 pdca_current_phase → null（cycle 完成）
[ ] 4. 更新 Zone B §7.2 → 追加 Act 执行记录
[ ] 5. 若 verdict=pass 且 review_level=L0/L1 → Zone B §7.1 设置 audit_eligible: true
[ ] 6. 若 verdict=pass → 触发 create_lesson_learned()（经验回流）
[ ] 7. 若 verdict=pass 且 L0/L1 → Zone B §7.1 经验回流 = "LL-{YYYY-MM-DD}.md"
[ ] 8. 刷新 MISSION_BOARD（见下方）
[ ] 9. 更新 heartbeat-state.json（见下方）
[ ] 10. 推荐下一个 Task（见下方）
```

**MISSION_BOARD 派生刷新（步骤 8，必须执行）**：
```
[ ] 8a. 重新计算 §一 各指标（从 §二/§三/§五/§六 计数）
[ ] 8b. 更新 最后更新 时间戳
[ ] 8c. 更新 变更人 字段
[ ] 8d. 重新读取 MISSION_BOARD 验证写入成功
```

**heartbeat-state.json 更新（步骤 9）**：
```
[ ] 9a. last_pdca: {task_card_id, cycle_index, verdict, timestamp}
[ ] 9b. stats: total_cycles += 1; {verdict}_count += 1; consecutive_fails = (verdict=fail ? +1 : 0)
[ ] 9c. 若 verdict=pending: 追加 task_card_id 到 paused_tasks
```

**下一个 Task 推荐（步骤 10）**：

按 §2.1 优先级选取，输出格式：
```
Next recommended: {TASK_ID} — {reason}
```

只建议，不自动执行。Harold 在会话中则直接问。

#### 3.5.3 必调命令

```bash
python scripts/pdca.py a \
  --task-card-id {TASK_ID} \
  --summary "verdict={verdict}; {可读总结}; next_input_for_plan: {下次Plan的输入}" \
  --next-task {NEXT_TASK_ID} \
  --lessons "{lesson_1}|{lesson_2}"
```

- `--summary` **必须**包含 `next_input_for_plan`（Harness 规则 A1）
- `--next-task`：步骤 10 推荐的下一个 Task ID
- `--lessons`：verdict=pass 且 create_lesson_learned() 产出了经验时填写

#### 3.5.4 必写更新

| 位置 | 字段 | 更新为 |
|------|------|--------|
| Zone B §7.1 | `当前状态值` | `[x]` / `[P]` / `[V]`（按 verdict） |
| Zone B §7.1 | `pdca_current_phase` | `null` |
| Zone B §7.1 | `MISSION BOARD 同步` | `✅ 已同步` |
| Zone B §7.1 | `经验回流` | `LL-{date}.md`（verdict=pass）或 `null` |
| Zone A §四 | 交付物状态 | verdict=pass 时全部 ✅；否则失败项 🟡/❌ |
| Zone B §7.2 | 执行记录 | `"{DATE} \| Act \| verdict={verdict}; status→[{new}]; next={TASK_ID} \| {PIC}"` |

#### 3.5.5 必发日志

```
A: verdict={verdict} → [{status_mark}]; next: {NEXT_TASK_ID} [{verdict}]
```

示例：`A: verdict=pass → [x]; next: T02 [pass]`

若触发了 lesson_learned，追加：
```
L: {经验摘要} [knowledge]
```

#### 3.5.6 必验结果

- pdca.py 返回 `ok: true` 且 `phase: "completed"`
- Task-CARD 状态标记与 verdict 一致
- Zone B pdca_current_phase = null
- MISSION_BOARD 已刷新且 §一 指标正确
- heartbeat-state.json 已更新

#### 3.5.7 闸门条件

**全部**满足才认为 PDCA cycle 完成：
1. pdca.py 返回 `phase: "completed"`
2. Task-CARD 状态标记与 verdict 一致
3. MISSION_BOARD 已刷新并验证
4. heartbeat-state.json 已更新
5. Zone B pdca_current_phase = null

Cycle 完成后，下次 heartbeat 选取新 Task（或推荐 Task）。

### 3.6 断点续传

> **问题**：heartbeat 可能中途中断（超时、token 耗尽、手动停止）。需要从断点继续而非重新开始。

**机制**：Task-CARD Zone B §7.1 的 `pdca_current_phase` 字段记录当前 PDCA 位置（已在 §3.1-3.5 各步骤的"必写更新"中定义）。

| Phase 完成时 | Zone B 更新 |
|-------------|------------|
| Plan 完成 | `pdca_current_phase = "do"` |
| Do 完成 | `pdca_current_phase = "cqo_review"` |
| CQO Review pass | `pdca_current_phase = "check"` |
| Check 完成 | `pdca_current_phase = "act"` |
| Act 完成 | `pdca_current_phase = null`（本轮完成） |

**下次 heartbeat 选取到该 Task 时**：

1. 读取 Zone B §7.1 的 `pdca_current_phase`
2. 如果 `null` → 新一轮 PDCA，从 Plan 开始
3. 如果有值 → 从断点继续：

| 断点 Phase | 续传动作 | 额外校验 |
|-----------|---------|---------|
| `"do"` | 跳过 Plan，直接进入 Do；从 §五 第一个 🟡/⬜ 步骤继续 | 验证 §7.2 执行记录与 §五 状态列一致 |
| `"cqo_review"` | 跳过 Plan/Do，进入 CQO Review | 验证交付物文件仍存在于 §四 声明路径 |
| `"check"` | 跳过 Plan/Do/CQO，进入 Check | 验证 CQO pass 结果仍在 §7.1 |
| `"act"` | 跳过 Plan/Do/CQO/Check，进入 Act | 验证 Check verdict 仍可访问 |

**规则**：
- 断点续传时跳过的步骤不算"跳步"——它们在上次 heartbeat 已完成
- 续传时先验证前置步骤的产出仍在 Zone B，如果丢失 → 回退到最早缺失的步骤
- 断点在 `"do"` 时，**不要重新开始整个 Do**——从 §五 第一个未完成步骤继续，已 ✅ 的步骤跳过
- 飞书日志标记 `[resume from {phase}]`

---

## 四、飞书步骤级执行日志（v8.0 新增）

> **目的**：让 Harold 在飞书中实时看到每个 Task 的 PDCA 执行进度，无需等到晨/夕会报告。

### 4.1 日志格式

每个 PDCA 步骤完成后，向飞书渠道（Agent 对应的 DM 或大群）发送一条步骤日志：

```
📋 {agent_name} | {project_id} [by {project_owner}]
  └─ {topic_id} [by {topic_owner}]
      └─ {task_id} [round {n}]
          ├─ P: {plan_summary} [{status}]
          ├─ D: {do_summary} [{status}]
          ├─ Q: CQO合规审核 [{cqo_result}] — {不通过项}
          ├─ C: {check_summary} [{status}]
          └─ A: {act_summary} [{verdict}]
```

**字段说明**：

| 字段 | 含义 | 示例 |
|------|------|------|
| `agent_name` | 执行 Agent 名称 | 银月 |
| `project_id` | 项目 ID | ZT-P015 |
| `project_owner` | 项目负责人 | 张铁 (cqo) |
| `topic_id` | Topic ID | N4-P1-T08 |
| `topic_owner` | Topic 负责人 | 张铁 |
| `task_id` | Task ID | T01 |
| `round n` | 第 N 轮 PDCA | round 3 |
| `P/D/C/A` | PDCA 各步骤 | |
| `summary` | 该步骤的简要描述（一行） | "规划集成测试框架选型" |
| `status` | 该步骤完成状态 | `done` / `pending` / `failed` / `skipped` |
| `verdict` | Act 的结论 | `pass` / `fail` / `partial` / `pending(Harold)` |

### 4.2 发送规则

| 规则 | 说明 |
|------|------|
| **发送时机** | 每个 PDCA 步骤完成时**立即**发送，不积攒 |
| **发送渠道** | Agent 私信 DM（银月 → Harold 的 DM）；子 Agent → 银月的 DM |
| **静默时段** | 非汇报时段仍发送步骤日志（与晨夕报告不同，步骤日志是"过程记录"而非"汇报"） |
| **避免 spam** | 同一 Task 同一轮 PDCA 的步骤日志合并为一条消息（见下方增量模式） |
| **Learn 步骤** | 如果 Learn 蒸馏了有效知识，追加 `L: {insight_summary}` |

### 4.3 增量模式

为了避免飞书消息过多，同一轮 PDCA 的步骤日志采用**增量追加**模式：

> **实现方式**：优先编辑原消息（减少消息数）。如果飞书 API 不支持编辑，则发新消息并通过 `task_id+round` 关联。

**Plan 完成** → 发送：
```
📋 银月 | ZT-P015 [by 张铁]
  └─ N4-P1-T08 [by 张铁]
      └─ T01 [round 3]
          └─ P: 规划集成测试框架选型 [done]
```

**Do 完成** → 追加（编辑原消息或新消息）：
```
📋 银月 | ZT-P015 [by 张铁]
  └─ N4-P1-T08 [by 张铁]
      └─ T01 [round 3]
          ├─ P: 规划集成测试框架选型 [done]
          └─ D: 实现 pytest conftest + 3 个 test case [done]
```

**全轮完成** → 最终消息：
```
📋 银月 | ZT-P015 [by 张铁]
  └─ N4-P1-T08 [by 张铁]
      └─ T01 [round 3]
          ├─ P: 规划集成测试框架选型 [done]
          ├─ D: 实现 pytest conftest + 3 个 test case [done]
          ├─ Q: CQO合规审核 [pass]
          ├─ C: 3/3 test passed, coverage 82% [pass]
          ├─ A: verdict=pass → [x] [pass]
          └─ L: pytest conftest 模式可复用于其他 Agent 测试 [knowledge]

  🎯 Next: ZT-P015-T02 — 扩展 mock 覆盖率
```

### 4.4 子 Agent 的步骤日志

子 Agent（CTO、CQO 等）的步骤日志发送到**银月的 DM**，由银月汇总后决定是否转发给 Harold。

**银月汇总规则**：
- 子 Agent 的步骤日志 → 银月 DM（自动）
- 有 `verdict=fail` 或 `verdict=pending(Harold)` → 银月转发给 Harold
- 银月晨夕会报告 → 包含所有子 Agent 的 PDCA 产出摘要

---

## 五、Review 阻塞管理

### 5.1 Review 等待状态

当 PDCA 在 Check 阶段需要人类 Review 时：

```
Task 标记 [V] → 通知 Review 人 → 记录到 MISSION_BOARD §四
    ↓
Review 人回复：
  ├─ approve → 下次 heartbeat: Act(verdict=pass) → [x]
  ├─ reject  → 下次 heartbeat: Plan(基于 reject 原因)
  └─ 超时    → 超时处理（见下方）
```

### 5.2 Review 超时处理

| Review 级别 | 预期响应时间 | 超时动作 |
|------------|------------|---------|
| L1（银月） | 2 小时 | 自动提醒 |
| L2（Harold 抽样） | 24 小时 | 银月 follow up |
| L3（Harold 全量） | 72 小时 | 银月 follow up，7 天未决升级为异常 |

### 5.3 Harold 在会话中的即时 Review

如果 Harold 在会话中直接对某个 `[V]` 任务给出 approve/reject → 立即执行 Act，无需等下次 heartbeat。

---

## 六、汇报规则（PDCA 的副产品）

> 汇报是 PDCA 执行后的信息同步，不是 heartbeat 的目的。

### 6.1 汇报类型

| 汇报类型 | 时间 | 内容 | 条件 |
|----------|------|------|------|
| **晨会报告** | 07:00 | 每个 Agent 的 PDCA 进展、阻塞、今日计划（PREP汇总） | 每日固定 |
| **夕会报告** | 21:00 | 今日 PDCA 完成、明日计划（PREP汇总） | 每日固定 |
| **异常报告** | 实时 | PDCA 异常（SPARK模型） | 有异常或状态变更 |
| **决策请求** | 需Harold裁决时 | 方案对比（RIDE模型） | 准备好方案后立即 |

### 6.2 静默执行

**非 7:00/21:00**：执行 PDCA → 刷新 MISSION_BOARD → 不发飞书消息（除非有异常或状态变更）

### 6.3 时间窗口判断

- 晨会窗口：6:30 — 7:30 → 发送晨会报告
- 夕会窗口：20:30 — 21:30 → 发送夕会报告
- 其他时间 → 静默执行

---

## 七、银月职责（作为协调者）

### 7.1 银月的 heartbeat vs 子 Agent 的 heartbeat

| 维度 | 银月 | 子 Agent |
|------|------|---------|
| **Task 选取** | 从全局 MISSION_BOARD 选取自己负责的 Task | 从自己的 MISSION_BOARD 选取 |
| **PDCA 执行** | 推进自己的 Task | 推进自己的 Task |
| **协调** | 汇总所有 Agent 状态 | 向银月汇报 PDCA 结果 |
| **全局报告** | 生成晨夕会报告 | 不生成全局报告 |
| **MISSION_BOARD** | 维护根目录全局版 + 自己的 | 维护自己的 |

### 7.2 银月发起子 Agent heartbeat

```
sessions_spawn(
    agentId="cto",
    task="## Heartbeat PDCA\n\n请执行 heartbeat：读取 MISSION_BOARD，选取 Task-CARD，执行一轮 PDCA",
    timeoutSeconds=120,
    mode="run",
    runtime="subagent"
)
```

> 120s 超时 → 标记"未响应"，继续其他 Agent。

---

## 八、PDCA 与 nucleus 的关系

| 维度 | governance-heartbeat（本 Skill） | governance-nucleus |
|------|--------------------------------|-------------------|
| **职责** | PDCA 执行入口 + 流程驱动 | pdca.py 状态记录 + 聚合 |
| **层级** | L2 | L3（内部工具） |
| **触发** | heartbeat 定时 / 人类驱动 | 由 heartbeat 在 Act 步骤调用 |
| **产出** | Task-CARD 推进 + MISSION_BOARD 刷新 | pdca/*.yaml 状态文件 |

**heartbeat 在 Act 步骤调用 pdca.py**：记录本轮 PDCA verdict、触发 aggregate() 层间传播。

**nucleus 不再是独立触发入口**：所有 PDCA 执行都通过 heartbeat 入口。nucleus 的 pdca.py 退化为底层状态记录工具。

> **v9.0 注意**：pdca.py 的 CLI 命令及参数已在 §3.1-3.5 各步骤的"必调命令"中内联指定。执行 PDCA 时无需再引用 nucleus SKILL.md 或 pdca-harness.md。

---

## 九、L0/L1 自验收审计机制

> L0/L1 任务 Agent 自验收通过，没有人类 Review 兜底。需要后续审计来保证质量。

### 9.1 审计触发

Act 步骤中，verdict=pass 且 Review 级别为 L0/L1 的任务，自动标记 `audit_eligible: true`，写入 Task-CARD Zone B 和 pdca 记录。

### 9.2 审计执行

每个 heartbeat 在选取 Task-CARD 之前，先检查是否有待审计任务：

1. 查询 `audit_eligible: true` 且 `audit_result: null` 的 PDCA 周期
2. 如果存在 → 本次 heartbeat 优先执行审计（而非推进新 Task）
3. 审计方式：读取 Task-CARD + 交付物 → 质量评分（0-100）
   - 80+ : 审计通过，标记 `audit_result: pass`
   - 60-79 : 审计通过但记录改进建议
   - < 60 : 审计不通过，任务回退到 `[P]`，需要重新执行 PDCA
4. **审计结果自动进入 Learn 步骤**：审计发现的问题作为 Knowledge 类型蒸馏，改进建议可触发锁住收益

### 9.3 审计优先级

| 任务优先级 | 审计概率 |
|-----------|---------|
| P0 | 100%（必须审计） |
| P1 | 50% |
| P2 | 20% |
| P3 | 10% |

---

## 十、特殊情况

| 情况 | 处理 |
|------|------|
| **所有 Task 都在等 Review** | heartbeat 产出"全队等待"报告，列出所有 pending review 项 |
| **连续 3 次 fail** | 上报 Harold，标记 `[!]` |
| **连续 3 次 blocked** | 标记 pdca_paused，从候选队列移除，上报 Harold |
| **Task 输入物不就绪** | Plan 阶段识别，标记 `[?]`，通知输入物提供方 |
| **无 Task-CARD 可选** | Agent 报告"空闲"给银月，银月协调分配 |

---

## 十一、命令规范

> **详细 Command Spec** 见 `core/commands.md`

| 命令 | 用途 |
|------|------|
| `gov heartbeat run-pdca [--task-card-id <id>]` | 执行一轮 PDCA+Learn（自动选取或指定） |
| `gov heartbeat select-task [--agent-id <id>]` | 选取下一个 PDCA 候选 Task |
| `gov heartbeat refresh-mission-board [--agent-id <id>]` | 派生刷新 MISSION_BOARD §一 |
| `gov heartbeat generate-report [--type morning\|evening\|exception]` | 生成报告 |
| `gov heartbeat check-review-pending` | 检查等待 Review 的任务 |
| `gov heartbeat read-state` / `write-state` | 状态读写 |
| `gov heartbeat log-step [--step P\|D\|Q\|C\|A\|L]` | 发送飞书步骤日志（v8.0） |
| `gov heartbeat learn [--task-card-id <id>]` | 执行 Learn 步骤（蒸馏+回溯+锁入+建议） |
| `gov heartbeat suggest-next` | 基于 Learn 建议下一个 Task |

---

## 十二、模板清单

| 模板 | 用途 | 适用对象 | 版本 |
|------|------|----------|------|
| `TMPL-HEARTBEAT.md` | Main Agent heartbeat 协议 | 银月 | v4.0 |
| `TMPL-HEARTBEAT-SUB.md` | Sub Agent heartbeat 协议 | 其他 Agent | v2.0 |
| `heartbeat-state.json` | 状态记录模板 | 所有 Agent | v2.0 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **9.0.0** | 2026-05-07 | **PDCA 执行模型强约束重构**：§3.1-3.5 全部改为 7 段式 checklist（必读输入→必做动作→必调命令→必写更新→必发日志→必验结果→闸门条件）；Do 增加§五逐步骤追踪（⬜→🟡→✅）+ 交付物文件校验；Check 增加逐交付物验收表格 + evidence 编码；Act 增加严格 10 步副作用顺序；§1.2 流程图加注闸门条件；§3.6 断点续传增加 Do 子步骤追踪；§8 添加 CLI 内联说明 |
| **8.1.0** | 2026-05-06 | **CQO 合规闸门**：新增 §3.3 CQO 合规闸门（Do→CQO Review→Check）；CQO-01~05 审核项；CQO spawn 协议；pass/revise/reject 判定规则；退回 rework 流程；飞书日志 Q: 标记；断点续传增加 cqo_review phase |
| **8.0.0** | 2026-05-05 | **闭环增强**：新增 §3.5 断点续传（pdca_current_phase）；Act 经验回流（create_lesson_learned）；Plan 经验检索（enhance_knowledge）；完成即推荐；新增 §4 飞书步骤级执行日志 |
| **7.0.0** | 2026-04-26 | 重构为 PDCA 执行器模型：heartbeat = PDCA 入口；MISSION_BOARD 派生视图；人类驱动同流程；Review 阻塞管理 |
| **6.2.0** | 2026-04-23 | Step 6 新增 PDCA 审计队列巡检 |
| **6.0.0** | 2026-04-18 | 新增 Step 3 文件编辑强制要求 |

---

*版本: 9.0.0 | 更新: 2026-05-07 | 变更: PDCA 执行模型强约束重构*

## Related Skills
- [[openclaw-governance-task]] - 任务管理，Task-CARD 生命周期
- [[openclaw-governance-core]] - 核心运行机制
- [[openclaw-governance-nucleus]] - pdca.py 状态记录工具（heartbeat 在 Act 步骤调用）
- [[openclaw-governance-delegation]] - Review 级别判定
- [[openclaw-governance-hierarchy]] - 层级管理，bubble_up()
