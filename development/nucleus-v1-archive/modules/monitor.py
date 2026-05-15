#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor Module - 系统状态感知

实现只读的系统状态感知功能，不写入任何 CycleUnit。

依据：ARCH v1.4.3 §3.1

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import glob
import json
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timezone
from dataclasses import dataclass


# ── 数据结构定义 ─────────────────────────────────────

@dataclass
class SystemSnapshot:
    """系统快照"""
    timestamp: datetime
    active_cycles: Dict[str, int]  # scope -> count
    log_entries: List[Dict]
    execution_entries: List[Dict]
    wait_queue_sizes: Dict[str, int]


@dataclass
class Anomaly:
    """异常对象"""
    type: str  # 'performance', 'error', 'concurrency'
    severity: str  # 'low', 'medium', 'high'
    message: str
    timestamp: datetime


@dataclass
class AggregatedResult:
    """聚合结果"""
    parent_id: str
    child_count: int
    success_count: int
    failure_count: int
    aggregated_evidence: List[Dict]


# ── 核心接口 ────────────────────────────────────────

def sense_system_state() -> SystemSnapshot:
    """
    感知系统状态
    
    Returns:
        SystemSnapshot: 系统快照对象
    """
    
    current_time = datetime.now(timezone.utc)
    
    # 1. 获取活跃 CycleUnit 数量
    active_cycles = _get_active_cycle_counts()
    
    # 2. 获取日志条目（今天）
    today_str = current_time.strftime('%Y-%m-%d')
    log_entries = get_log_entries(today_str)
    execution_entries = get_execution_entries(today_str)
    
    # 3. 获取等待队列大小
    wait_queue_sizes = _get_wait_queue_sizes()
    
    return SystemSnapshot(
        timestamp=current_time,
        active_cycles=active_cycles,
        log_entries=log_entries,
        execution_entries=execution_entries,
        wait_queue_sizes=wait_queue_sizes
    )


def detect_anomalies(snapshot: SystemSnapshot) -> List[Anomaly]:
    """
    检测异常
    
    Args:
        snapshot: 系统快照
    
    Returns:
        List[Anomaly]: 异常列表
    """
    
    anomalies = []
    
    # 1. 并发异常检测
    for scope, count in snapshot.active_cycles.items():
        if scope == 'task' and count > 10:
            anomalies.append(Anomaly(
                type='concurrency',
                severity='high',
                message=f'Task concurrency exceeded limit: {count} > 10',
                timestamp=snapshot.timestamp
            ))
        elif scope == 'topic' and count > 5:
            anomalies.append(Anomaly(
                type='concurrency',
                severity='high',
                message=f'Topic concurrency exceeded limit: {count} > 5',
                timestamp=snapshot.timestamp
            ))
        elif scope == 'project' and count > 3:
            anomalies.append(Anomaly(
                type='concurrency',
                severity='high',
                message=f'Project concurrency exceeded limit: {count} > 3',
                timestamp=snapshot.timestamp
            ))
        elif scope == 'system' and count > 1:
            anomalies.append(Anomaly(
                type='concurrency',
                severity='high',
                message=f'System concurrency exceeded limit: {count} > 1',
                timestamp=snapshot.timestamp
            ))
    
    # 2. 性能异常检测（执行日志过多可能表示问题）
    if len(snapshot.execution_entries) > 1000:
        anomalies.append(Anomaly(
            type='performance',
            severity='medium',
            message=f'High execution volume: {len(snapshot.execution_entries)} entries',
            timestamp=snapshot.timestamp
        ))
    
    # 3. 错误日志检测
    error_count = 0
    for entry in snapshot.log_entries:
        if isinstance(entry, dict) and entry.get('level') == 'ERROR':
            error_count += 1
    
    if error_count > 10:
        anomalies.append(Anomaly(
            type='error',
            severity='high',
            message=f'High error rate: {error_count} errors in logs',
            timestamp=snapshot.timestamp
        ))
    
    # 4. 等待队列异常
    for scope, size in snapshot.wait_queue_sizes.items():
        if scope == 'task' and size > 20:
            anomalies.append(Anomaly(
                type='concurrency',
                severity='medium',
                message=f'Task wait queue too large: {size} > 20',
                timestamp=snapshot.timestamp
            ))
        elif scope == 'topic' and size > 10:
            anomalies.append(Anomaly(
                type='concurrency',
                severity='medium',
                message=f'Topic wait queue too large: {size} > 10',
                timestamp=snapshot.timestamp
            ))
    
    return anomalies


def aggregate_child_results(parent_id: str) -> AggregatedResult:
    """
    聚合子环结果
    
    Args:
        parent_id: 父环 ID
    
    Returns:
        AggregatedResult: 聚合结果
    """
    
    # 查找父环的子环
    child_cycles = _find_child_cycles(parent_id)
    
    child_count = len(child_cycles)
    success_count = 0
    failure_count = 0
    aggregated_evidence = []
    
    for child_cycle in child_cycles:
        try:
            # 读取子环的 check.evidence
            if 'check' in child_cycle and 'evidence' in child_cycle['check']:
                evidence_list = child_cycle['check']['evidence']
                aggregated_evidence.extend(evidence_list)
            
            # 判断子环是否成功
            if 'check' in child_cycle and 'verdict' in child_cycle['check']:
                verdict = child_cycle['check']['verdict']
                if verdict == 'pass':
                    success_count += 1
                elif verdict in ['fail', 'partial']:
                    failure_count += 1
        
        except Exception as e:
            # 子环文件损坏，计入失败
            failure_count += 1
    
    return AggregatedResult(
        parent_id=parent_id,
        child_count=child_count,
        success_count=success_count,
        failure_count=failure_count,
        aggregated_evidence=aggregated_evidence
    )


def get_log_entries(date: str = None) -> List[Dict]:
    """
    获取日志条目
    
    Args:
        date: 日期（YYYY-MM-DD），默认今天
    
    Returns:
        List[Dict]: 日志条目列表
    """
    
    if date is None:
        date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    log_file = f"logs/{date}.jsonl"
    return _read_jsonl_file(log_file)


def get_execution_entries(date: str = None) -> List[Dict]:
    """
    获取执行条目
    
    Args:
        date: 日期（YYYY-MM-DD），默认今天
    
    Returns:
        List[Dict]: 执行条目列表
    """
    
    if date is None:
        date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    exec_file = f"executions/{date}.jsonl"
    return _read_jsonl_file(exec_file)


# ── 辅助函数 ────────────────────────────────────────

def _get_active_cycle_counts() -> Dict[str, int]:
    """获取各 scope 的活跃 CycleUnit 数量"""
    
    scopes = ['task', 'topic', 'project', 'system']
    counts = {}
    
    for scope in scopes:
        pattern = f"cycles/{scope}/*.yaml"
        files = glob.glob(pattern)
        
        active_count = 0
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cycle_data = yaml.safe_load(f)
                
                # 检查是否为活跃状态
                if cycle_data and 'phase' in cycle_data:
                    phase = cycle_data['phase']
                    if phase not in ['completed', 'archived']:
                        active_count += 1
            except Exception:
                # 文件损坏，跳过
                continue
        
        counts[scope] = active_count
    
    return counts


def _get_wait_queue_sizes() -> Dict[str, int]:
    """获取各 scope 的等待队列大小"""
    
    scopes = ['task', 'topic', 'project', 'system']
    sizes = {}
    
    for scope in scopes:
        queue_file = f"cycles/wait_queue_{scope}.yaml"
        if not os.path.exists(queue_file):
            sizes[scope] = 0
            continue
        
        try:
            with open(queue_file, 'r', encoding='utf-8') as f:
                queue_data = yaml.safe_load(f)
            
            if queue_data and 'pending_requests' in queue_data:
                sizes[scope] = len(queue_data['pending_requests'])
            else:
                sizes[scope] = 0
        except Exception:
            sizes[scope] = 0
    
    return sizes


def _find_child_cycles(parent_id: str) -> List[Dict]:
    """查找父环的所有子环（通过 parent_cycle_id 字段过滤）"""

    # 子环存储在比父环低一级的目录
    # 例：parent 是 topic 级别 → 子环在 cycles/task/
    scope_hierarchy = ['task', 'topic', 'project', 'system']
    child_files = []

    for scope in scope_hierarchy:
        pattern = f"cycles/{scope}/*.yaml"
        child_files.extend(glob.glob(pattern))

    child_cycles = []
    for file_path in child_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cycle_data = yaml.safe_load(f)

            if not cycle_data:
                continue

            # 只收集 parent_cycle_id 匹配的子环
            if cycle_data.get('parent_cycle_id') == parent_id:
                child_cycles.append(cycle_data)
        except Exception:
            continue

    return child_cycles


def _read_jsonl_file(file_path: str) -> List[Dict]:
    """读取 JSONL 文件"""
    
    if not os.path.exists(file_path):
        return []
    
    entries = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError:
                        # 无效 JSON 行，跳过
                        continue
    except Exception:
        # 文件读取失败，返回空列表
        pass
    
    return entries


# ── 单元测试入口 ────────────────────────────────────

if __name__ == "__main__":
    print("Monitor Module 测试...")
    
    # 创建必要的目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("executions", exist_ok=True)
    os.makedirs("cycles/task", exist_ok=True)
    
    print(f"\n1. 测试系统状态感知...")
    snapshot = sense_system_state()
    print(f"   active_cycles: {snapshot.active_cycles}")
    print(f"   log_entries: {len(snapshot.log_entries)}")
    print(f"   execution_entries: {len(snapshot.execution_entries)}")
    
    print(f"\n2. 测试异常检测...")
    anomalies = detect_anomalies(snapshot)
    print(f"   detected anomalies: {len(anomalies)}")
    
    print("\n✅ 基础测试完成")