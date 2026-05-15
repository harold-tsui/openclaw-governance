# 故障报告模板

> **Template ID**: TMPL-INCIDENT-REPORT
> **用途**: 记录单个故障的完整信息
> **生成时机**: 故障发现时

---

```yaml
---
incident_id: INC-{YYYY}-{MMDD}-{序号}
title: "[SEV-{级别}] {故障标题}"
severity: [SEV-1|SEV-2|SEV-3|SEV-4]
status: [detected|confirmed|responding|recovering|recovered|verified|closed]
source: [alert|user|agent|manual]
created_at: {ISO8601}
detected_at: {ISO8601}
assigned_to: {agent_id}
commander: {指挥人}
---

# 故障详情

## 1. 基本信息

| 字段 | 值 |
|------|-----|
| **故障 ID** | INC-YYYY-MMDD-XXX |
| **级别** | SEV-1/SEV-2/SEV-3/SEV-4 |
| **状态** | detected/confirmed/responding/recovering/recovered/verified/closed |
| **来源** | alert/user/agent/manual |
| **指挥人** | {agent_id} |
| **技术负责** | {agent_id} |

## 2. 描述

{故障详细描述}

## 3. 影响评估

- **影响系统**: {系统列表}
- **影响服务**: {服务列表}
- **影响用户**: {数量/比例}
- **影响功能**: {功能列表}
- **数据影响**: {数据丢失/损坏情况}
- **业务影响**: {业务损失估计}

## 4. 时间线

| 时间 | 事件 | 操作人 | 备注 |
|------|------|--------|------|
| {detected_at} | 故障发现 | {agent} | {备注} |
| {confirmed_at} | 故障确认 | {agent} | {备注} |
| {responding_at} | 开始响应 | {team} | {备注} |
| {recovering_at} | 开始恢复 | {agent} | {备注} |
| {recovered_at} | 恢复完成 | {agent} | {备注} |
| {verified_at} | 验证通过 | {agent} | {备注} |
| {closed_at} | 故障关闭 | {agent} | {备注} |

## 5. 响应团队

| 角色 | 负责人 | Agent ID |
|------|--------|----------|
| **故障指挥** | {name} | {agent_id} |
| **技术负责** | {name} | {agent_id} |
| **沟通负责** | {name} | {agent_id} |
| **记录员** | {name} | {agent_id} |

## 6. 恢复方案

### 6.1 恢复步骤

1. {step_1}
2. {step_2}
3. {step_3}

### 6.2 资源需求

- {resource_1}
- {resource_2}

### 6.3 风险评估

- {risk_1}
- {risk_2}

## 7. 验证记录

### 7.1 验证步骤

- [ ] {check_1}
- [ ] {check_2}
- [ ] {check_3}

### 7.2 验证结果

| 验证项 | 结果 | 备注 |
|--------|------|------|
| {item} | ✅/❌ | {备注} |

## 8. 改进措施

| 措施 | 责任人 | 截止时间 | 状态 |
|------|--------|----------|------|
| {action} | {owner} | {due} | {status} |

## 9. 关联信息

### 关联告警

- 告警 ID: {alert_id}
- 关联关系: 升级/关联

### 关联任务

- 任务 ID: {task_id}
- 关联关系: 恢复任务/改进任务

---

*创建时间: {created_at}*
*最后更新: {updated_at}*
```

---

*Version: 1.0 | Created: 2026-03-31 | Author: 张铁 (cqo)*