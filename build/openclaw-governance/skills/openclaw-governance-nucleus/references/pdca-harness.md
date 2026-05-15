# PDCA Harness — Detailed Reference

> Moved from nucleus SKILL.md §四, §六 to reduce main file size.

## §四 Harness 执行协议

> **核心目标**：驱动 LLM 对每个 task 持续 PDCA 迭代，直到 verdict=pass 且验收标准全部满足。
> **分工原则**：Python (scripts/pdca.py) 只做状态记录；LLM 负责所有推断、执行、判断。
> **持久性原则**：所有状态存于 pdca/{task_id}.yaml，每次 heartbeat 从文件重建上下文。

### 两条触发路径

| 路径 | 触发时机 | 适用场景 |
|------|---------|---------|
| **A（直接入口）** | dispatch 创建 task-card 后，同会话立即执行 | 紧急/高优先级任务 |
| **B（heartbeat 入口）** | heartbeat 定时触发 Step 3a | 常规任务、后台推进 |

### heartbeat 完整执行序列

```
前置: scheduler_state.py bump → check → pdca.py aggregate
Step 0: pdca.py pending → 处理 Harold 回复（A/B/C/D 解析）
Step 1: 选最高优先级 [P] 或 [V] 任务
Step 2: pdca.py status → 读取历史 PDCA 状态
Step 3-6: 完整 P→D→C→A 循环
```

### 单轮 PDCA 协议

#### Step 3 — Plan (P)
```bash
python scripts/pdca.py p --task-card-id {id} \
  --summary "本轮目标：{具体改进点}；上次失败原因：{根因}；本次调整：{调整方案}" \
  [--criteria "标准1|标准2|标准3"] [--task-card-path PATH] \
  [--topic-id T06] [--project-id ZT-P015]
```

**Harness 规则**：
- **P1**：Plan summary 必须说明「本轮相比上次做了什么不同」
- **P2（条件强制）**：上轮 partial + Harold 条件 → Plan 必须逐条回应，否则 Check 自动 fail
- **P3**：`--task-card-path` 首次传入后持久化，跨 cycle 自动携带
- **P4**：`--topic-id` 和 `--project-id` 首次传入后持久化，a() 后自动 aggregate

#### Step 4 — Do (D)
```bash
python scripts/pdca.py d --task-card-id {id} \
  --summary "完成内容：{具体做了什么}；交付物：{文件/状态变更}" \
  --status completed|blocked|partial [--blocker "阻塞原因"]
```

**D1**：Do summary 必须描述**实际变化**
**D2**：`--status completed` 后 phase 变为 `cqo_review`（非 `do`）；blocked/partial 保持 `do`

#### Step 4.5 — CQO Review (CQO 合规闸门)
```bash
python scripts/pdca.py cqo-review --task-card-id {id} \
  --result pass|revise|reject \
  [--report-path PATH] \
  [--issues "CQO-01|CQO-02"]
```

**CQO 审核项** (CQO-01~05)：
| 编号 | 审核项 | 说明 |
|------|--------|------|
| CQO-01 | 模板合规 | 是否使用规定模板 |
| CQO-02 | 元数据完整性 | frontmatter 必填字段 |
| CQO-03 | 路径合规 | 文件存放位置 |
| CQO-04 | 内容完整性 | 章节/字段齐备 |
| CQO-05 | 引用一致性 | 交叉引用有效 |

**结果处理**：
| result | phase 变化 | 说明 |
|--------|-----------|------|
| `pass` | → `check` | 进入 Check 阶段 |
| `revise` | → `do`（同 cycle） | revise_count +1，需修改后重新 Do |
| `reject` | → `do`（同 cycle） | revise_count +1，通知银月，需重做 |

**CQO 规则**：
- **CQO-REVISE-LIMIT**：连续 revise 超过 3 次自动升级为 reject
- **CQO-REPORT**：result=pass 时应提供 `--report-path` 指向合规报告
- **CQO-BACKWARD**：跳过 cqo-review 直接调用 c() 仍可工作（向后兼容）

#### Step 5 — Check (C)

| 级别 | LLM 动作 | pdca.py 调用 | review_deliverable() |
|------|---------|-------------|----------------------|
| **L0** | 自动通过 | `c --verdict pass --level L0` | 不触发 |
| **L1** | LLM 逐项自查 | `c --verdict pass\|fail --level L1` | 不触发 |
| **L2** | 银月抽检 20-30% | `c --verdict pass\|pending --level L2` | 抽中时触发 |
| **L3** | Harold 全量审批 (A/B/C/D) | `c --verdict pending --level L3` | 触发，7 天逾期升级 |

```bash
python scripts/pdca.py c --task-card-id {id} \
  --verdict pass|partial|fail|skip|pending \
  --level L0|L1|L2|L3 [--evidence "证据1|证据2"]
```

**C1**：verdict=fail 时 evidence 必须说明哪条标准失败、具体表现
**C2**：L3 pending is_overdue=true → heartbeat Step 0 升级到 MISSION_BOARD `[!]`

**审计出口**（L0/L1 pass 后）：
- `c --verdict pass --level L0|L1` → audit_eligible=true
- `pdca.py audit-queue` → 获取待审计队列
- `pdca.py mark-audit --score {0-100}` → 写回审计结果
- 评分 < 80 → create_lesson_learned 质疑对应 DL

#### Step 6 — Act (A)

| verdict | Act 行动 | Task-CARD 状态 | MISSION_BOARD |
|---------|---------|--------------|--------------|
| **pass** | 更新 task-card §三；`--next-task` 指向下一任务 | `[x]` | 标记完成 |
| **partial** | 记录已完成/未完成项 | `[P]` | 更新进度 |
| **fail** | 记录根因分析 | `[P]` | 更新进度 |
| **skip** | 无需操作 | `[P]` | 保持 |
| **pending** | 跳过，等 Step 0 回填 | `[V]` | 保持 |

```bash
python scripts/pdca.py a --task-card-id {id} \
  --summary "根因/结论：{...}；下次调整：{...}" \
  [--next-task {下一任务ID}] [--lessons "经验1|经验2"]
```

**Harness 规则**：
- **A1**：Act summary 必须包含「下次 Plan 的输入」
- **A2（写穿透）**：a() 完成后必须立即更新 Task-CARD + MISSION_BOARD
- **A3（自动聚合）**：a() 完成后自动调用 aggregate()
- **A4（知识沉淀）**：verdict=fail 时强制沉淀

### 持续迭代规则

**完成条件**：verdict=pass + task-card §五所有验收标准满足 + task-card §三状态更新 + MISSION_BOARD 标记完成

**迭代加速**：
- 连续 3 次 fail → Act 上报 MISSION_BOARD「需要 Harold 介入」
- 连续 partial 但有进展 → 正常继续
- 不允许连续 2 次 Do 内容完全相同（blocked 除外）

### 特殊情况

| 情况 | 处理 |
|------|------|
| 任务 blocked | Do: `--status blocked`；Check: `--verdict fail` |
| 阻塞冷却（连续 3 次 blocked） | 标记 pdca_paused: true，移出候选队列，MISSION_BOARD `[~]` |
| L3 pending 审批 | feishu_post 通知 Harold；下次 Step 0 检查回填 |
| 连续 3 次 fail | Act 写明「需要 Harold 介入」，MISSION_BOARD `[!]` |

## §六 CLI 参考

### pdca.py
```bash
python scripts/pdca.py p   --task-card-id {id} --summary "..." [--criteria "a|b"] [--task-card-path PATH] [--dl-refs "DL-1|DL-2"] [--topic-id T06] [--project-id ZT-P015]
python scripts/pdca.py d   --task-card-id {id} --summary "..." --status completed|blocked|partial [--blocker "..."]
python scripts/pdca.py cqo-review --task-card-id {id} --result pass|revise|reject [--report-path PATH] [--issues "CQO-01|CQO-02"]
python scripts/pdca.py c   --task-card-id {id} --verdict pass|partial|fail|skip|pending --level L0|L1|L2|L3 [--evidence "a|b"]
python scripts/pdca.py a   --task-card-id {id} --summary "..." [--next-task T1.2] [--lessons "a|b"]
python scripts/pdca.py status  --task-card-id {id}
python scripts/pdca.py history --task-card-id {id}
python scripts/pdca.py pending
python scripts/pdca.py audit-queue
python scripts/pdca.py mark-audit --task-card-id {id} --cycle-index N --score {0-100} [--issues "..."]
python scripts/pdca.py aggregate
python scripts/pdca.py check-concurrency [--scope topic --scope-id T06]
python scripts/pdca.py verify-integrity [--task-card-id {id}]
python scripts/pdca.py health-check
python scripts/pdca.py archive [--older-than-days N] [--dry-run]
```

### scheduler_state.py
```bash
python scripts/scheduler_state.py read     # 读取当前调度计数器
python scripts/scheduler_state.py bump     # 递增所有计数器
python scripts/scheduler_state.py check    # 返回应触发的 scope 列表
python scripts/scheduler_state.py reset task  # 重置 task 计数器
```

## §六 文件结构

```
scripts/
  pdca.py              ← PDCA 状态记录器 + aggregate + check_concurrency + verify/health/archive
  scheduler_state.py   ← 轻量多粒度调度计数器
pdca/
  {task_card_id}.yaml  ← 每个 task 的 PDCA 历史（自动创建，含 SHA-256 checksum）
  _state.yaml          ← 聚合状态（topic/project verdict 派生，含 mtime 缓存 + version）
  _archive/            ← 归档已完成且 >30 天的 PDCA 文件
config/
  pdca_config.yaml     ← 外部化配置（限制/超时/聚合参数）
docs/
  archive/
    nucleus-v1/        ← 旧系统归档
```
