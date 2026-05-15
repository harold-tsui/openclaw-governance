# ALERT-RECEIVE-SOP · 告警接收流程

> **版本**：v1.0
> **触发条件**：告警事件发生
> **审批级别**：L1（自动接收）
> **预计耗时**：5 分钟

---

## 一、流程概览

```
Step 1: 告警识别 → Step 2: 信息收集 → Step 3: 初步分类 → Step 4: 记录入库 → Step 5: 触发分级
```

---

## 二、详细步骤

### Step 1: 告警识别（预计 1min）

```
□ 确认告警来源（监控/Agent/外部/用户）
□ 验证告警有效性（非误报）
□ 获取告警时间戳
□ 输出：告警基本信息
```

**关键字段**：
- `alert_id`: 唯一标识
- `source`: 来源
- `timestamp`: 时间戳
- `title`: 告警标题
- `description`: 详细描述

---

### Step 2: 信息收集（预计 2min）

```
□ 收集上下文信息
□ 获取相关系统/服务状态
□ 查询历史告警记录
□ 输出：完整告警上下文
```

**收集内容**：
- 影响范围（系统/服务/用户）
- 当前状态
- 相关日志
- 历史告警频率

---

### Step 3: 初步分类（预计 1min）

```
□ 根据告警类型初步分类
  - 系统级：基础设施、网络、存储
  - 服务级：应用服务、API
  - 业务级：业务逻辑、数据
□ 输出：分类结果
```

**分类标签**：
- `system`: 系统告警
- `service`: 服务告警
- `business`: 业务告警
- `security`: 安全告警

---

### Step 4: 记录入库（预计 1min）

```
□ 创建告警记录
□ 分配 alert_id
□ 记录所有信息
□ 输出：告警记录 ID
```

**记录位置**：`.system/governance/current/alerts/{alert_id}.md`

---

### Step 5: 触发分级流程

```
□ 调用 ALERT-ESCALATION-SOP
□ 进入告警分级流程
□ 开始计时（响应时间）
```

**下一步**：`procedures/ALERT-ESCALATION-SOP.md`

---

## 三、告警记录格式

```yaml
# alerts/{alert_id}.md
---
alert_id: ALERT-2026-0331-001
source: heartbeat
timestamp: 2026-03-31T13:20:00+08:00
title: "[P0] Agent 心跳超时"
description: |
  Agent: cqo
  最后心跳: 2026-03-31T13:10:00+08:00
  超时时长: 10 分钟
category: system
status: open
assigned_to: main
---
```

---

## 四、模板文件

- `templates/TMPL-ALERT-REPORT.md`

---

*Version: 1.0 | Created: 2026-03-31*