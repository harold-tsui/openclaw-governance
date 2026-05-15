# 修复报告 · NUCLEUS-4.0-TEST-002

> **Task ID**: NUCLEUS-4.0-TEST-002
> **标题**: Heartbeat 周期性任务触发机制缺失修复
> **修复日期**: 2026-04-20
> **修复人**: CTO (菡云芝)
> **状态**: ✅ 修复完成，待银月验收

---

## 一、问题概述

### 1.1 问题发现
- **发现时间**: 2026-04-20 08:02
- **发现人**: Harold
- **问题现象**: 询问备份情况，发现备份已滞后 12 天

### 1.2 影响范围
| 影项 | 具体情况 |
|------|----------|
| **SYS-DATA-OPS-T01** | 每日备份（03:00）→ 最后执行 2026-04-08，滞后 12 天 |
| **SYS-DATA-OPS-T05** | 湖仓监控（09:30）→ 从未执行 |
| **SYS-DATA-OPS-T02** | 周日全量备份 → 从未执行 |
| **数据安全风险** | ⚠️ 高风险 - 12 天数据无备份保护 |

---

## 二、根因分析

### 2.1 表面现象
- Heartbeat 每 30 分钟正常触发 ✅
- Agent 正常读取 MISSION_BOARD ✅
- 但周期性任务从未自动执行 ❌

### 2.2 深层根因
**Heartbeat 缺少时间匹配逻辑**

```
当前 Heartbeat 流程：
  Gateway 每 30 分钟触发 → Agent 读取 MISSION_BOARD → 执行 PDCA → 汇报状态

缺失的逻辑：
  ❌ 检查"当前时间是否匹配任务触发条件"
  ❌ 调用对应的执行脚本（backup.sh 等）
  ❌ 验证执行结果
```

**MISSION_BOARD 定义存在但未被使用**

MISSION_BOARD §十一 定义了周期性任务触发规则：
- SYS-DATA-OPS-T01: 每天 03:00 执行备份
- SYS-DATA-OPS-T05: 每天 09:30 执行湖仓监控
- SYS-DATA-OPS-T02: 每周日 04:30 执行全量备份

但这些定义只是文档，Heartbeat 流程没有读取和匹配逻辑。

### 2.3 根因结论
**设计缺陷**：Heartbeat 只定义了触发机制和巡检流程，但没有周期性任务的时间匹配和触发执行逻辑。

---

## 三、修复方案

### 3.1 设计原则
1. **不引入外部 cron** - 保持 Heartbeat 作为统一触发入口
2. **时间窗口匹配** - 允许 15 分钟偏差，适应 heartbeat 30 分钟周期
3. **执行验证闭环** - 不仅触发执行，还要验证结果
4. **状态可追溯** - 记录每次执行状态到 JSON 文件

### 3.2 修复内容

#### Deliverable 1: heartbeat_scheduler.py（时间匹配引擎）

**功能**：
- 解析 MISSION_BOARD §十一 的周期性任务定义
- 匹配当前时间与任务触发条件
- 识别应执行但未执行的任务
- 调用对应的执行脚本
- 记录执行状态

**用法**：
```bash
# 检查当前应执行的任务
python heartbeat_scheduler.py check

# 触发指定任务
python heartbeat_scheduler.py trigger --task-id SYS-DATA-OPS-T01

# 查看执行状态
python heartbeat_scheduler.py status
```

**时间窗口逻辑**：
```
触发时间: 03:00
时间窗口: 02:45 - 03:15 (前后 15 分钟)
Heartbeat 30 分钟周期内会被捕获
```

#### Deliverable 2: backup_validator.py（执行验证器）

**功能**：
- 检查备份目录是否存在
- 验证备份文件数量和大小
- 检查关键文件是否已备份
- 生成验证报告

**用法**：
```bash
# 检查今日备份
python backup_validator.py check --date 2026-04-20

# 生成备份报告
python backup_validator.py report
```

**验证标准**：
- 增量备份：≥100 文件，≥10MB
- 全量备份：≥500 文件，≥50MB
- 关键文件：MISSION_BOARD.md, SOUL.md, IDENTITY.md 等

#### Deliverable 3: SKILL.md 修订（流程集成）

新增 Step 3b 周期性任务触发引擎：

```
[Step 3b] 周期性任务触发引擎
    0. 时间匹配检查: heartbeat_scheduler.py check
    1. 任务触发: heartbeat_scheduler.py trigger --task-id {id}
    2. 执行验证: backup_validator.py check --date {date}
    3. 状态同步: 更新 MISSION_BOARD + heartbeat-state.json
```

---

## 四、修复执行

### 4.1 文件创建

| 文件 | 路径 | 状态 |
|------|------|------|
| heartbeat_scheduler.py | scripts/heartbeat_scheduler.py | ✅ 已创建 |
| backup_validator.py | scripts/backup_validator.py | ✅ 已创建 |
| SKILL.md 修订版 | SKILL.md (v5.8.0) | ✅ 已修改 |

### 4.2 补漏备份执行

| 操作 | 状态 | 结果 |
|------|------|------|
| 创建备份目录 | ✅ | ~/Workspaces/openclaw.bak/incremental |
| 执行增量备份 | ✅ | 2026-04-20 备份完成 |
| 备份验证 | ✅ | 3908 文件，293MB |

**备份详情**：
```
工作区：/Users/haroldtsui/Workspaces/openclaw/main
备份目录：/Users/haroldtsui/Workspaces/openclaw.bak/incremental/2026-04-20
文件数：3908
目录数：1181
备份大小：293M
```

---

## 五、回归测试计划

### 5.1 测试场景

| 场景 | 测试方法 | 预期结果 |
|------|----------|----------|
| **03:00 任务触发** | 在 02:45-03:15 期间执行 heartbeat_scheduler.py check | 返回 SYS-DATA-OPS-T01 应执行 |
| **09:30 任务触发** | 在 09:15-09:45 期间执行 heartbeat_scheduler.py check | 返回 SYS-DATA-OPS-T05 应执行 |
| **周日任务触发** | 周日 04:15-04:45 期间执行 heartbeat_scheduler.py check | 返回 SYS-DATA-OPS-T02 应执行 |
| **任务已执行检查** | 执行后再次 check | 返回已执行，不重复触发 |
| **备份验证** | 执行 backup_validator.py check | 返回备份有效 |

### 5.2 测试命令

```bash
# 模拟 03:00 时间检查
python heartbeat_scheduler.py check --time 03:00

# 触发备份任务
python heartbeat_scheduler.py trigger --task-id SYS-DATA-OPS-T01

# 验证备份
python backup_validator.py check --date 2026-04-20
```

---

## 六、后续改进建议

### 6.1 短期改进
1. **创建湖仓监控脚本** - SYS-DATA-OPS-T05 目前无执行脚本
2. **配置环境变量** - OPENCLAW_BACKUP_WORKSPACE 需要在系统中配置
3. **添加心跳日志目录** - .system/governance/heartbeat-logs/

### 6.2 中期改进
1. **监控告警** - 备份滞后超过 2 天时发送飞书告警
2. **恢复演练** - 季度恢复测试自动化
3. **备份策略优化** - 根据数据增长调整备份频率

---

## 七、知识沉淀

### 7.1 教训记录
- **教训 1**: 设计文档定义的功能必须要有对应的执行逻辑
- **教训 2**: 周期性任务不能只依赖文档定义，必须有代码实现
- **教训 3**: Heartbeat 作为统一入口，应该包含所有自动化任务的触发

### 7.2 决策库更新
- **决策**: 周期性任务由 heartbeat 时间匹配触发，不引入独立 cron
- **理由**: 保持架构简洁，统一管理入口

---

*修复报告版本: v1.0*
*创建时间: 2026-04-20 10:05*
*负责人: CTO (菡云芝)*