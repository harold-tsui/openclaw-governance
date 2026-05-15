# TOOLS.md · {agent_name} ({agent_id})

> **文件性质**：Sub Agent 工具清单 · 可用工具与使用规范
> **存放路径**：`${OPENCLAW_AGENT_LOCAL_WORKSPACE}/{agent_id}/TOOLS.md`
> **版本**：v2.0
> **更新日期**：2026-04-18

---

## 一、OpenClaw 内置工具

| 工具 | 用途 |
|------|------|
| `Read` | 读取文件内容 |
| `Write` | 写入/创建文件 |
| `Edit` | 编辑文件（精确替换） |
| `Bash` | 执行 shell 命令 |
| `Grep` | 搜索文件内容 |
| `Glob` | 文件路径匹配 |
| `Agent` | 启动子 Agent（并行/串行） |
| `WebSearch` | 网络搜索 |
| `WebFetch` | 获取网页内容 |

> 完整工具文档见 [OpenClaw 官方文档](https://docs.openclaw.ai)

---

## 二、跨 Agent 通信

### sessions_spawn vs sessions_send

| 工具 | 本质 | 适用场景 |
|------|------|----------|
| **sessions_spawn** | Fork 新进程 | 一次性任务，完成后自动报告 |
| **sessions_send** | 进程间通信 | 向已存在会话发消息，多轮协商 |

**关键规则**：
- sessions_send 要求目标会话**已存在且可见**
- 如果没有活跃会话 → 必须用 sessions_spawn
- 跨 Agent 通信需要 `tools.sessions.visibility=all` 配置

### 飞书群聊限制

群聊中**必须 @ 机器人**才会响应。这是 OpenClaw 默认行为（`requireMention: true`），不是故障。

---

## 三、Governance Skills 作为工具

Skills 提供你的工具能力。当你需要执行治理流程时，检查对应 Skill 的 `SKILL.md`。

| Skill | 用途 | 触发 |
|-------|------|------|
| `governance-task` | 任务创建/更新/关闭 | 意图触发 |
| `governance-quality` | 审核/验收/DOD 检查 | 意图触发 |
| `governance-data` | 数据分级/路径校验 | 意图触发 |
| `governance-delegation` | 授权/降级/Review 级别 | 意图触发 |
| `governance-heartbeat` | 心跳巡检 | 定时触发 |
| `governance-hierarchy` | 项目/Topic 创建 | 意图触发 |

**Skill 路径**：`skills/openclaw-governance/skills/openclaw-governance-{name}/SKILL.md`

---

## 四、文件路径规范

```bash
# ✅ 正确：使用绝对路径或环境变量
${OPENCLAW_LOCAL_WORKSPACE}/.system/governance/current/config/user/persons.yaml
${OPENCLAW_AGENT_LOCAL_WORKSPACE}/{agent_id}/MISSION_BOARD.md

# ❌ 错误：相对路径或假设路径
./file.md
~/file.md
```

---

## 五、权限边界

| 路径 | 读 | 写 | 说明 |
|------|----|----|------|
| `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/{agent_id}/*` | ✅ | ✅ | 自己的工作空间 |
| `${OPENCLAW_LOCAL_WORKSPACE}/10_Projects/{project_id}` | ✅ | ⚠️ | 参与的项目（写权限需授权） |
| `${OPENCLAW_LOCAL_WORKSPACE}/.system/governance/current/*` | ✅ | ⚠️ | 治理配置（仅银月可写） |
| `${OPENCLAW_LOCAL_WORKSPACE}/SOUL.md` | ✅ | ❌ | 全局灵魂（只读） |
| `${OPENCLAW_AGENT_LOCAL_WORKSPACE}/{other_agent_id}/*` | ✅ | ❌ | 其他 Agent 的输出（只读） |

---

## 六、Agent 专属工具

{agent_specific_tools}

> 由银月在创建 Sub Agent 时定义。

---

## 七、版本信息

- **Version**: v2.0
- **Created At**: {created_at}
- **Last Updated**: 2026-04-18
- **Approved By**: {approved_by}

---

*本文件从 v2.0 起精简，保留核心参考，详细 session 机制见 OpenClaw 官方文档。*
