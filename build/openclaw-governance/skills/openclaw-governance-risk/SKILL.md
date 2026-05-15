---
name: managing-risk
description: |
  Managing risk identification, analysis, response, and monitoring.
  
  Activates when: Project startup, risk discovered, or heartbeat巡检
  
  Capabilities:
  - Risk register creation and maintenance
  - Risk analysis and prioritization
  - Risk response strategy definition
  - Risk monitoring and reporting
  
  Keywords: risk, risk-register, analysis, response, monitoring, mitigation
  
  For detailed documentation, see:
  - templates/TMPL-RISK-REGISTER.md
  
author: "辛如音 (cdo)"
license: "Internal Use Only"
version: "2.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L2"
  os: ["darwin", "linux"]
  owner: "cdo"
  tags: ["risk", "risk-register", "analysis", "response", "monitoring", "mitigation"]
---

# Governance Risk - 风险管理 Skill

> **触发模式**：项目启动/发现风险/Heartbeat 巡检
> 风险登记册、风险分析、风险应对、风险监控

## 何时使用

- **Project startup**: 项目启动时识别风险
- **Risk discovered**: 执行过程中，从 Task-CARD 或 heartbeat 日志发现新风险
- **Heartbeat inspection**: Heartbeat 循环中的定期风险监控
- **Risk escalation**: 风险等级上升（概率/影响增加）
- **Do NOT use for**: 故障管理 — 风险一旦实际化为故障，切换到 `governance-incident`

## 常见陷阱

1. **风险分数 = 概率 × 影响**: 在决定应对策略前，始终计算数值分数（1-9）。不要猜"高/中/低"而不做数学计算。
2. **高风险（6-9）需要立即 Harold 升级**: 不要等到下一次 heartbeat 才上报 — 立即发送飞书 DM。
3. **风险来源是多渠道的**: 检查 TASK-CARD 风险章节、heartbeat 阻塞记录、issue ticket 和变更请求影响分析。不要只看一个来源。
4. **风险应对策略取决于等级**: 高风险 = 规避/转移。中风险 = 减轻。低风险 = 接受。不要对低风险过度设计应对措施。

---

## 一、核心功能

| 功能 | 说明 |
|------|------|
| **identify_risks()** | 识别风险 |
| **analyze_risks()** | 定性风险分析 |
| **plan_risk_responses()** | 规划风险应对 |
| **monitor_risks()** | 监督风险 |
| **report_risk()** | 风险预警上报 |

---

## 二、核心函数

### 2.1 identify_risks() - 识别风险

**职责**：识别项目风险。

**输入**：
```json
{
  "action": "identify_risks",
  "project_id": "ZT-P009",
  "sources": ["task_cards", "heartbeat_logs", "changes"]
}
```

**风险来源**：
- TASK-CARD 中的风险与依赖章节
- Heartbeat 日志中的阻塞记录
- Issue Ticket 中的问题
- 变更请求中的影响分析

**输出**：
```json
{
  "status": "OK",
  "risks_identified": [
    {
      "id": "R-001",
      "description": "资源不足导致延期",
      "source": "TASK-CARD",
      "initial_probability": "中",
      "initial_impact": "高"
    }
  ]
}
```

### 2.2 analyze_risks() - 定性风险分析

**职责**：分析风险概率和影响。

**输入**：
```json
{
  "action": "analyze_risks",
  "project_id": "ZT-P009",
  "risk_id": "R-001"
}
```

**分析维度**：

| 维度 | 等级 | 分值 |
|------|------|------|
| **概率** | 高/中/低 | 3/2/1 |
| **影响** | 高/中/低 | 3/2/1 |
| **风险等级** | 概率 × 影响 | 1-9 |

**风险等级分类**：
- **高风险**：6-9 → 红色，即时上报 Harold
- **中风险**：3-5 → 黄色，记录并跟踪
- **低风险**：1-2 → 绿色，记录即可

**输出**：
```json
{
  "status": "OK",
  "risk_id": "R-001",
  "probability": "中",
  "impact": "高",
  "risk_level": "高",
  "score": 6
}
```

### 2.3 plan_risk_responses() - 规划风险应对

**职责**：制定风险应对策略。

**输入**：
```json
{
  "action": "plan_risk_responses",
  "project_id": "ZT-P009",
  "risk_id": "R-001"
}
```

**应对策略**：

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| **规避** | 消除风险源 | 高影响、可预防 |
| **转移** | 转移给第三方 | 高影响、可转移 |
| **减轻** | 降低概率/影响 | 中等风险 |
| **接受** | 接受风险存在 | 低风险 |

**输出**：
```json
{
  "status": "OK",
  "risk_id": "R-001",
  "response_strategy": "减轻",
  "actions": [
    "协调资源",
    "调整进度"
  ],
  "owner": "main"
}
```

### 2.4 monitor_risks() - 监督风险

**职责**：定期检查风险状态。

**输入**：
```json
{
  "action": "monitor_risks",
  "project_id": "ZT-P009"
}
```

**输出**：
```json
{
  "status": "OK",
  "total_risks": 5,
  "open_risks": {
    "high": 1,
    "medium": 2,
    "low": 2
  },
  "closed_risks": 3,
  "changes": [
    {
      "risk_id": "R-001",
      "change": "概率从低变为中",
      "reason": "资源缺口确认"
    }
  ]
}
```

### 2.5 report_risk() - 风险预警上报

**职责**：向 Harold 上报高风险。

**输入**：
```json
{
  "action": "report_risk",
  "project_id": "ZT-P009",
  "risk_id": "R-001"
}
```

**触发条件**：
- 风险等级 ≥ 6（高风险）
- 风险状态变化（概率/影响上升）
- 新增高风险

**输出**：
```json
{
  "status": "OK",
  "risk_id": "R-001",
  "reported_to": "Harold",
  "channel": "feishu_dm",
  "reported_at": "2026-03-23T17:00:00+08:00"
}
```

---

## 三、对齐机制

### 3.1 内部对齐（本地文档）

| 场景 | 触发 | 对齐文件 |
|------|------|----------|
| **识别风险** | 即时 | RISK-REGISTER.md |
| **分析风险** | 即时 | RISK-REGISTER.md |
| **风险状态变化** | 即时 | RISK-REGISTER.md |
| **Heartbeat 巡检** | 每日 | RISK-REGISTER.md |

### 3.2 外部对齐（飞书）

| 场景 | 触发 | 渠道 |
|------|------|------|
| **发现高风险** | 即时 | 飞书 DM → Harold |
| **风险等级上升** | 即时 | 飞书 DM → Harold |
| **Heartbeat 日报** | 每日 | 飞书 DM → Harold |
| **风险关闭** | 关闭时 | 飞书 DM → Harold |

---

## 四、与 PMBOK 对应

| PMBOK 过程 | 本 Skill |
|------------|----------|
| **识别风险** | identify_risks() |
| **实施定性风险分析** | analyze_risks() |
| **规划风险应对** | plan_risk_responses() |
| **监督风险** | monitor_risks() |

---

## 五、触发关键词

- 风险、风险管理、风险登记册、风险预警、高风险

---

## 六、版本信息

- **Version**: v1.0.0
- **Created At**: 2026-03-23
- **Owner**: CDO (辛如音)

---

*版本: 2.1.0 | 更新: 2026-04-23 | 变更: 补充 When to Use / Pitfalls 章节 + frontmatter 增强*