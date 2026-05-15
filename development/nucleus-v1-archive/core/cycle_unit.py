#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleUnit 读写工具库

实现 CycleUnit 的原子性读写操作，确保数据一致性。
基于 NUCLEUS-4.0 架构设计，支持 Task/Topic/Project/System 四层粒度。

文件路径约定：
- cycles/{scope}/{id}.yaml          # 主文件
- cycles/archive/{scope}/{id}_v{version}.yaml  # 归档文件

Author: 张铁 (CQO)
Version: 1.0
Date: 2026-04-05
"""

import os
import shutil
import yaml
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path


class CycleUnitError(Exception):
    """CycleUnit 操作异常基类"""
    pass


class CycleUnitNotFoundError(CycleUnitError):
    """CycleUnit 文件未找到"""
    pass


class CycleUnitWriteError(CycleUnitError):
    """CycleUnit 写入错误"""
    pass


def _get_cycle_path(id: str, scope: str) -> str:
    """
    获取 CycleUnit 文件路径
    
    Args:
        id: CycleUnit ID（格式：{scope}-{timestamp}-{random}）
        scope: 执行粒度（task/topic/project/system）
    
    Returns:
        完整文件路径
    """
    return f"cycles/{scope}/{id}.yaml"


def _get_archive_path(id: str, scope: str, version: int) -> str:
    """
    获取归档文件路径
    
    Args:
        id: CycleUnit ID
        scope: 执行粒度
        version: 版本号
    
    Returns:
        归档文件路径
    """
    return f"cycles/archive/{scope}/{id}_v{version}.yaml"


def _ensure_directory_exists(path: str) -> None:
    """
    确保目录存在
    
    Args:
        path: 文件路径
    """
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)


def load_cycle(id: str, scope: str) -> Dict[str, Any]:
    """
    加载 CycleUnit
    
    Args:
        id: CycleUnit ID（格式：{scope}-{timestamp}-{random}）
        scope: 执行粒度（task/topic/project/system）
    
    Returns:
        CycleUnit dict，包含所有字段
    
    Raises:
        CycleUnitNotFoundError: 文件不存在
        yaml.YAMLError: YAML 格式错误
    """
    path = _get_cycle_path(id, scope)
    
    if not os.path.exists(path):
        raise CycleUnitNotFoundError(f"CycleUnit file not found: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"YAML parsing error in {path}: {e}")


def save_cycle(unit: Dict[str, Any]) -> None:
    """
    原子性保存 CycleUnit
    
    Args:
        unit: CycleUnit dict
    
    Features:
        - 自动递增 version
        - 自动更新 updated_at
        - 原子性写入（.tmp + rename）
    
    Raises:
        CycleUnitWriteError: 写入失败
    """
    # 验证必需字段
    required_fields = ['id', 'scope', 'phase', 'metadata']
    for field in required_fields:
        if field not in unit:
            raise CycleUnitWriteError(f"Missing required field: {field}")
    
    # 自动更新 metadata 字段
    if 'metadata' not in unit:
        unit['metadata'] = {}
    
    metadata = unit['metadata']
    if 'version' not in metadata:
        metadata['version'] = 0
    metadata['version'] += 1
    
    # 使用 UTC 时间戳
    metadata['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    # 如果没有 created_at，设置为当前时间
    if 'created_at' not in metadata:
        metadata['created_at'] = metadata['updated_at']
    
    # 构建文件路径
    path = _get_cycle_path(unit['id'], unit['scope'])
    tmp_path = path + '.tmp'
    
    # 确保目录存在
    _ensure_directory_exists(path)
    
    try:
        # 写入临时文件
        with open(tmp_path, 'w', encoding='utf-8') as f:
            yaml.dump(unit, f, allow_unicode=True, default_flow_style=False, indent=2)
        
        # 原子性重命名（覆盖现有文件）
        os.rename(tmp_path, path)
        
    except Exception as e:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise CycleUnitWriteError(f"Failed to save CycleUnit: {e}")


def update_phase(id: str, scope: str, new_phase: str) -> None:
    """
    更新 phase 并归档旧版本
    
    Args:
        id: CycleUnit ID
        scope: 执行粒度
        new_phase: 新阶段（plan/do/check/act）
    
    Features:
        - 归档旧版本到 archive/
        - 更新 phase 字段
        - 触发 save_cycle()
    
    Raises:
        CycleUnitNotFoundError: 原文件不存在
        CycleUnitWriteError: 写入失败
    """
    # 验证 phase 值
    valid_phases = ['plan', 'do', 'check', 'act', 'completed']
    if new_phase not in valid_phases:
        raise ValueError(f"Invalid phase: {new_phase}. Must be one of {valid_phases}")
    
    # 加载当前 CycleUnit
    unit = load_cycle(id, scope)
    
    # 获取当前版本用于归档
    current_version = unit['metadata'].get('version', 0)
    
    # 创建归档目录
    archive_path = _get_archive_path(id, scope, current_version)
    _ensure_directory_exists(archive_path)
    
    # 复制当前文件到归档
    current_path = _get_cycle_path(id, scope)
    if os.path.exists(current_path):
        shutil.copy2(current_path, archive_path)
    
    # 更新 phase
    unit['phase'] = new_phase
    
    # 保存更新后的版本
    save_cycle(unit)


def create_cycle(id: str, scope: str, task_card_id: str, initial_data: Dict[str, Any]) -> None:
    """
    创建新的 CycleUnit (v1.2 Schema)
    
    Args:
        id: CycleUnit ID
        scope: 执行粒度（task/topic/project/system）
        task_card_id: 绑定的 task-card ID（必填，唯一真相源）
        initial_data: 初始数据（不含 intent/actions/success_criteria）
    
    Features:
        - v1.2: CycleUnit 聚焦状态跟踪，不存储 intent/actions
        - 设置初始 metadata
        - 调用 save_cycle() 进行原子性写入
    
    Raises:
        ValueError: task_card_id 为空或无效
    """
    # 验证必填字段
    if not task_card_id:
        raise ValueError("task_card_id is required (v1.2 Schema)")
    
    # 设置基础字段（v1.3-fixed Schema）
    cycle_data = {
        'id': id,
        'scope': scope,
        'task_card_id': task_card_id,  # v1.2: 绑定唯一真相源
        'task_card_path': None,  # v1.3-fixed: 继承 v1.2
        'phase': 'plan',  # 默认从 plan 开始
        'plan': {
            # v1.3: 移除 check_reference，验收策略改为内存 review_context
            # review_level/acceptance_criteria 从 task-card 读取
            'time_horizon_cycles': 10,
            'review_window': '24h',  # 可由 task-card 覆盖
            'human_approval_required': False,
            'max_cycles': 10
        },
        'do': {
            'status': 'not_started',
            'blocked_reason': None,  # v1.3-fixed: 继承 v1.2
            'children': [],  # v1.2: ID 引用，非嵌套
            'execution_log_ref': None
        },
        'check': {
            'verdict': None,
            'evidence': [],
            'criteria_results': []  # v1.2: 逐项核对结果
        },
        'act': {
            'adjustments': [],
            'incoming_adjustments': [],
            'propagate_to': 'self',
            'next_cycle_id': None,  # v1.2: ID 引用，非嵌套
            'lesson_learn_ref': None  # v1.3-fixed: 继承 v1.2
        },
        'metadata': {
            'version': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'global_max_cycles': 100
        }
    }
    
    # 合并用户提供的初始数据
    cycle_data.update(initial_data)
    
    # 确保必填字段不被覆盖
    cycle_data['id'] = id
    cycle_data['scope'] = scope
    cycle_data['task_card_id'] = task_card_id
    cycle_data['phase'] = 'plan'
    
    # 保存
    save_cycle(cycle_data)


def get_cycle_version(id: str, scope: str) -> int:
    """
    获取 CycleUnit 当前版本号
    
    Args:
        id: CycleUnit ID
        scope: 执行粒度
    
    Returns:
        当前版本号
    """
    unit = load_cycle(id, scope)
    return unit['metadata'].get('version', 0)


# 导出公共接口
__all__ = [
    'load_cycle',
    'save_cycle',
    'update_phase',
    'create_cycle',
    'get_cycle_version',
    'CycleUnitError',
    'CycleUnitNotFoundError',
    'CycleUnitWriteError'
]


# ── CLI 入口 ────────────────────────────────────────
# 用法：python core/cycle_unit.py update --cycle-id X --scope S [选项]
#
# 选项：
#   --phase PHASE              推进到新阶段（plan/do/check/act/completed）
#   --task-card-path PATH      写入 task_card_path（顶层 + plan 块同步）
#   --task-card-id ID          写入 task_card_id
#   --do-status STATUS         写入 do.status（completed/blocked/failed）
#   --do-summary SUMMARY       写入 do.summary
#   --check-verdict VERDICT    写入 check.verdict
#   --topic-id TOPIC_ID        写入 metadata.topic_id

if __name__ == "__main__":
    import argparse
    import json
    import sys as _sys

    parser = argparse.ArgumentParser(description='CycleUnit 读写工具')
    subparsers = parser.add_subparsers(dest='command')

    # update 子命令
    update_parser = subparsers.add_parser('update', help='更新 CycleUnit 字段')
    update_parser.add_argument('--cycle-id', required=True, help='CycleUnit ID（如 task-20260416T090000Z）')
    update_parser.add_argument('--scope', required=True, choices=['task', 'topic', 'project', 'system'])
    update_parser.add_argument('--phase', choices=['plan', 'do', 'check', 'act', 'completed'],
                               help='推进到新阶段')
    update_parser.add_argument('--task-card-path', help='Task-CARD 文件路径（写入顶层 + plan 块）')
    update_parser.add_argument('--task-card-id', help='Task-CARD ID')
    update_parser.add_argument('--do-status', choices=['not_started', 'completed', 'blocked', 'failed'],
                               help='写入 do.status')
    update_parser.add_argument('--do-summary', help='写入 do.summary（LLM 执行摘要）')
    update_parser.add_argument('--check-verdict',
                               choices=['pass', 'partial', 'fail', 'skip', 'pending', 'pending_sampling'],
                               help='写入 check.verdict')
    update_parser.add_argument('--topic-id', help='写入 metadata.topic_id')

    # show 子命令
    show_parser = subparsers.add_parser('show', help='显示 CycleUnit 内容')
    show_parser.add_argument('--cycle-id', required=True)
    show_parser.add_argument('--scope', required=True, choices=['task', 'topic', 'project', 'system'])

    args = parser.parse_args()

    if args.command == 'update':
        try:
            unit = load_cycle(args.cycle_id, args.scope)
        except CycleUnitNotFoundError as e:
            print(json.dumps({'ok': False, 'error': str(e)}))
            _sys.exit(1)

        changed = []

        if args.phase:
            unit['phase'] = args.phase
            changed.append(f'phase={args.phase}')

        if args.task_card_path:
            unit['task_card_path'] = args.task_card_path
            if 'plan' not in unit:
                unit['plan'] = {}
            unit['plan']['task_card_path'] = args.task_card_path
            changed.append(f'task_card_path={args.task_card_path}')

        if args.task_card_id:
            unit['task_card_id'] = args.task_card_id
            if 'plan' not in unit:
                unit['plan'] = {}
            unit['plan']['task_card_id'] = args.task_card_id
            changed.append(f'task_card_id={args.task_card_id}')

        if args.do_status:
            if 'do' not in unit:
                unit['do'] = {}
            unit['do']['status'] = args.do_status
            changed.append(f'do.status={args.do_status}')

        if args.do_summary:
            if 'do' not in unit:
                unit['do'] = {}
            unit['do']['summary'] = args.do_summary
            changed.append(f'do.summary=...')

        if args.check_verdict:
            if 'check' not in unit:
                unit['check'] = {}
            unit['check']['verdict'] = args.check_verdict
            changed.append(f'check.verdict={args.check_verdict}')

        if args.topic_id:
            if 'metadata' not in unit:
                unit['metadata'] = {}
            unit['metadata']['topic_id'] = args.topic_id
            changed.append(f'metadata.topic_id={args.topic_id}')

        try:
            save_cycle(unit)
            print(json.dumps({'ok': True, 'changed': changed, 'cycle_id': args.cycle_id}))
        except CycleUnitWriteError as e:
            print(json.dumps({'ok': False, 'error': str(e)}))
            _sys.exit(1)

    elif args.command == 'show':
        try:
            unit = load_cycle(args.cycle_id, args.scope)
            print(json.dumps(unit, ensure_ascii=False, indent=2, default=str))
        except CycleUnitNotFoundError as e:
            print(json.dumps({'ok': False, 'error': str(e)}))
            _sys.exit(1)

    else:
        parser.print_help()
        _sys.exit(1)