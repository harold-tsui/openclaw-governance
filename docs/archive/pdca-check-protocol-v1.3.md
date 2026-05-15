# PDCA Check 策略协议

> **版本**：v1.3
> **日期**：2026-04-05
> **状态**：草案，待 Harold 确认
> **依据**：ARCH v1.4.2 §2.1.3 · governance-delegation SKILL v1.2.0 · TMPL-TASK-CARD v1.2 §五 · cycle_unit.schema v1.3-fixed
>
> **变更摘要** :
> - v1.1：补全 P0 评审问题（parent_review_level · adjust 接口签名 · skip 行为 · L2 reviewer 映射 · DoD 扩展）
> - v1.2：数据来源重构——`check_reference` 从 cycle_unit 移除；`determine_review()` 改为读取 task-card，不写入 cycle_unit；§7.2 / §7.3 字段映射拆分重写
> - **v1.3：级别定义对齐 TMPL-TASK-CARD §五——L0=免审，L3=全量人工（Harold 必须介入）；全文级别含义反转修正；`human_approval_required` 规则、skip 触发条件、升降级约束同步更新；子环约束方向修正（§3.2: 不得低于 max(parent-1, L0)，§3.7: 更宽松时自动收紧）**

---

## 一、协议目标

定义 PDCA 环中 **Check 阶段** 的验收机制，确保：

1. **唯一真相源**：验收标准、Review 级别、交付物定义统一在 task-card 中声明；cycle_unit 只做运行时状态跟踪
2. **明确验收标准**：Plan 阶段从 task-card 读取，Check 阶段严格执行
3. **分级评审机制**：基于 task-card §一 Review 级别（L0-L3），确定 Review 方式与 reviewer
4. **驱动 Act 调整**：根据 verdict，调整下次自动化级别
5. **知识沉淀闭环**：Task 关闭后触发 LESSON-LEARN 四问法，未完成不视为真正关闭

---

## 二、核心流程

### 2.1 整体流程图

```
Plan 阶段
    ↓
调用 determine_review()
    ↓ 读取 task-card §一（Review 级别 L0-L3）+ §五（Deliverable 验收标准）
    ↓ 生成 review_context（内存结构，不写入 cycle_unit）
    ↓
Do 阶段
    ↓ 执行 task-card §四 执行流程 + 子环
    ↓ 执行状态写入 cycle_unit.do
    ↓
Check 阶段
    ↓ 按 review_context 执行验收
    ↓   L0：Task PIC 直接流转，Harold 不介入 → verdict=skip
    ↓   L1：正常流转，异常时上报 Harold
    ↓   L2：银月抽样（20-30%），抽中进七区等待 Harold
    ↓   L3：Harold 全量审阅，必须介入
    ↓ verdict + criteria_results + evidence → 写入 cycle_unit.check
    ↓
Act 阶段
    ↓ 调用 adjust_automation_level()
    ↓ adjustments → 写入 cycle_unit.act
    ↓ 传播 adjustments → 下一环或父环
```

### 2.2 关键接口定义

| 接口 | 调用时机 | 数据来源 | 输出目标 | 负责方 |
|------|----------|----------|----------|--------|
| `determine_review()` | Plan 阶段开始时 | task-card §一 + §五 | review_context（内存，不持久化） | Plan 模块 |
| `adjust_automation_level()` | Act 阶段开始时 | cycle_unit.check.verdict + 当前级别 + consecutive_count | cycle_unit.act.adjustments | Act 模块 |

> **设计原则**：`determine_review()` 只读取，不写入。cycle_unit 中不存储 check_reference 块。

---

## 三、determine_review() 接口规范

### 3.1 调用时机

- **触发点**：Plan 阶段开始时（task-card 已加载、task_id / scope / review_level 已确认之后）
- **前置条件**：task-card 存在且 §一 Review 级别字段非空
- **调用频率**：每个 CycleUnit 实例调用一次
- **输出去向**：review_context 保持内存，供当轮 Check 阶段直接使用；**不写入 cycle_unit**

### 3.2 输入参数

```json
{
  "task_card_ref": {
    "task_id": "NUC-01-TP01-T01",
    "card_path": "tasks/TASK-CARD-NUC-01-TP01-T01.md"
  },
  "task_type": "常规|系统级|周期性|应急|一次性",
  "project_phase": "establishing|transition|cruising|maintaining",
  "dl_refs": ["DL-2026-001", "DL-2026-002"],
  "is_first_time": false,
  "priority": "P0|P1|P2|P3",
  "agent_id": "main|cqo|cto|ceo",
  "parent_review_level": "L0|L1|L2|L3|null"
}
```

> **`parent_review_level`**：子环 review_level 不得**低于** `max(parent_review_level - 1, L0)`。
> 即子环自动化程度不能比父环更高（更宽松）超过 1 级。顶层 CycleUnit 传 `null`，不做父级约束。

### 3.3 读取逻辑

`determine_review()` 从 task-card 读取以下字段，**不推断、不覆写**：

| task-card 字段 | 位置 | 映射到 review_context |
|---|---|---|
| Review 级别 | §一 基本信息表（默认 L3） | `review_level` |
| 授权编号 | §一 `DA-[编号]` | `delegation_ref` |
| Deliverable 验收标准 | §五 验收标准列 | `acceptance_criteria[]` |
| Deliverable Review 级别（单项覆盖） | §五 Review 级别列 | 单 Deliverable 粒度覆盖 `review_level` |

### 3.4 输出格式（review_context）

```json
{
  "review_level": "L0|L1|L2|L3",
  "acceptance_criteria": [
    "标准1描述",
    "标准2描述"
  ],
  "reviewer": "harold|yin-yue|null",
  "delegation_ref": "DA-001|null",
  "references": [
    "docs/pdca-check-protocol.md",
    "DL-2026-001"
  ],
  "parent_constraint_applied": false
}
```

> **`parent_constraint_applied`**：若实际 review_level 因父级约束被调整，此字段为 `true`，并在 cycle_unit 执行记录中注明原因。

### 3.5 L0-L3 级别映射

> **级别定义以 TMPL-TASK-CARD §五 为准：L0=免审（自动化最高），L3=全量人工（Harold 必须介入）。**

| 级别 | 名称 | Harold 介入 | 审批方式 | 适用场景 | reviewer | verdict |
|------|------|-------------|----------|----------|----------|---------|
| **L0** | 免审 | ❌ 不介入 | Task PIC 直接流转 `[V]`，银月验收后改 `[x]` | Routine Task，成熟流程，有 DL 支撑 | `null` | `skip` |
| **L1** | 异常上报 | ⚠️ 异常时 | Task PIC 正常流转 `[V]`；有疑虑标记 `[!?]`，银月判断是否上报 Harold | 较复杂 Task，有疑虑需上报 | Harold（异常时） | `pass` / `partial` |
| **L2** | 抽样核查 | 🔀 抽中时 | 银月抽样（20-30%）；抽中标记 `[!]` 进七区等待 Harold；未抽中直接流转 `[V]` | 重要 Task，需抽样核查 | `yin-yue`（抽中升级为 `harold`） | `pass` / `partial` |
| **L3** | 全量人工 | ✅ 必须介入 | Harold 全量审阅，Task PIC 标记 `[!]`，银月录入七区，等待 Harold | 全新场景，无 DL 支撑，高风险 | `harold`（必填） | `pass` / `partial` / `fail` |

### 3.6 reviewer 选择规则

- **L0**：`reviewer = null`，Task PIC 直接流转，Harold 不介入
- **L1**：`reviewer = null`（正常路径）；有疑虑时银月判断是否触发 `harold`
- **L2**：`reviewer = yin-yue`（银月执行抽样）；抽中升级为 `harold`，在执行记录中更新，**不修改 review_context**
- **L3**：`reviewer = harold`，必填，不可为 `null`

### 3.7 校验规则

| 场景 | 处理策略 |
|------|----------|
| `acceptance_criteria` 为空列表 `[]` | 等同字段缺失，触发默认值：`review_level=L2, reviewer=yin-yue` |
| `review_level` 字段缺失或无效值 | 降级到 L2，记录告警，继续执行 |
| task-card 不存在或无法读取 | 阻断 Plan 阶段，标记 `[?]` 等待 Harold 决策 |
| 子环 review_level 比父级更宽松 | 自动收紧至 `max(parent_review_level - 1, L0)`，`parent_constraint_applied = true` |

---

## 四、Check 阶段执行规范

### 4.1 验收标准处理

- **acceptance_criteria 来源**：由 `determine_review()` 从 task-card §五 读取，存于 review_context，**不存 cycle_unit**
- **验收方式**：

| review_level | 验收方式 | 状态标记 |
|---|---|---|
| **L0** | Task PIC 直接流转，银月验收后改 `[x]`，Harold 不介入 | `[V]` → `[x]` |
| **L1** | Task PIC 正常流转；有疑虑标记 `[!?]`，银月判断是否上报 Harold | `[V]` 或 `[!?]` |
| **L2** | 银月抽样（20-30%）；抽中标记 `[!]` 进七区；未抽中直接流转 `[V]` | `[!]` 或 `[V]` |
| **L3** | Task PIC 标记 `[!]`，银月录入 MISSION_BOARD 七区，Harold 全量审阅 | `[!]` → Harold 审阅 |

- **证据收集**：所有验收过程必须记录到 `cycle_unit.check.evidence`
- **逐项记录**：`cycle_unit.check.criteria_results` 记录每条标准的核对结果（`CriterionResult` 结构）

### 4.2 verdict 生成规则

| 条件 | verdict | 说明 |
|------|---------|------|
| review_level=L0（免审） | `skip` | Task PIC 直接流转，Harold 不介入。**Act 阶段仍须调用 `adjust_automation_level()`**；`consecutive_count` 不变；`act.adjustments` 写入 `type=maintain, reason=skip` |
| 所有标准通过 | `pass` | 完全成功（适用 L1/L2/L3） |
| 部分标准通过 | `partial` | 部分成功（含 human_timeout 降级场景） |
| 所有标准失败 | `fail` | 完全失败（适用 L3，Harold 介入仍失败） |
| human_review 超时未响应 | `partial` | `human_review.status = timed_out`，verdict 强制降为 `partial` |

### 4.3 human_review 处理

当 `review_level` 为 **L3** 时（Harold 必须介入）：
- 自动设置 `cycle_unit.plan.human_approval_required = true`
- 自动设置 `cycle_unit.check.human_review.required = true`
- 发送飞书通知到 Harold，记录 `feishu_message_id`（防止重复发送）
- 启动 `review_window` 计时器（默认 **24h**，可在 task-card 中通过 `review_window_hours` 字段覆盖）
- 超时处理流程：`pending → escalated → timed_out → verdict = partial`
- escalate 触发后，`plan.time_horizon_cycles` 从 `escalated_at` 开始计

> **L2 抽中情形**：银月触发抽样后，动态将该 Deliverable 的 `human_review.required` 置为 `true`，**不在 Plan 阶段预设**。

---

## 五、adjust_automation_level() 接口规范

### 5.1 触发条件

> **级别方向说明**：数字越大（L3）= 人工介入越多 = 自动化程度越低；数字越小（L0）= 自动化程度越高。
> **升级** = 自动化程度提高 = 级别数字减小（如 L2→L1）。
> **降级** = 自动化程度降低 = 级别数字增大（如 L1→L2）。

| verdict | 当前级别 | 调整动作 | 触发条件 |
|---------|----------|----------|----------|
| `pass` | L1-L3 | 升级（数字减小） | 连续 3 次 pass |
| `partial` | L0-L3 | 维持 | 每次触发，需人工判断是否干预 |
| `fail` | L1-L3 | 降级（数字增大） | 连续 2 次 fail |
| `skip` | L0 | 维持 | `consecutive_count` 不变；`act.adjustments` 写入 `type=maintain, reason=skip` |

> **L2→L3 升降级保护**：
> - **升级到 L3**（L2→L3 pass 连续 ≥3）：L3 为全量人工，须 Harold 确认方可生效，`adjustment_applied = false` 直至确认
> - **L0 边界**：L0 已是免审底线，不可再升级（数字不能小于 0）；`pass` 在 L0 时 `consecutive_count` 累积但不触发升级

### 5.2 输入参数

```json
{
  "task_id": "NUC-01-TP01-T01",
  "agent_id": "cqo",
  "current_level": "L2",
  "verdict": "pass|partial|fail|skip",
  "consecutive_count": {
    "success": 3,
    "failure": 0
  },
  "dl_hit_rate": 0.85
}
```

### 5.3 输出格式

```json
{
  "previous_level": "L2",
  "new_level": "L1",
  "adjustment_reason": "连续 3 次 pass，满足升级条件（L2→L1，自动化程度提高）",
  "adjustment_applied": true,
  "rationale": [
    {
      "factor": "consecutive_success",
      "value": 3,
      "rule": ">=3 → 可升级"
    }
  ]
}
```

> **`adjustment_applied`**：若因 L2→L3 保护或边界约束未实际执行调整，此字段为 `false`，并在 `adjustment_reason` 中说明原因。

### 5.4 调整约束

- **逐级调整**：只能单步（如 L2→L1 或 L1→L2），不能跨级
- **边界**：L0 不能升级（已是免审底线）；L3 不能降级（已是全量人工上限）
- **L2→L3 升级保护**：须 Harold 人工确认后方可执行（升到全量人工是重大决策）
- **历史记录**：所有调整（含 `adjustment_applied=false`）必须记录到 `automation-levels.yaml`
- **级别扩展**：如需新增级别，须走治理流程，同步修改 protocol、task-card 模板、automation-levels.yaml 三处

---

## 六、LESSON-LEARN 四问法集成

### 6.1 触发时机

- **触发点**：Task 完成并关闭时（`verdict != null` 且 `cycle_unit.act.next_cycle_id = null`）
- **前置条件**：Task 生命周期结束；task-card §十 知识沉淀未填写
- **执行顺序**：Act 阶段完成后立即执行

### 6.2 四问法内容

1. **What worked well?**（什么做得好？）
   - 提取成功经验，形成 DL 条目草稿，填入 task-card §十

2. **What didn't work?**（什么没做好？）
   - 识别问题根因，形成 LL 条目

3. **What would you do differently?**（下次会怎么做？）
   - 生成改进建议，评估是否更新 TMPL-TASK-CARD

4. **What knowledge should be shared?**（什么知识需要分享？）
   - 提炼可复用知识，更新 MEMORY.md

### 6.3 输出处理

- **DL 条目**：写入 `knowledge/DL-YYYY-MM-DD.md`，同步 HAROLD-DECISION-LIBRARY
- **LL 条目**：写入 `knowledge/LL-YYYY-MM-DD.md`
- **模板更新**：如需修改 `TMPL-*`，提交治理流程
- **知识沉淀核查**：银月在 Heartbeat Step 3 中核查 task-card §十 是否填写；**未完成知识沉淀的 Task 不视为真正关闭**

---

## 七、与现有系统的集成

### 7.1 governance-delegation 集成

- **L0-L3 定义**：以 TMPL-TASK-CARD §五 为唯一真相源；governance-delegation 如有不一致以本协议 §3.5 为准
- **determine_review()**：从 task-card 直接读取级别，不调用 governance-delegation 判级逻辑（来源已在 task-card 明确声明）
- **adjust_automation_level()**：输出写入 cycle_unit.act.adjustments，并更新 automation-levels.yaml

### 7.2 cycle_unit 字段映射

> v1.3：check_reference 已从 cycle_unit 移除，cycle_unit 只做状态跟踪（见 cycle_unit.schema v1.3-fixed）。

| 协议字段 | cycle_unit 路径 | 说明 |
|----------|----------------|------|
| `task_card_ref.task_id` | `cycle_unit.task_card_id` | 绑定唯一真相源，所有定义从 task-card 读取 |
| `verdict` | `cycle_unit.check.verdict` | Check 阶段运行时写入 |
| `criteria_results` | `cycle_unit.check.criteria_results[]` | 逐项核对结果，运行时写入 |
| `evidence` | `cycle_unit.check.evidence[]` | 验收证据引用，运行时写入 |
| `human_review.*` | `cycle_unit.check.human_review.*` | 人工审批状态追踪（L3 必有；L2 抽中时动态设置） |
| `adjustments` | `cycle_unit.act.adjustments[]` | adjust_automation_level() 写入 |
| `lesson_learn_ref` | `cycle_unit.act.lesson_learn_ref` | 对应 task-card §十，未填不算关闭 |

### 7.3 task-card 字段映射

> determine_review() 的读取来源清单。

| 协议字段 | task-card 位置 | 说明 |
|----------|---------------|------|
| `review_level` | §一 Review 级别 | 任务级别声明，默认 **L3**（全量人工） |
| `delegation_ref` | §一 `DA-[编号]` | 授权依据编号，可将级别从 L3 下调 |
| `acceptance_criteria[]` | §五 验收标准列 | 每个 Deliverable 的验收标准 |
| `reviewer` | 由 §3.5 从 review_level 推导，不单独存储 | — |
| `review_window_hours` | §一（可选覆盖字段） | 覆盖默认 24h review_window |

### 7.4 错误处理

| 错误场景 | 处理策略 |
|---|---|
| `acceptance_criteria` 为空列表 `[]` | 等同缺失，触发默认值（L2 + `yin-yue`） |
| `review_level` 字段缺失或无效 | 降级到 L2，记录告警，继续执行 |
| task-card 不存在或无法读取 | 阻断 Plan，标记 `[?]`，等待 Harold 决策 |
| 接口调用失败 | 保持当前级别，记录错误日志 |
| L2→L3 升级未获 Harold 确认 | `adjustment_applied=false`，维持 L2，记录待确认状态 |

---

## 八、DoD Checklist

- [ ] `pdca-check-protocol.md` 完整描述 Plan / Check / Act 三阶段中 Check 机制的调用时机和接口
- [ ] L0-L3 级别定义与 TMPL-TASK-CARD §五 完全对齐（L0=免审，L3=全量人工）
- [ ] `determine_review()` 明确从 task-card §一 + §五 读取，不写入 cycle_unit，有完整输入/输出定义
- [ ] `determine_review()` 包含 `parent_review_level` 参数及子环约束逻辑（`parent_constraint_applied` 字段）
- [ ] `adjust_automation_level()` 完整输入/输出接口签名已定义（含 `adjustment_applied` 字段）
- [ ] 级别方向已明确注释：L0=自动化最高，L3=人工介入最多；升级=数字减小，降级=数字增大
- [ ] `verdict=skip` 触发条件已更正为 L0（免审），不再是旧版 L3
- [ ] `verdict=skip` 时 Act 行为已明确：必须调用、`consecutive_count` 不变、写入 `type=maintain` 记录
- [ ] `human_approval_required` 规则已更正：L3 必须为 true，L0/L1/L2 为 false（L2 抽中时动态触发）
- [ ] L2→L3 升级须 Harold 人工确认，`adjustment_applied=false` 直至确认
- [ ] L2 reviewer 规则已定义：银月抽样 → 抽中则 Harold 审阅，执行记录更新不改 review_context
- [ ] `acceptance_criteria` 空列表处理规则已定义（默认 L2 + `yin-yue`）
- [ ] `review_window` 默认值已定义（24h），可由 task-card `review_window_hours` 覆盖
- [ ] 级别扩展须走治理流程，同步三处（protocol / task-card 模板 / automation-levels.yaml）
- [ ] cycle_unit 字段映射（§7.2）已更新：check_reference 移除，改为 task_card_id 引用
- [ ] task-card 字段映射（§7.3）已确认 determine_review() 读取来源
- [ ] 文档经 Harold 确认，签字存档

---

## 九、版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-04-05 | 基于 ARCH v1.4.2 + governance-delegation SKILL v1.2.0 初始版本 |
| v1.1 | 2026-04-05 | 补全 P0 评审问题：parent_review_level、adjust 接口签名、skip 行为、L2 reviewer 映射、DoD 扩展 |
| v1.2 | 2026-04-05 | 数据来源重构：check_reference 从 cycle_unit 移除；determine_review() 改为读取 task-card；§7.2/§7.3 拆分重写 |
| **v1.3** | **2026-04-05** | **级别定义对齐 TMPL-TASK-CARD §五：L0=免审，L3=全量人工（Harold 必须介入）；skip 触发条件改为 L0；human_approval_required 规则更正；升降级方向重新注释；L2→L3 升级保护替换旧版 L1→L0 保护；子环约束方向修正（§3.2 + §3.7）** |

---

*v1.3 · 2026-04-05 · 依据 ARCH v1.4.2 · TMPL-TASK-CARD v1.2 §五 · cycle_unit.schema v1.3-fixed*
