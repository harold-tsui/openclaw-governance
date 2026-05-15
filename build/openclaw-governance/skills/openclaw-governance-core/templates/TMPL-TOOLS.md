# TMPL-TOOLS.md - 会话工具使用指南模板

> **文件性质**：模板文件（新 Agent 创建 TOOLS.md 时使用）
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/skills/openclaw-governance/skills/openclaw-governance-core/templates/`
> **版本**：v1.1
> **创建日期**：2026-04-17
> **更新日期**：2026-04-17
> **更新原因**：Harold 发现 "如果没有活跃会话怎么办" 的关键问题

---

## ⭐ 核心区别：sessions_spawn vs sessions_send

### 通俗比喻（必须理解）

| 工具 | 比喻 | 本质 | 适用场景 |
|------|------|------|----------|
| **sessions_spawn** | **雇佣新员工** | Fork 新进程 | 一次性任务，完成后自动提交报告 |
| **sessions_send** | **与现有同事沟通** | 进程间通信（IPC） | 向已存在的会话发消息，多轮协商 |

**关键区别**：

| 维度 | sessions_spawn | sessions_send |
|------|----------------|---------------|
| **会话状态** | 创建新会话 | 复用已有会话 |
| **生命周期** | 一次性（mode="run"）或持久化（mode="session"） | 已存在会话的延续 |
| **用户可见性** | 默认不可见（后台执行） | 可见（在已有会话中） |
| **结果返回** | 自动推送（announce） | 同步等待或异步投递 |
| **通信方式** | 单向任务分配 | 双向多轮协商（最多 5 轮） |
| **权限要求** | 需要 allowAgents 配置 | 需要会话可见性 |

### 使用场景对比

#### sessions_spawn 典型场景

```typescript
// 场景 1：派专家执行一次性任务
sessions_spawn({
  agent: "analyzer",       // 启动分析专家
  task: "分析这个日志文件", // 任务描述
  mode: "run"              // 一次性，完成后自动报告
})

// 场景 2：并行处理多个分片
sessions_spawn({ agent: "analyzer", task: "处理分片 A" })
sessions_spawn({ agent: "analyzer", task: "处理分片 B" })
sessions_spawn({ agent: "analyzer", task: "处理分片 C" })
// 三个并行执行，完成后各自推送结果
```

#### sessions_send 典型场景

```typescript
// 场景 1：向已启动的专家提问（同步等待）
const reply = await sessions_send({
  sessionKey: "agent:analyzer:subagent-abc",
  message: "这个错误是什么原因？",
  timeoutSeconds: 30  // 等待 30 秒回复
})

// 场景 2：向专家发起多轮协商（异步）
sessions_send({
  sessionKey: "agent:reviewer:session-123",
  message: "请审查这段代码",
  timeoutSeconds: 0   // 立即返回，后台协商
})
// 后台进行最多 5 轮协商，最终结果投递到频道
```

---

## ⭐ 飞书群聊限制：必须 @ 机器人

### 官方文档明确说明

> **来源**：火山引擎官方文档《OpenClaw飞书机器人无响应与连接失败：完整排查指南》
>
> **检查项 8：群聊是否 @机器人？**
>
> **如果是群聊，默认需要 @ 机器人才会响应。**

### 原因解析

**OpenClaw 默认配置**：

```json
{
  "channels": {
    "feishu": {
      "requireMention": true  // 默认值，群聊必须 @ 才响应
    }
  }
}
```

**设计哲学**：
1. **防止滥用**：避免机器人被拉入群后自动回复所有消息
2. **减少噪音**：群聊消息量大，不 @ 不响应可以减少干扰
3. **明确意图**：用户 @ 机器人表示明确希望机器人参与

### 如何测试机器人是否在群聊中正常工作

**正确方式**：
```
用户在群聊中：@机器人 请帮我分析这个日志
机器人：收到，正在分析...  ✅ 正常响应
```

**错误方式**：
```
用户在群聊中：请帮我分析这个日志（未 @）
机器人：（无响应）  ❌ 这是正常行为，不是故障！
```

### 如何修改配置（可选）

如果希望群聊中不 @ 也响应，可以修改配置：

```bash
# 关闭 requireMention（不推荐，会增加噪音）
openclaw config set channels.feishu.requireMention false

# 重启 Gateway
openclaw gateway restart
```

**警告**：关闭后机器人会响应群聊中所有消息，可能导致：
- 大量无效回复（回复不相关的消息）
- 增加 API 调用成本
- 群聊体验下降

---

## 三、完整使用指南

### sessions_spawn 详细参数

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `task` | ✅ | 任务描述（传给子 Agent 的上下文） | - |
| `agentId` | ❌ | 目标 Agent ID（runtime="acp" 时必填） | - |
| `mode` | ❌ | "run"（一次性）或 "session"（持久化） | "run" |
| `thread` | ❌ | 是否绑定到消息线程（mode="session" 时建议 true） | false |
| `runtime` | ❌ | "subagent"（默认）或 "acp"（外部 harness） | "subagent" |
| `model` | ❌ | 子会话模型覆盖 | - |
| `cleanup` | ❌ | "keep"（保留记录）或 "delete"（清理） | "keep" |

**关键约束**：
1. 需要 `agents.list[].subagents.allowAgents` 配置权限
2. 默认最大递归深度 1 层（叶子 Agent 不能再 spawn）
3. 默认最大并发数 5 个/会话

### sessions_send 详细参数

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `message` | ✅ | 发送的消息内容 | - |
| `sessionKey` | ❌ | 目标会话键（推荐） | - |
| `label` | ❌ | 目标会话标签（模糊匹配） | - |
| `timeoutSeconds` | ❌ | 等待回复时间（0=立即返回） | - |

**关键特性**：
1. 支持多轮协商（最多 5 轮 ping-pong）
2. 任一方可回复 `REPLY_SKIP_TOKEN` 结束协商
3. 最终可回复 `ANNOUNCE_SKIP_TOKEN` 保持沉默

---

## 四、常见错误与排查

### 错误 1：sessions_spawn 权限被拒绝

**现象**：
```
agentId is not allowed for sessions_spawn (allowed: none)
agents_list returns allowAny: false
```

**原因**：未配置 allowAgents 白名单

**解决**：
```bash
# 查看官方文档确认正确配置位置
# https://docs.openclaw.ai

# 正确配置路径：agents.list[].subagents.allowAgents
openclaw config set agents.list.main.subagents.allowAgents '["researcher","coder"]'
openclaw gateway restart
```

**教训**：不要盲信 AI 的自我诊断，查阅官方文档确认配置路径

### 错误 2：群聊中机器人不响应

**现象**：群聊中发送消息，机器人无响应

**排查清单**：
1. ✅ Gateway 是否运行？ `openclaw gateway status`
2. ✅ 是否 @ 了机器人？ **默认必须 @**
3. ✅ 机器人是否已加入群聊？
4. ✅ 权限是否已开通？ `im:message.send_as_bot`
5. ✅ 是否已完成用户授权？ `openclaw pairing approve feishu <code>`

**关键教训**：群聊不 @ 不响应是**正常行为**，不是故障！

---

## 五、推荐配置

### 多 Agent 协作推荐配置

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "subagents": {
          "allowAgents": ["*"],  // 允许 spawn 任何 Agent
          "maxSpawnDepth": 2     // 允许 2 层递归（主 -> 子 -> 孙）
        }
      }
    ]
  },
  "channels": {
    "feishu": {
      "requireMention": true  // 保持默认，群聊必须 @
    }
  }
}
```

---

## 六、相关文档

| 文档 | URL | 说明 |
|------|-----|------|
| 官方文档 | https://docs.openclaw.ai/zh-CN/concepts/session-tool | 会话工具完整说明 |
| CSDN 博客 | https://blog.csdn.net/tommychian/article/details/159348509 | sessions_spawn 权限踩坑实录 |
| 火山引擎解析 | https://developer.volcengine.com/articles/7622890850875670555 | sessions_spawn vs sessions_send 深度解析 |
| 飞书排查指南 | https://developer.volcengine.com/articles/7618057705978560518 | 飞书机器人无响应完整排查 |

---

## 七、会话可见性机制（2026-04-17 新增）⭐

> **核心问题**：sessions_send 需要目标会话存在且可见

### 4 种可见性级别

| 级别 | 范围 | 说明 | 适用场景 |
|------|------|------|----------|
| **self** | 仅当前会话 | 最严格 | 高安全场景 |
| **tree** | 当前会话 + 子会话 | 默认值 | 一般场景 |
| **agent** | 该 Agent 所有会话 | 中等宽松 | 本 Agent 内协作 |
| **all** | 所有会话（跨 Agent） | 最宽松 | 跨 Agent 协作 |

### 当前配置（示例）

```json
{
  "tools": {
    "sessions": {
      "visibility": "agent"  // 当前：可见本 Agent 所有会话
    }
  }
}
```

### 跨 Agent 通信要求

| 工具 | 前提条件 | 配置要求 |
|------|----------|----------|
| **sessions_spawn** | 无需会话存在 | `agents.list[].subagents.allowAgents` |
| **sessions_send** | 会话必须存在且可见 | `tools.sessions.visibility=all`（跨 Agent） |

### ⭐ 如果没有活跃会话怎么办？

> **这是 Harold 提出的核心问题！

**正确流程**：

```
需要联系某 Agent
    ↓
1. 检查是否有活跃会话 (sessions_list)
    ↓
├── 有活跃会话
│   ↓
│   2. 检查会话可见性
│   ↓
│   ├── 可见 → sessions_send (复用现有会话)
│   └── 不可见 → sessions_spawn (启动新会话)
│
└── 无活跃会话
    ↓
    sessions_spawn (主动启动)
```

**关键结论**：

1. **sessions_send 不会自动创建会话**
   - 需要会话已存在
   - 需要会话可见（visibility 配置）

2. **如果没有活跃会话 → 必须用 sessions_spawn**
   - sessions_spawn 会创建新会话
   - 不需要会话预先存在

3. **如果会话存在但不可见 → 也必须用 sessions_spawn**
   - sessions_send 会报错 "visibility is restricted"
   - 需要配置 visibility=all 才能看到其他 Agent 的会话

### 会话生命周期管理

**会话状态**：

| 状态 | 说明 | sessions_send 可用性 |
|------|------|---------------------|
| **running** | 正在运行 | ✅ 可用 |
| **done** | 已结束 | ✅ 可用（测试验证） |
| **不存在** | 会话未创建 | ❌ 报错 |

**会话清理**：

```bash
# 查看过期会话
openclaw sessions cleanup --dry-run

# 清理过期会话
openclaw sessions cleanup --enforce
```

**关键发现**：

- sessions_send 可以向 status=done 的会话发送消息（已验证）
- 活跃会话定义：updatedAt 时间范围（不是 status=running）
- sessions_list 的 activeMinutes 参数基于 updatedAt 过滤

---

## 八、版本信息

- **Version**: v1.0
- **Created At**: 2026-04-17
- **Created By**: 张铁 (cqo) + Harold Tsui
- **Status**: Active
- **Review**: 已由 Harold 确认核心区别

---

## 八、推广计划

**立即推广到所有 Agent**：

1. 各 Agent TOOLS.md 添加此章节引用
2. 新 Agent 创建时使用此模板
3. governance-core Skill 中引用此模板

**推广命令**：
```bash
# 各 Agent 目录执行
cp ${OPENCLAW_LOCAL_WORKSPACE}/skills/.../TMPL-TOOLS.md ${AGENT_WORKSPACE}/TOOLS.md
```

---

*本模板由张铁创建，基于 Harold 发现的问题和官方文档梳理。*