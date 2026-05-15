#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler - 多粒度调度器

实现基于 Heartbeat 的多粒度调度逻辑，支持 task/topic/project/system 四层调度。

依据：ARCH v1.4.3 §2.2

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import glob
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# 导入 T2.1 的计数器模块
from core.scheduler_state import (
    increment_counter,
    get_all_triggers,
    get_next_trigger_count
)

# 导入 T2.3 的等待队列模块
from core.wait_queue import (
    add_to_wait_queue,
    get_wait_queue_size
)

# ── 常量定义 ────────────────────────────────────────

# 并发上限（ARCH v1.4.3 §2.2.4）
CONCURRENCY_LIMITS = {
    'task': 10,
    'topic': 5,
    'project': 3,
    'system': 1
}

# 等待队列容量上限（并发上限的 2 倍）
WAIT_QUEUE_LIMITS = {
    'task': 20,
    'topic': 10,
    'project': 6,
    'system': 2
}

VALID_SCOPES = ['task', 'topic', 'project', 'system']

# CycleUnit 文件路径模板
CYCLE_UNIT_PATH_TEMPLATE = "cycles/{scope}/{cycle_id}.yaml"


# ── 核心接口 ────────────────────────────────────────

def on_heartbeat(state_path: str = "cycles/scheduler_state.yaml") -> Dict[str, Any]:
    """
    Heartbeat 入口函数
    
    Returns:
        {
            'triggered_scopes': List[str],  # 触发的 scope 列表
            'created_cycles': List[str],    # 创建的 CycleUnit ID
            'rejected': List[Dict],         # 被拒绝的请求
            'errors': List[str]             # 错误列表
        }
    """
    
    result = {
        'triggered_scopes': [],
        'created_cycles': [],
        'rejected': [],
        'errors': []
    }
    
    try:
        # 1. 递增所有计数器并检查触发
        triggered_scopes = []
        for scope in VALID_SCOPES:
            counter_result = increment_counter(scope, state_path)
            if counter_result['triggered']:
                triggered_scopes.append(scope)
        
        result['triggered_scopes'] = triggered_scopes
        
        # 2. 为每个触发的 scope 创建 CycleUnit
        for scope in triggered_scopes:
            try:
                cycle_id = create_cycle_for_scope(scope)
                if cycle_id:
                    result['created_cycles'].append(cycle_id)
            except Exception as e:
                error_msg = f"Failed to create cycle for {scope}: {str(e)}"
                result['errors'].append(error_msg)
                print(f"ERROR: {error_msg}")
        
    except Exception as e:
        error_msg = f"Scheduler heartbeat failed: {str(e)}"
        result['errors'].append(error_msg)
        print(f"ERROR: {error_msg}")
    
    return result


def should_trigger(scope: str, state_path: str = "cycles/scheduler_state.yaml") -> bool:
    """
    检查指定 scope 是否应该触发
    
    Args:
        scope: 调度范围（task/topic/project/system）
        state_path: 状态文件路径
    
    Returns:
        bool: 是否应该触发
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    # 使用 T2.1 的 increment_counter 来检查是否触发
    # 因为 increment_counter 会实际递增并返回触发状态
    from core.scheduler_state import load_scheduler_state
    
    state = load_scheduler_state(state_path)
    counter = state['counters'].get(scope, 0)
    threshold = state['thresholds'].get(scope, CONCURRENCY_LIMITS.get(scope, 1))
    
    # 如果当前计数 >= 阈值-1，则下一次应该触发
    # 例如：threshold=1, counter=0 → 下一次触发
    #       threshold=4, counter=3 → 下一次触发
    return counter >= (threshold - 1)


def get_active_cycle_count(scope: str) -> int:
    """
    获取指定 scope 的活跃 CycleUnit 数量
    
    Args:
        scope: 调度范围
    
    Returns:
        int: 活跃 CycleUnit 数量
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    # 查找该 scope 下的所有 CycleUnit 文件
    pattern = CYCLE_UNIT_PATH_TEMPLATE.format(scope=scope, cycle_id="*")
    files = glob.glob(pattern)
    
    # 过滤出活跃的 CycleUnit（phase 不是 completed 或 archived）
    active_count = 0
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cycle_data = yaml.safe_load(f)
            
            # 检查 phase 状态
            if cycle_data and 'phase' in cycle_data:
                phase = cycle_data['phase']
                if phase not in ['completed', 'archived']:
                    active_count += 1
        except Exception:
            # 文件损坏或格式错误，跳过
            continue
    
    return active_count


def check_concurrency_limit(scope: str) -> bool:
    """
    检查是否未超过并发上限
    
    Args:
        scope: 调度范围
    
    Returns:
        bool: True 表示未超过上限，可以继续
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    current_count = get_active_cycle_count(scope)
    limit = CONCURRENCY_LIMITS[scope]
    
    return current_count < limit


def create_cycle_for_scope(scope: str) -> Optional[str]:
    """
    为指定 scope 创建 CycleUnit
    
    Args:
        scope: 调度范围
    
    Returns:
        str: 创建的 CycleUnit ID，失败返回 None
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    # 1. 检查并发上限
    if not check_concurrency_limit(scope):
        # 超出并发上限，检查等待队列
        wait_queue_size = get_wait_queue_size(scope)
        if wait_queue_size >= WAIT_QUEUE_LIMITS[scope]:
            # 等待队列也满了，拒绝请求
            log_rejection(scope, "concurrency_limit_exceeded_and_wait_queue_full")
            return None
        else:
            # 加入等待队列
            add_to_wait_queue(scope)
            return None
    
    # 2. 生成 CycleUnit ID
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    cycle_id = f"{scope}-{timestamp}"
    
    # 3. 创建 CycleUnit 目录（如果不存在）
    dir_path = f"cycles/{scope}"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    
    # 4. 创建初始 CycleUnit 数据
    # task_card_path 由 LLM 在 Plan 阶段填充（SKILL.md §4.2 Step 2）
    cycle_data = {
        'id': cycle_id,
        'scope': scope,
        'phase': 'plan',
        'task_card_id': f"auto-{scope}-cycle",
        'task_card_path': None,        # LLM Plan 阶段填充；缺失时跳过本环
        'parent_cycle_id': None,       # schema v1.4：子环由 do.py 填充
        'metadata': {
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'version': 1,
            'global_max_cycles': 100,
            'topic_id': None,          # LLM Plan 阶段填充，供 state_sync 使用
        },
        'plan': {
            'task_card_id': f"auto-{scope}-cycle",
            'task_card_path': None,    # LLM Plan 阶段同步写入（与顶层一致）
            'human_approval_required': False,
            'time_horizon_cycles': 10,
            'max_cycles': 10
        }
    }
    
    # 5. 写入文件
    file_path = CYCLE_UNIT_PATH_TEMPLATE.format(scope=scope, cycle_id=cycle_id)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
        return cycle_id
    except Exception as e:
        print(f"ERROR: Failed to create cycle file {file_path}: {e}")
        return None


# ── 辅助函数 ────────────────────────────────────────

def log_rejection(scope: str, reason: str) -> None:
    """
    记录被拒绝的请求到日志
    
    Args:
        scope: 调度范围
        reason: 拒绝原因
    """
    
    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'scope': scope,
        'reason': reason,
        'action': 'rejected'
    }
    
    # 写入 logs/ 目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    log_file = f"{log_dir}/scheduler_rejections.jsonl"
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            import json
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"WARNING: Failed to log rejection: {e}")

def get_scheduler_status(state_path: str = "cycles/scheduler_state.yaml") -> Dict[str, Any]:
    """
    获取调度器状态摘要
    
    Returns:
        调度器状态字典
    """
    
    status = {}
    
    # 获取计数器状态
    try:
        from core.scheduler_state import load_scheduler_state
        state = load_scheduler_state(state_path)
        status['counters'] = state.get('counters', {})
        status['thresholds'] = state.get('thresholds', {})
    except Exception as e:
        status['counters'] = {}
        status['thresholds'] = {}
        status['error'] = str(e)
    
    # 获取活跃数量
    status['active_counts'] = {}
    for scope in VALID_SCOPES:
        try:
            status['active_counts'][scope] = get_active_cycle_count(scope)
        except Exception as e:
            status['active_counts'][scope] = -1  # 错误标记
    
    # 获取等待队列大小
    status['wait_queue_sizes'] = {}
    for scope in VALID_SCOPES:
        try:
            status['wait_queue_sizes'][scope] = get_wait_queue_size(scope)
        except Exception as e:
            status['wait_queue_sizes'][scope] = -1  # 错误标记
    
    return status


# ── 单元测试入口 ────────────────────────────────────

if __name__ == "__main__":
    import tempfile
    import os
    
    print("Scheduler 模块测试...")
    
    # 使用临时目录测试
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            # 创建必要的目录
            os.makedirs("cycles/task", exist_ok=True)
            os.makedirs("cycles/topic", exist_ok=True)
            os.makedirs("logs", exist_ok=True)
            
            print(f"\n1. 测试调度器状态...")
            status = get_scheduler_status()
            print(f"   counters: {status.get('counters', {})}")
            print(f"   active_counts: {status.get('active_counts', {})}")
            
            print(f"\n2. 测试心跳触发...")
            result = on_heartbeat()
            print(f"   triggered_scopes: {result['triggered_scopes']}")
            print(f"   created_cycles: {result['created_cycles']}")
            print(f"   errors: {len(result['errors'])}")
            
            print(f"\n3. 测试并发检查...")
            task_limit_ok = check_concurrency_limit('task')
            print(f"   task concurrency limit ok: {task_limit_ok}")
            
            print("\n✅ 基础测试完成")
            
        finally:
            os.chdir(original_cwd)