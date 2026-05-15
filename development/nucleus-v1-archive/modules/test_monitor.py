#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor Module 单元测试

测试系统状态感知的核心功能

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import unittest
import tempfile
import json
import yaml
from datetime import datetime, timezone

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.monitor import (
    sense_system_state,
    detect_anomalies,
    aggregate_child_results,
    get_log_entries,
    get_execution_entries,
    SystemSnapshot,
    Anomaly,
    AggregatedResult
)


class TestMonitor(unittest.TestCase):
    """测试 Monitor 模块核心功能"""
    
    def setUp(self):
        """创建临时测试目录和数据"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 创建必要的目录
        os.makedirs("logs", exist_ok=True)
        os.makedirs("executions", exist_ok=True)
        os.makedirs("cycles/task", exist_ok=True)
        os.makedirs("cycles/topic", exist_ok=True)
        os.makedirs("cycles/project", exist_ok=True)
        os.makedirs("cycles/system", exist_ok=True)
        
        # 创建测试日志
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        with open(f"logs/{today}.jsonl", 'w') as f:
            json.dump({'level': 'INFO', 'message': 'test log'}, f)
            f.write('\n')
            json.dump({'level': 'ERROR', 'message': 'test error'}, f)
            f.write('\n')
        
        with open(f"executions/{today}.jsonl", 'w') as f:
            json.dump({'action': 'create_cycle', 'scope': 'task'}, f)
            f.write('\n')
        
        # 创建测试 CycleUnit
        cycle_data = {
            'id': 'task-test-001',
            'scope': 'task',
            'phase': 'plan'
        }
        with open('cycles/task/task-test-001.yaml', 'w') as f:
            yaml.dump(cycle_data, f)
    
    def tearDown(self):
        """清理临时目录"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_sense_system_state(self):
        """测试系统状态感知"""
        snapshot = sense_system_state()
        
        self.assertIsInstance(snapshot, SystemSnapshot)
        self.assertIsInstance(snapshot.timestamp, datetime)
        self.assertIsInstance(snapshot.active_cycles, dict)
        self.assertIsInstance(snapshot.log_entries, list)
        self.assertIsInstance(snapshot.execution_entries, list)
        self.assertIsInstance(snapshot.wait_queue_sizes, dict)
    
    def test_get_log_entries_today(self):
        """测试获取今日日志条目"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        entries = get_log_entries(today)
        
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]['level'], 'INFO')
        self.assertEqual(entries[1]['level'], 'ERROR')
    
    def test_get_log_entries_nonexistent(self):
        """测试获取不存在日期的日志"""
        entries = get_log_entries('2026-01-01')
        self.assertEqual(len(entries), 0)
    
    def test_get_execution_entries_today(self):
        """测试获取今日执行条目"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        entries = get_execution_entries(today)
        
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['action'], 'create_cycle')
    
    def test_detect_anomalies_normal(self):
        """测试正常状态下的异常检测"""
        snapshot = sense_system_state()
        anomalies = detect_anomalies(snapshot)
        
        # 正常情况下应该没有高严重性异常
        high_severity = [a for a in anomalies if a.severity == 'high']
        self.assertEqual(len(high_severity), 0)
    
    def test_detect_anomalies_concurrency_high(self):
        """测试高并发异常检测"""
        # 创建大量活跃 CycleUnit 来触发并发异常
        for i in range(15):  # 超过 task 上限 10
            cycle_data = {
                'id': f'task-test-{i:03d}',
                'scope': 'task',
                'phase': 'plan'
            }
            with open(f'cycles/task/task-test-{i:03d}.yaml', 'w') as f:
                yaml.dump(cycle_data, f)
        
        snapshot = sense_system_state()
        anomalies = detect_anomalies(snapshot)
        
        # 应该检测到高并发异常
        concurrency_anomalies = [a for a in anomalies if a.type == 'concurrency']
        self.assertGreater(len(concurrency_anomalies), 0)
    
    def test_detect_anomalies_error_logs(self):
        """测试错误日志异常检测"""
        # 添加大量错误日志
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        with open(f"logs/{today}.jsonl", 'a') as f:
            for i in range(15):  # 超过 10 个错误
                json.dump({'level': 'ERROR', 'message': f'test error {i}'}, f)
                f.write('\n')
        
        snapshot = sense_system_state()
        anomalies = detect_anomalies(snapshot)
        
        # 应该检测到高错误率异常
        error_anomalies = [a for a in anomalies if a.type == 'error']
        self.assertGreater(len(error_anomalies), 0)
    
    def test_aggregate_child_results_empty(self):
        """测试空子环聚合"""
        result = aggregate_child_results('parent-test-001')
        
        self.assertIsInstance(result, AggregatedResult)
        self.assertEqual(result.parent_id, 'parent-test-001')
        self.assertEqual(result.child_count, 1)  # 我们创建了一个测试 CycleUnit
        self.assertEqual(result.success_count, 0)
        self.assertEqual(result.failure_count, 0)
    
    def test_aggregate_child_results_with_verdict(self):
        """测试带 verdict 的子环聚合"""
        # 创建带 verdict 的子环
        child_data = {
            'id': 'task-child-001',
            'scope': 'task',
            'phase': 'check',
            'check': {
                'verdict': 'pass',
                'evidence': [{'type': 'test', 'result': 'success'}]
            }
        }
        with open('cycles/task/task-child-001.yaml', 'w') as f:
            yaml.dump(child_data, f)
        
        result = aggregate_child_results('parent-test-002')
        
        self.assertEqual(result.child_count, 2)  # 原来的 + 新的
        self.assertEqual(result.success_count, 1)
        self.assertEqual(result.failure_count, 0)
        self.assertEqual(len(result.aggregated_evidence), 1)
    
    def test_dataclass_types(self):
        """测试数据类类型"""
        snapshot = SystemSnapshot(
            timestamp=datetime.now(timezone.utc),
            active_cycles={'task': 1},
            log_entries=[],
            execution_entries=[],
            wait_queue_sizes={}
        )
        
        anomaly = Anomaly(
            type='test',
            severity='low',
            message='test message',
            timestamp=datetime.now(timezone.utc)
        )
        
        aggregated = AggregatedResult(
            parent_id='test',
            child_count=1,
            success_count=1,
            failure_count=0,
            aggregated_evidence=[]
        )
        
        self.assertIsInstance(snapshot, SystemSnapshot)
        self.assertIsInstance(anomaly, Anomaly)
        self.assertIsInstance(aggregated, AggregatedResult)


if __name__ == "__main__":
    unittest.main(verbosity=2)