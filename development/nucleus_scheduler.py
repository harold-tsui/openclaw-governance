#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NUCLEUS Scheduler Integration Script

将 NUCLEUS 4.0 调度器集成到 OpenClaw heartbeat。

调用方式：
python {baseDir}/scripts/nucleus_scheduler.py --agent_id {agent_id}

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path


# ── NUCLEUS 项目定位 ───────────────────────────────────

def find_nucleus_project():
    """
    定位 NUCLEUS 项目目录
    
    搜索路径：
    1. $OPENCLAW_LOCAL_WORKSPACE/10_Projects/ZT-P015_NUCLEUS-4-0
    2. $OPENCLAW_WORKSPACE/10_Projects/ZT-P015_NUCLEUS-4-0
    3. ./10_Projects/ZT-P015_NUCLEUS-4-0（相对路径）
    """
    
    # 方式1：环境变量
    workspace = os.environ.get('OPENCLAW_LOCAL_WORKSPACE')
    if workspace:
        path = Path(workspace) / '10_Projects' / 'ZT-P015_NUCLEUS-4-0'
        if path.exists():
            return str(path)
    
    # 方式2：备用环境变量
    workspace = os.environ.get('OPENCLAW_WORKSPACE')
    if workspace:
        path = Path(workspace) / '10_Projects' / 'ZT-P015_NUCLEUS-4-0'
        if path.exists():
            return str(path)
    
    # 方式3：硬编码路径（开发环境）
    hardcoded = '/Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0'
    if Path(hardcoded).exists():
        return hardcoded
    
    return None


# ── 调度器执行 ───────────────────────────────────

def execute_nucleus_scheduler(agent_id: str, nucleus_path: str) -> dict:
    """
    执行 NUCLEUS Scheduler
    
    Args:
        agent_id: Agent ID（如 'cqo'）
        nucleus_path: NUCLEUS 项目路径
    
    Returns:
        执行结果 dict
    """
    
    # 切换到 NUCLEUS 项目目录
    original_cwd = os.getcwd()
    os.chdir(nucleus_path)
    
    try:
        # 导入 scheduler 模块
        sys.path.insert(0, nucleus_path)
        from core.scheduler import on_heartbeat
        
        # 执行调度器
        result = on_heartbeat()
        
        # 记录结果
        log_result(agent_id, result, nucleus_path)
        
        return {
            'status': 'success',
            'agent_id': agent_id,
            'nucleus_path': nucleus_path,
            'scheduler_result': result
        }
    
    except ImportError as e:
        return {
            'status': 'error',
            'error_type': 'ImportError',
            'message': f'NUCLEUS scheduler not found: {e}',
            'nucleus_path': nucleus_path
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'error_type': 'Exception',
            'message': str(e),
            'nucleus_path': nucleus_path
        }
    
    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)


def log_result(agent_id: str, result: dict, nucleus_path: str):
    """
    记录调度结果到日志
    
    Args:
        agent_id: Agent ID
        result: 调度器返回结果
        nucleus_path: NUCLEUS 项目路径
    """
    
    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'type': 'nucleus_scheduler_result',
        'agent_id': agent_id,
        'nucleus_path': nucleus_path,
        'data': result
    }
    
    # 写入日志文件
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    log_dir = Path(nucleus_path) / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f'{today}.jsonl'
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


# ── 主入口 ───────────────────────────────────

def main():
    """主入口"""
    
    parser = argparse.ArgumentParser(description='NUCLEUS Scheduler Integration')
    parser.add_argument('--agent_id', required=True, help='Agent ID (如 cqo)')
    parser.add_argument('--test', action='store_true', help='测试模式')
    
    args = parser.parse_args()
    
    # 定位 NUCLEUS 项目
    nucleus_path = find_nucleus_project()
    
    if not nucleus_path:
        result = {
            'status': 'not_found',
            'message': 'NUCLEUS project not found',
            'agent_id': args.agent_id
        }
        print(json.dumps(result, ensure_ascii=False))
        return
    
    # 测试模式
    if args.test:
        result = {
            'status': 'test',
            'agent_id': args.agent_id,
            'nucleus_path': nucleus_path,
            'message': 'NUCLEUS project found, ready to integrate'
        }
        print(json.dumps(result, ensure_ascii=False))
        return
    
    # 执行调度器
    result = execute_nucleus_scheduler(args.agent_id, nucleus_path)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()