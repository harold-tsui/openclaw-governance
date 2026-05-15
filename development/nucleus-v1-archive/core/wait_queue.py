#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wait Queue - 等待队列管理

实现等待队列的持久化存储、优先级排序、自动处理和过期清理。

依据：ARCH v1.4.3 §2.2.4

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta


# ── 常量定义 ────────────────────────────────────────

VALID_SCOPES = ['task', 'topic', 'project', 'system']

# 默认过期时间（小时）
DEFAULT_MAX_AGE_HOURS = 24


# ── 核心接口 ────────────────────────────────────────

def load_wait_queue(scope: str) -> Dict[str, Any]:
    """
    加载等待队列
    
    Args:
        scope: 调度范围
    
    Returns:
        等待队列数据
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    queue_path = f"cycles/wait_queue_{scope}.yaml"
    
    if not os.path.exists(queue_path):
        return {
            'scope': scope,
            'pending_requests': []
        }
    
    try:
        with open(queue_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return {
                'scope': scope,
                'pending_requests': []
            }
        
        # 确保 pending_requests 存在
        if 'pending_requests' not in data:
            data['pending_requests'] = []
        
        return data
    
    except Exception as e:
        print(f"WARNING: Failed to load wait queue for {scope}: {e}")
        return {
            'scope': scope,
            'pending_requests': []
        }


def save_wait_queue(scope: str, queue_data: Dict[str, Any]) -> bool:
    """
    保存等待队列
    
    Args:
        scope: 调度范围
        queue_data: 队列数据
    
    Returns:
        bool: 是否成功
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    queue_path = f"cycles/wait_queue_{scope}.yaml"
    
    # 确保目录存在
    os.makedirs(os.path.dirname(queue_path), exist_ok=True)
    
    try:
        with open(queue_path, 'w', encoding='utf-8') as f:
            yaml.dump(queue_data, f, allow_unicode=True, default_flow_style=False)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save wait queue for {scope}: {e}")
        return False


def add_to_wait_queue(scope: str, reason: str = "concurrency_limit") -> bool:
    """
    添加请求到等待队列
    
    Args:
        scope: 调度范围
        reason: 原因
    
    Returns:
        bool: 是否成功
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    queue_data = load_wait_queue(scope)
    
    # 创建新请求
    request = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'scope': scope,
        'reason': reason,
        'priority': 0  # 默认优先级
    }
    
    queue_data['pending_requests'].append(request)
    
    return save_wait_queue(scope, queue_data)


def pop_from_wait_queue(scope: str) -> Optional[Dict[str, Any]]:
    """
    从等待队列取出一个请求（FIFO）
    
    Args:
        scope: 调度范围
    
    Returns:
        取出的请求，队列为空时返回 None
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    queue_data = load_wait_queue(scope)
    
    if not queue_data['pending_requests']:
        return None
    
    # 按时间戳排序（最早的在前）
    queue_data['pending_requests'].sort(
        key=lambda x: x.get('timestamp', '')
    )
    
    # 取出第一个请求
    request = queue_data['pending_requests'].pop(0)
    
    # 保存更新后的队列
    save_wait_queue(scope, queue_data)
    
    return request


def get_wait_queue_size(scope: str) -> int:
    """
    获取等待队列大小
    
    Args:
        scope: 调度范围
    
    Returns:
        int: 队列大小
    """
    
    queue_data = load_wait_queue(scope)
    return len(queue_data.get('pending_requests', []))


def process_wait_queue(scope: str) -> Optional[str]:
    """
    处理等待队列，取出一个请求并创建 CycleUnit
    
    Args:
        scope: 调度范围
    
    Returns:
        str: 创建的 CycleUnit ID，失败返回 None
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    # 取出请求
    request = pop_from_wait_queue(scope)
    
    if not request:
        return None
    
    # 创建 CycleUnit
    from core.scheduler import create_cycle_for_scope
    
    cycle_id = create_cycle_for_scope(scope)
    
    if not cycle_id:
        # 创建失败，把请求放回队列
        queue_data = load_wait_queue(scope)
        queue_data['pending_requests'].insert(0, request)
        save_wait_queue(scope, queue_data)
        return None
    
    return cycle_id


def clean_expired_requests(
    scope: str,
    max_age_hours: int = DEFAULT_MAX_AGE_HOURS
) -> int:
    """
    清理过期的等待请求
    
    Args:
        scope: 调度范围
        max_age_hours: 最大年龄（小时）
    
    Returns:
        int: 清理的请求数量
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    queue_data = load_wait_queue(scope)
    
    if not queue_data['pending_requests']:
        return 0
    
    # 计算截止时间
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    
    # 过滤过期请求
    original_count = len(queue_data['pending_requests'])
    valid_requests = []
    
    for request in queue_data['pending_requests']:
        try:
            timestamp_str = request.get('timestamp', '')
            if timestamp_str:
                request_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if request_time > cutoff_time:
                    valid_requests.append(request)
        except Exception:
            # 时间戳解析失败，保留请求
            valid_requests.append(request)
    
    queue_data['pending_requests'] = valid_requests
    cleaned_count = original_count - len(valid_requests)
    
    if cleaned_count > 0:
        save_wait_queue(scope, queue_data)
    
    return cleaned_count


def get_queue_status(scope: str) -> Dict[str, Any]:
    """
    获取等待队列状态
    
    Args:
        scope: 调度范围
    
    Returns:
        队列状态字典
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    
    queue_data = load_wait_queue(scope)
    requests = queue_data.get('pending_requests', [])
    
    # 计算统计信息
    oldest_timestamp = None
    newest_timestamp = None
    
    if requests:
        timestamps = [r.get('timestamp', '') for r in requests]
        timestamps = [t for t in timestamps if t]  # 过滤空值
        if timestamps:
            timestamps.sort()
            oldest_timestamp = timestamps[0]
            newest_timestamp = timestamps[-1]
    
    return {
        'scope': scope,
        'queue_size': len(requests),
        'oldest_request': oldest_timestamp,
        'newest_request': newest_timestamp
    }


def get_all_queue_status() -> Dict[str, Dict[str, Any]]:
    """
    获取所有队列状态
    
    Returns:
        所有队列状态字典
    """
    
    status = {}
    for scope in VALID_SCOPES:
        status[scope] = get_queue_status(scope)
    
    return status


# ── 单元测试入口 ────────────────────────────────────

if __name__ == "__main__":
    import tempfile
    import os
    
    print("Wait Queue 模块测试...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            # 创建必要的目录
            os.makedirs("cycles", exist_ok=True)
            os.makedirs("cycles/task", exist_ok=True)
            
            print(f"\n1. 测试添加请求...")
            add_to_wait_queue('task')
            add_to_wait_queue('task')
            size = get_wait_queue_size('task')
            print(f"   queue size: {size}")
            
            print(f"\n2. 测试取出请求...")
            request = pop_from_wait_queue('task')
            print(f"   popped request: {request}")
            size = get_wait_queue_size('task')
            print(f"   queue size after pop: {size}")
            
            print(f"\n3. 测试队列状态...")
            status = get_queue_status('task')
            print(f"   status: {status}")
            
            print(f"\n4. 测试过期清理...")
            # 添加一个请求
            add_to_wait_queue('task')
            # 清理（设置很短的过期时间，应该不会清理刚添加的）
            cleaned = clean_expired_requests('task', max_age_hours=1)
            print(f"   cleaned: {cleaned}")
            
            print("\n✅ 基础测试完成")
            
        finally:
            os.chdir(original_cwd)