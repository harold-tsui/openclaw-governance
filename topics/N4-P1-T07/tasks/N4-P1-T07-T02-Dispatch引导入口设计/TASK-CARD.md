# TASK-CARD · N4-P1-T07-T02-Dispatch引导入口设计

> **文件性质**：Task-CARD（Zone A/B/C 三区分层架构）
> **存放路径**：`10_Projects/ZT-P015_NUCLEUS-4-0/topics/N4-P1-T07/tasks/N4-P1-T07-T02-Dispatch引导入口设计/TASK-CARD.md`
> **模板版本**：TMPL-TASK-CARD v3.1

---

## Zone A：任务定义（创建时填写）

### §一、任务基本信息

| 字段 | 值 |
|------|-----|
| **Task ID** | N4-P1-T07-T02 |
| **Task 名称** | Dispatch 引导入口设计 |
| **Task 类型** | 📋 改进任务 |
| **所属 Topic** | N4-P1-T07 BotLearn 方案 |
| **所属 Project** | ZT-P015 NUCLEUS 4.0 |
| **Task PIC** | 张铁 (cqo) |
| **指派人** | Harold Tsui |
| **创建日期** | 2026-04-15 |
| **Review 级别** | L2（抽样核查） |

---

### §二、任务上下文

| 上下文项 | 说明 |
|----------|------|
| **前置任务** | T01 BotLearn 设计理念提炼 |
| **依赖研究** | botlearn-design-analysis.md §2.1 引导式提问机制 |
| **改进对象** | governance-dispatch SKILL.md v2.10.0 |

---

### §三、任务目标

> **核心目标**：让 dispatch 从"分发器"升级为"引导入口"，在意图不清晰时引导用户选择。

**验收标准**：
- [ ] 引导式提问机制设计完成
- [ ] dispatch-state.json 模板创建
- [ ] governance-dispatch SKILL.md 改进方案文档完成

---

### §四、Deliverable 定义

| Deliverable | 路径 | 内容要求 | 完成标准 |
|-------------|------|----------|----------|
| **引导机制设计** | `outputs/dispatch-guidance-design.md` | 引导流程 + 示例 | 完整设计文档 |
| **状态模板** | `templates/dispatch-state.json` | 状态字段定义 | 模板文件 |
| **改进方案** | `outputs/dispatch-improvement-plan.md` | SKILL.md 改进点列表 | 可执行方案 |

---

### §五、关键约束

| 约束类型 | 约束内容 |
|----------|----------|
| **不污染生产环境** | ❌ 不修改 `.system/governance/current/skills/` |
| **开发环境优先** | ✅ 所有设计文档放在 `10_Projects/ZT-P015_NUCLEUS-4-0` |
| **验证后再迁移** | ⚠️ 设计完成后需 Harold 审批，再应用到生产环境 |

---

### §六、资源需求

| 资源 | 需求 |
|------|------|
| **人力** | 1 人（张铁） |
| **工具** | read/write 工具 |
| **时间** | 预估 2-3 小时 |

---

## Zone B：运行时状态（执行中更新）

### §七、执行记录

#### 7.1 当前状态值

| 状态字段 | 值 | 最后更新时间 |
|----------|-----|--------------|
| **当前状态** | `[P]` 执行中 | 2026-04-15 09:50 |
| **完成进度** | 60% | 2026-04-15 09:53 |

---

#### 7.2 工作进展

| 步骤 | 内容 | 状态 | 完成时间 |
|------|------|------|----------|
| Step 1 | 加载 governance-dispatch SKILL.md | ✅ 完成 | 2026-04-15 09:50 |
| Step 2 | BotLearn 引导机制对比分析 | ✅ 完成 | 2026-04-15 09:52 |
| Step 3 | 设计引导式提问流程 | ✅ 完成 | 2026-04-15 09:52 |
| Step 4 | 创建 dispatch-state.json 模板 | ✅ 完成 | 2026-04-15 09:52 |
| Step 5 | 编写改进方案文档 | ✅ 完成 | 2026-04-15 09:53 |
| Step 6 | 等待 Harold 审批 | ⬜ 待执行 | - |

---

*创建时间：2026-04-15 09:50 | 创建人：张铁 (cqo) | 当前状态：执行中*