# Review Request Protocol (Human-in-the-Loop) — Detailed Reference

> Moved from delegation SKILL.md §十 to reduce main file size.

## 10.1 Trigger Conditions

| Trigger | Condition |
|---------|-----------|
| PDCA Check phase | `review_level=L3` (Harold full review) |
| PDCA Check phase | `review_level=L2` and sampled (20-30%) |
| Heartbeat Step 0 | `pdca.py pending` returns non-empty |

## 10.2 Review Request Format (Feishu Message)

```
📋 Review 请求 · {task_card_id} · {review_level}

**任务**: {task_card_title}
**执行摘要**: {do_summary}

**验收标准逐项自查**:
  ✅ 1. {criterion_1}  — {self_assessment_1}
  ✅ 2. {criterion_2}  — {self_assessment_2}
  ❓ 3. {criterion_3}  — 不确定，需 Harold 判断：{specific_question}

**相关历史决策**（来自 DL）:
  - {dl_id}: "{dl_decision}" (相关度 {relevance}%)
  （无相关历史 → 此节省略）

**需要 Harold 决策的点**:
  1. {specific_decision_point_1}
  2. {specific_decision_point_2}（如无则省略）

---
请从下方选择决策（**回复字母即可快速答复**，也支持全文格式）:

  **A. 批准** — 验收标准全部满足，本轮 PDCA 关闭
  **B. 条件批准** — 核心逻辑可接受，补充条件：[请填写]
  **C. 拒绝 / 返工** — 不通过，原因：[请填写]
  **D. 需更多信息** — 问题：[请填写]（等待补充后重新提交）

或使用全文格式:
  决策: 批准 / 条件批准 / 拒绝
  原因: ...
  条件: ...（条件批准时填写）
  新原则: ...（如本次决策形成新规律，可选填）
```

**Delivery**: `feishu_post` to Harold DM.
**Validity**: 7 calendar days (after which heartbeat Step 0 auto-escalates to MISSION_BOARD `[!]`).

## 10.3 Harold Reply Format

```
决策: 批准
原因: 验收标准3的实现方式可接受，符合ZT-2026-007路径规范
条件: （无）
新原则: 此类路径校验任务，LLM自查通过即可，无需全量Review → 下次Review级别可降至L1
```

## 10.4 Reply Parsing Rules

| Harold Reply | Maps to pdca.py | Follow-up |
|-------------|-----------------|-----------|
| **A** / 决策: 批准 | `c --verdict pass` | Execute Act |
| **B** + conditions / 决策: 条件批准 | `c --verdict partial` | Conditions written; Act; next Plan references conditions |
| **C** + reason / 决策: 拒绝 | `c --verdict fail` | Reason in evidence; Act; next Plan must cite rejection reason |
| **D** + question / 需更多信息 | Keep `verdict=pending`; LLM supplements info and resends | — |
| *(>7 days no reply)* | heartbeat Step 0 marks `is_overdue=true`; MISSION_BOARD `[!]` | Notify Harold of overdue Review |

## 10.5 Knowledge Persistence Rules

| Harold Decision | Has "新原则" | Action |
|-----------------|-------------|--------|
| Approved | Yes | `governance-knowledge.update_dl()`: write new principle to decision library |
| Approved | No | No extra action |
| Conditionally approved | Yes/No | `governance-knowledge.update_dl()`: record conditions and applicable scenarios |
| Rejected | Yes/No | `governance-knowledge.create_lesson_learned()`: record failure reason, affected criteria, improvement suggestions |

## 10.6 Knowledge Pre-loading (Plan Phase)

**Trigger**: Heartbeat Step 2 (after reading task-card, before `pdca.py p`)

```
Step 2.5 — Knowledge Pre-loading
    governance-knowledge.enhance_knowledge(
        task_id="{task_card_id}",
        keywords=[extracted from task-card title + acceptance criteria]
    )
    → Returns: related DL entries, related LL entries
    → LLM uses results as constraint input for this round's Plan
    →特别注意: LL entries with type=failure = paths to avoid repeating
```

## 10.7 Automation Level Linkage

| Pattern | Trigger | Action |
|---------|---------|--------|
| Continuous approval | Same task type approved 3x (no conditions) | `determine_automation_level()` evaluates upgrade (L3 → L2); Harold confirms |
| LL rejection | Harold rejects + generates LL entry | `determine_automation_level()` evaluates downgrade; notify Harold immediately |
| New principle produced | Harold fills "新原则" field | `update_dl()` + mark DL's impact on `determine_review()` |
