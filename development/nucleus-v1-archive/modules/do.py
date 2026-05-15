#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Do Module - 执行阶段（写入层）

Python 职责（确定性 I/O）：
  - record_do_result(): 将 LLM 的执行结果持久化到 CycleUnit
  - create_child_cycle(): 创建子环 YAML
  - write_execution_log(): 记录执行日志

LLM 职责（SKILL.md §4.2 Step 3 定义）：
  - 读取 Task-CARD 判断任务进度
  - 识别阻塞，推进任务
  - 决定执行结果（status/blocker）

依据：ARCH v1.4.3 §3.2

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import json
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


# ── 常量定义 ────────────────────────────────────────

VALID_SCOPES = ['task', 'topic', 'project', 'system']

# 最大子环数量限制
MAX_CHILDREN_LIMITS = {
    'task': 10,
    'topic': 5,
    'project': 3,
    'system': 1
}


# ── 核心接口 ────────────────────────────────────────

def record_do_result(
    cycle_id: str,
    status: str,
    summary: str,
    blocker: Optional[str] = None,
    children_to_create: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    将 LLM 的 Do 阶段执行结果写入 CycleUnit。

    此函数由 LLM 在完成实际任务推进后调用（SKILL.md §4.2 Step 3）。
    Python 不执行任何任务逻辑，只负责持久化。

    Args:
        cycle_id: CycleUnit ID
        status: 执行状态（completed / blocked / failed）
        summary: 执行摘要（LLM 描述实际做了什么）
        blocker: 阻塞原因（status=blocked 时填写）
        children_to_create: 需要创建的子环 scope 列表（如 ['task', 'task']）

    Returns:
        {
            'status': str,
            'children_created': List[str],
            'errors': List[str]
        }
    """

    VALID_STATUSES = {'completed', 'blocked', 'failed'}
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}, must be one of {VALID_STATUSES}")

    result: Dict[str, Any] = {
        'status': status,
        'children_created': [],
        'errors': []
    }

    cycle_path = _get_cycle_path(cycle_id)
    if not os.path.exists(cycle_path):
        result['status'] = 'failed'
        result['errors'].append(f"CycleUnit not found: {cycle_path}")
        return result

    try:
        # 1. 写入 do 块
        _update_do_status(cycle_id, status, summary=summary, blocker=blocker)

        # 2. 推进 phase → check（blocked/failed 也推进，让 Check 阶段记录失败原因）
        _advance_phase(cycle_id, 'check')

        # 3. 创建子环（可选，LLM 决定是否需要）
        for child_scope in (children_to_create or []):
            if child_scope not in VALID_SCOPES:
                result['errors'].append(f"Invalid child scope: {child_scope}")
                continue
            child_id = create_child_cycle(cycle_id, child_scope)
            if child_id:
                result['children_created'].append(child_id)
            else:
                result['errors'].append(f"Failed to create child cycle: {child_scope}")

        # 4. 记录执行日志
        write_execution_log(
            cycle_id=cycle_id,
            action='record_do_result',
            result=status,
            metadata={
                'summary': summary,
                'blocker': blocker,
                'children_created': len(result['children_created'])
            }
        )

    except Exception as e:
        result['status'] = 'failed'
        result['errors'].append(str(e))
        write_execution_log(
            cycle_id=cycle_id,
            action='record_do_result',
            result='failed',
            metadata={'error': str(e)}
        )

    return result


def create_child_cycle(parent_id: str, child_scope: str) -> Optional[str]:
    """
    创建子环 CycleUnit
    
    Args:
        parent_id: 父环 ID
        child_scope: 子环范围
    
    Returns:
        子环 CycleUnit ID
    """
    
    if child_scope not in VALID_SCOPES:
        return None
    
    # 生成子环 ID
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    child_id = f"{child_scope}-{timestamp}"
    
    # 创建子环目录
    dir_path = f"cycles/{child_scope}"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    
    # 创建子环数据
    child_data = {
        'id': child_id,
        'scope': child_scope,
        'phase': 'plan',
        'task_card_id': f"child-of-{parent_id}",
        'parent_cycle_id': parent_id,  # schema v1.4: 子环必须写入父环 ID
        'metadata': {
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'version': 1,
            'global_max_cycles': 100
        },
        'plan': {
            'human_approval_required': False,
            'time_horizon_cycles': 10,
            'max_cycles': 10
        }
    }
    
    # 写入文件
    file_path = f"cycles/{child_scope}/{child_id}.yaml"
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(child_data, f, allow_unicode=True, default_flow_style=False)
        
        # 写入执行日志
        write_execution_log(
            cycle_id=parent_id,
            action='create_child_cycle',
            result='success',
            metadata={
                'child_id': child_id,
                'child_scope': child_scope
            }
        )
        
        return child_id
    
    except Exception as e:
        write_execution_log(
            cycle_id=parent_id,
            action='create_child_cycle',
            result='failed',
            metadata={
                'child_scope': child_scope,
                'error': str(e)
            }
        )
        return None


def check_children_status(parent_id: str) -> Dict[str, Any]:
    """
    检查子环执行状态
    
    Args:
        parent_id: 父环 ID
    
    Returns:
        子环状态字典
    """
    
    children_status = {
        'total': 0,
        'completed': 0,
        'in_progress': 0,
        'failed': 0,
        'blocked': 0
    }
    
    # 查找所有子环（简化实现：假设都在 cycles/task/ 目录）
    child_files = []
    for scope in VALID_SCOPES:
        pattern = f"cycles/{scope}/*.yaml"
        files = []
        try:
            import glob
            files = glob.glob(pattern)
        except:
            pass
        child_files.extend(files)
    
    for file_path in child_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                child_data = yaml.safe_load(f)

            if child_data and child_data.get('parent_cycle_id') == parent_id:
                children_status['total'] += 1
                
                phase = child_data.get('phase', 'unknown')
                if phase == 'completed':
                    children_status['completed'] += 1
                elif phase in ['plan', 'do', 'check', 'act']:
                    children_status['in_progress'] += 1
                elif phase == 'failed':
                    children_status['failed'] += 1
                elif phase == 'blocked':
                    children_status['blocked'] += 1
        
        except Exception:
            # 文件损坏，跳过
            continue
    
    return children_status


def write_execution_log(
    cycle_id: str,
    action: str,
    result: str,
    metadata: Optional[Dict] = None
) -> None:
    """
    写入执行日志
    
    Args:
        cycle_id: CycleUnit ID
        action: 执行动作
        result: 执行结果
        metadata: 元数据
    """
    
    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'cycle_id': cycle_id,
        'action': action,
        'result': result,
        'scope': _get_scope_from_cycle_id(cycle_id),
        'metadata': metadata or {}
    }
    
    # 写入 executions/ 目录
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    log_dir = "executions"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    log_file = f"{log_dir}/{today}.jsonl"
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"WARNING: Failed to write execution log: {e}")


# ── 辅助函数 ────────────────────────────────────────

def _get_cycle_path(cycle_id: str) -> str:
    """获取 CycleUnit 文件路径"""
    scope = _get_scope_from_cycle_id(cycle_id)
    return f"cycles/{scope}/{cycle_id}.yaml"


def _get_scope_from_cycle_id(cycle_id: str) -> str:
    """从 CycleUnit ID 提取 scope"""
    if '-' in cycle_id:
        return cycle_id.split('-')[0]
    return 'task'  # 默认


def _advance_phase(cycle_id: str, new_phase: str) -> None:
    """原子更新 phase 字段"""
    cycle_path = _get_cycle_path(cycle_id)
    if not os.path.exists(cycle_path):
        return
    try:
        with open(cycle_path, 'r', encoding='utf-8') as f:
            cycle_data = yaml.safe_load(f)
        cycle_data['phase'] = new_phase
        cycle_data['metadata']['updated_at'] = datetime.now(timezone.utc).isoformat()
        tmp_path = cycle_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
        os.replace(tmp_path, cycle_path)
    except Exception as e:
        print(f"WARNING: Failed to advance phase to {new_phase}: {e}")


def _update_do_status(
    cycle_id: str,
    status: str,
    summary: Optional[str] = None,
    blocker: Optional[str] = None
) -> None:
    """更新 Do 阶段状态，写入 LLM 执行摘要和阻塞原因"""
    try:
        cycle_path = _get_cycle_path(cycle_id)
        if not os.path.exists(cycle_path):
            return

        with open(cycle_path, 'r', encoding='utf-8') as f:
            cycle_data = yaml.safe_load(f)

        if 'do' not in cycle_data:
            cycle_data['do'] = {}

        cycle_data['do']['status'] = status
        if summary is not None:
            cycle_data['do']['summary'] = summary
        if blocker is not None:
            cycle_data['do']['blocked_reason'] = blocker
        elif status != 'blocked':
            cycle_data['do'].pop('blocked_reason', None)

        cycle_data['metadata']['updated_at'] = datetime.now(timezone.utc).isoformat()

        # 原子写入
        tmp_path = cycle_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
        os.replace(tmp_path, cycle_path)

    except Exception as e:
        print(f"WARNING: Failed to update do status: {e}")


# ── 单元测试入口 ────────────────────────────────────

if __name__ == "__main__":
    print("Do Module 测试...")
    
    # 创建必要的目录
    os.makedirs("executions", exist_ok=True)
    os.makedirs("cycles/task", exist_ok=True)
    
    print(f"\n1. 测试执行日志...")
    write_execution_log(
        cycle_id="test-001",
        action="test_action",
        result="success",
        metadata={"test": "data"}
    )
    print("   ✅ 日志写入完成")
    
    print(f"\n2. 测试创建子环...")
    child_id = create_child_cycle("parent-001", "task")
    if child_id:
        print(f"   ✅ 子环创建成功: {child_id}")
    else:
        print("   ❌ 子环创建失败")
    
    print("\n✅ 基础测试完成")