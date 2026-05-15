# 告警升级通知模板

> **Template ID**: TMPL-ALERT-ESCALATION
> **用途**: 告警升级时发送通知
> **生成时机**: 告警升级时

---

```markdown
# 🚨 告警升级通知

> **告警 ID**: {alert_id}
> **升级时间**: {escalation_time}
> **升级原因**: {reason}

---

## 告警信息

| 字段 | 值 |
|------|-----|
| **告警级别** | P{level} |
| **告警标题** | {title} |
| **原处理人** | {original_assignee} |
| **升级到** | {escalated_to} |
| **升级类型** | {escalation_type} |

---

## 升级详情

### 升级原因

{reason_detail}

### 升级路径

```
{original_level} ({original_assignee})
    ↓ {escalation_type}
{new_level} ({escalated_to})
```

### 时间线

| 时间 | 事件 |
|------|------|
| {alert_time} | 告警触发 |
| {receive_time} | 告警接收 |
| {timeout_time} | 超时/手动升级触发 |
| {escalation_time} | 升级到 {escalated_to} |

---

## 告警描述

{description}

---

## 当前状态

- **状态**: {status}
- **已等待**: {elapsed_time}
- **目标响应时间**: {target_response_time}

---

## 请立即处理

{action_required}

---

## 相关资源

- 告警详情: {alert_link}
- 处理 SOP: {sop_link}
- 历史告警: {history_link}

---

*自动升级时间: {escalation_time}*
*负责人: {escalated_to}*
```

---

*Version: 1.0 | Created: 2026-03-31 | Author: 张铁 (cqo)*