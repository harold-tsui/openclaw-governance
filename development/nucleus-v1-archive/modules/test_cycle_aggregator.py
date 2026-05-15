#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleAggregator 单元测试

验证 aggregate_children()、bubble_up_status()、propagate_adjustments()。

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import tempfile
import yaml
import sys

sys.path.insert(0, os.path.dirname(__file__))
from cycle_aggregator import CycleAggregator, AggregatedResult


def test_aggregate_all_pass():
    """测试所有子环 pass → 父环 pass"""
    print("Testing aggregate_all_pass...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建父环
        parent_id = 'topic-001'
        parent_path = f"{tmpdir}/topic/{parent_id}.yaml"
        os.makedirs(f"{tmpdir}/topic", exist_ok=True)
        
        parent_data = {
            'id': parent_id,
            'scope': 'topic',
            'check': {'verdict': 'pending', 'evidence': []}
        }
        with open(parent_path, 'w') as f:
            yaml.dump(parent_data, f)
        
        # 创建子环（全部 pass）
        os.makedirs(f"{tmpdir}/task", exist_ok=True)
        
        for i in range(3):
            child_id = f'task-{i}'
            child_path = f"{tmpdir}/task/{child_id}.yaml"
            child_data = {
                'id': child_id,
                'scope': 'task',
                'parent_cycle_id': parent_id,
                'check': {'verdict': 'pass', 'evidence': [f'evidence_{i}']}
            }
            with open(child_path, 'w') as f:
                yaml.dump(child_data, f)
        
        # 测试聚合
        aggregator = CycleAggregator(tmpdir)
        result = aggregator.aggregate_children(parent_id)
        
        assert result.verdict == 'pass'
        assert result.child_count == 3
        assert result.pass_count == 3
        assert result.fail_count == 0
        assert len(result.evidence) == 3
        
        print("✅ aggregate_all_pass passed")


def test_aggregate_any_fail():
    """测试任一子环 fail → 父环 fail/partial"""
    print("Testing aggregate_any_fail...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建父环
        parent_id = 'topic-002'
        parent_path = f"{tmpdir}/topic/{parent_id}.yaml"
        os.makedirs(f"{tmpdir}/topic", exist_ok=True)
        
        parent_data = {'id': parent_id, 'scope': 'topic'}
        with open(parent_path, 'w') as f:
            yaml.dump(parent_data, f)
        
        # 创建子环（混合 pass/fail）
        os.makedirs(f"{tmpdir}/task", exist_ok=True)
        
        # 2 pass, 1 fail → partial
        child_data_list = [
            {'verdict': 'pass', 'evidence': ['e1']},
            {'verdict': 'pass', 'evidence': ['e2']},
            {'verdict': 'fail', 'evidence': ['e3']}
        ]
        
        for i, data in enumerate(child_data_list):
            child_id = f'task-{i}'
            child_path = f"{tmpdir}/task/{child_id}.yaml"
            child_data = {
                'id': child_id,
                'scope': 'task',
                'parent_cycle_id': parent_id,
                'check': data
            }
            with open(child_path, 'w') as f:
                yaml.dump(child_data, f)
        
        # 测试聚合
        aggregator = CycleAggregator(tmpdir)
        result = aggregator.aggregate_children(parent_id)
        
        assert result.verdict == 'partial'
        assert result.pass_count == 2
        assert result.fail_count == 1
        
        print("✅ aggregate_any_fail passed")


def test_bubble_up_status():
    """测试状态冒泡"""
    print("Testing bubble_up_status...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建父环
        parent_id = 'topic-003'
        parent_path = f"{tmpdir}/topic/{parent_id}.yaml"
        os.makedirs(f"{tmpdir}/topic", exist_ok=True)
        
        parent_data = {
            'id': parent_id,
            'scope': 'topic',
            'check': {'verdict': 'pending', 'evidence': ['parent_evidence']}
        }
        with open(parent_path, 'w') as f:
            yaml.dump(parent_data, f)
        
        # 创建子环
        child_id = 'task-003'
        child_path = f"{tmpdir}/task/{child_id}.yaml"
        os.makedirs(f"{tmpdir}/task", exist_ok=True)
        
        child_data = {
            'id': child_id,
            'scope': 'task',
            'parent_cycle_id': parent_id,
            'check': {'verdict': 'pass', 'evidence': ['child_evidence']}
        }
        with open(child_path, 'w') as f:
            yaml.dump(child_data, f)
        
        # 测试冒泡
        aggregator = CycleAggregator(tmpdir)
        aggregator.bubble_up_status(child_id)
        
        # 验证父环 evidence
        with open(parent_path, 'r') as f:
            updated_parent = yaml.safe_load(f)
        
        evidence = updated_parent['check']['evidence']
        assert len(evidence) == 2
        assert 'child_evidence' in evidence
        
        print("✅ bubble_up_status passed")


def test_propagate_adjustments():
    """测试调整传播"""
    print("Testing propagate_adjustments...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建父环
        parent_id = 'topic-004'
        parent_path = f"{tmpdir}/topic/{parent_id}.yaml"
        os.makedirs(f"{tmpdir}/topic", exist_ok=True)
        
        parent_data = {
            'id': parent_id,
            'scope': 'topic',
            'act': {'incoming_adjustments': []}
        }
        with open(parent_path, 'w') as f:
            yaml.dump(parent_data, f)
        
        # 创建子环（带 adjustments）
        child_id = 'task-004'
        child_path = f"{tmpdir}/task/{child_id}.yaml"
        os.makedirs(f"{tmpdir}/task", exist_ok=True)
        
        child_data = {
            'id': child_id,
            'scope': 'task',
            'parent_cycle_id': parent_id,
            'act': {
                'adjustments': [{'type': 'upgrade', 'priority': 'P0'}],
                'propagate_to': 'parent'
            }
        }
        with open(child_path, 'w') as f:
            yaml.dump(child_data, f)
        
        # 测试传播
        aggregator = CycleAggregator(tmpdir)
        aggregator.propagate_adjustments(child_id)
        
        # 验证父环 incoming_adjustments
        with open(parent_path, 'r') as f:
            updated_parent = yaml.safe_load(f)
        
        incoming = updated_parent['act']['incoming_adjustments']
        assert len(incoming) == 1
        assert incoming[0]['type'] == 'upgrade'
        
        print("✅ propagate_adjustments passed")


def main():
    """运行所有测试"""
    print("Running CycleAggregator tests...\n")
    
    try:
        test_aggregate_all_pass()
        test_aggregate_any_fail()
        test_bubble_up_status()
        test_propagate_adjustments()
        
        print("\n🎉 All tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)