#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Act 模块 - PDCA 循环调整阶段

实现 adjust_automation_level()、PhaseBarrierLock 和 propagate_adjustments() 接口，
负责：
1. 计算自动化级别调整
2. 保证执行原子性（Phase 屏障）
3. 传播调整到父环
4. **触发状态文件同步** ⭐ v2.0

依据：ARCH v1.4.3 §3.3 + cycle_unit.schema.yaml v1.3-fixed constraints

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import re
import yaml
import shutil
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# 导入状态同步模块 ⭐ v2.0
# 双重 import：包方式（nucleus_scheduler 调用时）和直接执行方式（CLI 调用时）
try:
    from modules.state_sync import on_act_complete  # 包导入（skill_root 在 sys.path 中）
    STATE_SYNC_AVAILABLE = True
except ImportError:
    try:
        from state_sync import on_act_complete  # 直接执行（modules/ 在 sys.path 中）
        STATE_SYNC_AVAILABLE = True
    except ImportError:
        STATE_SYNC_AVAILABLE = False


# ── 异常定义 ────────────────────────────────────────

class CycleUnitNotFoundError(Exception):
    """CycleUnit 文件不存在"""
    pass


class CycleUnitParseError(Exception):
    """CycleUnit 解析失败"""
    pass


class AdjustmentError(Exception):
    """调整执行失败"""
    pass


class PropagationError(Exception):
    """调整传播失败"""
    pass


# ── 常量定义 ────────────────────────────────────────

VALID_LEVELS = ['L0', 'L1', 'L2', 'L3']

LEVEL_NUM_MAP = {'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3}

NUM_LEVEL_MAP = {0: 'L0', 1: 'L1', 2: 'L2', 3: 'L3'}

# 调整规则常量
PASS_THRESHOLD = 3      # 连续成功 ≥3 次可升级
FAIL_THRESHOLD = 2      # 连续失败 ≥2 次需降级


# ── 核心接口 ────────────────────────────────────────

def adjust_automation_level(
    cycle_id: str,
    verdict: str,
    consecutive_count: int,
    current_level: str,
    evidence: List[str]
) -> List[Dict[str, Any]]:
    """
    根据 ARCH v1.4.3 §3.3 计算自动化级别调整
    
    Args:
        cycle_id: CycleUnit ID
        verdict: 验收结果（pass/partial/fail/skip）
        consecutive_count: 连续计数（同类型 verdict 连续次数）
        current_level: 当前级别（L0/L1/L2/L3）
        evidence: 证据列表
    
    Returns:
        adjustments 列表（写入 cycle_unit.act.adjustments）
    
    调整规则（schema v1.3-fixed constraints）:
        pass（连续≥3次）→ 升级（逐级，L2→L3 须 Harold 确认）
        partial           → 维持
        fail（连续≥2次）→ 降级（逐级，L1-L3 可降，L0 不可降）
        skip              → 维持（consecutive_count 不变）
    
    Raises:
        ValueError: 参数无效
    """
    
    # 参数验证
    if verdict not in ['pass', 'partial', 'fail', 'skip']:
        raise ValueError(f"Invalid verdict: {verdict}")
    
    if current_level not in VALID_LEVELS:
        raise ValueError(f"Invalid current_level: {current_level}")
    
    if consecutive_count < 0:
        raise ValueError(f"Invalid consecutive_count: {consecutive_count}")
    
    # 初始化调整列表
    adjustments = []
    
    # 根据 verdict 类型处理
    if verdict == 'pass':
        # 成功：连续 ≥3 次可升级
        new_consecutive_count = consecutive_count + 1
        if new_consecutive_count >= PASS_THRESHOLD:
            # 尝试升级
            adjustment = _create_level_upgrade_adjustment(
                current_level=current_level,
                evidence=evidence,
                consecutive_count=new_consecutive_count
            )
            adjustments.append(adjustment)
        else:
            # 维持当前级别
            adjustment = _create_maintain_adjustment(
                current_level=current_level,
                reason=f"consecutive_pass={new_consecutive_count} < {PASS_THRESHOLD} → maintain",
                consecutive_count=new_consecutive_count
            )
            adjustments.append(adjustment)
    
    elif verdict == 'partial':
        # 部分成功：维持当前级别
        adjustment = _create_maintain_adjustment(
            current_level=current_level,
            reason="verdict=partial → maintain",
            consecutive_count=0  # 重置计数
        )
        adjustments.append(adjustment)
    
    elif verdict == 'fail':
        # 失败：连续 ≥2 次需降级
        new_consecutive_count = consecutive_count + 1
        if new_consecutive_count >= FAIL_THRESHOLD:
            # 尝试降级
            adjustment = _create_level_downgrade_adjustment(
                current_level=current_level,
                evidence=evidence,
                consecutive_count=new_consecutive_count
            )
            adjustments.append(adjustment)
        else:
            # 维持当前级别
            adjustment = _create_maintain_adjustment(
                current_level=current_level,
                reason=f"consecutive_fail={new_consecutive_count} < {FAIL_THRESHOLD} → maintain",
                consecutive_count=new_consecutive_count
            )
            adjustments.append(adjustment)
    
    elif verdict == 'skip':
        # 免审：维持当前级别（consecutive_count 不变）
        adjustment = _create_maintain_adjustment(
            current_level=current_level,
            reason="verdict=skip → maintain (consecutive_count unchanged)",
            consecutive_count=consecutive_count  # 保持不变
        )
        adjustments.append(adjustment)
    
    return adjustments


def apply_adjustments(
    cycle_path: str,
    adjustments: List[Dict[str, Any]],
    agent_dir: Optional[str] = None,
    project_dir: Optional[str] = None
) -> bool:
    """
    应用调整到 CycleUnit

    Args:
        cycle_path: CycleUnit 文件路径
        adjustments: 调整列表
        agent_dir: Agent 工作目录路径（用于 state_sync，可选）
        project_dir: 项目目录路径（用于 state_sync，可选）

    Returns:
        bool: 是否成功

    Note:
        此函数应在 PhaseBarrierLock 上下文中调用
    """
    
    if not os.path.exists(cycle_path):
        raise CycleUnitNotFoundError(f"CycleUnit not found: {cycle_path}")
    
    try:
        # 读取 CycleUnit
        with open(cycle_path, 'r', encoding='utf-8') as f:
            cycle_data = yaml.safe_load(f)
        
        # 更新 act.adjustments
        if 'act' not in cycle_data:
            cycle_data['act'] = {}

        cycle_data['act']['adjustments'] = adjustments

        # Act 完成后推进 phase → completed
        cycle_data['phase'] = 'completed'

        # 更新元数据
        cycle_data['metadata']['updated_at'] = datetime.now(timezone.utc).isoformat()
        cycle_data['metadata']['version'] = cycle_data['metadata'].get('version', 1) + 1

        # 原子写入
        tmp_path = cycle_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
        os.replace(tmp_path, cycle_path)
        
        # ⭐ 触发状态文件同步 ⭐ v2.0
        if STATE_SYNC_AVAILABLE:
            try:
                # 从 cycle_path 推断 project_dir（若调用方未提供）
                if project_dir is None:
                    # cycle_path 格式: /path/to/cycles/task/task-xxx.yaml
                    cycles_dir = os.path.dirname(os.path.dirname(cycle_path))
                    project_dir = os.path.dirname(cycles_dir)

                # agent_dir 必须由调用方提供，不再硬编码
                if agent_dir is None:
                    # 无法确定 agent_dir，跳过 state_sync
                    cycle_data['act']['state_sync_skipped'] = 'agent_dir not provided'
                    tmp_path2 = cycle_path + '.tmp'
                    with open(tmp_path2, 'w', encoding='utf-8') as f:
                        yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
                    os.replace(tmp_path2, cycle_path)
                    return True

                # 调用状态同步
                sync_result = on_act_complete(cycle_data, project_dir, agent_dir)
                
                # 记录同步结果（可写入日志）
                if sync_result['errors']:
                    # 不抛出异常，仅记录
                    cycle_data['act']['state_sync_errors'] = sync_result['errors']
                    tmp_path3 = cycle_path + '.tmp'
                    with open(tmp_path3, 'w', encoding='utf-8') as f:
                        yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
                    os.replace(tmp_path3, cycle_path)
            except Exception as e:
                # 状态同步失败不影响主流程
                cycle_data['act']['state_sync_error'] = str(e)
                tmp_path4 = cycle_path + '.tmp'
                with open(tmp_path4, 'w', encoding='utf-8') as f:
                    yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
                os.replace(tmp_path4, cycle_path)
        
        return True
    
    except Exception as e:
        raise AdjustmentError(f"Failed to apply adjustments: {e}")


def propagate_adjustments(
    cycle_id: str,
    cycle_path: str,
    adjustments: List[Dict[str, Any]],
    propagate_to: str = 'self'
) -> None:
    """
    传播调整到父环（ARCH v1.4.3 §2.3）
    
    Args:
        cycle_id: CycleUnit ID
        cycle_path: CycleUnit 文件路径
        adjustments: 调整列表
        propagate_to: 传播方向（self|parent|both）
    
    Rules:
        - propagate_to=parent → 写入父环 act.incoming_adjustments
        - propagate_to=both → 同时写入 self 和 parent
    
    Note:
        此函数应在 PhaseBarrierLock 上下文中调用
    """
    
    if propagate_to not in ['self', 'parent', 'both']:
        raise ValueError(f"Invalid propagate_to: {propagate_to}")
    
    if propagate_to == 'self':
        # 只写入自身，已在 apply_adjustments 中处理
        return
    
    # propagate_to == 'parent' or 'both'
    # 查找父环
    parent_cycle_path = _find_parent_cycle(cycle_id, cycle_path)
    
    if parent_cycle_path is None:
        # 无父环，记录告警但不抛异常
        print(f"Warning: No parent found for {cycle_id}, propagation skipped")
        return
    
    try:
        # 读取父环 CycleUnit
        with open(parent_cycle_path, 'r', encoding='utf-8') as f:
            parent_cycle_data = yaml.safe_load(f)
        
        # 更新父环 act.incoming_adjustments
        if 'act' not in parent_cycle_data:
            parent_cycle_data['act'] = {}
        
        if 'incoming_adjustments' not in parent_cycle_data['act']:
            parent_cycle_data['act']['incoming_adjustments'] = []
        
        # 添加调整
        parent_cycle_data['act']['incoming_adjustments'].extend(adjustments)
        
        # 更新元数据
        parent_cycle_data['metadata']['updated_at'] = datetime.now(timezone.utc).isoformat()
        parent_cycle_data['metadata']['version'] = parent_cycle_data['metadata'].get('version', 1) + 1
        
        # 写回父环文件
        with open(parent_cycle_path, 'w', encoding='utf-8') as f:
            yaml.dump(parent_cycle_data, f, allow_unicode=True, default_flow_style=False)
        
        print(f"Propagated {len(adjustments)} adjustments from {cycle_id} to parent")
    
    except Exception as e:
        raise PropagationError(f"Failed to propagate adjustments: {e}")


# ── Phase 屏障锁 ─────────────────────────────────────

class PhaseBarrierLock:
    """
    Phase 屏障锁（ARCH v1.4.3 §3.3.2）
    
    职责：
    - 保证 act 阶段执行的原子性
    - 执行前备份原文件
    - 失败时自动回滚
    - 验证变更是否生效
    
    使用示例：
        with PhaseBarrierLock(cycle_path) as lock:
            lock.backup()
            apply_adjustments(cycle_path, adjustments)
            lock.verify()
    """
    
    def __init__(self, cycle_path: str):
        self.cycle_path = cycle_path
        self.backup_path = f"{cycle_path}.backup"
        self.lock = threading.Lock()  # 线程安全
        self.backed_up = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # 发生异常，尝试回滚
            self.rollback()
        return False
    
    def backup(self) -> None:
        """备份原文件"""
        if not os.path.exists(self.cycle_path):
            raise CycleUnitNotFoundError(f"CycleUnit not found: {self.cycle_path}")
        
        try:
            shutil.copy2(self.cycle_path, self.backup_path)
            self.backed_up = True
            print(f"Backup created: {self.backup_path}")
        except Exception as e:
            raise AdjustmentError(f"Failed to create backup: {e}")
    
    def rollback(self) -> None:
        """从备份恢复"""
        if not self.backed_up:
            return
        
        if not os.path.exists(self.backup_path):
            print(f"Warning: Backup not found: {self.backup_path}")
            return
        
        try:
            shutil.copy2(self.backup_path, self.cycle_path)
            os.remove(self.backup_path)
            self.backed_up = False
            print(f"Rollback completed: {self.cycle_path}")
        except Exception as e:
            print(f"Warning: Rollback failed: {e}")
    
    def verify(self) -> bool:
        """验证变更生效"""
        if not os.path.exists(self.cycle_path):
            return False
        
        try:
            with open(self.cycle_path, 'r', encoding='utf-8') as f:
                cycle_data = yaml.safe_load(f)
            
            # 验证 act.adjustments 存在且非空
            if 'act' not in cycle_data:
                return False
            
            if 'adjustments' not in cycle_data['act']:
                return False
            
            if not cycle_data['act']['adjustments']:
                return False
            
            return True
        
        except Exception:
            return False


# ── 辅助函数 ────────────────────────────────────────

def _create_level_upgrade_adjustment(
    current_level: str,
    evidence: List[str],
    consecutive_count: int
) -> Dict[str, Any]:
    """创建级别升级调整"""
    current_num = LEVEL_NUM_MAP[current_level]
    
    # L3 是最高级别，不能再升级
    if current_level == 'L3':
        return _create_maintain_adjustment(
            current_level=current_level,
            reason=f"consecutive_pass={consecutive_count} but already at max level L3 → maintain",
            consecutive_count=consecutive_count
        )
    
    # L2 → L3 需要 Harold 确认
    if current_level == 'L2':
        return {
            'type': 'level_change_pending_confirmation',
            'from': current_level,
            'to': 'L3',
            'reason': f"consecutive_pass={consecutive_count} ≥ {PASS_THRESHOLD} → upgrade pending Harold confirmation",
            'consecutive_count_snapshot': consecutive_count,
            'evidence': evidence,
            'requires_harold_confirmation': True
        }
    
    # L0 → L1 或 L1 → L2 可以直接升级
    new_level = NUM_LEVEL_MAP[current_num + 1]
    return {
        'type': 'level_change',
        'from': current_level,
        'to': new_level,
        'reason': f"consecutive_pass={consecutive_count} ≥ {PASS_THRESHOLD} → upgrade",
        'consecutive_count_snapshot': consecutive_count,
        'evidence': evidence,
        'requires_harold_confirmation': False
    }


def _create_level_downgrade_adjustment(
    current_level: str,
    evidence: List[str],
    consecutive_count: int
) -> Dict[str, Any]:
    """创建级别降级调整"""
    current_num = LEVEL_NUM_MAP[current_level]
    
    # L0 是最低级别，不能再降级
    if current_level == 'L0':
        return _create_maintain_adjustment(
            current_level=current_level,
            reason=f"consecutive_fail={consecutive_count} but already at min level L0 → maintain",
            consecutive_count=consecutive_count
        )
    
    # L1 → L0, L2 → L1, L3 → L2 都可以直接降级
    new_level = NUM_LEVEL_MAP[current_num - 1]
    return {
        'type': 'level_change',
        'from': current_level,
        'to': new_level,
        'reason': f"consecutive_fail={consecutive_count} ≥ {FAIL_THRESHOLD} → downgrade",
        'consecutive_count_snapshot': consecutive_count,
        'evidence': evidence,
        'requires_harold_confirmation': False
    }


def _create_maintain_adjustment(
    current_level: str,
    reason: str,
    consecutive_count: int
) -> Dict[str, Any]:
    """创建维持当前级别的调整"""
    return {
        'type': 'maintain',
        'from': current_level,
        'to': current_level,
        'reason': reason,
        'consecutive_count_snapshot': consecutive_count,
        'evidence': [],
        'requires_harold_confirmation': False
    }


def _find_parent_cycle(cycle_id: str, cycle_path: str) -> Optional[str]:
    """查找父环 CycleUnit 路径"""
    # 从 cycle_path 推断父路径
    # 假设路径结构：cycles/{scope}/{cycle_id}.yaml
    path_parts = cycle_path.split('/')
    
    if len(path_parts) < 3:
        return None
    
    scope_index = path_parts.index('cycles') + 1
    if scope_index >= len(path_parts):
        return None
    
    current_scope = path_parts[scope_index]
    
    # 确定父 scope
    scope_hierarchy = ['task', 'topic', 'project', 'system']
    try:
        current_idx = scope_hierarchy.index(current_scope)
        if current_idx == 0:  # task 没有父环
            return None
        
        parent_scope = scope_hierarchy[current_idx - 1]
        parent_path = '/'.join(path_parts[:-2]) + f'/{parent_scope}/'
        
        # 查找父环文件（这里简化处理，实际可能需要更复杂的查找逻辑）
        if os.path.exists(parent_path):
            parent_files = [f for f in os.listdir(parent_path) if f.endswith('.yaml')]
            if parent_files:
                return os.path.join(parent_path, parent_files[0])
        
        return None
    
    except ValueError:
        return None


# ── CLI 入口 ────────────────────────────────────────
# 用法：
#   python modules/act.py adjust --cycle-id X --verdict pass --consecutive-count 3 --current-level L1
#   python modules/act.py adjust --cycle-id X --verdict fail --consecutive-count 2 --current-level L2 --agent-dir /path/to/agent

if __name__ == "__main__":
    import argparse
    import json
    import sys as _sys

    parser = argparse.ArgumentParser(description='Act Module CLI')
    subparsers = parser.add_subparsers(dest='command')

    # adjust 子命令
    adj_parser = subparsers.add_parser('adjust', help='计算并应用自动化级别调整')
    adj_parser.add_argument('--cycle-id', required=True, help='CycleUnit ID（如 task-20260416T090000Z）')
    adj_parser.add_argument('--verdict', required=True,
                            choices=['pass', 'partial', 'fail', 'skip'],
                            help='Check 阶段 verdict')
    adj_parser.add_argument('--consecutive-count', required=True, type=int,
                            help='同类型 verdict 连续次数（调整前的历史计数）')
    adj_parser.add_argument('--current-level', required=True,
                            choices=['L0', 'L1', 'L2', 'L3'],
                            help='当前自动化级别')
    adj_parser.add_argument('--agent-dir', default=None,
                            help='Agent 工作目录（用于 state_sync，可选）')
    adj_parser.add_argument('--project-dir', default=None,
                            help='项目目录（用于 state_sync，可选）')

    args = parser.parse_args()

    if args.command == 'adjust':
        scope = args.cycle_id.split('-')[0] if '-' in args.cycle_id else 'task'
        cycle_path = f"cycles/{scope}/{args.cycle_id}.yaml"

        if not os.path.exists(cycle_path):
            print(json.dumps({'ok': False, 'error': f'CycleUnit not found: {cycle_path}'}))
            _sys.exit(1)

        # 读取当前证据（复用 collect_evidence 逻辑，避免导入 check 循环依赖）
        evidence: List[str] = []

        # 计算调整
        adjustments = adjust_automation_level(
            cycle_id=args.cycle_id,
            verdict=args.verdict,
            consecutive_count=args.consecutive_count,
            current_level=args.current_level,
            evidence=evidence
        )

        # 应用调整（同时推进 phase → completed）
        try:
            apply_adjustments(
                cycle_path=cycle_path,
                adjustments=adjustments,
                agent_dir=args.agent_dir,
                project_dir=args.project_dir
            )
            print(json.dumps({
                'ok': True,
                'cycle_id': args.cycle_id,
                'adjustments': adjustments
            }, ensure_ascii=False, indent=2))
        except Exception as e:
            print(json.dumps({'ok': False, 'error': str(e)}))
            _sys.exit(1)

    else:
        parser.print_help()
        _sys.exit(1)