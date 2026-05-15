# Session Log 字段映射表

> **版本**：v1.0  
> **日期**：2026-04-05  
> **用途**：定义 Monitor 模块如何从 sessions/*.jsonl 提取监控指标

---

## 一、监控指标映射

### 1.1 user_message_intervals（用户交互间隔）

| 目标字段 | 数据源 | 提取逻辑 | 必需性 |
|---------|--------|----------|--------|
| timestamp | `timestamp` | ISO 8601 时间戳 | 必需 |
| role | `message.role` | 必须等于 "user" | 必需 |

**说明**：
- 这是**用户消息之间的时间间隔**，不是系统 heartbeat 周期
- 系统 heartbeat 监控由 `CycleScheduler` 负责

### 1.2 model_usage（模型使用统计）

| 目标字段 | 数据源 | 提取逻辑 | 必需性 |
|---------|--------|----------|--------|
| provider | `message.provider` | 模型提供商标识 | 必需 |
| model | `message.model` | 模型标识符 | 必需 |
| total_tokens | `message.usage.totalTokens` | 总 token 数量 | 必需 |
| total_cost | `message.cost.total` | 总成本（USD） | 可选 |
| stop_reason | `message.stopReason` | 停止原因 | 必需 |

**降级策略**：
- `usage.totalTokens` 缺失时设为 0
- `cost.total` 缺失时不统计成本
- `stopReason` 缺失时视为 "stop"

### 1.3 error_rate（错误率）

| 目标字段 | 数据源 | 提取逻辑 | 必需性 |
|---------|--------|----------|--------|
| is_error | `message.stopReason` | stopReason != "stop" | 必需 |

**说明**：
- 错误类型包括：timeout, api_error, content_filter 等

### 1.4 session_count（会话计数）

| 目标字段 | 数据源 | 提取逻辑 | 必需性 |
|---------|--------|----------|--------|
| session_id | `id` | 会话 UUID | 必需 |
| cwd | `cwd` | 工作目录 | 必需 |

**说明**：
- 仅统计 `type="session"` 的事件

### 1.5 thinking_level（思考级别分布）

| 目标字段 | 数据源 | 提取逻辑 | 必需性 |
|---------|--------|----------|--------|
| thinking_level | `message.thinkingLevel` | off/on/stream | 可选 |

**说明**：
- 仅在启用 thinking 功能时存在
- 缺失时不统计

---

## 二、增量消费要求

### 2.1 去重机制

Monitor 实现必须采用以下去重机制之一：

**选项 A：filepath + offset**
- 记录每个文件的字节偏移位置
- 每次从上次处理的位置继续

**选项 B：event_id**
- 生成稳定事件 ID：`{session_id}_{line_number}`
- 维护已处理 event_id 集合

**禁止行为**：
- ❌ 仅依赖 mtime 判断文件变化
- ❌ 重跑整个文件导致重复统计

### 2.2 状态存储路径

| 状态类型 | 存储路径 | 说明 |
|---------|----------|------|
| 聚合日志 | `logs/YYYY-MM-DD.jsonl` | 系统根目录 |
| 最新状态 | `logs/latest.json` | 系统根目录 |
| Watermark | `cycles/scheduler_state.yaml` | monitor_watermarks 字段 |

---

## 三、错误处理策略

### 3.1 字段缺失处理

| 场景 | 处理策略 |
|------|----------|
| 必需字段缺失 | 跳过该事件，不崩溃 |
| 可选字段缺失 | 使用默认值或跳过 |
| malformed JSON | 跳过该行，记录错误计数 |

### 3.2 可观测性要求

- 统计 malformed JSON 行数
- 记录字段缺失事件数量
- 监控处理延迟和吞吐量

---

## 四、验证样本

需要至少 3 个真实 session 样本通过 Schema 校验：

1. **正常会话**：包含完整 message 和 usage 字段
2. **错误会话**：包含 stopReason="error" 的事件  
3. **thinking 会话**：包含 thinkingLevel 字段的事件

---

*v1.0 · 2026-04-05 · T0.2 字段映射规范*