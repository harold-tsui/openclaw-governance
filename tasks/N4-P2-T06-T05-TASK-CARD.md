# TASK-CARD · N4-P2-T06-T05

> **文件性质**：执行记录文件（唯一真相源）
> **Task ID**：N4-P2-T06-T05
> **Topic ID** | N4-P2-T06
> **Project ID** | ZT-P015
> **唯一真相源** | 本文件

---

## §一、项目上下文

| 字段 | 值 |
|------|-----|
| **Task ID** | N4-P2-T06-T05 |
| **Task 名称** | Governance Skills 改进计划 |
| **Topic ID** | N4-P2-T06（通过 BotLearn 优化 OpenClaw Governance） |
| **Project ID** | ZT-P015（NUCLEUS 4.0） |
| **Task PIC** | 张铁 (CQO) |
| **优先级** | P1 |
| **Review 级别** | L2（银月审批） |
| **Workspace** | `/Users/haroldtsui/Workspaces/openclaw/main` |
| **完整路径** | `10_Projects/ZT-P015_NUCLEUS-4-0/tasks/N4-P2-T06-T05-TASK-CARD.md` |

---

## §二、Task 定义

### 2.1 执行目标

基于 T6.2（Skills 自评估）和 T6.4（BotLearn 推荐），制定 Governance Skills 改进计划。

### 2.2 成功标准

- [ ] 制定 P0 改进方案（三层记忆系统 + 自动巡检机制）
- [ ] 制定 P1 改进方案（外部 AI 评审集成）
- [ ] 制定 P2 改进方案（截图审核 + 冲突检测）
- [ ] 确定时间安排和资源需求

### 2.3 执行约束

- **时间约束**：立即开始，60 分钟内完成
- **质量约束**：方案必须有明确的实施步骤和验证方法
- **依赖**：T6.1 + T6.2 + T6.4 完成

---

## §三、改进方案汇总

### 3.1 P0 改进方案（立即执行）

#### 方案 A：三层记忆系统

**目标**：解决 memory 维度短板（缺少历史追溯）

**涉及 Skills**：
- governance-config（memory=3）
- governance-data（memory=3）
- governance-evolution（memory=3）
- governance-dispatch（memory=3）
- governance-delegation（memory=3）

**BotLearn 推荐**：`ktpriyatham/triple-memory`

**实施步骤**：

| Step | 任务 | 负责人 | 周期 | 交付物 |
|------|------|--------|------|--------|
| **A.1** | 研究 triple-memory Skill 架构 | 张铁 | 1 天 | 记忆架构分析文档 |
| **A.2** | 设计 Governance 记忆系统集成方案 | 张铁 | 2 天 | 集成方案设计文档 |
| **A.3** | 实现 config/data 记忆模块 | 张铁 | 3 天 | 记忆模块代码 |
| **A.4** | 实现 evolution/dispatch/delegation 记忆模块 | 张铁 | 3 天 | 记忆模块代码 |
| **A.5** | 验证记忆系统效果 | 张铁 | 1 天 | 验证报告 |

**总计周期**：10 天

#### 方案 B：自动巡检机制

**目标**：解决 autonomy 维度短板（完全被动）

**涉及 Skills**：
- governance-config（autonomy=2）
- governance-data（autonomy=2）
- governance-evolution（autonomy=2）
- governance-task（autonomy=3）
- governance-quality（autonomy=3）

**实施步骤**：

| Step | 任务 | 负责人 | 周期 | 交付物 |
|------|------|--------|------|--------|
| **B.1** | 设计 heartbeat 集成机制 | 张铁 | 1 天 | 集成机制设计文档 |
| **B.2** | 实现 config 自动巡检 | 张铁 | 2 天 | 自动巡检代码 |
| **B.3** | 实现 data 自动巡检 | 张铁 | 2 天 | 自动巡检代码 |
| **B.4** | 实现 evolution 自动巡检 | 张铁 | 2 天 | 自动巡检代码 |
| **B.5** | 验证自动巡检效果 | 张铁 | 1 天 | 验证报告 |

**总计周期**：8 天

---

### 3.2 P1 改进方案（短期执行）

#### 方案 C：外部 AI 评审集成

**目标**：增强 quality/evolution Skills 的外部评审能力

**涉及 Skills**：
- governance-quality
- governance-evolution

**已安装 Skill**：`browser` v2.0.2

**实施步骤**：

| Step | 任务 | 负责人 | 周期 | 交付物 |
|------|------|--------|------|--------|
| **C.1** | 配置 sider.ai 外部评审流程 | 张铁 | 1 天 | sider.ai 配置文档 |
| **C.2** | 实现 quality 外部评审触发 | 张铁 | 2 天 | 外部评审触发代码 |
| **C.3** | 实现 evolution 外部对齐触发 | 张铁 | 2 天 | 外部对齐触发代码 |
| **C.4** | 验证外部评审效果 | 张铁 | 1 天 | 验证报告 |

**总计周期**：6 天

---

### 3.3 P2 改进方案（长期执行）

#### 方案 D：UI 截图审核

**目标**：增强 quality/heartbeat Skills 的可视化能力

**涉及 Skills**：
- governance-quality
- governance-heartbeat

**已安装 Skill**：`steipete/peekaboo` v1.0.0

**实施步骤**：

| Step | 任务 | 负责人 | 周期 | 交付物 |
|------|------|--------|------|--------|
| **D.1** | 研究 peekaboo Skill API | 张铁 | 1 天 | peekaboo API 分析文档 |
| **D.2** | 实现 quality 截图审核 | 张铁 | 2 天 | 截图审核代码 |
| **D.3** | 实现 heartbeat 状态可视化 | 张铁 | 2 天 | 状态可视化代码 |
| **D.4** | 验证截图审核效果 | 张铁 | 1 天 | 验证报告 |

**总计周期**：6 天

#### 方案 E：冲突检测机制

**目标**：解决 guard 维度短板（跨 Agent/Phase 冲突检测）

**涉及 Skills**：
- governance-heartbeat（guard=4）
- governance-nucleus（guard=4）

**实施步骤**：

| Step | 任务 | 负责人 | 周期 | 交付物 |
|------|------|--------|------|--------|
| **E.1** | 设计跨 Agent 冲突检测规则 | 张铁 | 1 天 | 冲突检测规则文档 |
| **E.2** | 设计跨 Phase 冲突检测规则 | 张铁 | 1 天 | 冲突检测规则文档 |
| **E.3** | 实现 heartbeat 冲突检测 | 张铁 | 2 天 | 冲突检测代码 |
| **E.4** | 实现 nucleus 冲突检测 | 张铁 | 2 天 | 冲突检测代码 |
| **E.5** | 验证冲突检测效果 | 张铁 | 1 天 | 验证报告 |

**总计周期**：7 天

---

## §四、时间安排

### 4.1 总体时间线（Gantt 图）

```
Week 1-2 (P0):
  ├─ Day 1-10: 方案 A（三层记忆系统）
  │   ├─ Day 1: A.1 研究 triple-memory 架构
  │   ├─ Day 2-3: A.2 设计集成方案
  │   ├─ Day 4-6: A.3 实现 config/data 记忆模块
  │   ├─ Day 7-9: A.4 实现 evolution/dispatch/delegation 记忆模块
  │   └─ Day 10: A.5 验证记忆系统效果
  │
  └─ Day 1-8: 方案 B（自动巡检机制）- 并行执行
      ├─ Day 1: B.1 设计 heartbeat 集成机制
      ├─ Day 2-3: B.2 实现 config 自动巡检
      ├─ Day 4-5: B.3 实现 data 自动巡检
      ├─ Day 6-7: B.4 实现 evolution 自动巡检
      └─ Day 8: B.5 验证自动巡检效果

Week 3-4 (P1):
  └─ Day 1-6: 方案 C（外部 AI 评审集成）
      ├─ Day 1: C.1 配置 sider.ai 外部评审流程
      ├─ Day 2-3: C.2 实现 quality 外部评审触发
      ├─ Day 4-5: C.3 实现 evolution 外部对齐触发
      └─ Day 6: C.4 验证外部评审效果

Week 5-6 (P2):
  ├─ Day 1-6: 方案 D（UI 截图审核）- 并行执行
  │
  └─ Day 1-7: 方案 E（冲突检测机制）- 并行执行
```

### 4.2 总周期估算

| 方案 | 周期 | 优先级 | 并行可能性 |
|------|------|--------|-----------|
| **方案 A** | 10 天 | P0 | ✅ 可与方案 B 并行 |
| **方案 B** | 8 天 | P0 | ✅ 可与方案 A 并行 |
| **方案 C** | 6 天 | P1 | - |
| **方案 D** | 6 天 | P2 | ✅ 可与方案 E 并行 |
| **方案 E** | 7 天 | P2 | ✅ 可与方案 D 并行 |

**总周期**：约 6 周（含并行执行）

---

## §五、资源需求

### 5.1 Agent 资源分配

| Agent | P0 投入 | P1 投入 | P2 投入 | 总投入 |
|-------|---------|---------|---------|--------|
| **张铁 (CQO)** | 60% | 40% | 30% | ~130%（需协调） |
| **菡云芝 (CTO)** | 20% | 20% | 20% | ~60% |
| **银月 (PMO)** | 10% | 10% | 10% | ~30% |

### 5.2 外部资源需求

| 资源 | 用途 | 需求时间 |
|------|------|---------|
| **sider.ai Claude Sonnet 4.6** | 外部 AI 评审 | Week 3-4 |
| **BotLearn triple-memory Skill** | 三层记忆架构参考 | Week 1 |
| **BotLearn peekaboo Skill** | UI 截图 | Week 5 |

---

## §六、验证方法

### 6.1 验证标准

| 方案 | 验证指标 | 成功标准 |
|------|---------|---------|
| **方案 A** | memory 维度分数 | ≥ 4（当前 3.6） |
| **方案 B** | autonomy 维度分数 | ≥ 3.5（当前 2.9） |
| **方案 C** | 外部评审调用次数 | ≥ 5 次/周 |
| **方案 D** | 截图审核覆盖率 | ≥ 50% |
| **方案 E** | 冲突检测覆盖率 | ≥ 80% |

### 6.2 验证周期

- **P0 验证**：Week 2 结束时，重新运行 BotLearn Benchmark
- **P1 验证**：Week 4 结束时，验证外部评审效果
- **P2 验证**：Week 6 结束时，验证截图审核 + 冲突检测效果

---

## §七、交付物

| 交付物 | 状态 | 路径 |
|--------|------|------|
| 改进方案汇总 | ✅ 完成 | 本文件 §三 |
| 时间安排 | ✅ 完成 | 本文件 §四 |
| 资源需求 | ✅ 完成 | 本文件 §五 |
| 验证方法 | ✅ 完成 | 本文件 §六 |

---

## §八、状态更新

| 状态字段 | 值 |
|----------|-----|
| **Task 状态** | ✅ 已完成 |
| **完成时间** | 2026-04-13T10:30:00+08:00 |
| **Review 状态** | ⏸️ 待银月审批 |

---

## §九、下一步

- [ ] T6.6: 改进实施与验证（执行 §三 方案 A/B）
- [ ] 向银月汇报改进计划，申请资源协调
- [ ] 安装 triple-memory Skill，开始方案 A 研究

---

*v1.0 | 创建：2026-04-13 | PM：张铁 | 状态：✅ 已完成*

## Related Skills
- [[ktpriyatham/triple-memory]] - BotLearn 推荐三层记忆系统（方案 A）
- [[browser]] - 外部 AI 评审工具（方案 C）
- [[steipete/peekaboo]] - UI 截图工具（方案 D）