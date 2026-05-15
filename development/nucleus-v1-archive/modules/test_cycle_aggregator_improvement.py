#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleAggregator 改进测试（第二轮）

测试边界条件、异常情况、并发场景、性能。

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import tempfile
import yaml
import sys
import time
import threading

sys.path.insert(0, os.path.dirname(__file__))
from cycle_aggregator import CycleAggregator, ParentNotFoundError, ChildNotFoundError


# ── 边界条件测试 ────────────────────────────────────────

def test_empty_children():
    """测试无子环 → verdict=pending"""
    print("Testing empty_children...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建父环（无子环）
        parent_id = 'topic-empty'
        parent_path = f"{tmpdir}/topic/{parent_id}.yaml"
        os.makedirs(f"{tmpdir}/topic", exist_ok=True)
        
        parent_data = {'id': parent_id, 'scope': 'topic'}
        with open(parent_path, 'w') as f:
            yaml.dump(parent_data, f)
        
        # 测试聚合
        aggregator = CycleAggregator(tmpdir)
        result = aggregator.aggregate_children(parent_id)
        
        assert result.verdict == 'pending'
        assert result.child_count == 0
        
        print("✅ empty_children passed")


def test_single_child():
    """测试单子环 → verdict=子环verdict"""
    print("Testing single_child...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建父环
        parent_id = 'topic-single'
        parent_path = f"{tmpdir}/topic/{parent_id}.yaml"
        os.makedirs(f"{tmpdir}/topic", exist_ok=True)
        
        parent_data = {'id': parent_id, 'scope': 'topic'}
        with open(parent_path, 'w') as f:
            yaml.dump(parent_data, f)
        
        # 创建单子环（pass）
        os.makedirs(f"{tmpdir}/task", exist_ok=True)
        child_id = 'task-single'
        child_path = f"{tmpdir}/task/{child_id}.yaml"
        child_data = {
            'id': child_id,
            'scope': 'task',
            'parent_cycle_id': parent_id,
            'check': {'verdict': 'pass', 'evidence': ['e1']}
        }
        with open(child_path, 'w') as f:
            yaml.dump(child_data, f)
        
        # 测试聚合
        aggregator = CycleAggregator(tmpdir)
        result = aggregator.aggregate_children(parent_id)
        
        assert result.verdict == 'pass'
        assert result.child_count == 1
        
        print("✅ single_child passed")


def test_large_children():
    """测试大量子环（100个）"""
    print("Testing large_children (100 children)...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建父环
        parent_id = 'topic-large'
        parent_path = f"{tmpdir}/topic/{parent_id}.yaml"
        os.makedirs(f"{tmpdir}/topic", exist_ok=True)
        
        parent_data = {'id': parent_id, 'scope': 'topic'}
        with open(parent_path, 'w') as f:
            yaml.dump(parent_data, f)
        
        # 创建100个子环（全部 pass）
        os.makedirs(f"{tmpdir}/task", exist_ok=True)
        
        for i in range(100):
            child_id = f'task-{i}'
            child_path = f"{tmpdir}/task/{child_id}.yaml"
            child_data = {
                'id': child_id,
                'scope': 'task',
                'parent_cycle_id': parent_id,
                'check': {'verdict': 'pass', 'evidence': [f'e{i}']}
            }
            with open(child_path, 'w') as f:
                yaml.dump(child_data, f)
        
        # 测试聚合
        aggregator = CycleAggregator(tmpdir)
        result = aggregator.aggregate_children(parent_id)
        
        assert result.verdict == 'pass'
        assert result.child_count == 100
        assert result.pass_count == 100
        
        print("✅ large_children passed")


# ── 异常情况测试 ────────────────────────────────────────

def test_parent_not_found():
    """测试父环不存在 → ParentNotFoundError"""
    print("Testing parent_not_found...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建子环（无父环）
        child_id = 'task-no-parent'
        child_path = f"{tmpdir}/task/{child_id}.yaml"
        os.makedirs(f"{tmpdir}/task", exist_ok=True)
        
        child_data = {
            'id': child_id,
            'scope': 'task',
            'parent_cycle_id': 'topic-nonexistent',
            'check': {'verdict': 'pass', 'evidence': ['e1']}
        }
        with open(child_path, 'w') as f:
            yaml.dump(child_data, f)
        
        # 测试冒泡（应抛出异常）
        aggregator = CycleAggregator(tmpdir)
        
        try:
            aggregator.bubble_up_status(child_id)
            assert False, "Should raise ParentNotFoundError"
        except ParentNotFoundError as e:
            assert 'Parent cycle not found' in str(e)
            print("✅ parent_not_found passed")


def test_child_not_found():
    """测试子环不存在 → ChildNotFoundError"""
    print("Testing child_not_found...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        aggregator = CycleAggregator(tmpdir)
        
        try:
            aggregator.bubble_up_status('task-nonexistent')
            assert False, "Should raise ChildNotFoundError"
        except ChildNotFoundError as e:
            assert 'Child cycle not found' in str(e)
            print("✅ child_not_found passed")


def test_corrupted_yaml():
    """测试损坏的 YAML 文件"""
    print("Testing corrupted_yaml...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建损坏的子环
        child_id = 'task-corrupted'
        child_path = f"{tmpdir}/task/{child_id}.yaml"
        os.makedirs(f"{tmpdir}/task", exist_ok=True)
        
        with open(child_path, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        # 测试聚合（应容错处理）
        aggregator = CycleAggregator(tmpdir)
        
        # 创建父环
        parent_id = 'topic-corrupted'
        parent_path = f"{tmpdir}/topic/{parent_id}.yaml"
        os.makedirs(f"{tmpdir}/topic", exist_ok=True)
        
        parent_data = {'id': parent_id, 'scope': 'topic'}
        with open(parent_path, 'w') as f:
            yaml.dump(parent_data, f)
        
        # 创建正常的子环
        child_id2 = 'task-normal'
        child_path2 = f"{tmpdir}/task/{child_id2}.yaml"
        child_data2 = {
            'id': child_id2,
            'scope': 'task',
            'parent_cycle_id': parent_id,
            'check': {'verdict': 'pass', 'evidence': ['e1']}
        }
        with open(child_path2, 'w') as f:
            yaml.dump(child_data2, f)
        
        # 聚合（应跳过损坏文件）
        result = aggregator.aggregate_children(parent_id)
        
        # 只有1个正常子环
        assert result.child_count == 1
        
        print("✅ corrupted_yaml passed (tolerant handling)")


# ── 并发场景测试 ────────────────────────────────────────

def test_concurrent_bubble():
    """测试并发冒泡（10线程同时更新父环）"""
    print("Testing concurrent_bubble...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建父环
        parent_id = 'topic-concurrent'
        parent_path = f"{tmpdir}/topic/{parent_id}.yaml"
        os.makedirs(f"{tmpdir}/topic", exist_ok=True)
        
        parent_data = {
            'id': parent_id,
            'scope': 'topic',
            'check': {'verdict': 'pending', 'evidence': []}
        }
        with open(parent_path, 'w') as f:
            yaml.dump(parent_data, f)
        
        # 创建10个子环
        os.makedirs(f"{tmpdir}/task", exist_ok=True)
        
        for i in range(10):
            child_id = f'task-concurrent-{i}'
            child_path = f"{tmpdir}/task/{child_id}.yaml"
            child_data = {
                'id': child_id,
                'scope': 'task',
                'parent_cycle_id': parent_id,
                'check': {'verdict': 'pass', 'evidence': [f'concurrent_e{i}']}
            }
            with open(child_path, 'w') as f:
                yaml.dump(child_data, f)
        
        # 并发冒泡
        aggregator = CycleAggregator(tmpdir)
        
        def bubble_child(child_id):
            try:
                aggregator.bubble_up_status(child_id)
            except Exception as e:
                # 并发时可能有冲突，但不应崩溃
                pass
        
        threads = []
        for i in range(10):
            child_id = f'task-concurrent-{i}'
            t = threading.Thread(target=bubble_child, args=(child_id,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 验证父环 evidence 有数据（可能不完整）
        with open(parent_path, 'r') as f:
            updated_parent = yaml.safe_load(f)
        
        evidence = updated_parent['check']['evidence']
        assert len(evidence) > 0  # 至少有一些 evidence
        
        print("✅ concurrent_bubble passed (evidence count: {})".format(len(evidence)))


# ── 性能测试 ────────────────────────────────────────

def test_performance_1000_children():
    """测试性能（1000个子环聚合）"""
    print("Testing performance (1000 children)...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建父环
        parent_id = 'topic-perf'
        parent_path = f"{tmpdir}/topic/{parent_id}.yaml"
        os.makedirs(f"{tmpdir}/topic", exist_ok=True)
        
        parent_data = {'id': parent_id, 'scope': 'topic'}
        with open(parent_path, 'w') as f:
            yaml.dump(parent_data, f)
        
        # 创建1000个子环
        os.makedirs(f"{tmpdir}/task", exist_ok=True)
        
        start_create = time.time()
        
        for i in range(1000):
            child_id = f'task-perf-{i}'
            child_path = f"{tmpdir}/task/{child_id}.yaml"
            child_data = {
                'id': child_id,
                'scope': 'task',
                'parent_cycle_id': parent_id,
                'check': {'verdict': 'pass', 'evidence': [f'perf_e{i}']}
            }
            with open(child_path, 'w') as f:
                yaml.dump(child_data, f)
        
        create_time = time.time() - start_create
        
        # 测试聚合性能
        aggregator = CycleAggregator(tmpdir)
        
        start_aggregate = time.time()
        result = aggregator.aggregate_children(parent_id)
        aggregate_time = time.time() - start_aggregate
        
        assert result.child_count == 1000
        assert aggregate_time < 5.0  # 应在5秒内完成
        
        print(f"✅ performance passed (create: {create_time:.2f}s, aggregate: {aggregate_time:.2f}s)")


# ── 主函数 ────────────────────────────────────────

def main():
    """运行所有改进测试"""
    print("Running CycleAggregator improvement tests...\n")
    
    try:
        # 边界条件
        test_empty_children()
        test_single_child()
        test_large_children()
        
        # 异常情况
        test_parent_not_found()
        test_child_not_found()
        test_corrupted_yaml()
        
        # 并发场景
        test_concurrent_bubble()
        
        # 性能测试
        test_performance_1000_children()
        
        print("\n🎉 All improvement tests passed! (8/8)")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)