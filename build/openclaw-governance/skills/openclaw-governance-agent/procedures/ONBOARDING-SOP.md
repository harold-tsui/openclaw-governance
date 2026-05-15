# ONBOARDING-SOP · Agent 入职流程

> **版本**：v1.0
> **触发条件**：新 Agent 创建
> **审批级别**：L3 (Harold)
> **预计耗时**：3 小时

---

## 一、流程概览

```
Step 1: 环境熟悉 → Step 2: 工具熟悉 → Step 3: 定位理解 → Step 4: 上下文创建 → Step 5: 入职汇报 → Step 6: 银月初审 → Step 7: Harold 终审
```

---

## 二、详细步骤

### Step 1: 环境熟悉（预计 30min）

```
□ 读取 ${OPENCLAW_AGENT_LOCAL_WORKSPACE}/ 目录结构
□ 确认可访问的文件范围（隔离验证）
□ 测试跨 workspace 读取权限（应只能读 persons.yaml）
□ 输出：环境自检报告
```

**交付物**：`ONBOARD-ENV-CHECK-{agent_id}.md`

---

### Step 2: 工具熟悉（预计 30min）

```
□ 读取 TOOLS.md
□ 测试关键工具调用（read/write/exec）
□ 验证文件操作范围限制
□ 输出：工具可用性清单
```

**交付物**：`ONBOARD-TOOLS-LIST-{agent_id}.md`

---

### Step 3: 定位理解（预计 45min）

```
□ 深度阅读 IDENTITY.md
□ 理解职责边界和协作规则
□ 明确与银月的关系
□ 输出：职责理解确认书
```

**交付物**：`ONBOARD-DUTY-CONFIRM-{agent_id}.md`

---

### Step 4: 上下文创建（预计 30min）

```
□ 创建个人工作目录结构（inbox/working/archive）
□ 从模板生成核心文件（见 §模板变量替换）
□ 初始化必要的配置文件
□ 设置个人知识沉淀目录
□ 输出：工作空间初始化完成确认
```

**交付物**：工作空间初始化

#### 模板变量替换

从 `governance-core/templates/` 复制模板到 Agent 工作空间时，必须替换所有变量占位符。

**替换规则**：
1. `${VARIABLE}` — 必须替换（大写+花括号），缺失值视为错误
2. `{variable}` — 必须替换（小写+花括号），运行时上下文填充
3. `[variable]` — 可选替换（方括号），如无值则移除整段

**生成文件清单**：

| 模板 | 生成文件 | 目标路径 |
|------|----------|----------|
| `TMPL-IDENTITY-SUB.md` | `IDENTITY.md` | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/IDENTITY.md` |
| `TMPL-AGENTS-SUB.md` | `AGENTS.md` | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/AGENTS.md` |
| `TMPL-SOUL-SUB.md` | `SOUL.md` | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/SOUL.md` |
| `TMPL-TOOLS-SUB.md` | `TOOLS.md` | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/TOOLS.md` |
| `TMPL-MISSION_BOARD.md` | `MISSION_BOARD.md` | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/MISSION_BOARD.md` |
| `TMPL-HEARTBEAT-SUB.md` | `HEARTBEAT.md` | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/HEARTBEAT.md` |
| `TMPL-USER-SUB.md` | `USER.md` | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/USER.md` |

**变量清单**（按来源分组）：

| 变量 | 来源 | 说明 |
|------|------|------|
| `${OPENCLAW_LOCAL_WORKSPACE}` | 系统环境 | 主工作空间根目录 |
| `${OPENCLAW_AGENT_LOCAL_WORKSPACE}` | 系统环境 | Agent 工作空间目录 |
| `${OPENCLAW_WORKSPACE_SYSTEM}` | 系统环境 | 系统配置目录 |
| `${AGENT_ID}` / `{agent_id}` / `{agent-id}` | agents.yaml | Agent 唯一标识 |
| `${AGENT_NAME}` | agents.yaml | Agent 显示名 |
| `${AGENT_ROLE}` | agents.yaml | Agent 角色 |
| `${AGENT_DOMAIN}` | agents.yaml | Agent 领域 |
| `${AGENT_POSITIONING}` | agents.yaml | Agent 定位 |
| `${AGENT_MISSION}` | agents.yaml | Agent 核心使命 |
| `${REPORTING_CHAIN}` | agents.yaml | 汇报链 |
| `${CAN_DO_LIST}` | agents.yaml | 能力列表 |
| `${CANNOT_DO_LIST}` | agents.yaml | 限制列表 |
| `${TOOLS_LIST}` | agents.yaml | 工具列表 |
| `${TOOLS_USAGE}` | agents.yaml | 工具使用规范 |
| `${TEMPLATE_VERSION}` | 模板元数据 | 模板版本号 |
| `${LOCAL_VERSION}` | 生成时设定 | 生成文件版本号（初始 = 模板版本） |
| `${LAST_SYNC_DATE}` | 生成时设定 | 最后同步日期（初始 = 生成日期） |
| `{project_id}` | Task Card | 项目 ID |
| `{topic_id}` | Task Card | 主题 ID |
| `{task_id}` | Task Card | 任务 ID |
| `{other_agent_id}` | agents.yaml | 协作 Agent ID |

**替换验证**：生成后检查文件中不应残留未替换的 `${` 或 `{` 占位符（`[...]` 除外）。

---

### Step 5: 入职汇报撰写（预计 45min）

```
□ 整理 Steps 1-4 的输出
□ 撰写入职汇报文档
□ 提出对工作的理解和期望
□ 输出：ONBOARD-REPORT-{agent_id}.md
```

**交付物**：`ONBOARD-REPORT-{agent_id}.md`

---

### Step 6: 银月初审

```
□ 向银月提交所有交付物
□ 银月审核并给出意见
□ 如需修订，返回对应 Step
```

**审批人**：银月
**审批级别**：L2

---

### Step 7: Harold 最终审批

```
□ 银月汇总后提交 Harold
□ Harold Review（L3）
□ 批准 / 驳回 / 要求修订
```

**审批人**：Harold
**审批级别**：L3

---

## 三、完成后状态更新

```yaml
# agents.yaml
{agent_id}:
  onboarding_status: completed
  onboarded_at: 2026-03-31
```

---

## 四、模板文件

- `templates/TMPL-ONBOARDING-TASK-CARD.md`

---

*Version: 1.1 | Created: 2026-03-31 | Updated: 2026-04-24 | 变更: Step 4 增加模板变量替换步骤和变量清单*