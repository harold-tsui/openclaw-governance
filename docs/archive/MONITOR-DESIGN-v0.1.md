# Monitor 模块设计草案 v0.1

> **版本**：v0.1  
> **日期**：2026-04-05  
> **状态**：参考实现（非 T0.2 规范的一部分）  
> **基于**：T0.2 消费规范 + Claude Sonnet 4.6 评审建议

---

## 一、设计背景

本文档是 **T5.1 Monitor 模块** 的设计草案，基于 T0.2 深度调研的结论：

- **消费方式**：增量解析 + 聚合存储（filepath + offset 去重）
- **数据路径**：系统级 `logs/` + `cycles/scheduler_state.yaml`
- **约束条件**：零数据库、Harness Engineering、向后兼容

---

## 二、架构设计

### 2.1 目录结构

```
NUCLEUS-4-0/
├── logs/                       # 系统级日志目录（统一）
│   ├── YYYY-MM-DD.jsonl        # Monitor 聚合结果（追加模式）
│   └── latest.json             # 最新状态（覆盖模式）
├── cycles/
│   └── scheduler_state.yaml    # 调度状态（含 monitor_watermarks）
└── modules/
    └── monitor.py              # Monitor 主逻辑
```

**关键变更**（根据 Claude 评审）：
- ❌ 旧方案：`governance-heartbeat/logs/`（分裂日志树）
- ✅ 新方案：系统级 `logs/`（统一路径）

### 2.2 核心流程

```
Heartbeat 触发
    ↓
读取 scheduler_state.yaml（monitor_watermarks）
    ↓
扫描 sessions/*.jsonl（检测新文件）
    ↓
增量解析（只处理 offset 之后的内容）
    ↓
聚合统计（event_id 去重）
    ↓
写入 logs/YYYY-MM-DD.jsonl（追加）
    ↓
更新 scheduler_state.yaml（watermarks）
```

---

## 三、增量更新机制（P0-1 修复）

### 3.1 Watermark 结构

```yaml
# cycles/scheduler_state.yaml
monitor_watermarks:
  "~/.openclaw/agents/main/sessions/abc123.jsonl":
    mtime: 1712345678.123
    last_offset: 1024        # 已处理的字节偏移
    last_event_id: "msg_456" # 最后一条 event_id
  "~/.openclaw/agents/cqo/sessions/def456.jsonl":
    mtime: 1712345679.456
    last_offset: 2048
    last_event_id: "msg_789"
```

### 3.2 增量解析逻辑

```python
def parse_session_file_incremental(filepath: str, watermark: Dict) -> List[Dict]:
    """
    增量解析 JSONL 文件，只处理 offset 之后的内容
    
    Args:
        filepath: JSONL 文件路径
        watermark: {mtime, last_offset, last_event_id}
    
    Returns:
        新事件列表（从 last_offset 之后开始）
    """
    events = []
    current_mtime = Path(filepath).stat().st_mtime
    
    # 1. 检查 mtime 是否变化
    if current_mtime == watermark.get('mtime'):
        # 文件未修改，无需处理
        return []
    
    # 2. 从 last_offset 开始读取
    last_offset = watermark.get('last_offset', 0)
    
    with open(filepath, 'r') as f:
        f.seek(last_offset)  # 跳到上次处理的位置
        
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                obj = json.loads(line)
                
                # 3. 生成稳定的 event_id
                event_id = generate_event_id(filepath, f.tell(), obj)
                
                # 4. 提取监控事件
                event = extract_monitor_event(obj, filepath, line_num, event_id)
                if event:
                    events.append(event)
                    
            except json.JSONDecodeError:
                # 跳过 malformed JSON 行
                continue
    
    # 5. 更新 watermark
    new_watermark = {
        'mtime': current_mtime,
        'last_offset': f.tell(),  # 当前读取位置
        'last_event_id': events[-1]['event_id'] if events else watermark.get('last_event_id')
    }
    
    return events, new_watermark

def generate_event_id(filepath: str, offset: int, obj: Dict) -> str:
    """
    生成稳定的 event_id（用于去重）
    
    格式：session_id + offset
    """
    session_id = obj.get('id', 'unknown')
    return f"{session_id}_{offset}"
```

### 3.3 去重机制

```python
def aggregate_events_incremental(daily_stats: Dict, new_events: List[Dict]) -> Dict:
    """
    聚合新事件（使用 event_id 去重）
    
    Args:
        daily_stats: 当前日统计数据（含 processed_event_ids）
        new_events: 新的监控事件列表
    
    Returns:
        更新后的日统计数据
    """
    # 1. 初始化已处理 event_id 集合
    if 'processed_event_ids' not in daily_stats:
        daily_stats['processed_event_ids'] = set()
    
    # 2. 过滤已处理的事件
    unprocessed_events = [
        event for event in new_events 
        if event['event_id'] not in daily_stats['processed_event_ids']
    ]
    
    # 3. 聚合新事件
    for event in unprocessed_events:
        # ...（聚合逻辑）
        daily_stats['processed_event_ids'].add(event['event_id'])
    
    return daily_stats
```

---

## 四、监控指标设计

### 4.1 用户交互间隔（P1-2 修正）

**概念澄清**（根据 Claude 评审）：
- ❌ 旧名称：`heartbeat_intervals`（概念错位）
- ✅ 新名称：`user_message_intervals`（明确是用户交互间隔）

```json
{
  "user_message_intervals": {
    "mean": 1800,       // 平均间隔（秒）
    "median": 1950,     // 中位数间隔
    "max": 3600,        // 最大间隔
    "min": 300,         // 最小间隔
    "count": 50         // 样本数量
  }
}
```

**说明**：
- 这是用户消息之间的时间间隔，**不是系统 heartbeat 周期**
- 系统 heartbeat 监控由 `CycleScheduler` 负责（参见 T2）

### 4.2 模型使用统计

```json
{
  "model_usage": {
    "bailian-coding/glm-5": {
      "total_tokens": 10000,
      "total_cost": 0.5,
      "count": 50,
      "error_count": 2,
      "avg_tokens_per_request": 200
    },
    "openrouter/anthropic/claude-sonnet-4.6": {
      "total_tokens": 5000,
      "total_cost": 0.3,
      "count": 25,
      "error_count": 0,
      "avg_tokens_per_request": 200
    }
  }
}
```

### 4.3 错误统计

```json
{
  "error_stats": {
    "total_requests": 75,
    "error_count": 2,
    "error_rate": 0.0267,
    "error_types": {
      "timeout": 1,
      "api_error": 1
    }
  }
}
```

---

## 五、实现代码（参考）

### 5.1 Monitor 主逻辑

```python
# modules/monitor.py

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

def on_heartbeat(agent_id: str):
    """
    Monitor 模块主入口（每次 heartbeat 调用）
    
    Args:
        agent_id: Agent ID（main, cqo, ceo, cto）
    """
    # 1. 加载 scheduler_state.yaml
    scheduler_state = load_scheduler_state()
    watermarks = scheduler_state.get('monitor_watermarks', {})
    
    # 2. 扫描 sessions 目录
    sessions_dir = os.path.expanduser(f"~/.openclaw/agents/{agent_id}/sessions")
    session_files = list(Path(sessions_dir).glob("*.jsonl"))
    
    # 3. 增量解析每个文件
    all_events = []
    updated_watermarks = {}
    
    for filepath in session_files:
        filepath_str = str(filepath)
        watermark = watermarks.get(filepath_str, {'mtime': 0, 'last_offset': 0})
        
        events, new_watermark = parse_session_file_incremental(filepath_str, watermark)
        all_events.extend(events)
        updated_watermarks[filepath_str] = new_watermark
    
    # 4. 聚合统计
    today = datetime.now().strftime('%Y-%m-%d')
    daily_file = f"logs/{today}.jsonl"
    daily_stats = load_daily_stats(daily_file)
    
    updated_stats = aggregate_events_incremental(daily_stats, all_events)
    save_daily_stats(daily_file, updated_stats)
    
    # 5. 更新 scheduler_state.yaml
    scheduler_state['monitor_watermarks'] = updated_watermarks
    save_scheduler_state(scheduler_state)
    
    # 6. 更新 latest.json
    save_latest_stats("logs/latest.json", updated_stats)

def load_scheduler_state() -> Dict:
    """加载调度状态"""
    with open("cycles/scheduler_state.yaml", 'r') as f:
        return yaml.safe_load(f)

def save_scheduler_state(state: Dict):
    """原子写入调度状态"""
    tmp_file = "cycles/scheduler_state.yaml.tmp"
    with open(tmp_file, 'w') as f:
        yaml.dump(state, f)
    os.rename(tmp_file, "cycles/scheduler_state.yaml")

# ...（其他辅助函数）
```

---

## 六、DoD Checklist（WBS T5.1）

| DoD 项 | 状态 | 说明 |
|-------|------|------|
| watermark 持久化到 scheduler_state.yaml | ✅ 设计完成 | monitor_watermarks 字段 |
| session 日志字段缺失降级策略 | ⚠️ 待实现 | 参考 T0.2 规范 |
| 日志损坏时跳过并记录告警 | ✅ 设计完成 | malformed JSON 计数 |
| 观测事件写入 logs/YYYY-MM-DD.jsonl | ✅ 设计完成 | 追加模式 |
| 单元测试（3 个真实样本） | ❌ 待实现 | Phase 1 实施 |

---

## 七、风险与限制

### 7.1 当前限制

1. **--days 参数未实现**：当前只处理当天数据（需要扩展时间窗口）
2. **processed_event_ids 内存占用**：大量历史数据时可能膨胀（需要定期清理）
3. **文件首次全量处理**：新 session 文件首次会全量解析（正常行为）

### 7.2 待优化项

1. **event_id 持久化**：processed_event_ids 集合需要定期归档
2. **性能基准测试**：需要测试 100+ JSONL 文件场景
3. **malformed JSON 统计**：建议显式记录损坏行数

---

## 八、下一步行动

1. **Phase 1 实施**：在 T5.1 Task 中实现本设计
2. **单元测试**：验证增量更新和去重机制
3. **性能测试**：基准测试（100 个 JSONL 文件）
4. **集成测试**：与 governance-heartbeat 集成

---

*v0.1 · 2026-04-05 · 参考实现草案（非 T0.2 规范的一部分）*