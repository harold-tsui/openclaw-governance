# 告警报告模板

> **Template ID**: TMPL-ALERT-REPORT
> **用途**: 记录单个告警的完整信息
> **生成时机**: 告警接收时

---

```yaml
---
alert_id: ALERT-{YYYY}-{MMDD}-{序号}
source: [heartbeat|agent|external|user]
timestamp: {ISO8601 时间戳}
title: "[P{级别}] {告警标题}"
description: |
  {详细描述}
  - 影响范围: {范围描述}
  - 影响用户: {用户数量/比例}
  - 数据风险: {有/无}
category: [system|service|business|security]
level: [P0|P1|P2|P3]
status: [open|processing|resolved|closed]
assigned_to: {agent_id}
---

# 告警详情

## 1. 基本信息

| 字段 | 值 |
|------|-----|
| **告警 ID** | ALERT-YYYY-MMDD-XXX |
| **来源** | heartbeat/agent/external/user |
| **级别** | P0/P1/P2/P3 |
| **状态** | open/processing/resolved/closed |
| **责任人** | {agent_id} |

## 2. 描述

{告警详细描述}

## 3. 影响评估

- **影响范围**: {系统/服务/用户}
- **影响用户**: {数量/比例}
- **数据风险**: {描述}
- **业务影响**: {描述}

## 4. 上下文信息

### 相关系统
- {系统名称}
- {系统名称}

### 相关日志
```
{日志片段}
```

### 历史告警
- {历史告警 ID}: {简述}

## 5. 处理记录

| 时间 | 操作人 | 操作 | 备注 |
|------|--------|------|------|
| {时间} | {agent} | 接收 | 自动分配 |
| ... | ... | ... | ... |

## 6. 时间线

| 时间 | 事件 |
|------|------|
| {时间} | 告警触发 |
| {时间} | 告警接收 |
| {时间} | 开始处理 |
| ... | ... |

---

*创建时间: {timestamp}*
*最后更新: {timestamp}*
```

---

*Version: 1.0 | Created: 2026-03-31 | Author: 张铁 (cqo)*