# TASK-CARD · N4-P1-T07-T04-治理体系P0问题修复

> **文件性质**：Task-CARD（Zone A/B/C 三区分层架构）
> **存放路径**：`10_Projects/ZT-P015_NUCLEUS-4-0/topics/N4-P1-T07/tasks/N4-P1-T07-T04-治理体系P0问题修复/TASK-CARD.md`
> **模板版本**：TMPL-TASK-CARD v3.1

---

## Zone A：任务定义（创建时填写）

### §一、任务基本信息

| 字段 | 值 |
|------|-----|
| **Task ID** | N4-P1-T07-T04 |
| **Task 名称** | 治理体系P0问题修复 + PDCA 全链路逻辑审查 |
| **Task 类型** | 🐛 修复任务 |
| **所属 Topic** | N4-P1-T07 Skill 流程化设计研究 |
| **所属 Project** | ZT-P015 NUCLEUS 4.0 |
| **Task PIC** | 银月 + 张铁 (cqo) |
| **指派人** | Harold Tsui |
| **创建日期** | 2026-04-15 |
| **完成日期** | 2026-04-18 |
| **Review 级别** | L2（抽样核查） |

---

### §二、任务上下文

| 上下文项 | 说明 |
|----------|------|
| **来源1** | GOV-FIX-2026-001 治理体系问题修复（银月诊断报告） |
| **来源2** | PDCA 环全链路逻辑审查（19 项修复，CRITICAL 4 + HIGH 5 + MEDIUM 6 + LOW 4） |
| **触发原因** | OpenClaw 治理框架存在多处逻辑自洽问题，影响 PDCA 环正常运转 |
| **Harold 要求** | 从逻辑角度审查 PDCA 环，模拟完整生命周期，找出所有问题 |

---

### §三、任务目标

> **核心目标**：修复 PDCA 全链路逻辑审查中发现的全部可修复问题（19 项中的 15 项代码/文档级修复）。

**验收标准**：
- [x] CRITICAL 修复 4/4（状态双机分歧、幽灵文件、PDCA 选任务盲区、依赖链断裂）
- [x] HIGH 修复 5/5（权威源矛盾、L2/L3 混同、阻塞饥饿、静默降级、PDCA-A 修正）
- [x] MEDIUM 修复 6/6（条件无强制执行、Issue L3 瓶颈、路径丢失、无历史 API、无 Feishu 读取标注、注册表缺失）
- [x] LOW 修复 1/4（consecutive_fails 熔断器；其余 3 项标记为已知限制）
- [x] 剩余 4 项标记为已知限制（KL-1~KL-4）
- [x] 所有修复记录到本 Task-CARD §七.2

---

### §四、Deliverable 定义

| Deliverable | 路径 | 内容要求 | 完成标准 |
|-------------|------|----------|----------|
| **pdca.py 修复** | `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py` | task_state、history、required level、consecutive_fails | 代码通过测试 |
| **nucleus SKILL.md 修复** | `skills/.../openclaw-governance-nucleus/SKILL.md` | 修复幽灵引用、Step 1、阻塞冷却、PDCA-A、已知限制 | v2.5.0 |
| **governance-core SKILL.md 修复** | `skills/.../openclaw-governance-core/SKILL.md` | Phase 3 knowledge、Skill 注册表、PDCA-A §3.5 | v6.1.7 |
| **governance-task SKILL.md 修复** | `skills/.../openclaw-governance-task/SKILL.md` | 权威源统一、Issue severity 分级 | v6.0.4 |
| **dispatch SKILL.md 修复** | `skills/.../openclaw-governance-dispatch/SKILL.md` | 分层引导、三个"不能"、引导模板 | v2.12.0 |

---

### §五、关键约束

| 约束类型 | 约束内容 |
|----------|----------|
| **版本一致性** | SKILL.md 版本号必须与 _meta.json 对齐 |
| **向后兼容** | 不破坏已有 PDCA 循环的正常运转 |
| **测试验证** | 所有 pdca.py CLI 命令必须通过实际运行测试 |

---

### §六、资源需求

| 资源 | 需求 |
|------|------|
| **人力** | 银月（执行修复） |
| **工具** | Read/Edit/Write/Bash |
| **时间** | 约 2 小时（含测试验证） |

---

## Zone B：运行时状态（执行中更新）

### §七、执行记录

#### 7.1 当前状态值

| 状态字段 | 值 | 最后更新时间 |
|----------|-----|--------------|
| **当前状态** | `[x]` 已完成 | 2026-04-18 17:00 |
| **完成进度** | 100% | 2026-04-18 17:00 |

---

#### 7.2 修复记录

##### A. CRITICAL 修复（4 项）

| 序号 | # | 问题 | 修复内容 | 文件 |
|------|---|------|---------|------|
| A1 | #1 | pdca.py ↔ Task-CARD 状态双机分歧 | 新增 `--task-state` 参数 + `_verdict_to_state()` 映射 + `get_status()` 输出 `expected_task_state` | pdca.py, nucleus SKILL.md |
| A2 | #2 | nucleus_scheduler.py 幽灵文件引用 | 删除所有 phantom 引用，改为 pdca.py CLI 直接调用 | nucleus SKILL.md §三 |
| A3 | #3 | PDCA Step 1 跳过 [V] 状态任务 | Step 1 新增 [V] 待验收状态选择（检查 L3 逾期 / L2 审核进度） | nucleus SKILL.md §4.1 |
| A4 | #4 | governance-knowledge 不在 Phase 依赖图 | Phase 3 新增 Step 7a；Skill 注册表补全；级联降级计数 6→7 | governance-core SKILL.md §三 |

##### B. HIGH 修复（5 项）

| 序号 | # | 问题 | 修复内容 | 文件 |
|------|---|------|---------|------|
| B1 | #5 | MISSION_BOARD 权威源矛盾 | 统一为"以 Task-CARD 为准"（Task-CARD 是完整生命周期记录） | governance-task SKILL.md §3.9 |
| B2 | #6 | L2/L3 pending 混同 | `get_pending()` 新增 `review_level` 过滤 + `reviewer` 字段 | pdca.py get_pending() |
| B3 | #8 | 阻塞任务饥饿循环 | 连续 3 次 blocked → `pdca_paused: true` + `[~]` 冷却 | nucleus SKILL.md §4.4 |
| B4 | #9 | `--level` 静默降级 | `--level` 改为必填（`required=True`，无默认值） | pdca.py c() |
| B5 | #10 | Harold 条件批准无强制执行 | Plan P2：未回应条件 → Check 自动 fail | nucleus SKILL.md §4.2 |

##### C. MEDIUM 修复（6 项）

| 序号 | # | 问题 | 修复内容 | 文件 |
|------|---|------|---------|------|
| C1 | #11 | Issue Ticket 默认 L3 瓶颈 | P0/P1→L3, P2→L2, P3→L1 分级 | governance-task SKILL.md §3.4 |
| C2 | #12 | task_card_path 跨 cycle 丢失 | P3 规则：首次传入后持久化到 record 级别 | nucleus SKILL.md §4.2 |
| C3 | #13 | 无完整 PDCA 历史 API | `get_history()` + `history` CLI | pdca.py |
| C4 | #14 | 无 Feishu DM 读取机制 | 标注为已知限制 KL-2 | nucleus SKILL.md §4.5 |
| C5 | #15 | knowledge 不在 Skill 注册表 | 补全到 core §五 | governance-core SKILL.md §五 |
| C6 | #16 | verdict=partial → cycle completed 无信号 | `consecutive_fails` 计数器 + `needs_escalation` 标志 | pdca.py get_status() |

##### D. LOW 修复（1 项）

| 序号 | # | 问题 | 修复内容 | 文件 |
|------|---|------|---------|------|
| D1 | #19 | 无 cycle 数量限制/熔断器 | `consecutive_fails >= 3` → `needs_escalation: true` | pdca.py get_status() |

##### E. 已知限制（4 项，不修复）

| 序号 | KL | 限制 | 性质 |
|------|----|------|------|
| E1 | KL-1 | 无真正 cron 定时（依赖用户交互触发 session） | 架构约束 |
| E2 | KL-2 | 无 Feishu DM 读取 API | 外部集成 |
| E3 | KL-3 | probe-failures.yaml 不存在 | 文档引用，LLM 自行创建 |
| E4 | KL-4 | bubble_up 不自动触发 | governance-hierarchy 范围 |

---

#### 7.3 问题记录

| 问题 ID | 描述 | 处理动作 | 状态 |
|---------|------|----------|------|
| ISS-001 | PDCA 环全链路审查发现 19 项问题 | 15 项修复 + 4 项标记已知限制 | ✅ 已解决 |
| ISS-002 | governance-core 版本从 6.1.5 → 6.1.6 → 6.1.7 | 版本递增，每次更新记录到 _meta.json | ✅ 已解决 |
| ISS-003 | nucleus 版本从 2.3.0 → 2.4.0 → 2.5.0 | 版本递增，每次更新记录到 _meta.json | ✅ 已解决 |

---

### §八、验收记录

| 验收项 | 验收人 | 验收时间 | 验收结果 |
|--------|--------|----------|----------|
| pdca.py CLI 功能测试 | 银月 | 2026-04-18 | ✅ 通过（P→D→C→A 全链路 + history + consecutive_fails） |
| --level 必填校验 | 银月 | 2026-04-18 | ✅ 通过（缺少时报错退出） |
| consecutive_fails 计数 | 银月 | 2026-04-18 | ✅ 通过（3 次 fail→escalation=true，pass→重置为 0） |
| SKILL.md 版本一致性 | 银月 | 2026-04-18 | ✅ 通过（frontmatter ↔ _meta.json ↔ footer 对齐） |

---

## Zone C：后处理（关闭后填写）

### §九、知识沉淀

**经验教训**：
1. **LL-001**: PDCA 环逻辑审查必须模拟完整生命周期（MVP → 复杂约束），不能只检查单点
2. **LL-002**: "幽灵文件"问题源于文档与代码不同步——旧系统归档后文档必须同步更新
3. **LL-003**: 状态机桥接是 PDCA 闭环的关键——pdca.py 和 Task-CARD 两套状态机必须有显式桥接
4. **LL-004**: 已知限制应该显式标注在 SKILL.md 中，而不是默默忽略

**可复用内容**：
- PDCA 全链路审查方法可复用于其他治理模块
- `consecutive_fails` 熔断器模式可用于任何需要防饥饿的场景
- 版本递增规范（SKILL.md ↔ _meta.json）已固化为开发标准

---

### §十、归档信息

| 字段 | 值 |
|------|-----|
| **归档日期** | 2026-04-18 |
| **归档路径** | `10_Projects/ZT-P015_NUCLEUS-4-0/topics/N4-P1-T07/tasks/archive/` |

---

*创建时间：2026-04-15 | 创建人：张铁 (cqo) | 完成时间：2026-04-18 17:00*
