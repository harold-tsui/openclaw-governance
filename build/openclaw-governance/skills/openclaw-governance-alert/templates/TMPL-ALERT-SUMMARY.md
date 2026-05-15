# 告警汇总报告模板

> **Template ID**: TMPL-ALERT-SUMMARY
> **用途**: 生成告警统计汇总报告
> **生成时机**: 日报/周报/月报

---

```markdown
# 告警汇总报告

> **报告类型**: [日报|周报|月报]
> **时间范围**: {start_date} - {end_date}
> **生成时间**: {generated_at}
> **生成人**: {agent_id}

---

## 一、概览摘要

{报告摘要，包括关键发现和整体趋势}

---

## 二、统计数据

### 2.1 告警分布

| 级别 | 数量 | 占比 | 环比 |
|------|------|------|------|
| P0 | {count} | {percent}% | {change}% |
| P1 | {count} | {percent}% | {change}% |
| P2 | {count} | {percent}% | {change}% |
| P3 | {count} | {percent}% | {change}% |
| **总计** | **{total}** | **100%** | **{change}%** |

### 2.2 响应时间

| 级别 | 平均响应时间 | 目标 | 达标率 |
|------|--------------|------|--------|
| P0 | {avg_time} | 5min | {rate}% |
| P1 | {avg_time} | 15min | {rate}% |
| P2 | {avg_time} | 1h | {rate}% |
| P3 | {avg_time} | 4h | {rate}% |

### 2.3 处理效率

| 指标 | 数值 |
|------|------|
| 平均处理时间 | {avg_time} |
| MTTR | {mttr} |
| 闭环率 | {rate}% |

---

## 三、关键告警

### 3.1 P0 告警

| ID | 标题 | 时间 | 响应时间 | 处理时间 | 状态 |
|----|------|------|----------|----------|------|
| {alert_id} | {title} | {time} | {response} | {handle} | {status} |

### 3.2 P1 告警

| ID | 标题 | 时间 | 响应时间 | 处理时间 | 状态 |
|----|------|------|----------|----------|------|
| {alert_id} | {title} | {time} | {response} | {handle} | {status} |

---

## 四、趋势分析

### 4.1 告警数量趋势

{趋势描述或图表}

### 4.2 告警类型分布

| 类型 | 数量 | 占比 |
|------|------|------|
| system | {count} | {percent}% |
| service | {count} | {percent}% |
| business | {count} | {percent}% |
| security | {count} | {percent}% |

### 4.3 高频告警 Top 5

| 排名 | 告警模式 | 次数 | 占比 |
|------|----------|------|------|
| 1 | {pattern} | {count} | {percent}% |
| 2 | {pattern} | {count} | {percent}% |
| 3 | {pattern} | {count} | {percent}% |
| 4 | {pattern} | {count} | {percent}% |
| 5 | {pattern} | {count} | {percent}% |

---

## 五、问题分析

{针对关键告警的深入分析}

---

## 六、改进建议

1. {建议1}
2. {建议2}
3. {建议3}

---

## 七、附录

### 告警来源分布

| 来源 | 数量 | 占比 |
|------|------|------|
| heartbeat | {count} | {percent}% |
| agent | {count} | {percent}% |
| external | {count} | {percent}% |
| user | {count} | {percent}% |

---

*生成人: {agent_id} | 生成时间: {generated_at}*
*报告周期: {start_date} - {end_date}*
```

---

*Version: 1.0 | Created: 2026-03-31 | Author: 张铁 (cqo)*