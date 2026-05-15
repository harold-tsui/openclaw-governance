# 故障复盘报告模板

> **Template ID**: TMPL-POSTMORTEM
> **用途**: 故障复盘后生成复盘报告
> **生成时机**: SEV-1/SEV-2 故障恢复后

---

```markdown
# 故障复盘报告

> **故障 ID**: INC-{YYYY}-{MMDD}-{序号}
> **标题**: [SEV-{级别}] {故障标题}
> **级别**: SEV-{级别}
> **复盘时间**: {postmortem_date}
> **复盘参与人**: {participants}

---

## 一、概述

{故障简要描述，包括发生时间、持续时间、影响范围}

---

## 二、时间线

### 2.1 完整时间线

| 时间 | 事件 | 操作人 | 备注 |
|------|------|--------|------|
| {time} | {event} | {agent} | {note} |
| ... | ... | ... | ... |

### 2.2 关键节点

| 节点 | 时间 | 说明 |
|------|------|------|
| **故障开始** | {start_time} | {description} |
| **故障发现** | {detect_time} | {description} |
| **故障确认** | {confirm_time} | {description} |
| **开始响应** | {respond_time} | {description} |
| **开始恢复** | {recover_time} | {description} |
| **恢复完成** | {resolved_time} | {description} |
| **验证通过** | {verify_time} | {description} |
| **故障关闭** | {close_time} | {description} |

### 2.3 时间统计

| 指标 | 时间 |
|------|------|
| **检测时间** (Detection Time) | {duration} |
| **响应时间** (Response Time) | {duration} |
| **恢复时间** (Recovery Time) | {duration} |
| **总时长** (Total Duration) | {duration} |

---

## 三、影响分析

### 3.1 用户影响

| 维度 | 影响 |
|------|------|
| **影响用户数** | {count} |
| **影响用户比例** | {percent}% |
| **影响地域** | {regions} |
| **影响设备** | {devices} |

### 3.2 功能影响

| 功能 | 影响 | 持续时间 |
|------|------|----------|
| {function} | {impact} | {duration} |

### 3.3 业务影响

| 维度 | 影响 |
|------|------|
| **业务损失** | {estimate} |
| **订单影响** | {count} |
| **支付影响** | {amount} |

### 3.4 数据影响

| 维度 | 影响 |
|------|------|
| **数据丢失** | {yes/no} |
| **数据损坏** | {yes/no} |
| **影响范围** | {description} |

---

## 四、根因分析

### 4.1 5 Whys 分析

```
问题: {问题描述}

Why 1: {原因1}
    ↓
Why 2: {原因2}
    ↓
Why 3: {原因3}
    ↓
Why 4: {原因4}
    ↓
Why 5: {原因5}

根因: {根本原因}
```

### 4.2 贡献因素

| 因素 | 类型 | 影响程度 |
|------|------|----------|
| {factor} | 技术/流程/人员 | 高/中/低 |

### 4.3 根因类型

| 类型 | 说明 |
|------|------|
| **技术** | 代码缺陷、配置错误、架构问题 |
| **流程** | 流程缺失、流程执行不到位 |
| **人员** | 操作失误、知识不足 |

---

## 五、改进措施

### 5.1 措施清单

| 序号 | 措施 | 类型 | 责任人 | 截止时间 | 优先级 | 状态 |
|------|------|------|--------|----------|--------|------|
| 1 | {action} | 技术 | {owner} | {due} | P1 | 待开始 |
| 2 | {action} | 流程 | {owner} | {due} | P2 | 待开始 |
| 3 | {action} | 监控 | {owner} | {due} | P1 | 待开始 |
| 4 | {action} | 文档 | {owner} | {due} | P3 | 待开始 |

### 5.2 措施分类

#### 立即修复

1. {action_1}
2. {action_2}

#### 流程改进

1. {action_1}
2. {action_2}

#### 监控增强

1. {action_1}
2. {action_2}

#### 文档更新

1. {action_1}
2. {action_2}

#### 培训学习

1. {action_1}
2. {action_2}

---

## 六、经验总结

### 6.1 做得好的地方 ✅

1. {what_went_well}
   - 说明: {detail}
2. {what_went_well}
   - 说明: {detail}

### 6.2 需要改进的地方 🔄

1. {what_to_improve}
   - 问题: {problem}
   - 建议: {suggestion}
2. {what_to_improve}
   - 问题: {problem}
   - 建议: {suggestion}

### 6.3 经验沉淀 📝

1. {lesson_1}
   - 应用场景: {scenario}
2. {lesson_2}
   - 应用场景: {scenario}

---

## 七、后续跟踪

### 7.1 改进措施跟踪

| 时间 | 检查项 | 状态 |
|------|--------|------|
| {check_date_1} | 措施1进度检查 | {status} |
| {check_date_2} | 措施2进度检查 | {status} |

### 7.2 验证计划

| 验证项 | 验证方法 | 验证时间 |
|--------|----------|----------|
| {item} | {method} | {date} |

---

## 八、附录

### 8.1 完整日志

```
{log_content}
```

### 8.2 沟通记录

```
{communication_records}
```

### 8.3 截图证据

{screenshots}

---

*复盘人: {author}*
*复盘时间: {postmortem_date}*
*审核人: {reviewer} (银月/Harold)*
*审核时间: {review_date}*
```

---

*Version: 1.0 | Created: 2026-03-31 | Author: 张铁 (cqo)*