# HEARTBEAT.md · 银月 (main)

> **版本**：v3.2（统一重试机制 + 状态转移）
> **更新日期**：2026-04-16
> **关联 Skill**：governance-heartbeat v5.5.0

---

## 一、汇报规则（银月专用）

> **来源**：governance-heartbeat SKILL.md §五

### 1.1 汇报类型

| 汇报类型 | 时间 | 内容 | 条件 |
|----------|------|------|------|
| **晨会报告** | 早 7:00 左右 | 全局状态汇总、各 Agent 状态、今日重点 | 每日固定 |
| **夕会报告** | 晚 9:00 左右 | 今日完成汇总、各 Agent 进展、明日计划 | 每日固定 |
| **异常报告** | 实时 | 只报告变化/异常部分 | 有异常或阻塞时 |

### 1.2 报告失败处理

**晨会/夕会报告发送失败时**：
1. 报告发送失败 → 5分钟后重试（最多2次）
2. 2次重试均失败 → 记录失败，等待下一个定时汇报周期
3. 严重情况（连续2天失败） → 标记异常，等待人工处理

**超时设置**：报告生成超时 5分钟

### 1.3 静默执行规则

**其他时间（非 7:00/21:00）**：
- 执行完整 heartbeat 流程（Step 1-8）
- 更新全局 MISSION_BOARD.md
- **不发飞书消息**（除非有异常或状态变更）
- 本地记录到 `heartbeat-state.json`

### 1.4 报告模板

**晨会报告**：
```markdown
晨会报告 · YYYY-MM-DD 07:00

📋 全局状态：
- 活跃 Agent：N 个
- 活跃任务：N 个
- 阻塞任务：N 个

📊 各 Agent 状态：
- CEO (柳玉)：🟢 活跃任务 2
- CTO (菡云芝)：🟢 活跃任务 3
- CDO (辛如音)：🟡 有阻塞 1
...

🚫 阻塞项：
- [具体阻塞描述]

📅 今日重点：
- [ ] [重点事项 1]

状态：🟢/🟡/🔴
```

**夕会报告**：
```markdown
夕会报告 · YYYY-MM-DD 21:00

✅ 今日完成：
- [Agent] 完成事项 1
- [Agent] 完成事项 2

📊 统计：
- 今日完成任务数：N
- 本周完成任务数：N
- 活跃任务：N 个

🚫 待解决阻塞：
- [阻塞描述]

📅 明日计划：
- [ ] [重点事项 1]

状态：🟢/🟡/🔴
```

---

## 二、执行流程（八步）

> **详细规则**：governance-heartbeat SKILL.md §三

### 2.1 八步流程

```
Step 0  Scope Declaration     上下文加载与声明
Step 1  MISSION_BOARD Triage 任务板巡检与分类
Step 2  Review 级别判断     为新增任务确认 Review 级别
Step 3  执行推进 & 状态冒泡 推进阻塞、核查完成、向上同步状态
Step 4  知识沉淀后处理核查 Weekly Review 核查（不阻塞关闭但阻塞归档）
Step 5  授权降级评估         评估是否满足阶段升级或授权降级条件
Step 6  质量管控核查         核查张铁审核状态、质量指标、PDCA 审计队列
Step 7  Harold 日报          汇总今日情况，提交 Harold
Step 8  Heartbeat 归档       记录本次巡检结果
```

### 2.2 Skills 加载

```
if Heartbeat 执行:
    read governance-heartbeat SKILL.md
    read MISSION_BOARD.md (根目录)  # ⭐ 必须读取
    # 分布式扫描所有 Agent 的 MISSION_BOARD
    for agent in agents:
        read 60_Agents/{agent}/MISSION_BOARD.md
    # 根据情况加载对应 Skill（见 SKILL.md §二）
```

---

## 三、分布式扫描

### 3.1 扫描范围与周期

**银月需要扫描所有 Agent 的 MISSION_BOARD**：
```
agents = ["ceo", "cto", "cdo", "cco", "cvo", "cio", "cfo", "cqo", "ld", "ec-ceo"]

for agent in agents:
    read(f"60_Agents/{agent}/MISSION_BOARD.md")
    # 汇总到全局 MISSION_BOARD.md
```

**扫描周期配置**：
- **扫描频率**：每 5 分钟扫描 1 次
- **单次超时**：30 秒获取超时
- **失败重试**：失败后 60 秒重试（最多 2 次）
- **Agent健康检查**：120 秒未响应标记为异常

**扫描失败 vs Agent 未响应区分**：

| 场景 | 触发条件 | 处理方式 |
|------|---------|----------|
| **扫描失败** | 30秒超时（暂态） | 重试60秒（最多2次） |
| **Agent未响应** | 120秒未响应（持续） | 标记异常，继续扫描其他Agent |
| **所有Agent未响应** | 全部Agent 120秒未响应 | 触发分布式系统告警（P1） |

**注意**：扫描失败不等于 Agent 未响应，需区分处理

### 3.2 全局 MISSION_BOARD 维护

银月负责维护根目录的 `MISSION_BOARD.md`：
- 汇总全局状态
- 协调各 Agent
- Harold 日报

---

## 四、实时进展上报（Pop-up）

> **来源**：governance-heartbeat SKILL.md §四

关键步骤立即通过 Feishu 私信通知 Harold：
- 开始分析消息
- 判定为任务
- 任务创建完成
- 收到子 Agent 汇报
- 遇到阻塞

---

## 五、异常处理规则

### 5.1 异常触发条件

| 异常类型 | 触发条件 | 处理 |
|----------|----------|------|
| **Agent 未响应** | 超过 120s 未回复 heartbeat | 记录为「未响应」，继续扫描其他 Agent |
| **全局阻塞** | 多个 Agent 同一阻塞 | 协调解决，升级到 Harold |
| **P0 任务阻塞** | P0 任务超过 4 小时无进展 | 立即通知 Harold |

### 5.2 失败重试策略

**飞书消息发送失败**：
1. 立即重试 1 次
2. 延迟 5 分钟重试
3. 延迟 15 分钟重试
4. 记录失败日志，等待下一个定时汇报周期

**上限**：最多 2 次重试（与 §一.2 统一）

### 5.3 失败降级规则

**重试2次均失败后**：
1. **立即通知**：发送 P1 优先级通知给 Harold
2. **标记状态**：在 heartbeat-state.json 中记录 `failureEscalation.triggered = true`
3. **等待人工处理**：暂停自动重试，等待人工干预

**恢复条件**：
- **人工重置**：Harold 手动确认恢复
- **任务恢复**：失败任务已解决
- **自动恢复**：24小时超时自动重置（需谨慎）

### 5.4 异常规则优先级

**当多个异常同时触发时**：

| 优先级 | 触发条件 | 处理方式 |
|--------|----------|----------|
| **P0** | Agent未响应 + P0任务阻塞 | 立即通知 Harold |
| **P1** | P0任务阻塞 或 (全局阻塞 + Agent未响应) | 协调解决 + 通知 |
| **P2** | 仅全局阻塞 | 协调解决 |

**去重规则**：使用最高优先级规则处理

---

## 六、状态记录

**文件路径**：`.system/governance/heartbeat-state.json`

**模板路径**：`governance-heartbeat/templates/heartbeat-state.json`

**初始化方式**：
```bash
# 从模板复制到银月目录
cp templates/heartbeat-state.json .system/governance/heartbeat-state.json

# 替换占位符
# ${AGENT_ID} → main
# ${OPENCLAW_LOCAL_WORKSPACE} → 实际路径
```

---

## 七、AI 总线机制

> **决策来源**：T08 AI 总线机制研究，Harold 批准实施方案A

Task-CARD 是 Agent 间上下文传递的标准机制。详见 governance-heartbeat skill 第八章。

---

## 八、决策自动化分级驱动

> **调用 governance-delegation v1.2.0**

银月在 heartbeat 中驱动决策自动化分级评估：
- 每次 Task 完成后
- 每周汇总时
- Agent 主动请求时

详见 governance-heartbeat SKILL.md §三.4

---

## 九、无需检查时

回复 `HEARTBEAT_OK`

---

## 十、版本管理

**当前版本**：v3.2（统一重试机制 + 状态转移）

**变更记录**：
- v3.2 (2026-04-16)：统一重试次数为2次 + 新增恢复条件 + 扫描失败区分
- v3.1 (2026-04-16)：补充容错规则
- v3.0 (2026-04-16)：标准化模板

**兼容性**：
- 替代原有 v2.0 精简版
- 银月自行从本模板学习，无需迁移工具

---

*Version: v3.2 - 2026-04-16 统一重试机制 + 状态转移（Main Agent 专用）*