#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scheduler_state.py — 轻量级多粒度调度计数器

Python 职责：原子读写 config/scheduler_state.yaml（持久化计数器）。
LLM 职责：在 heartbeat 中根据计数器决定哪个 scope 达到触发阈值。

频率设计：
  task:    每 1 heartbeat（~30m）— 计数器每次 heartbeat 递增
  topic:   每 4 heartbeat（~2h）
  project: 每 48 heartbeat（~1d）
  system:  每 96 heartbeat（~2d）

用法：
  python scripts/scheduler_state.py read          # 读取当前计数器
  python scripts/scheduler_state.py bump            # 递增所有计数器
  python scripts/scheduler_state.py check           # 返回应触发的 scope 列表
  python scripts/scheduler_state.py reset scope_id  # 重置某个 scope 计数器

Author: 银月
Date: 2026-04-18
"""

import os
import sys
import json
import yaml
from datetime import datetime, timezone

# ⭐ v6.2.0 修复：使用绝对路径，移除 CWD 依赖（与 pdca.py 保持一致）
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_ROOT = os.path.dirname(_SCRIPT_DIR)
STATE_PATH = os.path.join(_SKILL_ROOT, "config", "scheduler_state.yaml")

DEFAULTS = {
    'scope': 'scheduler_state',
    'tick': 0,
    'task_tick': 0,
    'topic_tick': 0,
    'project_tick': 0,
    'system_tick': 0,
}

# 触发阈值
THRESHOLDS = {
    'task': 1,       # 每个 heartbeat 都触发
    'topic': 4,      # 每 4 个 heartbeat
    'project': 48,   # 每 48 个 heartbeat（约 1 天）
    'system': 96,    # 每 96 个 heartbeat（约 2 天）
}


def _setup():
    """不再需要 CWD 切换，路径已全部绝对路径化（v6.2.0 修复）"""
    pass


def _load() -> dict:
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if data:
            # 合并默认值，防止缺少字段
            for k, v in DEFAULTS.items():
                if k not in data:
                    data[k] = v
            return data
    return dict(DEFAULTS)


def _save(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_PATH) or '.', exist_ok=True)
    tmp = STATE_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        yaml.dump(state, f, allow_unicode=True, default_flow_style=False)
    os.replace(tmp, STATE_PATH)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_state() -> dict:
    """读取当前调度计数器状态"""
    state = _load()
    return {
        'ok': True,
        'tick': state['tick'],
        'counters': {
            'task': state['task_tick'],
            'topic': state['topic_tick'],
            'project': state['project_tick'],
            'system': state['system_tick'],
        },
        'thresholds': THRESHOLDS,
    }


def bump() -> dict:
    """递增所有计数器（heartbeat 每轮调用一次）"""
    state = _load()
    state['tick'] += 1
    state['task_tick'] += 1
    state['topic_tick'] += 1
    state['project_tick'] += 1
    state['system_tick'] += 1
    state['last_bumped'] = _now()
    _save(state)
    return {
        'ok': True,
        'tick': state['tick'],
        'counters': {
            'task': state['task_tick'],
            'topic': state['topic_tick'],
            'project': state['project_tick'],
            'system': state['system_tick'],
        },
    }


def check() -> dict:
    """
    检查哪些 scope 达到触发阈值，并自动重置已触发的计数器。
    heartbeat 根据返回结果执行对应 scope 的 PDCA。

    ⭐ v6.2.0 修复：check() 自动重置计数器，避免 heartbeat 遗漏 reset 导致
    计数器无限增长、所有 scope 每次都触发的问题。
    """
    state = _load()
    triggered = []
    scopes_to_reset = []

    for scope, threshold in THRESHOLDS.items():
        tick_key = f'{scope}_tick'
        current = state.get(tick_key, 0)
        if current >= threshold:
            triggered.append({
                'scope': scope,
                'tick': current,
                'threshold': threshold,
            })
            scopes_to_reset.append(tick_key)

    # 自动重置已触发 scope 的计数器（避免遗漏 reset 导致累积）
    if scopes_to_reset:
        for tick_key in scopes_to_reset:
            state[tick_key] = 0
        state.setdefault('last_reset', {})['auto'] = _now()
        _save(state)

    return {
        'ok': True,
        'tick': state['tick'],
        'triggered': triggered,
        'scopes_needing_action': [t['scope'] for t in triggered],
    }


def reset(scope: str) -> dict:
    """重置某个 scope 的计数器（触发后调用）"""
    tick_key = f'{scope}_tick'
    if tick_key not in DEFAULTS:
        return {'ok': False, 'error': f'未知 scope: {scope}'}

    state = _load()
    state[tick_key] = 0
    state.setdefault('last_reset', {})[scope] = _now()
    _save(state)
    return {
        'ok': True,
        'scope': scope,
        'tick': state['tick'],
        'counter': 0,
    }


def main():
    _setup()

    if len(sys.argv) < 2:
        print("用法: python scripts/scheduler_state.py <read|bump|check|reset>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'read':
        result = read_state()
    elif cmd == 'bump':
        result = bump()
    elif cmd == 'check':
        result = check()
    elif cmd == 'reset':
        if len(sys.argv) < 3:
            print("用法: python scripts/scheduler_state.py reset <scope>")
            sys.exit(1)
        result = reset(sys.argv[2])
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
