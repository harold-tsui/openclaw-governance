#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleAggregator 集成测试 - Task→Topic→Project 层间传播
"""

import os
import sys
import yaml
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../modules'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../core'))

from modules.cycle_aggregator import CycleAggregator


def test_task_to_topic_propagation():
    """测试 Task → Topic 传播"""
    
    # 创建临时 cycles 目录
    temp_dir = tempfile.mkdtemp()
    cycles_dir = os.path.join(temp_dir, 'cycles')
    os.makedirs(os.path.join(cycles_dir, 'task'))
    os.makedirs(os.path.join(cycles_dir, 'topic'))
    
    aggregator = CycleAggregator(cycles_dir)
    
    try:
        # 创建 Topic 父环
        topic_data = {
            'id': 'topic-20260411',
            'scope': 'topic',
            'phase': 'act',
            'task_card_id': 'N4-P2-T01',
            'plan': {
                'human_approval_required': False,
                'time_horizon_cycles': 4,
                'max_cycles': 10
            },
            'check': {
                'verdict': 'pending',
                'evidence': []
            },
            'act': {
                'adjustments': [],
                'incoming_adjustments': [],
                'propagate_to': 'parent',
                'next_cycle': None
            },
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'version': 1
            }
        }
        
        topic_path = os.path.join(cycles_dir, 'topic', 'topic-20260411.yaml')
        with open(topic_path, 'w', encoding='utf-8') as f:
            yaml.dump(topic_data, f, allow_unicode=True, default_flow_style=False)
        
        # 创建 3 个 Task 子环
        task_ids = []
        for i in range(3):
            task_id = f'task-11111111{i}'
            task_data = {
                'id': task_id,
                'scope': 'task',
                'phase': 'act',
                'task_card_id': f'test-task-{i}',
                'parent_cycle_id': 'topic-20260411',
                'plan': {
                    'human_approval_required': False,
                    'time_horizon_cycles': 1,
                    'max_cycles': 3
                },
                'check': {
                    'verdict': 'pass' if i < 2 else 'fail',  # 2 个 pass，1 个 fail
                    'evidence': [f'{task_id} evidence 1', f'{task_id} evidence 2']
                },
                'act': {
                    'adjustments': [
                        {
                            'id': f'adjust-{i}',
                            'priority': 'P1' if i == 0 else 'P2',
                            'content': f'调整项 {i}'
                        }
                    ],
                    'propagate_to': 'parent',
                    'next_cycle': None
                },
                'metadata': {
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                    'version': 1
                }
            }
            
            task_path = os.path.join(cycles_dir, 'task', f'{task_id}.yaml')
            with open(task_path, 'w', encoding='utf-8') as f:
                yaml.dump(task_data, f, allow_unicode=True, default_flow_style=False)
            
            task_ids.append(task_id)
        
        # 验证 1: 聚合子环结果
        result = aggregator.aggregate_children('topic-20260411')
        print(f"聚合结果: verdict={result.verdict}")
        assert result.verdict == 'partial'  # 2 pass + 1 fail = partial
        assert result.child_count == 3
        assert result.pass_count == 2
        assert result.fail_count == 1
        print(f"  子环数: {result.child_count}, pass: {result.pass_count}, fail: {result.fail_count}")
        
        # 验证 2: 调整传播
        for task_id in task_ids:
            aggregator.propagate_adjustments(task_id)
        
        # 检查 Topic 的 incoming_adjustments
        with open(topic_path, 'r', encoding='utf-8') as f:
            topic_data = yaml.safe_load(f)
        
        assert len(topic_data['act']['incoming_adjustments']) == 3
        print(f"调整传播完成: {len(topic_data['act']['incoming_adjustments'])} 条调整项")
        
        # 验证 3: 状态冒泡
        for task_id in task_ids:
            aggregator.bubble_up_status(task_id)
        
        # 检查 Topic 的 evidence
        with open(topic_path, 'r', encoding='utf-8') as f:
            topic_data = yaml.safe_load(f)
        
        assert len(topic_data['check']['evidence']) == 6  # 3 个 task × 2 条 evidence
        print(f"状态冒泡完成: {len(topic_data['check']['evidence'])} 条 evidence")
        
        print("\nTask → Topic 传播验证通过！")
        
    finally:
        shutil.rmtree(temp_dir)


def test_topic_to_project_propagation():
    """测试 Topic → Project 传播"""
    
    # 创建临时 cycles 目录
    temp_dir = tempfile.mkdtemp()
    cycles_dir = os.path.join(temp_dir, 'cycles')
    os.makedirs(os.path.join(cycles_dir, 'topic'))
    os.makedirs(os.path.join(cycles_dir, 'project'))
    
    aggregator = CycleAggregator(cycles_dir)
    
    try:
        # 创建 Project 父环
        project_data = {
            'id': 'project-20260411',
            'scope': 'project',
            'phase': 'act',
            'task_card_id': 'ZT-P015',
            'plan': {
                'human_approval_required': True,  # L3
                'time_horizon_cycles': 48,
                'max_cycles': 10
            },
            'check': {
                'verdict': 'pending',
                'evidence': []
            },
            'act': {
                'adjustments': [],
                'incoming_adjustments': [],
                'propagate_to': 'parent',
                'next_cycle': None
            },
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'version': 1
            }
        }
        
        project_path = os.path.join(cycles_dir, 'project', 'project-20260411.yaml')
        with open(project_path, 'w', encoding='utf-8') as f:
            yaml.dump(project_data, f, allow_unicode=True, default_flow_style=False)
        
        # 创建 2 个 Topic 子环
        topic_ids = []
        for i in range(2):
            topic_id = f'topic-22222222{i}'
            topic_data = {
                'id': topic_id,
                'scope': 'topic',
                'phase': 'act',
                'task_card_id': f'test-topic-{i}',
                'parent_cycle_id': 'project-20260411',
                'plan': {
                    'human_approval_required': False,
                    'time_horizon_cycles': 4,
                    'max_cycles': 10
                },
                'check': {
                    'verdict': 'pass',
                    'evidence': [f'{topic_id} evidence 1', f'{topic_id} evidence 2']
                },
                'act': {
                    'adjustments': [
                        {
                            'id': f'topic-adjust-{i}',
                            'priority': 'P1',
                            'content': f'Topic 调整项 {i}'
                        }
                    ],
                    'propagate_to': 'parent',
                    'next_cycle': None
                },
                'metadata': {
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                    'version': 1
                }
            }
            
            topic_path = os.path.join(cycles_dir, 'topic', f'{topic_id}.yaml')
            with open(topic_path, 'w', encoding='utf-8') as f:
                yaml.dump(topic_data, f, allow_unicode=True, default_flow_style=False)
            
            topic_ids.append(topic_id)
        
        # 验证: 聚合 Topic → Project
        result = aggregator.aggregate_children('project-20260411')
        print(f"聚合结果: verdict={result.verdict}")
        assert result.verdict == 'pass'  # 所有 Topic 都 pass
        assert result.child_count == 2
        print(f"  子环数: {result.child_count}, pass: {result.pass_count}, fail: {result.fail_count}")
        
        # 调整传播
        for topic_id in topic_ids:
            aggregator.propagate_adjustments(topic_id)
        
        # 检查 Project 的 incoming_adjustments
        with open(project_path, 'r', encoding='utf-8') as f:
            project_data = yaml.safe_load(f)
        
        assert len(project_data['act']['incoming_adjustments']) == 2
        print(f"调整传播完成: {len(project_data['act']['incoming_adjustments'])} 条调整项")
        
        print("\nTopic → Project 传播验证通过！")
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("=" * 60)
    print("CycleAggregator 集成测试")
    print("=" * 60)
    
    print("\n### 测试 1: Task → Topic 传播 ###")
    test_task_to_topic_propagation()
    
    print("\n### 测试 2: Topic → Project 传播 ###")
    test_topic_to_project_propagation()
    
    print("\n" + "=" * 60)
    print("所有集成测试通过！")
    print("=" * 60)
