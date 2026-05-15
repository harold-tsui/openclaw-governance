---
name: handling-incidents
description: |
  Handling incidents from detection through recovery to postmortem analysis.
  
  Activates when: Incident events detected (keywords: incident, 故障, postmortem, 复盘, recovery)
  
  Capabilities:
  - Incident detection and classification
  - Response and recovery SOPs
  - Postmortem analysis and timeline tracking
  - Incident reporting and documentation
  
  Keywords: incident, fault, postmortem, recovery, detection, escalation
  
  For detailed documentation, see:
  - procedures/ (incident SOPs)
  - templates/ (incident report and postmortem templates)
  
author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "2.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L3"
  os: ["darwin", "linux"]
  tags: ["incident", "postmortem", "recovery", "detection", "escalation"]
---

# 故障管理 - Skill

> **职责**：标准化管理故障从发现到复盘的全生命周期
> **触发**：故障事件（P0/P1 告警升级、手动申报）
> **负责 Agent**：main（银月）

## 何时使用

- **SEV-1/SEV-2 故障发现**: 核心业务完全或严重中断
- **Alert escalation**: P0/P1 告警确认为故障（不是瞬态问题）
- **Postmortem 需要**: 故障恢复后进行根因分析
- **Do NOT use for**: 简单告警管理 — 如果只是 P2/P3 告警，留在 `governance-alert`

## 常见陷阱

1. **SEV-1 需要 Harold 担任事故指挥官**: Harold 必须领导 SEV-1 事件的响应团队。没有 Harold 不要进行。
2. **Postmortem 截止日期是严格的**: SEV-1 = 恢复后 24 小时内。SEV-2 = 恢复后 72 小时内。不要让复盘无限期拖延。
3. **Incident → Alert 不可逆**: 告警一旦确认为故障，在恢复前一直保持故障状态。不要在解决中途"降级"回告警。
4. **5 Whys 是复盘必需的**: SEV-1/SEV-2 复盘必须包含使用 5 Whys 或等效方法的根因分析 — "表面原因"不够充分。
5. **改进项必须有责任人**: 没有指定责任人和截止日期的复盘行动项只是文档，不是改进。

---

## 一、故障分级标准

| 级别 | 定义 | 响应时间 | 恢复目标 | 复盘要求 | 对应告警级别 |
|------|------|----------|----------|----------|-------------|
| **SEV-1** | 核心业务完全中断 | 15 分钟 | 1 小时 | 必须复盘 | P0 |
| **SEV-2** | 核心功能严重受损 | 30 分钟 | 4 小时 | 建议复盘 | P1 |
| **SEV-3** | 非核心功能受影响 | 2 小时 | 24 小时 | 可选复盘 | P2 |
| **SEV-4** | 轻微影响 | 1 天 | 3 天 | 不复盘 | P3 |

---

## 二、故障生命周期

```
发现 → 确认 → 响应 → 恢复 → 验证 → 复盘 → 改进
```

| 阶段 | 触发条件 | 审批级别 | SOP |
|------|----------|----------|-----|
| **故障发现** | P0/P1 告警、用户报告 | L1 | `procedures/INCIDENT-DETECT-SOP.md` |
| **故障响应** | 确认为故障 | L2 | `procedures/INCIDENT-RECOVER-SOP.md` |
| **故障恢复** | 执行恢复操作 | L2 | `procedures/INCIDENT-RECOVER-SOP.md` |
| **故障复盘** | SEV-1/SEV-2 恢复后 | L3 | `procedures/INCIDENT-POSTMORTEM-SOP.md` |

---

## 三、流程文件

| 文件 | 说明 |
|------|------|
| `procedures/INCIDENT-DETECT-SOP.md` | 故障发现流程 |
| `procedures/INCIDENT-RECOVER-SOP.md` | 故障恢复流程 |
| `procedures/INCIDENT-POSTMORTEM-SOP.md` | 故障复盘流程 |

---

## 四、模板文件

| 模板 | 用途 |
|------|------|
| `templates/TMPL-INCIDENT-REPORT.md` | 故障报告模板 |
| `templates/TMPL-POSTMORTEM.md` | 复盘报告模板 |
| `templates/TMPL-INCIDENT-TIMELINE.md` | 故障时间线模板 |

---

## 五、故障来源

| 来源 | 类型 | 转换条件 |
|------|------|----------|
| **告警升级** | P0/P1 告警 | 自动转为故障 |
| **用户报告** | 问题反馈 | 确认后转为故障 |
| **Agent 发现** | 运行异常 | 确认后转为故障 |
| **手动申报** | 预防性报告 | 直接创建故障 |

---

## 六、响应流程

### 7.1 响应团队

| 级别 | 响应团队 | 指挥人 |
|------|----------|--------|
| **SEV-1** | Harold + 银月 + 相关 Agent | Harold |
| **SEV-2** | 银月 + 相关 Agent | 银月 |
| **SEV-3** | 相关 Agent | Agent 负责人 |
| **SEV-4** | 相关 Agent | Agent 负责人 |

### 7.2 响应时间要求

```
SEV-1: 15 分钟内组建响应团队
SEV-2: 30 分钟内组建响应团队
SEV-3: 2 小时内开始处理
SEV-4: 1 天内开始处理
```

---

## 七、复盘机制

### 8.1 复盘触发条件

- SEV-1 故障：**必须复盘**
- SEV-2 故障：**建议复盘**
- SEV-3 故障：**可选复盘**
- SEV-4 故障：不复盘

### 8.2 复盘时间要求

| 级别 | 复盘截止时间 |
|------|--------------|
| SEV-1 | 故障恢复后 24 小时内 |
| SEV-2 | 故障恢复后 72 小时内 |
| SEV-3 | 故障恢复后 1 周内 |

### 8.3 复盘产出

1. **故障报告**：完整的时间线和影响分析
2. **根因分析**：5 Whys 或其他分析方法
3. **改进措施**：具体的行动计划和责任人
4. **经验沉淀**：文档更新、流程改进

---

## 八、改进闭环

```
复盘 → 改进措施 → 执行 → 验证 → 沉淀
```

| 阶段 | 产出 | 责任人 |
|------|------|--------|
| **复盘** | Postmortem 报告 | 故障指挥人 |
| **改进措施** | Action Items | 相关 Agent |
| **执行** | 改进完成 | 相关 Agent |
| **验证** | 验证报告 | 银月 |
| **沉淀** | 文档更新 | 银月 |

---

## 九、触发关键词

- incident、故障
- postmortem、复盘
- 故障恢复、incident recovery
- 根因分析、root cause
- SEV-1、SEV-2、SEV-3、SEV-4

---

## 十、与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| governance-alert | P0/P1 告警升级为故障 |
| governance-heartbeat | 心跳发现异常 |
| governance-task | 故障处理生成任务 |
| governance-evolution | 复盘改进触发进化 |

---

## 十一、SYS-OPS 集成

本 Skill 为 SYS-OPS 项目 **SYS-INCIDENT** Topic 提供能力：

| SYS-INCIDENT 需求 | 本 Skill 支持 |
|-------------------|---------------|
| 故障发现 | ✅ INCIDENT-DETECT-SOP |
| 故障响应 | ✅ INCIDENT-RECOVER-SOP |
| 故障恢复 | ✅ INCIDENT-RECOVER-SOP |
| 故障复盘 | ✅ INCIDENT-POSTMORTEM-SOP |
| 改进闭环 | ✅ 改进机制 |

---

*版本: 2.1.0 | 更新: 2026-04-23 | 变更: 补充 When to Use / Pitfalls 章节 + frontmatter 增强*