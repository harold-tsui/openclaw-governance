#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NUCLEUS Scheduler Integration - 调度器集成

将 NUCLEUS 4.0 调度器集成到 OpenClaw heartbeat 中。

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import json
from datetime import datetime, timezone


def integrate_nucleus_scheduler():
    """
    NUCLEUS 4.0 调度器集成
    
    在 OpenClaw heartbeat 中调用此函数
    """
    
    try:
        # 尝试导入 NUCLEUS 调度器
        from core.scheduler import on_heartbeat
        
        # 执行调度器
        result = on_heartbeat()
        
        # 记录结果
        _log_scheduler_result(result)
        
        return result
        
    except ImportError as e:
        # NUCLEUS 未安装，跳过
        _log_scheduler_info(f"NUCLEUS not found, skipping: {e}")
        return None
        
    except Exception as e:
        # 调度器错误，记录但不影响主流程
        _log_scheduler_error(f"NUCLEUS scheduler error: {e}")
        return None


def _log_scheduler_result(result: dict) -> None:
    """记录调度结果"""
    if result is None:
        return
    
    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'type': 'nucleus_scheduler_result',
        'data': result
    }
    
    _write_log_entry(log_entry)


def _log_scheduler_error(message: str) -> None:
    """记录调度错误"""
    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'type': 'nucleus_scheduler_error',
        'message': message
    }
    
    _write_log_entry(log_entry)


def _log_scheduler_info(message: str) -> None:
    """记录调度信息"""
    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'type': 'nucleus_scheduler_info',
        'message': message
    }
    
    _write_log_entry(log_entry)


def _write_log_entry(entry: dict) -> None:
    """写入日志条目"""
    try:
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/{today}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    except Exception as e:
        print(f"WARNING: Failed to write scheduler log: {e}")


# ── 集成使用示例 ────────────────────────────────────

if __name__ == "__main__":
    """
    集成使用示例：
    
    在 governance-heartbeat 的适当位置添加：
    
    ```python
    # Step 3a: NUCLEUS 4.0 调度器集成（非侵入式）
    try:
        from nucleus_scheduler_integration import integrate_nucleus_scheduler
        integrate_nucleus_scheduler()
    except Exception:
        pass  # 错误隔离，不影响主流程
    ```
    """
    
    print("NUCLEUS Scheduler Integration")
    print("Usage: import and call integrate_nucleus_scheduler()")
    
    # 测试集成
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("\nTesting integration...")
        result = integrate_nucleus_scheduler()
        print(f"Result: {result}")