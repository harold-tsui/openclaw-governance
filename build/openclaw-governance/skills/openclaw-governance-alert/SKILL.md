---
name: responding-alerts
description: |
  Responding to alerts with triage, escalation, and notification management.
  
  Activates when: Alert events triggered (keywords: p0_alert, 告警, alert, escalation)
  
  Capabilities:
  - Alert receiving and classification
  - Escalation workflow management
  - Notification routing and formatting
  - Alert summary and reporting
  
  Keywords: alert, alarm, escalation, notification, p0
  
  For detailed documentation, see:
  - procedures/ (alert SOPs)
  - templates/ (alert report templates)
  
author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "2.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L3"
  os: ["darwin", "linux"]
  tags: ["alert", "triage", "escalation", "notification", "p0"]
---

# 告警管理 - Skill

> **职责**：标准化管理告警从接收到闭环的全生命周期
> **触发**：告警事件（P0/P1/P2/P3）
> **负责 Agent**：main（银月）

## 何时使用

- **Alert triggered**: 任何监控系统、Agent 报告或用户反馈表明有问题
- **Alert escalation**: 告警在 SLA 窗口内未被处理
- **Alert summary**: 需要每日/每周告警汇总
- **Do NOT use for**: 故障管理 — 如果 P0/P1 告警升级为故障，切换到 `governance-incident`

## 常见陷阱

1. **Alert → Incident 升级**: 代表核心业务中断的 P0/P1 告警应该转为故障（SEV-1/SEV-2），不应作为告警处理。
2. **响应时间是严格的**: P0 = 5 分钟响应，15 分钟升级。P1 = 15 分钟响应，1 小时升级。不要延迟。
3. **通知路由因级别而异**: P0 = 即时消息 + 电话通知 Harold。P3 = 异步记录到工单系统。不要对 P3 过度通知或对 P0 通知不足。
4. **自动升级是基于时间的**: 如果告警在 SLA 内未被处理，会自动升级。这是自动的 — 不要等它发生，在 SLA 到期前行动。

---

## 一、告警分级标准

| 级别 | 定义 | 响应时间 | 升级时间 | 通知范围 |
|------|------|----------|----------|----------|
| **P0** | 系统不可用、核心业务中断 | 5 分钟 | 15 分钟 | Harold + 银月 + 相关 Agent |
| **P1** | 核心功能受损、影响用户 | 15 分钟 | 1 小时 | 银月 + 相关 Agent |
| **P2** | 非核心功能异常、有限影响 | 1 小时 | 4 小时 | 相关 Agent |
| **P3** | 潜在风险、需关注 | 4 小时 | 24 小时 | 相关 Agent（异步） |

---

## 二、告警流程

```
告警接收 → 告警分级 → 初步响应 → 升级判断 → 处理跟踪 → 闭环确认
```

| 阶段 | 触发条件 | 审批级别 |
|------|----------|----------|
| **告警接收** | 监控系统/外部报告 | L1 |
| **告警分级** | 告警分类 | L1 |
| **升级判断** | 超时/处理困难 | L2/L3 |
| **告警汇总** | 日报/周报需求 | L2 |

---

## 三、模板文件

| 模板 | 用途 |
|------|------|
| `templates/TMPL-ALERT-REPORT.md` | 告警报告模板 |
| `templates/TMPL-ALERT-SUMMARY.md` | 告警汇总模板 |
| `templates/TMPL-ALERT-ESCALATION.md` | 告警升级通知模板 |

---

## 四、告警来源

| 来源 | 类型 | 接收方式 |
|------|------|----------|
| **系统监控** | 自动告警 | Heartbeat 巡检发现 |
| **Agent 报告** | 手动上报 | Agent 主动报告异常 |
| **外部通知** | 第三方系统 | API/消息接收 |
| **用户反馈** | 问题反馈 | 飞书/其他渠道 |

---

## 五、升级规则

### 7.1 自动升级

```
if 告警未在规定时间内处理:
    自动升级到下一级别
    
P0: 5min 无响应 → 升级到 Harold
P1: 15min 无响应 → 升级到银月
P2: 1h 无响应 → 升级到银月
```

### 7.2 手动升级

```
if 处理人无法解决:
    手动升级并说明原因
    触发升级通知流程
```

---

## 六、通知渠道

| 级别 | 通知方式 | 接收人 |
|------|----------|--------|
| **P0** | 即时消息 + 电话 | Harold、银月、相关 Agent |
| **P1** | 即时消息 | 银月、相关 Agent |
| **P2** | 消息 | 相关 Agent |
| **P3** | 异步记录 | 工单系统 |

---

## 七、触发关键词

- p0_alert、告警、alert
- 告警汇总、alert summary
- 告警升级、escalation
- 系统异常、服务中断
- 故障预警、warning

---

## 八、与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| governance-heartbeat | 心跳巡检发现异常 → 触发告警 |
| governance-incident | 告警升级为故障 → 转入故障管理 |
| governance-dispatch | 消息分拣 → 路由到告警处理 |
| governance-task | 告警处理生成任务 |

---

## 九、SYS-OPS 集成

本 Skill 为 SYS-OPS 项目 **SYS-ALERT** Topic 提供能力：

| SYS-ALERT 需求 | 本 Skill 支持 |
|----------------|---------------|
| 告警接收 | ✅ ALERT-RECEIVE-SOP |
| 告警分级 | ✅ 一、告警分级标准 |
| 告警升级 | ✅ ALERT-ESCALATION-SOP |
| 告警通知 | ✅ 通知渠道定义 |
| 告警汇总 | ✅ ALERT-SUMMARY-SOP |

---

*版本: 2.1.0 | 更新: 2026-04-23 | 变更: 补充 When to Use / Pitfalls 章节 + frontmatter 增强*