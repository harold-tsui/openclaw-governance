# 故障时间线模板

> **Template ID**: TMPL-INCIDENT-TIMELINE
> **用途**: 记录故障从发现到关闭的完整时间线
> **生成时机**: 故障响应过程中持续更新

---

```markdown
# 故障时间线

> **故障 ID**: INC-{YYYY}-{MMDD}-{序号}
> **标题**: {title}
> **更新时间**: {last_update}

---

## 时间线概览

```
{detected_at}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  {closed_at}
     │           │                 │                │                │                │                │
   发现         确认             开始响应          开始恢复          恢复完成          验证通过         关闭
     │           │                 │                │                │                │                │
  {duration}   {duration}         {duration}       {duration}       {duration}       {duration}
```

---

## 详细时间线

| 时间 | 事件类型 | 事件描述 | 操作人 | 备注 |
|------|----------|----------|--------|------|
| {time} | 🚨 发现 | {description} | {agent} | {note} |
| {time} | ✅ 确认 | {description} | {agent} | {note} |
| {time} | 📢 响应 | {description} | {agent} | {note} |
| {time} | 🔧 恢复 | {description} | {agent} | {note} |
| {time} | ✅ 验证 | {description} | {agent} | {note} |
| {time} | 📝 关闭 | {description} | {agent} | {note} |

---

## 阶段详情

### 第一阶段：发现与确认 (Detection & Confirmation)

| 时间 | 事件 | 操作人 | 详情 |
|------|------|--------|------|
| {time} | 告警触发 | {system} | {alert_details} |
| {time} | 告警接收 | {agent} | {receive_details} |
| {time} | 初步调查 | {agent} | {investigation_details} |
| {time} | 故障确认 | {agent} | {confirmation_details} |

**持续时间**: {duration}
**关键决策**: {key_decision}

---

### 第二阶段：响应与团队组建 (Response & Team Assembly)

| 时间 | 事件 | 操作人 | 详情 |
|------|------|--------|------|
| {time} | 故障升级 | {agent} | {escalation_details} |
| {time} | 团队组建 | {commander} | {team_details} |
| {time} | 角色分配 | {commander} | {role_details} |
| {time} | 方案讨论 | {team} | {discussion_details} |

**持续时间**: {duration}
**关键决策**: {key_decision}

---

### 第三阶段：恢复执行 (Recovery Execution)

| 时间 | 事件 | 操作人 | 详情 |
|------|------|--------|------|
| {time} | 恢复方案确认 | {commander} | {plan_details} |
| {time} | 步骤1执行 | {agent} | {step_details} |
| {time} | 步骤2执行 | {agent} | {step_details} |
| {time} | 步骤3执行 | {agent} | {step_details} |
| {time} | 恢复完成 | {agent} | {completion_details} |

**持续时间**: {duration}
**关键决策**: {key_decision}

---

### 第四阶段：验证与关闭 (Verification & Closure)

| 时间 | 事件 | 操作人 | 详情 |
|------|------|--------|------|
| {time} | 功能验证 | {agent} | {verification_details} |
| {time} | 用户验证 | {agent} | {user_verification} |
| {time} | 稳定性监控 | {agent} | {monitoring_details} |
| {time} | 故障关闭 | {commander} | {closure_details} |

**持续时间**: {duration}
**关键决策**: {key_decision}

---

## 时间统计

### 关键指标

| 指标 | 定义 | 实际值 | 目标值 | 达标 |
|------|------|--------|--------|------|
| **MTTD** (Mean Time to Detect) | 发现到确认 | {actual} | {target} | ✅/❌ |
| **MTTR** (Mean Time to Respond) | 确认到开始响应 | {actual} | {target} | ✅/❌ |
| **MTTR** (Mean Time to Recover) | 开始恢复到恢复完成 | {actual} | {target} | ✅/❌ |
| **总时长** | 发现到关闭 | {actual} | {target} | ✅/❌ |

### 分阶段统计

| 阶段 | 开始时间 | 结束时间 | 持续时间 |
|------|----------|----------|----------|
| 发现与确认 | {start} | {end} | {duration} |
| 响应与组建 | {start} | {end} | {duration} |
| 恢复执行 | {start} | {end} | {duration} |
| 验证与关闭 | {start} | {end} | {duration} |

---

## 沟通记录

### 状态更新

| 时间 | 更新内容 | 发送人 | 接收人 |
|------|----------|--------|--------|
| {time} | {content} | {sender} | {receivers} |

### 关键决策

| 时间 | 决策内容 | 决策人 | 影响 |
|------|----------|--------|------|
| {time} | {decision} | {agent} | {impact} |

---

## 附录

### 相关日志

```
{log_snippets}
```

### 相关截图

{screenshots}

---

*记录人: {recorder}*
*创建时间: {created_at}*
*最后更新: {last_update}*
```

---

*Version: 1.0 | Created: 2026-03-31 | Author: 张铁 (cqo)*