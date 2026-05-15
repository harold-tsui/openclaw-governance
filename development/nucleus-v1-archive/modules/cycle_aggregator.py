#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleAggregator - 层间聚合器

实现子环聚合、状态冒泡、调整传播功能。
基于 ARCH v1.4.3 §2.3 规范。

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import yaml
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path


class CycleAggregatorError(Exception):
    """CycleAggregator 操作异常基类"""
    pass


class ParentNotFoundError(CycleAggregatorError):
    """父环未找到"""
    pass


class ChildNotFoundError(CycleAggregatorError):
    """子环未找到"""
    pass


# ── 核心类 ────────────────────────────────────────

class AggregatedResult:
    """聚合结果"""
    
    def __init__(self):
        self.verdict: str = 'pending'
        self.evidence: List[str] = []
        self.child_count: int = 0
        self.pass_count: int = 0
        self.fail_count: int = 0
        self.adjustments: List[Dict[str, Any]] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'verdict': self.verdict,
            'evidence': self.evidence,
            'child_count': self.child_count,
            'pass_count': self.pass_count,
            'fail_count': self.fail_count,
            'adjustments': self.adjustments
        }


class CycleAggregator:
    """
    层间聚合器
    
    职责：
    - 聚合子环结果
    - 状态冒泡
    - 调整传播
    
    依据：ARCH v1.4.3 §2.3
    """
    
    def __init__(self, cycles_dir: str):
        """
        Args:
            cycles_dir: cycles 目录路径
        """
        self.cycles_dir = cycles_dir
    
    def aggregate_children(self, parent_cycle_id: str) -> AggregatedResult:
        """
        聚合子环结果
        
        Args:
            parent_cycle_id: 父环 CycleUnit ID
            
        Returns:
            AggregatedResult: 聚合结果
        
        规则：
            - verdict: 所有子环 pass → pass；任一 fail → partial/fail
            - evidence: 子环 evidence 列表合并
            - adjustments: 子环 adjustments 按优先级排序
        """
        result = AggregatedResult()
        
        # 查找子环
        children = self._find_children(parent_cycle_id)
        result.child_count = len(children)
        
        if not children:
            # 无子环，返回 pending
            result.verdict = 'pending'
            return result
        
        # 聚合每个子环
        for child_path in children:
            with open(child_path, 'r', encoding='utf-8') as f:
                child_data = yaml.safe_load(f)
            
            # 获取 verdict
            child_verdict = child_data.get('check', {}).get('verdict', 'pending')
            
            if child_verdict == 'pass':
                result.pass_count += 1
            elif child_verdict == 'fail':
                result.fail_count += 1
            
            # 获取 evidence
            child_evidence = child_data.get('check', {}).get('evidence', [])
            result.evidence.extend(child_evidence)
            
            # 获取 adjustments
            child_adjustments = child_data.get('act', {}).get('adjustments', [])
            result.adjustments.extend(child_adjustments)
        
        # 计算 verdict
        if result.fail_count > 0:
            result.verdict = 'fail' if result.fail_count == result.child_count else 'partial'
        elif result.pass_count == result.child_count:
            result.verdict = 'pass'
        else:
            result.verdict = 'partial'
        
        # 按优先级排序 adjustments
        result.adjustments.sort(key=lambda a: a.get('priority', 'P3'))
        
        return result
    
    def bubble_up_status(self, child_cycle_id: str) -> None:
        """
        状态冒泡到父环
        
        Args:
            child_cycle_id: 子环 CycleUnit ID
        
        行为：
            - 更新父环 check.evidence（追加子环 evidence）
            - 更新父环 check.verdict（如果尚未完成）
        """
        # 找到子环文件
        child_path = self._find_cycle_file(child_cycle_id)
        
        if not child_path:
            raise ChildNotFoundError(f"Child cycle not found: {child_cycle_id}")
        
        # 加载子环数据
        with open(child_path, 'r', encoding='utf-8') as f:
            child_data = yaml.safe_load(f)
        
        # 找到父环
        parent_cycle_id = self._get_parent_cycle_id(child_cycle_id)
        
        if not parent_cycle_id:
            # 无父环（顶层），跳过冒泡
            return
        
        parent_path = self._find_cycle_file(parent_cycle_id)
        
        if not parent_path:
            raise ParentNotFoundError(f"Parent cycle not found: {parent_cycle_id}")
        
        # 加载父环数据
        with open(parent_path, 'r', encoding='utf-8') as f:
            parent_data = yaml.safe_load(f)
        
        # 冒泡 evidence
        child_evidence = child_data.get('check', {}).get('evidence', [])
        parent_evidence = parent_data.get('check', {}).get('evidence', [])
        parent_evidence.extend(child_evidence)
        
        # 更新父环 check
        if 'check' not in parent_data:
            parent_data['check'] = {}
        
        parent_data['check']['evidence'] = parent_evidence
        
        # 写回父环
        with open(parent_path, 'w', encoding='utf-8') as f:
            yaml.dump(parent_data, f, allow_unicode=True, default_flow_style=False)
    
    def propagate_adjustments(self, child_cycle_id: str) -> None:
        """
        调整传播到父环
        
        Args:
            child_cycle_id: 子环 CycleUnit ID
        
        行为：
            - 子环 adjustments → 父环 incoming_adjustments
            - 按 propagate_to 规则传播
        """
        # 找到子环文件
        child_path = self._find_cycle_file(child_cycle_id)
        
        if not child_path:
            raise ChildNotFoundError(f"Child cycle not found: {child_cycle_id}")
        
        # 加载子环数据
        with open(child_path, 'r', encoding='utf-8') as f:
            child_data = yaml.safe_load(f)
        
        # 获取 adjustments
        adjustments = child_data.get('act', {}).get('adjustments', [])
        
        # 检查 propagate_to
        propagate_to = child_data.get('act', {}).get('propagate_to', 'self')
        
        if propagate_to not in ['parent', 'both']:
            # 不传播到父环
            return
        
        # 找到父环
        parent_cycle_id = self._get_parent_cycle_id(child_cycle_id)
        
        if not parent_cycle_id:
            # 无父环，跳过传播
            return
        
        parent_path = self._find_cycle_file(parent_cycle_id)
        
        if not parent_path:
            raise ParentNotFoundError(f"Parent cycle not found: {parent_cycle_id}")
        
        # 加载父环数据
        with open(parent_path, 'r', encoding='utf-8') as f:
            parent_data = yaml.safe_load(f)
        
        # 更新父环 incoming_adjustments
        if 'act' not in parent_data:
            parent_data['act'] = {}
        
        incoming = parent_data['act'].get('incoming_adjustments', [])
        incoming.extend(adjustments)
        parent_data['act']['incoming_adjustments'] = incoming
        
        # 写回父环
        with open(parent_path, 'w', encoding='utf-8') as f:
            yaml.dump(parent_data, f, allow_unicode=True, default_flow_style=False)
    
    # ── 辅助方法 ────────────────────────────────────────
    
    def _find_children(self, parent_cycle_id: str) -> List[str]:
        """
        查找父环的所有子环
        
        Args:
            parent_cycle_id: 父环 CycleUnit ID
            
        Returns:
            子环文件路径列表
        """
        # 从 parent_cycle_id 解析粒度
        parent_scope = self._get_scope_from_id(parent_cycle_id)
        
        # 子环粒度 = 父环粒度的下一级
        child_scope_map = {
            'system': 'project',
            'project': 'topic',
            'topic': 'task',
            'task': None  # task 无子环
        }
        
        child_scope = child_scope_map.get(parent_scope)
        
        if not child_scope:
            return []
        
        # 扫描子环目录
        child_dir = os.path.join(self.cycles_dir, child_scope)
        
        if not os.path.exists(child_dir):
            return []
        
        children = []
        for filename in os.listdir(child_dir):
            if filename.endswith('.yaml'):
                child_path = os.path.join(child_dir, filename)
                
                # 检查是否属于该父环（容错处理）
                try:
                    with open(child_path, 'r', encoding='utf-8') as f:
                        child_data = yaml.safe_load(f)
                    
                    if not child_data:
                        # YAML 解析失败，跳过
                        continue
                    
                    # 通过 parent_cycle_id 字段判断
                    child_parent = child_data.get('parent_cycle_id')
                    
                    if child_parent == parent_cycle_id:
                        children.append(child_path)
                except yaml.YAMLError:
                    # YAML 解析错误，跳过损坏文件
                    continue
        
        return children
    
    def _find_cycle_file(self, cycle_id: str) -> Optional[str]:
        """
        查找 CycleUnit 文件
        
        Args:
            cycle_id: CycleUnit ID
            
        Returns:
            文件路径或 None
        """
        scope = self._get_scope_from_id(cycle_id)
        filename = f"{cycle_id}.yaml"
        filepath = os.path.join(self.cycles_dir, scope, filename)
        
        if os.path.exists(filepath):
            return filepath
        
        return None
    
    def _get_scope_from_id(self, cycle_id: str) -> str:
        """
        从 CycleUnit ID 解析粒度
        
        Args:
            cycle_id: CycleUnit ID（如 task-xxx, topic-xxx）
            
        Returns:
            粒度（task/topic/project/system）
        """
        # ID 格式: {scope}-{timestamp}
        if cycle_id.startswith('task-'):
            return 'task'
        elif cycle_id.startswith('topic-'):
            return 'topic'
        elif cycle_id.startswith('project-'):
            return 'project'
        elif cycle_id.startswith('system-'):
            return 'system'
        
        return 'task'  # 默认
    
    def _get_parent_cycle_id(self, child_cycle_id: str) -> Optional[str]:
        """
        获取父环 ID
        
        Args:
            child_cycle_id: 子环 CycleUnit ID
            
        Returns:
            父环 ID 或 None
        """
        # 从子环文件读取 parent_cycle_id
        child_path = self._find_cycle_file(child_cycle_id)
        
        if not child_path:
            return None
        
        with open(child_path, 'r', encoding='utf-8') as f:
            child_data = yaml.safe_load(f)
        
        return child_data.get('parent_cycle_id')


# ── CLI 接口 ────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='CycleAggregator 层间聚合器')
    parser.add_argument('--cycles-dir', required=True, help='cycles 目录路径')
    parser.add_argument('--parent-id', help='父环 CycleUnit ID')
    parser.add_argument('--child-id', help='子环 CycleUnit ID')
    parser.add_argument('--action', choices=['aggregate', 'bubble', 'propagate'], required=True)
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    
    args = parser.parse_args()
    
    aggregator = CycleAggregator(args.cycles_dir)
    
    if args.action == 'aggregate':
        result = aggregator.aggregate_children(args.parent_id)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(f"聚合结果: {result.verdict}")
            print(f"  子环数: {result.child_count}")
            print(f"  pass: {result.pass_count}, fail: {result.fail_count}")
    
    elif args.action == 'bubble':
        aggregator.bubble_up_status(args.child_id)
        print(f"✅ 状态冒泡完成")
    
    elif args.action == 'propagate':
        aggregator.propagate_adjustments(args.child_id)
        print(f"✅ 调整传播完成")