#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleAggregator 单元测试
"""

import os
import yaml
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path
import pytest

from modules.cycle_aggregator import (
    CycleAggregator,
    AggregatedResult,
    ParentNotFoundError,
    ChildNotFoundError
)


class TestCycleAggregator:
    """CycleAggregator 测试类"""
    
    def setup_method(self):
        """测试前准备"""
        # 创建临时 cycles 目录
        self.temp_dir = tempfile.mkdtemp()
        self.cycles_dir = os.path.join(self.temp_dir, 'cycles')
        os.makedirs(os.path.join(self.cycles_dir, 'task'))
        os.makedirs(os.path.join(self.cycles_dir, 'topic'))
        os.makedirs(os.path.join(self.cycles_dir, 'project'))
        os.makedirs(os.path.join(self.cycles_dir, 'system'))
        
        self.aggregator = CycleAggregator(self.cycles_dir)
    
    def teardown_method(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_cycle(self, scope: str, cycle_id: str, parent_id: str = None, verdict: str = 'pass', adjustments: list = None):
        """创建测试 CycleUnit 文件"""
        if adjustments is None:
            adjustments = []
        
        cycle_data = {
            'id': cycle_id,
            'scope': scope,
            'phase': 'act',
            'task_card_id': f'test-{scope}-001',
            'plan': {
                'human_approval_required': False,
                'time_horizon_cycles': 3,
                'max_cycles': 10
            },
            'check': {
                'verdict': verdict,
                'evidence': [f'{cycle_id} evidence 1', f'{cycle_id} evidence 2']
            },
            'act': {
                'adjustments': adjustments,
                'propagate_to': 'parent' if parent_id else 'self',
                'next_cycle': None
            },
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'version': 1
            }
        }
        
        if parent_id:
            cycle_data['parent_cycle_id'] = parent_id
        
        filepath = os.path.join(self.cycles_dir, scope, f'{cycle_id}.yaml')
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
        
        return filepath
    
    def test_aggregate_children_no_children(self):
        """测试聚合没有子环的情况"""
        self._create_test_cycle('topic', 'topic-1234567890')
        
        result = self.aggregator.aggregate_children('topic-1234567890')
        
        assert isinstance(result, AggregatedResult)
        assert result.verdict == 'pending'
        assert result.child_count == 0
        assert result.pass_count == 0
        assert result.fail_count == 0
        assert len(result.evidence) == 0
        assert len(result.adjustments) == 0
    
    def test_aggregate_children_all_pass(self):
        """测试所有子环都pass的情况"""
        # 创建父环
        self._create_test_cycle('topic', 'topic-1234567890')
        
        # 创建3个pass的子环
        for i in range(3):
            self._create_test_cycle(
                'task',
                f'task-111111111{i}',
                parent_id='topic-1234567890',
                verdict='pass',
                adjustments=[{'id': f'adjust-{i}', 'priority': 'P1', 'content': f'调整{i}'}]
            )
        
        result = self.aggregator.aggregate_children('topic-1234567890')
        
        assert result.verdict == 'pass'
        assert result.child_count == 3
        assert result.pass_count == 3
        assert result.fail_count == 0
        assert len(result.evidence) == 3 * 2  # 每个子环2条证据
        assert len(result.adjustments) == 3  # 每个子环1条调整
    
    def test_aggregate_children_some_fail(self):
        """测试部分子环fail的情况"""
        # 创建父环
        self._create_test_cycle('topic', 'topic-1234567890')
        
        # 2个pass，1个fail
        self._create_test_cycle('task', 'task-1111111110', parent_id='topic-1234567890', verdict='pass')
        self._create_test_cycle('task', 'task-1111111111', parent_id='topic-1234567890', verdict='fail')
        self._create_test_cycle('task', 'task-1111111112', parent_id='topic-1234567890', verdict='pass')
        
        result = self.aggregator.aggregate_children('topic-1234567890')
        
        assert result.verdict == 'partial'
        assert result.child_count == 3
        assert result.pass_count == 2
        assert result.fail_count == 1
    
    def test_aggregate_children_all_fail(self):
        """测试所有子环都fail的情况"""
        # 创建父环
        self._create_test_cycle('topic', 'topic-1234567890')
        
        # 3个fail
        for i in range(3):
            self._create_test_cycle('task', f'task-111111111{i}', parent_id='topic-1234567890', verdict='fail')
        
        result = self.aggregator.aggregate_children('topic-1234567890')
        
        assert result.verdict == 'fail'
        assert result.child_count == 3
        assert result.pass_count == 0
        assert result.fail_count == 3
    
    def test_aggregate_children_adjustments_sorted(self):
        """测试调整项按优先级排序"""
        # 创建父环
        self._create_test_cycle('topic', 'topic-1234567890')
        
        # 创建不同优先级的调整项
        self._create_test_cycle('task', 'task-1111111110', parent_id='topic-1234567890', verdict='pass',
                               adjustments=[{'id': 'adjust-1', 'priority': 'P3', 'content': '低优先级'}])
        self._create_test_cycle('task', 'task-1111111111', parent_id='topic-1234567890', verdict='pass',
                               adjustments=[{'id': 'adjust-2', 'priority': 'P1', 'content': '高优先级'}])
        self._create_test_cycle('task', 'task-1111111112', parent_id='topic-1234567890', verdict='pass',
                               adjustments=[{'id': 'adjust-3', 'priority': 'P2', 'content': '中优先级'}])
        
        result = self.aggregator.aggregate_children('topic-1234567890')
        
        # 检查排序结果：P1 → P2 → P3
        priorities = [a['priority'] for a in result.adjustments]
        assert priorities == ['P1', 'P2', 'P3']
    
    def test_bubble_up_status(self):
        """测试状态冒泡"""
        # 创建父环
        self._create_test_cycle('topic', 'topic-1234567890')
        # 创建子环
        self._create_test_cycle('task', 'task-1111111110', parent_id='topic-1234567890', verdict='pass')
        
        # 冒泡前父环已有 2 条 evidence（来自 _create_test_cycle）
        parent_path = os.path.join(self.cycles_dir, 'topic', 'topic-1234567890.yaml')
        with open(parent_path, 'r', encoding='utf-8') as f:
            parent_data = yaml.safe_load(f)
        assert len(parent_data['check']['evidence']) == 2
        
        # 执行冒泡
        self.aggregator.bubble_up_status('task-1111111110')
        
        # 检查父环evidence（应该是 4 条：父环原有 2 条 + 子环追加 2 条）
        with open(parent_path, 'r', encoding='utf-8') as f:
            parent_data = yaml.safe_load(f)
        assert len(parent_data['check']['evidence']) == 4
        assert 'task-1111111110 evidence 1' in parent_data['check']['evidence']
        assert 'task-1111111110 evidence 2' in parent_data['check']['evidence']
    
    def test_bubble_up_status_no_parent(self):
        """测试子环没有父环时冒泡不报错"""
        # 创建没有父环的子环
        self._create_test_cycle('task', 'task-1111111110', parent_id=None)
        
        # 执行冒泡，应该不报错
        self.aggregator.bubble_up_status('task-1111111110')  # 不抛出异常
    
    def test_bubble_up_status_child_not_found(self):
        """测试子环不存在时抛出异常"""
        with pytest.raises(ChildNotFoundError):
            self.aggregator.bubble_up_status('nonexistent-task-id')
    
    def test_propagate_adjustments(self):
        """测试调整传播"""
        # 创建父环
        self._create_test_cycle('topic', 'topic-1234567890')
        # 创建子环，带有调整项，propagate_to=parent
        self._create_test_cycle('task', 'task-1111111110', parent_id='topic-1234567890', verdict='pass',
                               adjustments=[{'id': 'adjust-1', 'priority': 'P1', 'content': '测试调整'}])
        
        # 传播前父环没有 incoming_adjustments
        parent_path = os.path.join(self.cycles_dir, 'topic', 'topic-1234567890.yaml')
        with open(parent_path, 'r', encoding='utf-8') as f:
            parent_data = yaml.safe_load(f)
        assert 'incoming_adjustments' not in parent_data.get('act', {})
        
        # 执行传播
        self.aggregator.propagate_adjustments('task-1111111110')
        
        # 检查父环 incoming_adjustments
        with open(parent_path, 'r', encoding='utf-8') as f:
            parent_data = yaml.safe_load(f)
        assert len(parent_data['act']['incoming_adjustments']) == 1
        assert parent_data['act']['incoming_adjustments'][0]['id'] == 'adjust-1'
    
    def test_propagate_adjustments_no_propagate(self):
        """测试 propagate_to=self 时不传播"""
        # 创建父环
        self._create_test_cycle('topic', 'topic-1234567890')
        # 创建子环，propagate_to=self
        self._create_test_cycle('task', 'task-1111111110', parent_id='topic-1234567890', verdict='pass',
                               adjustments=[{'id': 'adjust-1', 'priority': 'P1', 'content': '测试调整'}])
        # 修改子环的 propagate_to 为 self
        child_path = os.path.join(self.cycles_dir, 'task', 'task-1111111110.yaml')
        with open(child_path, 'r', encoding='utf-8') as f:
            child_data = yaml.safe_load(f)
        child_data['act']['propagate_to'] = 'self'
        with open(child_path, 'w', encoding='utf-8') as f:
            yaml.dump(child_data, f, allow_unicode=True, default_flow_style=False)
        
        # 执行传播
        self.aggregator.propagate_adjustments('task-1111111110')
        
        # 父环应该没有 incoming_adjustments
        parent_path = os.path.join(self.cycles_dir, 'topic', 'topic-1234567890.yaml')
        with open(parent_path, 'r', encoding='utf-8') as f:
            parent_data = yaml.safe_load(f)
        assert 'incoming_adjustments' not in parent_data.get('act', {})
    
    def test_propagate_adjustments_no_parent(self):
        """测试子环没有父环时传播不报错"""
        # 创建没有父环的子环
        self._create_test_cycle('task', 'task-1111111110', parent_id=None)
        
        # 执行传播，应该不报错
        self.aggregator.propagate_adjustments('task-1111111110')  # 不抛出异常
    
    def test_get_scope_from_id(self):
        """测试从ID解析粒度"""
        assert self.aggregator._get_scope_from_id('task-123456') == 'task'
        assert self.aggregator._get_scope_from_id('topic-123456') == 'topic'
        assert self.aggregator._get_scope_from_id('project-123456') == 'project'
        assert self.aggregator._get_scope_from_id('system-123456') == 'system'
        assert self.aggregator._get_scope_from_id('unknown-123456') == 'task'  # 默认
    
    def test_find_cycle_file(self):
        """测试查找CycleUnit文件"""
        self._create_test_cycle('task', 'task-1234567890')
        
        path = self.aggregator._find_cycle_file('task-1234567890')
        assert path is not None
        assert os.path.exists(path)
        
        # 不存在的ID
        assert self.aggregator._find_cycle_file('nonexistent-task') is None


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
