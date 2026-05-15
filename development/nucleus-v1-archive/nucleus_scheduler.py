#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NUCLEUS Scheduler CLI - Heartbeat 入口

用法：
  python nucleus_scheduler.py --agent_id {agent_id}
      触发 heartbeat，创建新 CycleUnit，输出 JSON 结果

  python nucleus_scheduler.py --agent_id {agent_id} --check-pending
      扫描 cycles/ 中 verdict=pending 或 pending_sampling 的环，
      供 LLM 在 SKILL.md §4.4 协议中继续处理

  python nucleus_scheduler.py --agent_id {agent_id} --status
      输出当前调度器状态（计数器、活跃数、等待队列）

Author: 张铁 (CQO)
Date: 2026-04-06 | Updated: 2026-04-16
"""

import os
import sys
import json
import glob
import argparse
import yaml
from datetime import datetime, timezone


# ── 路径初始化 ────────────────────────────────────────

def _setup_paths():
    """将 skill 根目录加入 sys.path 并切换 CWD，确保 core/ modules/ 可导入且文件路径正确解析"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.dirname(script_dir)  # scripts/ 的上级 = skill 根目录
    if skill_root not in sys.path:
        sys.path.insert(0, skill_root)
    # 所有模块使用相对路径（cycles/ logs/ 等），必须以 skill 根目录为 CWD
    os.chdir(skill_root)


# ── 核心操作 ─────────────────────────────────────────

def run_heartbeat(agent_id: str) -> dict:
    """触发 heartbeat，返回 created_cycles 等结果"""
    _setup_paths()
    try:
        from core.scheduler import on_heartbeat
        result = on_heartbeat()
        _write_log('nucleus_scheduler_result', result, agent_id)
        return result
    except ImportError as e:
        msg = f"NUCLEUS import failed: {e}"
        _write_log('nucleus_scheduler_error', {'message': msg}, agent_id)
        return {'triggered_scopes': [], 'created_cycles': [], 'errors': [msg]}
    except Exception as e:
        msg = f"NUCLEUS scheduler error: {e}"
        _write_log('nucleus_scheduler_error', {'message': msg}, agent_id)
        return {'triggered_scopes': [], 'created_cycles': [], 'errors': [msg]}


def check_pending(agent_id: str) -> dict:
    """
    扫描 cycles/ 下所有 pending / pending_sampling 的 CycleUnit。

    供 LLM 在 SKILL.md §4.4 协议中检查是否有上一轮等待审批的环
    已被回填 verdict，可以继续执行 Act 阶段。

    Returns:
        {
            'pending_cycles': [
                {
                    'cycle_id': str,
                    'scope': str,
                    'path': str,
                    'verdict': 'pending' | 'pending_sampling',
                    'requested_at': str | None
                }
            ],
            'ready_to_act': [   # verdict 已回填（非 pending），可继续 Act
                {
                    'cycle_id': str,
                    'scope': str,
                    'path': str,
                    'verdict': str
                }
            ]
        }
    """
    _setup_paths()

    pending_cycles = []
    ready_to_act = []

    scopes = ['task', 'topic', 'project', 'system']
    for scope in scopes:
        pattern = f"cycles/{scope}/*.yaml"
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cycle_data = yaml.safe_load(f)

                if not cycle_data:
                    continue

                phase = cycle_data.get('phase')
                verdict = cycle_data.get('check', {}).get('verdict')

                # 只关注 check 阶段未完成的环
                if phase not in ('check', 'act'):
                    continue

                cycle_id = cycle_data.get('id', os.path.splitext(os.path.basename(file_path))[0])

                if verdict in ('pending', 'pending_sampling'):
                    pending_cycles.append({
                        'cycle_id': cycle_id,
                        'scope': scope,
                        'path': file_path,
                        'verdict': verdict,
                        'requested_at': cycle_data.get('check', {})
                                                   .get('human_review', {})
                                                   .get('requested_at')
                    })
                elif verdict in ('pass', 'partial', 'fail', 'skip') and phase == 'check':
                    # verdict 已被回填，等待 Act
                    ready_to_act.append({
                        'cycle_id': cycle_id,
                        'scope': scope,
                        'path': file_path,
                        'verdict': verdict
                    })

            except Exception:
                continue

    result = {
        'pending_cycles': pending_cycles,
        'ready_to_act': ready_to_act
    }
    _write_log('nucleus_check_pending', result, agent_id)
    return result


def get_status(agent_id: str) -> dict:
    """输出调度器当前状态"""
    _setup_paths()
    try:
        from core.scheduler import get_scheduler_status
        return get_scheduler_status()
    except Exception as e:
        return {'error': str(e)}


# ── 日志 ─────────────────────────────────────────────

def _write_log(log_type: str, data: dict, agent_id: str) -> None:
    """写入 JSONL 日志"""
    try:
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'agent_id': agent_id,
            'type': log_type,
            'data': data
        }
        with open(f"{log_dir}/{today}.jsonl", 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"WARNING: Failed to write log: {e}", file=sys.stderr)


# ── CLI 入口 ─────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='NUCLEUS 4.0 Scheduler CLI'
    )
    parser.add_argument('--agent_id', required=True, help='Agent ID（如 cqo、cto）')
    parser.add_argument('--check-pending', action='store_true',
                        help='扫描 pending/pending_sampling 的 CycleUnit（§4.4 轮询）')
    parser.add_argument('--status', action='store_true',
                        help='输出调度器当前状态')

    args = parser.parse_args()

    if args.check_pending:
        result = check_pending(args.agent_id)
    elif args.status:
        result = get_status(args.agent_id)
    else:
        result = run_heartbeat(args.agent_id)

    print(json.dumps(result, ensure_ascii=False, indent=2))