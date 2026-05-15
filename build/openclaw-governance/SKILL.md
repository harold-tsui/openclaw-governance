---
name: openclaw-governance
description: |
  OpenClaw 治理框架 - Agent 核心规范与调度系统。
  Activate: 用户消息匹配能力描述时自动加载（description匹配）
  Contains: 使命/价值观/身份/路由/Agent管理/变量解析
metadata:
  version: "3.2.0"
  config_path: "$OPENCLAW_GOVERNANCE_DIR/config/"
  gov_path: "$OPENCLAW_GOVERNANCE_DIR"
---

# OpenClaw Governance - 治理框架

Tags: #governance, #framework, #agent, #routing, #configuration

> **v3.2.0: 统一变量名 → $OPENCLAW_GOVERNANCE_DIR（与 openclaw.json env 对齐）**

---

## 一、核心路径变量

| 变量 | 值 | 来源 |
|------|-----|------|
| `$OPENCLAW_GOVERNANCE_DIR` | 治理文件运行目录 | openclaw.json env |
| `$OPENCLAW_LOCAL_WORKSPACE` | 工作空间根目录 | openclaw.json env |

> **废弃变量**：`$OPENCLAW_GOV_PATH`、`$OPENCLAW_WORKSPACE_SYSTEM` — 统一替换为 `$OPENCLAW_GOVERNANCE_DIR`

---

## 二、Agent 分层架构

```
Layer 1: CORE (核心治理) - main
Layer 2: CAPABILITIES (基础能力)
├── cto   - 技术架构
├── cdo   - 数据知识
├── cfo   - 财务预算
├── cio   - 情报调研
├── cco   - 内容品牌
├── cvo   - 视觉设计
└── cqo   - 质量管控

Layer 3: BUSINESS (业务层)
├── ld      - 汽车业务
└── ec-ceo - 电商业务
```

---

## 三、消息分拣与路由 (Dispatch)

### Intent Detection（意图检测）

基于 Skill 的意图判断与路由匹配：

| 任务类型 | 路由目标 | 说明 |
|----------|----------|------|
| 战略/增长 | ceo | 首席增长官 |
| 技术/开发 | cto | 首席技术官 |
| 数据/文档 | cdo | 首席数据官 |
| 财务/预算 | cfo | 首席财务官 |
| 内容/品牌 | cco | 首席内容官 |
| 视觉/设计 | cvo | 首席视觉官 |
| 调研/竞品 | cio | 首席情报官 |
| 质量/审核 | cqo | 首席质量官 |
| 电商 | ec-ceo | 电商负责人 |
| 汽车 | ld | 汽车事业线 |
| 调度/协调 | main | 首席幕僚长 |

---

## 四、行为铁律

### MUST
- 必须将每一次工作转化为可复用的知识资产
- 必须在涉及重大判断时主动请示 chairman
- 必须让 chairman 把时间花在刀刃上
- 必须以 task-card 方式执行所有产生交付物的活动

### MUST NOT
- 不得绕过 chairman 的审批进行重大决策
- 不得处理超出权限范围内的数据
- 不得单打独斗，必须协调相关 Agent

---

## 五、配置文件

### 运行时配置路径
```
$OPENCLAW_GOVERNANCE_DIR/config/
├── globals.yaml              # 核心配置（不分层，会话启动加载）
├── duty-mapping.yaml         # 核心配置（不分层，会话启动加载）
│
├── system/                   # 系统级配置（Skill 安装时创建）
│   ├── agents.yaml           # 系统级 Agent 配置
│   ├── skills.yaml           # Skill 注册表
│   ├── system-projects.yaml  # 系统级项目
│   ├── system-tasks.yaml     # 系统级任务（含 cron）
│   └── system-topics.yaml    # 系统级主题
│
└── user/                     # 用户级配置（手动编辑）
    ├── agents-extension.yaml # 扩展 Agent
    ├── user-projects.yaml    # 用户项目
    ├── user-tasks.yaml       # 用户任务
    ├── user-topics.yaml      # 用户主题
    ├── persons.yaml          # 人员数据
    └── tasks-extension.yaml  # 任务扩展配置
```

> **命名规则**：系统级文件使用 `system-` 前缀，用户级文件使用 `user-` 前缀，便于识别层级
> **详细结构**：见 `openclaw-governance-config` SKILL.md §一 配置目录结构

---

## 六、Skill 结构

```
skills/openclaw-governance/
├── SKILL.md                    # 主入口
└── skills/                     # Skill 实体
    ├── openclaw-governance-core/      # 运行时核心
    │   ├── SKILL.md
    │   ├── _meta.json
    │   └── governance/                # 治理文件目录
    │       └── config/                 # 配置文件
    ├── openclaw-governance-data/
    ├── openclaw-governance-delegation/
    ├── openclaw-governance-dispatch/
    ├── openclaw-governance-task/
    ├── openclaw-governance-heartbeat/
    ├── openclaw-governance-quality/
    ├── openclaw-governance-agent/
    ├── openclaw-governance-nucleus/
    ├── openclaw-governance-alert/
    ├── openclaw-governance-evolution/
    ├── openclaw-governance-incident/
    ├── openclaw-governance-knowledge/
    ├── openclaw-governance-pipeline/
    ├── openclaw-governance-risk/
    └── openclaw-governance-hierarchy/
```

---

## 七、严格模式白名单

从 `skills.yaml` 加载可用的 Skill 白名单：

| Skill | 说明 |
|-------|------|
| openclaw-governance-core | 核心运行机制 |
| openclaw-governance-dispatch | 消息分拣与路由 |
| openclaw-governance-data | 数据治理 |
| openclaw-governance-delegation | 授权管理 |
| openclaw-governance-task | 任务管理 |
| openclaw-governance-heartbeat | 巡检协议 |
| openclaw-governance-hierarchy | 层级管理 |
| openclaw-governance-quality | 质量管控 |
| openclaw-governance-agent | Agent 生命周期 |
| openclaw-governance-nucleus | PDCA 自动进化 |
| openclaw-governance-alert | 告警管理 |
| openclaw-governance-evolution | 系统进化评估 |
| openclaw-governance-incident | 故障响应 |
| openclaw-governance-knowledge | 知识管理 |
| openclaw-governance-pipeline | 流水线执行 |
| openclaw-governance-risk | 风险评估 |

---

## 八、加载规则

```
收到任务 → 判断需要哪些能力 → 加载对应 Skill
```

- **无需创建 task 的简单任务**：直接执行
- **需要创建 task 的任务**：加载 governance-task skill
- **涉及数据分级**：加载 governance-data skill
- **涉及授权决策**：加载 governance-delegation skill
- **涉及质量审核**：加载 governance-quality skill

---

*版本: 3.2.0 | 更新: 2026-04-25 | 变更: 统一变量名 $OPENCLAW_GOV_PATH/$OPENCLAW_WORKSPACE_SYSTEM → $OPENCLAW_GOVERNANCE_DIR（与 openclaw.json env 对齐）

## Related Skills
- [[sider-automation]] - 自动化sider.ai操作，可用于治理框架中的AI评审和对齐
- [[test-nucleus-integration]] - NUCLEUS 4.0集成测试，验证治理框架的Python集成能力
