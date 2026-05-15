# HEARTBEAT.md · ${AGENT_NAME} (${agent_id})

> **版本**：v2.0
> **更新**：${LAST_SYNC_DATE}
> **关联 Skill**：governance-heartbeat v7.0.0

---

## 核心定义

**Heartbeat = PDCA 执行入口。每次 heartbeat 推进一个 Task-CARD 完成一轮 PDCA。**

---

## Skills 加载（心跳时触发）

心跳执行时：先读取 `governance-heartbeat/SKILL.md`，再读取 `MISSION_BOARD.md`。

---

## PDCA 执行流程

```
Heartbeat 触发
    ↓
选取 Task-CARD（优先级：[!]/[V] follow-up > [?]阻塞 > [P]进行中 > [ ]待启动）
    ↓
Plan  — 判断当前状态，规划下一步
    │   └─ 复杂/战略性任务可能需要 Harold 审批方案
    ↓
Do    — 执行计划动作，产出可见输出物
    ↓
Check — 对照 DOD 验证，按 Review 级别决定是否需要人类 Review
    │   L0: 自验收 │ L1: 银月 │ L2: 抽样 Harold │ L3: Harold 全量
    │   LLM 可主动升级 Review 级别
    ↓
Act   — 更新 Task-CARD 状态 + MISSION_BOARD 派生刷新 + pdca.py 记录
    ↓
需要人类 Review？
  ├─ 否 → 完成
  └─ 是 → 标记 [V]，通知 Review 人，PDCA 暂停等待
```

**关键规则**：
- PDCA 不可跳步
- 每次 heartbeat 至少推进一个 Task，除非所有 Task 都在等 Review
- MISSION_BOARD §一 数字从各 section 计数派生，不可手写
- 人类在会话中直接推进任务，走同一个 PDCA 流程

---

## MISSION_BOARD 派生刷新

每次 PDCA Act 步骤必须重新计算 §一 状态总览：

| 指标 | 算法 |
|------|------|
| 活跃任务数 | §三 Task ID 数 |
| 待处理任务数 | §五 Task ID 数 |
| 阻塞任务数 | §二 Task ID 数 |
| 本周完成任务数 | §六 中 close_date 在本周（周一~周日）的 Task ID 数 |

**"本周"定义**：周一 00:00 ~ 周日 23:59。每周一首次 heartbeat 清零 §六。

---

## 汇报规则

| 汇报类型 | 时间 | 内容 |
|----------|------|------|
| **晨会报告** | 早 7:00 左右 | PDCA 进展、阻塞、今日计划 |
| **夕会报告** | 晚 9:00 左右 | 今日 PDCA 完成、明日计划 |
| **异常报告** | 实时 | PDCA 异常（连续 fail、阻塞升级等） |

### 静默执行

**非 7:00/21:00**：执行 PDCA → 刷新 MISSION_BOARD → 不发飞书消息（除非有异常或状态变更）

---

## 检查列表

- [ ] 选取了一个 Task-CARD
- [ ] 执行了一轮完整 PDCA
- [ ] MISSION_BOARD §一 派生刷新完成
- [ ] 需要人类 Review 的任务已通知

---

## 记录状态

`memory/heartbeat-state.json`

---

*Version: v2.0 - 2026-04-26 - 重构为 PDCA 执行器模型*
