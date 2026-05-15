
# ADR-001 · Agent 文件分层架构决策

## 元数据

| 字段 | 内容 |
|---|---|
| **编号** | ADR-001 |
| **标题** | Agent 文件分层架构：灵魂层 / 身份层 / 执行层三层分离原则 |
| **状态** | ✅ 已批准 |
| **批准人** | Harold |
| **起草人** | Claude（参谋） |
| **批准日期** | 2026-02-24 |
| **关联项目** | NUC-TP01 · Agent 宪法体系 |

---

## 一、背景

掌天智能 openclaw 多 Agent 系统中，每个 Agent 拥有独立的 workspace 和 agentDir。在 NUC-TP01 执行过程中，发现需要明确以下问题：

- SOUL.md 应存放在哪里？是否每个 Agent 各有一份？
- IDENTITY.md 是模板还是每人一份？
- 随着 Agent 数量增长，文件管理如何保持一致性？

本 ADR 记录上述问题的最终架构决策。

---

## 二、决策内容

### 2.1 权限层级

**银月（main Agent）拥有唯一的最高全权**，是 Harold 的直接对话窗口。

```
银月（main）
├── 可访问所有 Agent workspace
├── 可调用所有 subagent（allowAgents: ["*"]）
├── 负责跨 Agent 协调、文件分发、状态汇总
└── 是唯一可与 Harold 直接交互的 Agent

其他所有 Agent（CEO/CIO/CTO/CCO/CDO/CFO/CVO/EC-CEO/LD）
└── 在自己的 workspace 内操作，不越界
```

### 2.2 文件三层分离原则

| 层级 | 文件 | 性质 | 内容策略 | 变化频率 |
|---|---|---|---|---|
| **灵魂层** | `SOUL.md` | 共同 · 只读 | 全员内容一致，银月维护母版并负责分发 | 极低（版本迭代） |
| **身份层** | `IDENTITY.md` | 专属 · 固定 | 每个 Agent 一份，内容不同，定义角色边界与职责 | 低 |
| **执行层** | `MISSION_BOARD.md` | 专属 · 动态 | 每个 Agent 一份，记录实时任务与状态 | 高 |
| **执行层** | 技能文件 | 专属 · 半固定 | 每个 Agent 一份，定义能力范围 | 中 |
| **执行层** | 记忆文件 | 专属 · 动态 | 每个 Agent 一份，记录上下文与历史 | 高 |

### 2.3 标准 agentDir 目录结构

每个 Agent 的 `agentDir` 遵循以下标准结构：

```
${OPENCLAW_AGENT_LOCAL_WORKSPACE}/{duty}/
├── SOUL.md              # 共同灵魂（内容与母版一致）
├── IDENTITY.md          # 本 Agent 专属宪法
├── MISSION_BOARD.md     # 本 Agent 实时任务看板
└── ...                  # 未来扩展：技能文件、记忆文件等
```

### 2.4 SOUL.md 分发机制

- **母版路径**：`policies/ZT-2026-000_SOUL.md`（Skill 内置规范文件）
- **分发责任人**：银月（main）
- **触发条件**：SOUL.md 版本升级时，银月负责将新版本同步至所有 Agent 的 agentDir
- **各 Agent 副本路径**：`${OPENCLAW_AGENT_LOCAL_WORKSPACE}/{duty}/SOUL.md`

---

## 三、当前 Agent 列表

| ID | 名称 | Workspace |
|---|---|---|
| main | 银月（总指挥） | `${OPENCLAW_LOCAL_WORKSPACE}` |
| ceo | 柳玉 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/ceo` |
| cio | 元瑶 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cio` |
| cto | 菡云芝 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cto` |
| cco | 紫灵 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cco` |
| cdo | 辛如音 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cdo` |
| cfo | 南宫婉 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cfo` |
| cvo | 宝花 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cvo` |
| ec-ceo | 忘语 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/ec-ceo` |
| ld | 厉飞雨 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/ld` |
| cqo | 张铁 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cqo` |
| cic | 大衍神君 | `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/cic` |

---

## 四、变更记录

| 版本 | 日期 | 变更说明 | 变更人 |
|---|---|---|---|
| v1.1 | 2026-04-17 | 补充 cqo（张铁）和 cic（大衍神君）至 Agent 列表 | 银月 |
| v1.0 | 2026-02-24 | 初始版本，正式批准 | Harold |
