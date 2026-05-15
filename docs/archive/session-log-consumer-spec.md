# sessions/*.jsonl 消费规范

> **版本**：v1.0
> **日期**：2026-04-05
> **状态**：调研完成，待 Harold 确认

---

## 一、sessions/*.jsonl 本质

**定义**：OpenClaw 框架生成的会话记录文件

**位置**：`~/.openclaw/agents/<agent>/sessions/*.jsonl`

**格式**：JSONL（每行一个 JSON 对象）

**生成者**：OpenClaw Gateway（自动生成）

**消费者**：NUCLEUS 4.0 Monitor 模块（被动读取）

---

## 二、实际文件结构分析

### 2.1 文件位置验证

```bash
ls -la ~/.openclaw/agents/cqo/sessions/*.jsonl
```

**输出**：

```
-rw-------  1 haroldtsui  staff   312442 Apr  5 14:51 343d02f5-c428-4eaa-ae12-2dceeb776a4d.jsonl
-rw-------  1 haroldtsui  staff    19082 Apr  4 08:52 5ea4d7c4-63d8-49e4-b597-068e84f18f18.jsonl
-rw-------  1 haroldtsui  staff   129941 Mar 31 12:37 7b4c9a3f-d6b0-4075-a982-5f913b40237e.jsonl
...
```

### 2.2 事件类型识别

| type | 说明 | 关键字段 |
|------|------|---------|
| `session` | 会话创建 | `id`, `cwd`, `timestamp` |
| `model_change` | 模型切换 | `provider`, `modelId` |
| `thinking_level_change` | 思考级别切换 | `thinkingLevel` |
| `custom` | 自定义事件 | `customType`, `data` |
| `message` | 用户/助手消息 | `role`, `content`, `usage`, `cost` |

---

## 三、message 事件详细结构

### 3.1 用户消息（role=user）

```json
{
  "type": "message",
  "id": "b934660f",
  "parentId": "4c375c5a",
  "timestamp": "2026-04-01T20:29:29.930Z",
  "message": {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "Read HEARTBEAT.md if it exists..."
      }
    ],
    "timestamp": 1775075369927
  }
}
```

### 3.2 助手消息（role=assistant）

```json
{
  "type": "message",
  "id": "26d261f7",
  "parentId": "5130cbc7",
  "timestamp": "2026-04-05T05:15:30.098Z",
  "message": {
    "role": "assistant",
    "content": [
      {
        "type": "thinking",
        "thinking": "This is another heartbeat request...",
        "thinkingSignature": "reasoning_content"
      },
      {
        "type": "text",
        "text": "HEARTBEAT_OK"
      }
    ],
    "api": "openai-completions",
    "provider": "bailian-coding",
    "model": "glm-5",
    "usage": {
      "input": 0,
      "output": 0,
      "cacheRead": 0,
      "cacheWrite": 0,
      "totalTokens": 0,
      "cost": {
        "input": 0,
        "output": 0,
        "cacheRead": 0,
        "cacheWrite": 0,
        "total": 0
      }
    },
    "stopReason": "stop",
    "timestamp": 1775366114262,
    "responseId": "chatcmpl-cb64c019-63d7-98d2-823e-433cd61b1a3e"
  }
}
```

---

## 四、Monitor 模块消费需求

### 4.1 监控事件类型

| Monitor 事件 | 需要的字段 | 计算逻辑 |
|-------------|-----------|---------|
| **heartbeat_interval** | `timestamp`, `type="message"` | 计算相邻 message 的时间差 |
| **model_usage** | `provider`, `model`, `usage.totalTokens`, `cost.total` | 累计统计 |
| **error_rate** | `stopReason="error"` | 计算错误比例 |
| **session_count** | `type="session"` | 统计会话总数 |
| **thinking_level** | `thinkingLevel` | 统计思考级别分布 |
| **model_change_count** | `type="model_change"` | 统计模型切换次数 |

### 4.2 字段到事件映射表

| JSON 字段路径 | Monitor 用途 | 数据类型 |
|--------------|-------------|---------|
| `timestamp` | heartbeat_interval 计算 | string (ISO 8601) |
| `message.role` | 区分用户/助手 | string |
| `message.provider` | 模型提供商统计 | string |
| `message.model` | 模型统计 | string |
| `message.usage.totalTokens` | Token 使用统计 | number |
| `message.cost.total` | 成本统计 | number |
| `message.stopReason` | 错误检测 | string |
| `thinkingLevel` | 思考级别统计 | string |

---

## 五、消费方式

### 5.1 Python 脚本实现

**位置**：`governance-heartbeat/scripts/monitor.py`

**核心逻辑**：

```python
import json
import os
from datetime import datetime

def parse_session_log(filepath):
    """解析 sessions/*.jsonl 文件"""
    events = []
    with open(filepath, 'r') as f:
        for line in f:
            event = json.loads(line)
            events.append(event)
    return events

def calculate_heartbeat_interval(events):
    """计算心跳间隔"""
    message_events = [e for e in events if e.get('type') == 'message']
    if len(message_events) < 2:
        return None
    
    timestamps = [datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) 
                  for e in message_events]
    
    intervals = []
    for i in range(1, len(timestamps)):
        interval = (timestamps[i] - timestamps[i-1]).total_seconds()
        intervals.append(interval)
    
    return intervals

def calculate_model_usage(events):
    """计算模型使用统计"""
    assistant_messages = [e for e in events 
                          if e.get('type') == 'message' 
                          and e.get('message', {}).get('role') == 'assistant']
    
    usage = {}
    for msg in assistant_messages:
        model = msg['message'].get('model')
        provider = msg['message'].get('provider')
        key = f"{provider}/{model}"
        
        if key not in usage:
            usage[key] = {
                'totalTokens': 0,
                'totalCost': 0,
                'count': 0
            }
        
        usage[key]['totalTokens'] += msg['message'].get('usage', {}).get('totalTokens', 0)
        usage[key]['totalCost'] += msg['message'].get('cost', {}).get('total', 0)
        usage[key]['count'] += 1
    
    return usage

def main():
    sessions_dir = os.path.expanduser("~/.openclaw/agents/cqo/sessions")
    
    # 获取最新的 session 文件
    files = [f for f in os.listdir(sessions_dir) if f.endswith('.jsonl')]
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(sessions_dir, f)))
    
    filepath = os.path.join(sessions_dir, latest_file)
    events = parse_session_log(filepath)
    
    # 计算监控指标
    heartbeat_intervals = calculate_heartbeat_interval(events)
    model_usage = calculate_model_usage(events)
    
    result = {
        'heartbeat_intervals': heartbeat_intervals,
        'model_usage': model_usage,
        'event_count': len(events)
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

### 5.2 SKILL.md 调用指导

```markdown
## Monitor 调用

python {baseDir}/scripts/monitor.py --agent cqo --days 7
python {baseDir}/scripts/monitor.py --agent main --output logs/YYYY-MM-DD.jsonl
```

---

## 六、缺字段降级策略

| 缺失字段 | 降级策略 | 说明 |
|---------|---------|------|
| `timestamp` | 跳过事件 | 无法计算时间差 |
| `usage.totalTokens` | 默认值 0 | 保守估计 |
| `cost.total` | 默认值 0 | 保守估计 |
| `provider/model` | 使用 "unknown" | 标记未知模型 |
| `stopReason` | 默认 "stop" | 假设正常结束 |

---

## 七、JSON Schema 定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OpenClaw Session Log Event",
  "type": "object",
  "required": ["type", "id", "timestamp"],
  "properties": {
    "type": {
      "type": "string",
      "enum": ["session", "model_change", "thinking_level_change", "custom", "message"]
    },
    "id": {"type": "string"},
    "parentId": {"type": ["string", "null"]},
    "timestamp": {"type": "string", "format": "date-time"},
    "message": {
      "type": "object",
      "properties": {
        "role": {"type": "string", "enum": ["user", "assistant"]},
        "content": {"type": "array"},
        "provider": {"type": "string"},
        "model": {"type": "string"},
        "usage": {
          "type": "object",
          "properties": {
            "totalTokens": {"type": "number"},
            "cost": {
              "type": "object",
              "properties": {
                "total": {"type": "number"}
              }
            }
          }
        },
        "stopReason": {"type": "string"}
      }
    },
    "thinkingLevel": {"type": "string"}
  }
}
```

---

## 八、确认清单

- [x] sessions/*.jsonl 本质已澄清（OpenClaw 已生成的会话记录）
- [x] 实际文件结构已验证（多个真实文件）
- [x] Monitor 消费需求已定义（6 种监控事件）
- [x] Python 脚本实现示例已提供
- [x] 缺字段降级策略已定义
- [x] JSON Schema 已定义
- [ ] Harold 确认签字

---

*v1.0 · 2026-04-05 · 调研完成，待 Harold 确认*