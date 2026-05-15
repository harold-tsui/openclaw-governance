#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler 单元测试

测试多粒度调度器的核心功能

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import unittest
import tempfile
import yaml
import json
from datetime import datetime, timezone

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.scheduler import (
    on_heartbeat,
    should_trigger,
    get_active_cycle_count,
    check_concurrency_limit,
    create_cycle_for_scope,
    get_wait_queue_size,
    add_to_wait_queue,
    get_scheduler_status
)


class TestScheduler(unittest.TestCase):
    """测试调度器核心功能"""
    
    def setUp(self):
        """创建临时测试目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 创建必要的目录
        os.makedirs("cycles/task", exist_ok=True)
        os.makedirs("cycles/topic", exist_ok=True)
        os.makedirs("cycles/project", exist_ok=True)
        os.makedirs("cycles/system", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def tearDown(self):
        """清理临时目录"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_should_trigger_default_state(self):
        """测试默认状态下触发条件"""
        # 默认状态所有计数器为 0
        # task 阈值 1，所以应该触发
        self.assertTrue(should_trigger('task'))
        
        # topic 阈值 4，计数器 0，不应该触发
        self.assertFalse(should_trigger('topic'))
        self.assertFalse(should_trigger('project'))
        self.assertFalse(should_trigger('system'))
    
    def test_get_active_cycle_count_empty(self):
        """测试空目录的活跃计数"""
        count = get_active_cycle_count('task')
        self.assertEqual(count, 0)
    
    def test_get_active_cycle_count_with_files(self):
        """测试有文件的活跃计数"""
        # 创建一个活跃的 CycleUnit
        cycle_data = {
            'id': 'task-test-001',
            'scope': 'task',
            'phase': 'plan'
        }
        with open('cycles/task/task-test-001.yaml', 'w') as f:
            yaml.dump(cycle_data, f)
        
        count = get_active_cycle_count('task')
        self.assertEqual(count, 1)
    
    def test_get_active_cycle_count_completed(self):
        """测试已完成的 CycleUnit 不计入活跃"""
        # 创建一个已完成的 CycleUnit
        cycle_data = {
            'id': 'task-test-002',
            'scope': 'task',
            'phase': 'completed'
        }
        with open('cycles/task/task-test-002.yaml', 'w') as f:
            yaml.dump(cycle_data, f)
        
        count = get_active_cycle_count('task')
        self.assertEqual(count, 0)
    
    def test_check_concurrency_limit(self):
        """测试并发上限检查"""
        # 空目录，应该通过
        self.assertTrue(check_concurrency_limit('task'))
        self.assertTrue(check_concurrency_limit('topic'))
        self.assertTrue(check_concurrency_limit('project'))
        self.assertTrue(check_concurrency_limit('system'))
    
    def test_create_cycle_for_scope(self):
        """测试创建 CycleUnit"""
        cycle_id = create_cycle_for_scope('task')
        
        self.assertIsNotNone(cycle_id)
        self.assertTrue(cycle_id.startswith('task-'))
        
        # 验证文件存在
        file_path = f"cycles/task/{cycle_id}.yaml"
        self.assertTrue(os.path.exists(file_path))
        
        # 验证文件内容
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self.assertEqual(data['id'], cycle_id)
        self.assertEqual(data['scope'], 'task')
        self.assertEqual(data['phase'], 'plan')
    
    def test_create_cycle_for_scope_concurrency_limit(self):
        """测试并发上限触发拒绝"""
        # 创建足够多的活跃 CycleUnit 达到上限
        for i in range(10):  # task 上限是 10
            cycle_data = {
                'id': f'task-test-{i:03d}',
                'scope': 'task',
                'phase': 'plan'
            }
            with open(f'cycles/task/task-test-{i:03d}.yaml', 'w') as f:
                yaml.dump(cycle_data, f)
        
        # 首先验证并发检查返回 False
        self.assertFalse(check_concurrency_limit('task'))
        
        # 填满等待队列（上限是 20）
        for i in range(20):
            add_to_wait_queue('task')
        
        # 现在尝试创建，应该被拒绝
        cycle_id = create_cycle_for_scope('task')
        self.assertIsNone(cycle_id)
        
        # 验证拒绝日志
        log_files = os.listdir('logs')
        rejection_logged = any('rejections' in f for f in log_files)
        self.assertTrue(rejection_logged)
    
    def test_get_wait_queue_size_empty(self):
        """测试空等待队列大小"""
        size = get_wait_queue_size('task')
        self.assertEqual(size, 0)
    
    def test_add_to_wait_queue(self):
        """测试添加到等待队列"""
        success = add_to_wait_queue('task')
        self.assertTrue(success)
        
        size = get_wait_queue_size('task')
        self.assertEqual(size, 1)
    
    def test_get_scheduler_status(self):
        """测试获取调度器状态"""
        status = get_scheduler_status()
        
        self.assertIn('counters', status)
        self.assertIn('active_counts', status)
        self.assertIn('wait_queue_sizes', status)
        
        # 默认状态应该有计数器数据
        self.assertIsInstance(status['counters'], dict)
        self.assertIsInstance(status['active_counts'], dict)
        self.assertIsInstance(status['wait_queue_sizes'], dict)
    
    def test_invalid_scope(self):
        """测试无效 scope"""
        with self.assertRaises(ValueError):
            should_trigger('invalid')
        
        with self.assertRaises(ValueError):
            get_active_cycle_count('invalid')
        
        with self.assertRaises(ValueError):
            check_concurrency_limit('invalid')
        
        with self.assertRaises(ValueError):
            create_cycle_for_scope('invalid')


class TestIntegration(unittest.TestCase):
    """测试集成场景"""
    
    def setUp(self):
        """创建临时测试目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 创建必要的目录和初始状态文件
        os.makedirs("cycles/task", exist_ok=True)
        os.makedirs("cycles/topic", exist_ok=True)
        os.makedirs("cycles/project", exist_ok=True)
        os.makedirs("cycles/system", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # 创建初始 scheduler_state.yaml
        initial_state = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'counters': {
                'task': 0,
                'topic': 3,  # 下一次触发
                'project': 47,  # 下一次触发
                'system': 335  # 下一次触发
            },
            'thresholds': {
                'task': 1,
                'topic': 4,
                'project': 48,
                'system': 336
            }
        }
        with open('cycles/scheduler_state.yaml', 'w') as f:
            yaml.dump(initial_state, f)
    
    def tearDown(self):
        """清理临时目录"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_on_heartbeat_integration(self):
        """测试完整的心跳集成"""
        result = on_heartbeat()
        
        # 应该触发所有 scope（因为计数器设置为阈值-1）
        expected_triggers = ['task', 'topic', 'project', 'system']
        self.assertEqual(set(result['triggered_scopes']), set(expected_triggers))
        
        # 应该创建对应的 CycleUnit
        self.assertEqual(len(result['created_cycles']), 4)
        
        # 检查创建的文件
        for scope in expected_triggers:
            created = [cid for cid in result['created_cycles'] if cid.startswith(scope)]
            self.assertEqual(len(created), 1)
            
            file_path = f"cycles/{scope}/{created[0]}.yaml"
            self.assertTrue(os.path.exists(file_path))
    
    def test_on_heartbeat_no_errors(self):
        """测试心跳无错误"""
        result = on_heartbeat()
        self.assertEqual(len(result['errors']), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)