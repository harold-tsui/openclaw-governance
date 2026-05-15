# Log Format Specification - 日志格式规范

> **版本**：v1.0
> **创建日期**：2026-04-06
> **依据**：ARCH v1.4.3 §3.1 + §2.3.3

---

## 一、概述

本规范定义了 NUCLEUS 4.0 系统的日志格式，包括：

- **logs/**：观测日志（Agent 行为记录）
- **executions/**：执行日志（Act 阶段写入）

所有日志采用 JSONL 格式（每行一个 JSON 对象）。

---

## 二、logs/YYYY-MM-DD.jsonl 格式

观测日志记录 Agent 的行为和系统事件。

### 2.1 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| timestamp | string | ✓ | ISO 8601 时间戳（UTC） |
| level | string | ✓ | 日志级别（INFO/WARN/ERROR） |
| message | string | ✓ | 日志消息 |
| source | string | ✓ | 消息来源（Agent ID） |
| metadata | object | ✗ | 元数据 |

### 2.2 示例

```json
{
  "timestamp": "2026-04-06T12:00:00Z",
  "level": "INFO",
  "message": "CycleUnit created successfully",
  "source": "cqo",
  "metadata": {
    "cycle_id": "task-20260406T120000Z-abc123",
    "scope": "task",
    "phase": "plan"
  }
}
```

### 2.3 日志级别

| 级别 | 说明 |
|------|------|
| INFO | 正常操作信息 |
| WARN | 警告信息（不影响功能） |
| ERROR | 错误信息（功能异常） |

---

## 三、executions/YYYY-MM-DD.jsonl 格式

执行日志记录 Act 阶段的具体操作。

### 3.1 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| timestamp | string | ✓ | ISO 8601 时间戳（UTC） |
| action | string | ✓ | 执行动作 |
| scope | string | ✓ | 作用范围（task/topic/project/system） |
| cycle_id | string | ✓ | CycleUnit ID |
| result | string | ✓ | 执行结果（success/failure） |
| metadata | object | ✗ | 执行元数据 |

### 3.2 动作类型

| 动作 | 说明 |
|------|------|
| create_cycle | 创建 CycleUnit |
| apply_adjustment | 应用调整 |
| propagate_adjustment | 传播调整 |
| escalate_review | 升级人工审批 |

### 3.3 示例

```json
{
  "timestamp": "2026-04-06T12:05:00Z",
  "action": "apply_adjustment",
  "scope": "task",
  "cycle_id": "task-20260406T120000Z-abc123",
  "result": "success",
  "metadata": {
    "adjustment_type": "level_change",
    "from_level": "L2",
    "to_level": "L3",
    "requires_confirmation": true
  }
}
```

---

## 四、文件管理

### 4.1 文件命名

- **logs/YYYY-MM-DD.jsonl**：按日期分割
- **executions/YYYY-MM-DD.jsonl**：按日期分割

### 4.2 轮转策略

- 每日自动创建新文件
- 旧文件保留 30 天
- 超过 30 天的文件自动归档到 `logs/archive/`

---

## 五、Monitor 模块兼容性

Monitor 模块通过以下接口消费日志：

```python
def get_log_entries(date: str = None) -> List[Dict]:
    """获取指定日期的日志条目"""

def get_execution_entries(date: str = None) -> List[Dict]:
    """获取指定日期的执行条目"""
```

日志格式必须与上述接口兼容。

---

## 六、验证

### 6.1 格式验证

所有日志写入前必须通过 JSON Schema 验证：

```python
def validate_log_entry(entry: Dict, log_type: str) -> bool:
    """验证日志条目格式"""
```

### 6.2 完整性检查

- 必填字段不能为空
- timestamp 必须为有效 ISO 8601 格式
- level/action 值必须在预定义范围内

---