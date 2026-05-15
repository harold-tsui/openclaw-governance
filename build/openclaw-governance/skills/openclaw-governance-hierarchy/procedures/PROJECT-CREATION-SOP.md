
# Project Creation SOP
# 项目创建标准作业程序

> **文件路径**：`${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/policies/PROJECT-CREATION-SOP.md`
> **文件性质**：治理流程文件
> **读写权限**：Harold 审批；银月可提议修订
> **上位引用**：ZT-2026-000_Agent共同灵魂_v1.0.md · IDENTITY.md v3.1
> **下位引用**：TMPL-PROJECT-CHARTER-v1.2.md
> **版本**：v1.2

---

## 一、适用范围

本 SOP 适用于 ZT 体系内所有新 Project 的创建，涵盖从提议到执行解冻的完整流程。

---

## 二、核心原则

| 原则 | 说明 |
|---|---|
| **Harold 唯一审批权** | 任何新 Project 未经 Harold 明确批准，不得创建 |
| **银月唯一创建权** | Harold 批准后，由银月负责建档，任何其他 Agent 不得自行创建 |
| **章程优先** | PROJECT-CHARTER.md 章程 Review 状态未达到「✅ Harold 已通过」前，禁止任何 Agent 投入实质性工作 |
| **唯一真相来源** | 项目配置文件（user-projects.yaml/system-projects.yaml）是所有 Project 信息的唯一真相来源 |

---

## 三、流程总览

```
Step 1  任何人提议
    ↓
Step 2  Harold 审批
    ├─ 拒绝 → 归档提议，流程结束
    └─ 批准 → 进入 Step 3
    ↓
Step 3  银月建档
        项目配置新增条目（status: planning）
        PROJECT-CHARTER.md 空白章程（章程 Review 状态: ⚠️ 待 Harold Review）
    ↓
Step 4  Harold 指定 PM
    ↓
Step 5  PM 细化项目章程
    ↓
Step 6  Harold Review 章程
    ├─ 打回 → PM 修订，重回 Step 5
    └─ 通过 → 进入 Step 7
    ↓
Step 7  解冻执行
        项目配置 status → active
        章程 Review 状态 → ✅ Harold 已通过
        Agent 开始投入工作
```

---

## 四、各步骤详细说明

### Step 1 · 提议

**执行人**：任何人（Harold · 银月 · 任意 Agent · 外部输入）

**提议内容**（口头或书面均可，银月负责结构化）：

| 字段 | 是否必填 | 说明 |
|---|---|---|
| 项目名称 | ✅ | 简短，能体现业务域 |
| 背景与目的 | ✅ | 为什么要做这个项目 |
| 预期交付物 | ✅ | 做完是什么样子 |
| 建议 PM | ⬜ | 可由 Harold 在 Step 4 再定 |
| 建议成员 | ⬜ | 可选 |

**银月职责**：
- 收到提议后，通过 `governance-config.load_user("projects")` 查询项目配置，确认不存在同名或同目的的 Project
- 如已存在，告知提议方并引导至已有 Project，流程终止
- 整理提议内容，呈报 Harold 审批

---

### Step 2 · Harold 审批

**执行人**：Harold

**审批维度**（银月在呈报时提供参考信息）：
- 与现有 Project 是否重叠？
- 是否符合当前战略优先级？
- 资源是否可承接？

**输出**：
- ✅ **批准**：Harold 口头或书面确认，银月记录审批决定，进入 Step 3
- ❌ **拒绝**：银月将提议归档至 `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/rejected-proposals/`，注明拒绝原因，流程结束

---

### Step 3 · 银月建档

**执行人**：银月（PMO）

**动作清单**：

**3.1 分配 Project ID**
- 通过 `governance-config.load_user("projects")` 读取项目配置，取当前最大序号 +1
- 格式：`ZT-PXXX`（三位数字，如 `ZT-P006`）
- 禁止使用任何其他前缀格式

**3.2 更新项目配置**

通过 `governance-config.update("user-projects", new_project)` 新增条目，必填字段：

```yaml
- id: "ZT-PXXX"
  name: "项目名称"
  description: "项目简述"
  status: "planning"                    # 新建项目固定为 planning
  charter_review_status: "pending"      # 章程 Review 状态，初始为 pending
  pm: "[Harold 指定的 PM ID]"           # Step 4 指定后填入
  pmo: "PA_yinyue"                      # 固定为银月
  members: ["PA_yinyue"]               # 银月默认在所有项目中
  start_date: "YYYY-MM-DD"
  privacy_level: "P1"                  # 默认 P1，Harold 可提升
  source: "manual"
  created_at: "YYYY-MM-DDTHH:MM:SS+08:00"
  updated_at: "YYYY-MM-DDTHH:MM:SS+08:00"
```

**`charter_review_status` 取值说明**：

| 值 | 含义 | 对应章程显示 |
|---|---|---|
| `pending` | 待 Harold Review | ⚠️ 待 Harold Review |
| `in_review` | Harold 审阅中 | 🟡 Harold Review 中 |
| `revision` | 打回修订中 | 🔄 打回修订中 |
| `approved` | Harold 已通过 | ✅ Harold 已通过 |

**3.3 创建目录与空白章程**

```
10_Projects/ZT-PXXX/
└── PROJECT-CHARTER.md    ← 使用 TMPL-PROJECT-CHARTER-v1.2.md 模板
                             初始状态: 🔵 Planning
                             初始章程 Review 状态: ⚠️ 待 Harold Review
```

**3.4 通知 Harold**

银月确认建档完成，告知 Harold：
- Project ID（`ZT-PXXX`）
- 文件路径
- 下一步行动：Step 4 指定 PM

---

### Step 4 · Harold 指定 PM

**执行人**：Harold

- Harold 从 `persons.yaml` 中指定 PM（Project Manager）
- 银月通过 `governance-config.update("user-projects", {...pm: pm_id})` 写入 PM 字段
- 银月通知 PM，说明职责和章程细化要求，附上章程模板路径：
  `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/templates/TMPL-PROJECT-CHARTER-项目章程模板.md`

> **PMO 固定为银月**，无需每次指定。

---

### Step 5 · PM 细化项目章程

**执行人**：PM（Harold 指定的负责人）

**章程必须包含以下内容**：

| 章节 | 说明 |
|---|---|
| **项目目标（Target）** | 可量化的成功标准；完成条件 |
| **里程碑规划（Planning）** | 关键阶段划分；每阶段交付物 |
| **Topic / Task 初步拆解** | 至少拆解至 Topic 层级 |
| **资源与成员** | 确认参与 Agent 列表 |
| **风险初判** | 已知风险和依赖项 |

**银月职责**：
- PM 起草期间，银月可提供模板和体系规范指引
- 但**不替代 PM 做章程内容决策**
- PM 完成后，银月将 `charter_review_status` 更新为 `in_review`，并将章程排入 Harold Review 队列

---

### Step 6 · Harold Review 章程

**执行人**：Harold

**Review 要点**：
- 目标是否清晰可衡量？
- 里程碑规划是否合理？
- 资源配置是否匹配？
- Topic / Task 拆解是否足够？

**输出**：

- ✅ **通过**：Harold 确认，银月执行以下两项同步更新，进入 Step 7：
  - 项目配置：`status → active`，`charter_review_status → approved`
  - `PROJECT-CHARTER.md`：状态 → `🟢 Active`，章程 Review 状态 → `✅ Harold 已通过`

- 🔄 **打回**：Harold 说明修订方向，银月将 `charter_review_status` 更新为 `revision`，通知 PM 按意见修订，重新提交，重回 Step 6

---

### Step 7 · 解冻执行

**执行人**：银月（通知）

- 银月正式通知相关 Agent：项目章程已通过，可以开始投入工作
- 银月将项目纳入 HEARTBEAT 巡检范围
- 银月在 MISSION_BOARD 中创建项目条目

> ⚠️ **在 Step 7 触发前（即章程 Review 状态未达到 `approved`），任何 Agent 不得对此 Project 展开实质性工作。**

---

## 五、状态流转

```
（不存在）→ planning → active → paused / closed
```

**`status` 与 `charter_review_status` 联动关系**：

| Project status | charter_review_status | 含义 |
|---|---|---|
| `planning` | `pending` | 已建档，PM 尚未提交章程 |
| `planning` | `in_review` | 章程已提交，Harold 审阅中 |
| `planning` | `revision` | 章程被打回，PM 修订中 |
| `active` | `approved` | 章程通过，执行中 |
| `paused` | `approved` | 暂停（Harold 决定或触发暂停条件） |
| `closed` | `approved` | 已关闭（Harold 最终裁定） |

---

## 六、异常处理

| 异常场景 | 处理方式 |
|---|---|
| 发现项目配置中已有同目的 Project | 银月拒绝建档，引导至已有 Project，上报 Harold |
| PM 长期未提交章程（超过 7 天） | 银月上报 Harold，请求裁定是否更换 PM 或关闭提议 |
| Agent 在章程 `approved` 前擅自开展工作 | 银月立即叫停，记录违规，上报 Harold |
| Harold 长期未 Review 章程（超过 7 天） | 银月在 Heartbeat 中标记为阻塞，提醒 Harold |

---

## 七、相关文件

| 文件 | 路径 | 用途 |
|---|---|---|
| user-projects.yaml | `config/user/user-projects.yaml` | 用户级 Project 主数据（唯一真相来源） |
| system-projects.yaml | `config/system/system-projects.yaml` | 系统级 Project 主数据 |
| persons.yaml | `config/user/persons.yaml` | 人员主数据 |
| 章程模板 | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/templates/TMPL-PROJECT-CHARTER-项目章程模板.md` | 章程标准模板 |
| HAROLD-DELEGATION.md | `${OPENCLAW_LOCAL_WORKSPACE}/${OPENCLAW_WORKSPACE_SYSTEM}/policies/HAROLD-DELEGATION.md` | 授权记录 |
| MISSION_BOARD.md | `${OPENCLAW_LOCAL_WORKSPACE}/MISSION_BOARD.md` | 任务全景 |

---

## 版本信息

- **Version**: v1.2
- **Changes from v1.1**:
  - 对齐 governance-config v1.2.0：统一使用"项目配置"术语，不再直接使用文件名
  - Step 3.1：读取方式改为 `governance-config.load_user("projects")`
  - Step 3.2：更新方式改为 `governance-config.update("user-projects", new_project)`
  - Step 4：更新方式改为 `governance-config.update("user-projects", {...pm: pm_id})`
  - Step 6：同步更新"项目配置"而非直接写文件名
  - 六、异常处理："projects.yaml" → "项目配置"
  - 七、相关文件：路径更新为新的配置目录结构
- **Changes from v1.0**:
  - 全文术语统一：`Project PIC` → `PM（Project Manager）`
  - 下位引用补充 `TMPL-PROJECT-CHARTER-v1.2.md`
  - 二、核心原则：「章程优先」描述对齐章程模板的「章程 Review 状态」字段表述
  - Step 3.2：新增 `charter_review_status` 字段及完整取值说明；新增 `pm` / `pmo` 字段区分
  - Step 3.3：明确初始状态 `🔵 Planning` 和初始章程 Review 状态 `⚠️ 待 Harold Review`；模板文件名更新为 `TMPL-PROJECT-CHARTER-v1.2.md`
  - Step 4：通知 PM 时附上章程模板路径
  - Step 5：PM 完成后，银月同步将 `charter_review_status → in_review`
  - Step 6：通过分支明确同步更新项目配置和 `PROJECT-CHARTER.md` 两处状态；打回分支明确更新 `charter_review_status → revision`
  - Step 7：禁止投入工作的判断条件从「Step 7 前」改为「`charter_review_status` 未达到 `approved`」，更精确
  - 五、状态流转：新增 `status` 与 `charter_review_status` 联动关系对照表
- **Created At**: 2026-02-25
- **Last Updated**: 2026-04-07
- **Approved By**: Harold Tsui
- **Status**: **Effective**
