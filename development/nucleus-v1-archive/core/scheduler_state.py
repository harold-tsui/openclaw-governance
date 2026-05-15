#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler State - 持久化调度计数器

实现跨 Heartbeat 的多粒度调度计数器，支持：
1. task/topic/project/system 四层独立计数
2. 原子写入（防止并发损坏）
3. 阈值触发检测
4. 进程崩溃恢复

依据：ARCH v1.4.3 §2.2.3

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import yaml
import tempfile
import shutil
import fcntl
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path


# ── 异常定义 ────────────────────────────────────────

class SchedulerStateError(Exception):
    """调度状态异常"""
    pass


class SchedulerStateCorruptedError(SchedulerStateError):
    """调度状态文件损坏"""
    pass


# ── 常量定义 ────────────────────────────────────────

DEFAULT_STATE_PATH = "cycles/scheduler_state.yaml"

# 触发阈值（ARCH v1.4.3 §2.2.2）
DEFAULT_THRESHOLDS = {
    'task': 1,      # 每 tick (30分钟)
    'topic': 4,     # 每 4 tick (2小时)
    'project': 48,  # 每 48 tick (1天)
    'system': 336   # 每 336 tick (1周)
}

VALID_SCOPES = ['task', 'topic', 'project', 'system']


# ── 文件锁 ─────────────────────────────────────────

class SchedulerStateLock:
    """调度状态文件锁"""
    
    _lock_file = None
    _lock_path = None
    
    @classmethod
    def acquire(cls, state_path: str, timeout: float = 5.0) -> bool:
        """获取文件锁"""
        lock_path = f"{state_path}.lock"
        
        try:
            cls._lock_path = lock_path
            cls._lock_file = open(lock_path, 'w')
            
            start_time = time.time()
            while True:
                try:
                    fcntl.flock(cls._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return True
                except (IOError, OSError):
                    if time.time() - start_time > timeout:
                        return False
                    time.sleep(0.01)
        except Exception:
            return False
    
    @classmethod
    def release(cls):
        """释放文件锁"""
        if cls._lock_file:
            try:
                fcntl.flock(cls._lock_file.fileno(), fcntl.LOCK_UN)
                cls._lock_file.close()
                if cls._lock_path and os.path.exists(cls._lock_path):
                    os.remove(cls._lock_path)
            except:
                pass
            finally:
                cls._lock_file = None
                cls._lock_path = None


def with_lock(func):
    """文件锁装饰器"""
    def wrapper(*args, **kwargs):
        state_path = kwargs.get('state_path', DEFAULT_STATE_PATH)
        if not state_path and len(args) > 0:
            state_path = args[-1] if isinstance(args[-1], str) else DEFAULT_STATE_PATH
        
        acquired = SchedulerStateLock.acquire(state_path)
        try:
            return func(*args, **kwargs)
        finally:
            if acquired:
                SchedulerStateLock.release()
    return wrapper


# ── 核心接口 ────────────────────────────────────────

@with_lock
def load_scheduler_state(state_path: str = DEFAULT_STATE_PATH) -> Dict[str, Any]:
    """
    加载调度状态（原子读取）
    
    Args:
        state_path: 状态文件路径
    
    Returns:
        调度状态字典
    
    Raises:
        SchedulerStateCorruptedError: 文件损坏
    """
    
    if not os.path.exists(state_path):
        # 文件不存在，返回默认状态
        return create_default_state()
    
    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            state = yaml.safe_load(f)
        
        # 验证必要字段
        if not validate_state(state):
            raise SchedulerStateCorruptedError(f"Invalid state structure in {state_path}")
        
        return state
    
    except yaml.YAMLError as e:
        raise SchedulerStateCorruptedError(f"YAML parse error: {e}")


@with_lock
def save_scheduler_state(
    state: Dict[str, Any],
    state_path: str = DEFAULT_STATE_PATH
) -> None:
    """
    保存调度状态（原子写入）
    
    Args:
        state: 调度状态字典
        state_path: 状态文件路径
    
    Implementation:
        1. 写入 .tmp 文件
        2. fsync 确保落盘
        3. atomic rename 替换原文件
    """
    
    # 确保目录存在
    dir_path = os.path.dirname(state_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    
    # 更新时间戳
    state['last_updated'] = datetime.now(timezone.utc).isoformat()
    
    # 原子写入
    atomic_write_yaml(state_path, state)


@with_lock
def increment_counter(
    scope: str,
    state_path: str = DEFAULT_STATE_PATH
) -> Dict[str, Any]:
    """
    递增指定 scope 计数器
    
    Args:
        scope: 计数器范围（task/topic/project/system）
        state_path: 状态文件路径
    
    Returns:
        {
            'triggered': bool,      # 是否触发阈值
            'counter': int,         # 当前计数
            'threshold': int,       # 阈值
            'state': Dict           # 更新后的状态
        }
    
    Raises:
        ValueError: 无效 scope
    """
    
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope: {scope}. Must be one of {VALID_SCOPES}")
    
    # 加载状态
    state = load_scheduler_state(state_path)
    
    # 递增计数器
    current_counter = state['counters'].get(scope, 0)
    new_counter = current_counter + 1
    state['counters'][scope] = new_counter
    
    # 检查阈值
    threshold = state['thresholds'].get(scope, DEFAULT_THRESHOLDS[scope])
    triggered = new_counter >= threshold
    
    # 如果触发，重置计数器
    if triggered:
        state['counters'][scope] = 0
    
    # 保存状态
    save_scheduler_state(state, state_path)
    
    return {
        'triggered': triggered,
        'counter': new_counter,
        'threshold': threshold,
        'state': state
    }


def check_threshold(scope: str, counter: int, state: Optional[Dict[str, Any]] = None) -> bool:
    """
    检查是否达到触发阈值
    
    Args:
        scope: 计数器范围
        counter: 当前计数
        state: 调度状态（可选，用于获取自定义阈值）
    
    Returns:
        bool: 是否达到阈值
    """
    
    if state and 'thresholds' in state:
        threshold = state['thresholds'].get(scope, DEFAULT_THRESHOLDS[scope])
    else:
        threshold = DEFAULT_THRESHOLDS[scope]
    
    return counter >= threshold


@with_lock
def reset_counter(
    scope: str,
    state_path: str = DEFAULT_STATE_PATH
) -> None:
    """
    重置指定 scope 计数器
    
    Args:
        scope: 计数器范围
        state_path: 状态文件路径
    """
    
    state = load_scheduler_state(state_path)
    state['counters'][scope] = 0
    save_scheduler_state(state, state_path)


@with_lock
def reset_all_counters(state_path: str = DEFAULT_STATE_PATH) -> None:
    """
    重置所有计数器
    
    Args:
        state_path: 状态文件路径
    """
    
    state = load_scheduler_state(state_path)
    for scope in VALID_SCOPES:
        state['counters'][scope] = 0
    save_scheduler_state(state, state_path)


# ── 辅助函数 ────────────────────────────────────────

def create_default_state() -> Dict[str, Any]:
    """创建默认状态"""
    return {
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'counters': {
            'task': 0,
            'topic': 0,
            'project': 0,
            'system': 0
        },
        'thresholds': DEFAULT_THRESHOLDS.copy()
    }


def validate_state(state: Dict[str, Any]) -> bool:
    """验证状态结构"""
    
    if not isinstance(state, dict):
        return False
    
    # 检查必要字段
    if 'counters' not in state:
        return False
    
    if 'thresholds' not in state:
        return False
    
    # 检查计数器字段
    counters = state['counters']
    if not isinstance(counters, dict):
        return False
    
    for scope in VALID_SCOPES:
        if scope not in counters:
            return False
        if not isinstance(counters[scope], int):
            return False
    
    return True


def atomic_write_yaml(path: str, data: Dict[str, Any]) -> None:
    """
    原子写入 YAML 文件
    
    Implementation:
        1. 写入 .tmp 文件
        2. fsync 确保落盘
        3. atomic rename 替换原文件
    """
    
    tmp_path = f"{path}.tmp"
    
    try:
        # 写入临时文件
        with open(tmp_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            f.flush()
            os.fsync(f.fileno())
        
        # 原子替换
        os.replace(tmp_path, path)
    
    except Exception as e:
        # 清理临时文件
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass
        raise SchedulerStateError(f"Failed to write state: {e}")


@with_lock
def get_all_triggers(state_path: str = DEFAULT_STATE_PATH) -> Dict[str, bool]:
    """
    获取所有 scope 的触发状态
    
    Args:
        state_path: 状态文件路径
    
    Returns:
        {scope: bool} 触发状态映射
    """
    
    state = load_scheduler_state(state_path)
    triggers = {}
    
    for scope in VALID_SCOPES:
        counter = state['counters'].get(scope, 0)
        threshold = state['thresholds'].get(scope, DEFAULT_THRESHOLDS[scope])
        triggers[scope] = counter >= threshold
    
    return triggers


@with_lock
def get_next_trigger_count(scope: str, state_path: str = DEFAULT_STATE_PATH) -> int:
    """
    获取距离下次触发还需多少次计数
    
    Args:
        scope: 计数器范围
        state_path: 状态文件路径
    
    Returns:
        剩余次数
    """
    
    state = load_scheduler_state(state_path)
    counter = state['counters'].get(scope, 0)
    threshold = state['thresholds'].get(scope, DEFAULT_THRESHOLDS[scope])
    
    return max(0, threshold - counter)


# ── 单元测试入口 ────────────────────────────────────

if __name__ == "__main__":
    import tempfile
    import os
    
    print("Scheduler State 模块测试...")
    
    # 使用临时文件测试
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = os.path.join(tmpdir, "scheduler_state.yaml")
        
        print(f"\n1. 测试默认状态创建...")
        state = create_default_state()
        print(f"   counters: {state['counters']}")
        print(f"   thresholds: {state['thresholds']}")
        
        print(f"\n2. 测试保存和加载...")
        save_scheduler_state(state, test_path)
        loaded_state = load_scheduler_state(test_path)
        print(f"   loaded counters: {loaded_state['counters']}")
        print(f"   last_updated: {loaded_state['last_updated']}")
        
        print(f"\n3. 测试计数器递增...")
        for i in range(5):
            result = increment_counter('task', test_path)
            print(f"   tick {i+1}: counter={result['counter']}, triggered={result['triggered']}")
        
        print(f"\n4. 测试 topic 阈值触发...")
        for i in range(5):
            result = increment_counter('topic', test_path)
            print(f"   tick {i+1}: counter={result['counter']}, triggered={result['triggered']}")
        
        print(f"\n5. 测试获取所有触发状态...")
        triggers = get_all_triggers(test_path)
        print(f"   triggers: {triggers}")
        
        print(f"\n6. 测试剩余次数...")
        for scope in VALID_SCOPES:
            remaining = get_next_trigger_count(scope, test_path)
            print(f"   {scope}: {remaining} ticks remaining")
        
        print("\n✅ 基础测试通过")