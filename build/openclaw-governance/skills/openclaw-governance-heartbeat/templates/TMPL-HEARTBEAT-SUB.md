# HEARTBEAT.md · {agent_name} ({agent_id})

> **版本**：v3.3（新增 MISSION_BOARD.md 文件编辑强制要求）
> **更新日期**：2026-04-18
> **关联 Skill**：governance-heartbeat v5.6.0

---

## 一、汇报规则（所有 Sub Agent 必须遵守）

> **来源**：governance-heartbeat SKILL.md §五

### 1.1 汇报类型

| 汇报类型 | 时间 | 内容 | 条件 |
|----------|------|------|------|
| **晨会报告** | 早 7:00 左右 | 任务进展、阻塞、今日计划 | 每日固定 |
| **夕会报告** | 晚 9:00 左右 | 今日完成、明日计划 | 每日固定 |
| **异常报告** | 实时 | 只报告变化/异常部分 | 有异常或阻塞时 |

### 1.2 报告失败处理

**晨会/夕会报告发送失败时**：
1. 报告发送失败 → 5分钟后重试（最多2次）
2. 2次重试均失败 → 记录失败，等待下一个定时汇报周期
3. 严重情况（连续2天失败） → 标记异常，等待人工处理

**超时设置**：报告生成超时 5分钟

### 1.3 静默执行规则

**其他时间（非 7:00/21:00）**：
- 执行完整 heartbeat 流程（Step 1-4）
- 更新 MISSION_BOARD
- **不发飞书消息**（除非有异常或状态变更）
- 本地记录到 `heartbeat-state.json`

### 1.4 报告模板

**晨会报告**：
```markdown
晨会报告 · YYYY-MM-DD 07:00

📋 任务进展：
- 活跃任务：N 个
- 进行中：[Task 名称]

🚫 阻塞：[无/具体阻塞]

📅 今日计划：
- [ ] [计划事项 1]

状态：🟢/🟡/🔴
```

**夕会报告**：
```markdown
夕会报告 · YYYY-MM-DD 21:00

✅ 今日完成：
- [x] [完成事项 1]

📊 统计：
- 本周完成任务数：N
- 活跃任务：N 个

📅 明日计划：
- [ ] [计划事项 1]

状态：🟢/🟡/🔴
```

---

## 二、执行流程

> **详细规则**：governance-heartbeat SKILL.md §六

### 2.1 标准步骤

```
[Step 1] 读取 MISSION_BOARD.md
    1.1 根据 Agent 类型选择正确路径：
        - main Agent: MISSION_BOARD.md（根目录）
        - 其他 Agent: 60_Agents/{agent_id}/MISSION_BOARD.md

[Step 2] 扫描待处理任务
    2.1 根据 Agent ID 识别任务格式：
        - cic: T\d+(-[A-Z]+)?-\d+ (例如：T01-CORE-01, T02-API-03)
        - cio: ZT-P\d+-T\d+ (例如：ZT-P001-T01, ZT-P015-T05)
        - 其他 Agent: 遵循项目任务编号规范（通常为 ZT-P\d+-T\d+）
    2.2 从 MISSION_BOARD 中提取匹配的任务
    2.3 按优先级排序（P0 > P1 > P2 > P3）

[Step 3] 执行任务推进（至少 1 个）
[Step 4] 更新状态文件
```

### 2.2 Skills 加载

```
if Heartbeat 执行:
    read governance-heartbeat SKILL.md
    
    # ⭐ 根据 Agent 类型读取正确的 MISSION_BOARD
    if agent_id == "main":
        read MISSION_BOARD.md  # 根目录
    else:
        read 60_Agents/{agent_id}/MISSION_BOARD.md
    
    # 根据情况加载对应 Skill（见 SKILL.md §二）
```

---

## 三、本地检查列表（轮换执行）

> **MISSION_BOARD 更新自检**：每次 Heartbeat 必须执行！

### 3.1 必须执行的检查项

- [ ] **读取 MISSION_BOARD**：了解当前项目状态 ⭐
- [ ] 项目状态：是否有新任务/阻塞？
- [ ] 任务推进：执行至少 1 个待办事项
- [ ] 记忆更新：沉淀重要事项到 MEMORY.md？
- [ ] **更新 MISSION_BOARD.md 文件**：状态变更后立即更新 ⭐

### 3.2 MISSION_BOARD.md 文件更新操作步骤 ⭐ 必须执行

**每次 Heartbeat 必须执行以下文件编辑操作**（不是只发消息，必须编辑文件）:

**Step 1: 检查最后更新时间**
```
读取 MISSION_BOARD.md §九 "最后更新" 字段
if 超过 24 小时 → ⚠️ 警告并立即执行 Step 2
```

**Step 2: 使用 edit 工具更新 MISSION_BOARD.md**
```json
// 必须更新的字段（使用 edit 工具）:
edit(path="MISSION_BOARD.md", edits=[
  {oldText: "最后更新：YYYY-MM-DD HH:MM", newText: "最后更新：当前时间"},
  {oldText: "整体状态 | 🟢 正常", newText: "整体状态 | 🟢 正常（当日 heartbeat 已执行）"}
])
```

**Step 3: 验证更新成功**
```
重新读取 MISSION_BOARD.md 检查 "最后更新" 字段
if 未更新成功 → ⚠️ 警告并重试一次
```

### 3.3 MISSION_BOARD 更新规则

| 检查项 | 条件 | 动作 |
|--------|------|------|
| **最后更新时间** | 超过 24 小时 | ⚠️ 立即更新（使用 edit 工具） |
| **Task 状态同步** | 有状态变更但未更新 | 立即更新 §三/§五（使用 edit 工具） |
| **Heartbeat 执行** | 每次 heartbeat | 必须更新 §九 最后更新时间 ⭐ |

**禁止行为**：
- ❌ Heartbeat 执行但不使用 edit 工具更新 MISSION_BOARD.md
- ❌ 只通过 message 工具发送报告，但不编辑文件
- ❌ 只更新 heartbeat-state.json，但不编辑 MISSION_BOARD.md

---

## 四、异常处理规则

### 4.1 异常触发条件

| 异常类型 | 触发条件 | 处理 |
|----------|----------|------|
| **任务阻塞** | 超过 2 天无进展 | 发飞书通知 + 记录到 MISSION_BOARD §三 |
| **依赖等待** | 等待其他 Agent 超过 4 小时 | 每 2 小时询问 1 次 |
| **外部阻塞** | 等待外部输入超过 24 小时 | 记录并等待，每天检查 1 次 |

### 4.2 失败重试策略

**飞书消息发送失败**：
1. 立即重试 1 次
2. 延迟 5 分钟重试
3. 延迟 15 分钟重试
4. 记录失败日志，等待下一个定时汇报周期

**上限**：最多 2 次重试（与 §一.2 统一）

### 4.3 失败降级规则

**重试2次均失败后**：
1. **立即通知**：发送 P1 优先级通知给 Agent Owner + Harold
2. **标记状态**：在 heartbeat-state.json 中记录 `failureEscalation.triggered = true`
3. **等待人工处理**：暂停自动重试，等待人工干预

**降级策略**：
- 如果是任务执行失败 → 标记任务为「待人工恢复」
- 如果是报告发送失败 → 简化报告格式，仅发送关键信息

**恢复条件**：
- **人工重置**：Harold 手动确认恢复
- **任务恢复**：失败任务已解决，可正常执行
- **自动恢复**：24小时超时自动重置（需谨慎）

### 4.4 异常规则优先级

**当任务同时触发多个异常条件时**：

| 优先级 | 触发条件 | 处理方式 |
|--------|----------|----------|
| **P0** | 阻塞2天 + 关键路径任务 | 立即通知 Harold |
| **P1** | 阻塞2天 或 (依赖等待4小时 + 外部阻塞24小时) | 发飞书通知 + 记录 |
| **P2** | 仅外部阻塞24小时 | 记录并等待 |

**去重规则**：使用最高优先级规则处理

---

## 五、状态记录

**文件路径**：`memory/heartbeat-state.json`

**模板路径**：`governance-heartbeat/templates/heartbeat-state.json`

**初始化方式**：
```bash
# 从模板复制到 Agent 目录
cp templates/heartbeat-state.json memory/heartbeat-state.json

# 替换占位符
# ${AGENT_ID} → {agent_id}
# ${OPENCLAW_LOCAL_WORKSPACE} → 实际路径
```

---

## 六、无需检查时

回复 `HEARTBEAT_OK`

---

## 七、版本管理

**当前版本**：v3.0（标准化模板）

**兼容性**：
- 替代原有 v2.0-v7.0 各版本
- Agent 自行从本模板学习，无需迁移工具

---

*Version: v3.3 - 2026-04-18 新增 MISSION_BOARD.md 文件编辑强制要求（方案 A+B）*