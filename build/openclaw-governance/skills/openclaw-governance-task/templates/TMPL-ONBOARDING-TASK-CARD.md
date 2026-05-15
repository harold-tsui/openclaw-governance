# TASK-CARD ·-ONBOARD-001

> **文件性质**：Sub Agent 入职培训专用 Task Card
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/10_Projects/{project_id}/{topic_id}/tasks/TASK-CARD-{agent_id}-ONBOARD-001.md`
> **模板来源**：`skills/openclaw-governance/skills/openclaw-governance-task/templates/TMPL-ONBOARDING-TASK-CARD.md`
> **版本**：v1.0

---

## 一、Task 基本信息

| 字段                   | 内容                                     |
| ---------------------- | ---------------------------------------- |
| **Task ID**      | {agent_id}-ONBOARD-001                   |
| **Task 标题**    | {agent_name} Agent 入职培训              |
| **归属 Topic**   | {topic_id} · Agent 团队建设             |
| **归属 Project** | {project_id} · {project_name}           |
| **Task PIC**     | 银月（创建） → {agent_name}（执行）     |
| **优先级**       | P0（入职前最高优先级）                   |
| **Review 级别**  | L3（需 Harold 最终批准）                 |
| **状态标记**     | `[ ]` → `[V]` → `[~]` → `[x]` |
| **创建时间**     | {created_at}                             |
| **计划完成日期** | {planned_completion}                     |
| **实际完成日期** | —                                       |

---

## 二、Task 目标与验收标准

### 2.1 目标陈述

让 {agent_name} 熟悉工作环境、掌握可用工具、理解自身定位、建立工作上下文，完成从「创建」到「可正式接任务」的转变。

### 2.2 验收标准（固定清单）

| # | 验收标准                         | 交付物                                 | Review 级别  |
| - | -------------------------------- | -------------------------------------- | ------------ |
| 1 | 环境自检报告                     | `ONBOARD-ENV-CHECK-{agent_id}.md`    | L1           |
| 2 | 工具可用性清单                   | `ONBOARD-TOOLS-LIST-{agent_id}.md`   | L1           |
| 3 | 职责理解确认书                   | `ONBOARD-DUTY-CONFIRM-{agent_id}.md` | L2           |
| 4 | 个人工作空间初始化完成           | 目录结构 + 配置文件                    | L1           |
| 5 | 入职汇报文档                     | `ONBOARD-REPORT-{agent_id}.md`       | L3           |
| 6 | 银月初审通过                     | 审核意见                               | L2           |
| 7 | **Harold 最终批准**        | 批准确认                               | **L3** |
| 8 | **更新 onboarding_status** | persons.yaml 更新                      | L1           |

---

## 三、输入物（Inputs）

| 输入物                         | 类型 | 来源                                      | 状态      |
| ------------------------------ | ---- | ----------------------------------------- | --------- |
| TMPL-IDENTITY-SUB.md           | 模板 | `skills/openclaw-governance/skills/openclaw-governance-task/templates/` | ✅ 已就绪 |
| TMPL-SOUL-SUB.md               | 模板 | `skills/openclaw-governance/skills/openclaw-governance-task/templates/` | ✅ 已就绪 |
| TMPL-AGENTS-SUB.md             | 模板 | `skills/openclaw-governance/skills/openclaw-governance-task/templates/` | ✅ 已就绪 |
| TMPL-HEARTBEAT-SUB.md          | 模板 | `skills/openclaw-governance/skills/openclaw-governance-task/templates/` | ✅ 已就绪 |
| TMPL-TOOLS-SUB.md              | 模板 | `skills/openclaw-governance/skills/openclaw-governance-task/templates/` | ✅ 已就绪 |
| TMPL-USER-SUB.md               | 模板 | `skills/openclaw-governance/skills/openclaw-governance-task/templates/` | ✅ 已就绪 |
| persons.yaml 中的本 Agent 条目 | 数据 | `.system/master_data/`                  | ✅ 已就绪 |

---

## 四、执行步骤

```
Step 1: 环境熟悉（预计 30min）
  □ 读取 ${OPENCLAW_AGENT_LOCAL_WORKSPACE}/ 目录结构
  □ 确认可访问的文件范围（隔离验证）
  □ 测试跨 workspace 读取权限（应只能读 persons.yaml）
  □ 输出：环境自检报告
  → Step 2

Step 2: 工具熟悉（预计 30min）
  □ 读取 TOOLS.md
  □ 测试关键工具调用（read/write/exec）
  □ 验证文件操作范围限制
  □ 输出：工具可用性清单
  → Step 3

Step 3: 定位理解（预计 45min）
  □ 深度阅读 IDENTITY.md
  □ 理解职责边界和协作规则
  □ 明确与 Main Agent（银月）的关系
  □ 输出：职责理解确认书
  → Step 4

Step 4: 上下文创建（预计 30min）
  □ 创建个人工作目录结构（inbox/working/archive）
  □ 初始化必要的配置文件
  □ 设置个人知识沉淀目录
  □ 输出：工作空间初始化完成确认
  → Step 5

Step 5: 入职汇报撰写（预计 45min）
  □ 整理 Steps 1-4 的输出
  □ 撰写入职汇报文档
  □ 提出对工作的理解和期望
  □ 输出：ONBOARD-REPORT-{agent_id}.md
  → Step 6

Step 6: 提交银月初审
  □ 向银月提交所有交付物
  □ 银月审核并给出意见
  □ 如需修订，返回对应 Step
  → Step 7

Step 7: Harold 最终审批 ⭐
  □ 银月汇总后提交 Harold
  □ Harold Review（L3）
  □ 批准 / 驳回 / 要求修订
  → 批准后：更新 onboarding_status = completed
```

---

## 五、Deliverable 列表

| # | Deliverable               | 类型     | 路径                                                                                                                                       | Review 级别  | 状态 |
| - | ------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ---- |
| 1 | 环境自检报告              | Markdown | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/{topic_id}/tasks/{task_id}/deliverables/ONBOARD-ENV-CHECK-{agent_id}.md`                             | L1           | ⬜   |
| 2 | 工具可用性清单            | Markdown | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/{topic_id}/tasks/{task_id}/deliverables/ONBOARD-TOOLS-LIST-{agent_id}.md`   | L1           | ⬜   |
| 3 | 职责理解确认书            | Markdown | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/{topic_id}/tasks/{task_id}/deliverables/ONBOARD-DUTY-CONFIRM-{agent_id}.md` | L2           | ⬜   |
| 4 | 工作空间初始化            | 目录结构 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/{agent_id}/`                                                                                          | L1           | ⬜   |
| 5 | 入职汇报文档              | Markdown | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/agent-resource/{topic_id}/tasks/{task_id}/deliverables/ONBOARD-REPORT-{agent_id}.md`       | L3           | ⬜   |
| 6 | 银月初审意见              | 文本     | Task Card §六                                                                                                                             | L2           | ⬜   |
| 7 | **Harold 批准确认** | 决策     | Task Card §六                                                                                                                             | **L3** | ⬜   |

---

## 六、依赖与阻塞

### 6.1 前置依赖

| 依赖对象     | 依赖内容                        | 状态      |
| ------------ | ------------------------------- | --------- |
| 银月         | 创建 Agent workspace 和基础文件 | ✅ 已就绪 |
| persons.yaml | 本 Agent 条目已创建             | ✅ 已就绪 |
| 模板文件     | 所有 6 个模板已就位             | ✅ 已就绪 |

### 6.2 当前阻塞

无阻塞。

---

## 七、资源需求

| 资源类型           | 需求      | 状态          |
| ------------------ | --------- | ------------- |
| {agent_name} 时间  | 约 3 小时 | ⏳ 待开始     |
| 银月审核时间       | 30 分钟   | ⏳ 待提交     |
| Harold Review 时间 | 15 分钟   | ⏳ 待银月提交 |

---

## 八、执行记录

| 时间         | 动作      | 结果                        | 备注     |
| ------------ | --------- | --------------------------- | -------- |
| {created_at} | Task 创建 | 启动 {agent_id}-ONBOARD-001 | 银月创建 |

---

## 九、验收记录

| 字段                   | 内容                    |
| ---------------------- | ----------------------- |
| **提交验收时间** | —                      |
| **提交人**       | {agent_name}            |
| **验收人**       | 银月初审 → Harold 终审 |
| **验收结果**     | ⬜ 待验收               |
| **修订说明**     | —                      |

### 银月初审意见

> （银月填写）

### Harold 终审意见

> （Harold 填写）

---

## 十、入职完成后状态更新

入职培训完成并通过 Harold 批准后：

1. **更新 persons.yaml**

   ```yaml
   - id: {agent_id}
     name: {agent_name}
     role: {role}
     onboarding_status: completed  # ← 从 pending/in_progress 更新
     onboarded_at: {date}
   ```
2. **Agent 状态变更**

   - 从「培训中」→「可正式接任务」
   - 可以接受银月派发的正式任务
3. **首次 Heartbeat**

   - 按简化版心跳协议执行日常巡检
   - 向银月发送首次日报

---

## 十一、状态历史

| 日期         | 状态变更     | 变更原因                 | 记录人 |
| ------------ | ------------ | ------------------------ | ------ |
| {created_at} | `[ ]` 创建 | 银月创建 Onboarding Task | 银月   |

---

## 版本信息

- **Version**: v1.0
- **Created At**: 2026-03-07
- **Updated At**: 2026-03-07
- **Changes**: 根据 ZT-2026-002 规范更新引用路径（skills/openclaw-governance/skills/openclaw-governance-task/templates/）

*本 Task Card 由银月创建，用于 Sub Agent 入职培训。*
