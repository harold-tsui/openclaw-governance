# INCIDENT-DETECT-SOP · 故障发现流程

> **版本**：v1.0
> **触发条件**：P0/P1 告警、用户报告、Agent 发现
> **审批级别**：L1（自动触发）→ L2（确认）
> **预计耗时**：5-15 分钟

---

## 一、流程概览

```
Step 1: 故障信号接收 → Step 2: 初步确认 → Step 3: 故障分级 → Step 4: 故障申报 → Step 5: 响应触发
```

---

## 二、故障来源

| 来源 | 触发条件 | 处理方式 |
|------|----------|----------|
| **告警升级** | P0/P1 告警自动升级 | 自动创建故障 |
| **用户报告** | 飞书/其他渠道 | 确认后创建故障 |
| **Agent 发现** | 运行异常检测 | 确认后创建故障 |
| **手动申报** | 预防性报告 | 直接创建故障 |

---

## 三、详细步骤

### Step 1: 故障信号接收（预计 1min）

```
□ 接收故障信号
□ 记录来源信息
□ 获取初始上下文
□ 输出：故障信号记录
```

**信号记录**：
- `signal_id`: 信号标识
- `source`: 来源
- `timestamp`: 时间戳
- `initial_info`: 初始信息

---

### Step 2: 初步确认（预计 5min）

```
□ 验证故障真实性
□ 排除误报可能性
□ 确认影响范围
□ 输出：确认结果
```

**确认清单**：
- [ ] 是否真实故障？
- [ ] 影响哪些系统/服务？
- [ ] 影响多少用户？
- [ ] 是否正在持续？

**排除误报**：
- 检查是否为计划维护
- 检查是否为监控误配置
- 检查是否为正常业务波动

---

### Step 3: 故障分级（预计 2min）

```
□ 评估影响程度
□ 确定故障级别（SEV-1 到 SEV-4）
□ 评估紧急程度
□ 输出：故障级别
```

**分级标准**：

| 级别 | 影响 | 用户影响 | 功能影响 | 响应时间 |
|------|------|----------|----------|----------|
| **SEV-1** | 核心业务中断 | 全部用户 | 完全不可用 | 15 分钟 |
| **SEV-2** | 核心功能受损 | 大量用户 | 严重受损 | 30 分钟 |
| **SEV-3** | 非核心功能受影响 | 部分用户 | 部分受限 | 2 小时 |
| **SEV-4** | 轻微影响 | 少量用户 | 基本可用 | 1 天 |

---

### Step 4: 故障申报（预计 2min）

```
□ 创建故障记录
□ 分配 incident_id
□ 记录故障信息
□ 输出：incident_id
```

**故障记录格式**：
```yaml
---
incident_id: INC-{YYYY}-{MMDD}-{序号}
title: "[SEV-{级别}] {故障标题}"
severity: [SEV-1|SEV-2|SEV-3|SEV-4]
status: detected
source: [alert|user|agent|manual]
created_at: {ISO8601}
detected_at: {ISO8601}
assigned_to: {agent_id}
---
```

**存储位置**：`.system/governance/current/incidents/{incident_id}/`

---

### Step 5: 响应触发（预计 5min）

```
□ 根据级别组建响应团队
□ 发送通知
□ 开始计时
□ 启动恢复流程
```

**响应团队**：
- SEV-1: Harold + 银月 + 相关 Agent
- SEV-2: 银月 + 相关 Agent
- SEV-3/4: 相关 Agent

**通知内容**：
```markdown
🚨 故障通知

**故障 ID**: {incident_id}
**级别**: SEV-{X}
**标题**: {title}
**时间**: {detected_at}
**影响**: {impact_description}

请立即响应！
```

---

## 四、故障记录目录结构

```
incidents/{incident_id}/
├── INCIDENT.md          # 故障主记录
├── timeline.md          # 时间线
├── logs/                # 相关日志
├── communications/      # 沟通记录
└── postmortem/          # 复盘材料（恢复后）
```

---

## 五、与告警的关系

```
Alert (P0/P1)
    ↓ 自动升级
Incident (SEV-1/SEV-2)
    ↓ 关联
Alert 记录保留，引用 Incident ID
```

---

## 六、模板文件

- `templates/TMPL-INCIDENT-REPORT.md`

---

*Version: 1.0 | Created: 2026-03-31*