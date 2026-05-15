#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wait Queue 单元测试

测试等待队列管理的核心功能

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import unittest
import tempfile
import yaml
from datetime import datetime, timezone, timedelta

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.wait_queue import (
    load_wait_queue,
    save_wait_queue,
    add_to_wait_queue,
    pop_from_wait_queue,
    get_wait_queue_size,
    process_wait_queue,
    clean_expired_requests,
    get_queue_status,
    get_all_queue_status
)


class TestWaitQueue(unittest.TestCase):
    """测试等待队列核心功能"""
    
    def setUp(self):
        """创建临时测试目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 创建必要的目录
        os.makedirs("cycles", exist_ok=True)
        os.makedirs("cycles/task", exist_ok=True)
    
    def tearDown(self):
        """清理临时目录"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_empty_queue(self):
        """测试加载空队列"""
        queue_data = load_wait_queue('task')
        
        self.assertEqual(queue_data['scope'], 'task')
        self.assertEqual(queue_data['pending_requests'], [])
    
    def test_add_to_wait_queue(self):
        """测试添加请求"""
        success = add_to_wait_queue('task', 'test_reason')
        self.assertTrue(success)
        
        size = get_wait_queue_size('task')
        self.assertEqual(size, 1)
    
    def test_add_multiple_requests(self):
        """测试添加多个请求"""
        for i in range(5):
            add_to_wait_queue('task')
        
        size = get_wait_queue_size('task')
        self.assertEqual(size, 5)
    
    def test_pop_from_wait_queue(self):
        """测试取出请求"""
        add_to_wait_queue('task', 'reason1')
        add_to_wait_queue('task', 'reason2')
        
        # 取出第一个
        request = pop_from_wait_queue('task')
        self.assertIsNotNone(request)
        self.assertEqual(request['reason'], 'reason1')
        
        # 验证队列大小
        size = get_wait_queue_size('task')
        self.assertEqual(size, 1)
        
        # 取出第二个
        request = pop_from_wait_queue('task')
        self.assertEqual(request['reason'], 'reason2')
        
        # 队列应该为空
        size = get_wait_queue_size('task')
        self.assertEqual(size, 0)
    
    def test_pop_from_empty_queue(self):
        """测试从空队列取出"""
        request = pop_from_wait_queue('task')
        self.assertIsNone(request)
    
    def test_fifo_order(self):
        """测试 FIFO 顺序"""
        # 添加多个请求
        for i in range(3):
            add_to_wait_queue('task', f'request_{i}')
        
        # 取出并验证顺序
        for i in range(3):
            request = pop_from_wait_queue('task')
            self.assertEqual(request['reason'], f'request_{i}')
    
    def test_get_queue_status(self):
        """测试获取队列状态"""
        add_to_wait_queue('task')
        add_to_wait_queue('task')
        
        status = get_queue_status('task')
        
        self.assertEqual(status['scope'], 'task')
        self.assertEqual(status['queue_size'], 2)
        self.assertIsNotNone(status['oldest_request'])
        self.assertIsNotNone(status['newest_request'])
    
    def test_get_all_queue_status(self):
        """测试获取所有队列状态"""
        add_to_wait_queue('task')
        add_to_wait_queue('topic')
        
        status = get_all_queue_status()
        
        self.assertIn('task', status)
        self.assertIn('topic', status)
        self.assertEqual(status['task']['queue_size'], 1)
        self.assertEqual(status['topic']['queue_size'], 1)
    
    def test_clean_expired_requests(self):
        """测试清理过期请求"""
        # 添加当前请求
        add_to_wait_queue('task', 'current')
        
        # 添加过期请求（手动修改时间戳）
        queue_data = load_wait_queue('task')
        expired_time = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
        queue_data['pending_requests'].insert(0, {
            'timestamp': expired_time,
            'scope': 'task',
            'reason': 'expired',
            'priority': 0
        })
        save_wait_queue('task', queue_data)
        
        # 清理
        cleaned = clean_expired_requests('task', max_age_hours=24)
        self.assertEqual(cleaned, 1)
        
        # 验证只剩当前请求
        size = get_wait_queue_size('task')
        self.assertEqual(size, 1)
    
    def test_clean_no_expired(self):
        """测试没有过期请求"""
        add_to_wait_queue('task')
        
        cleaned = clean_expired_requests('task', max_age_hours=24)
        self.assertEqual(cleaned, 0)
        
        size = get_wait_queue_size('task')
        self.assertEqual(size, 1)
    
    def test_invalid_scope(self):
        """测试无效 scope"""
        with self.assertRaises(ValueError):
            add_to_wait_queue('invalid')
        
        with self.assertRaises(ValueError):
            pop_from_wait_queue('invalid')
        
        with self.assertRaises(ValueError):
            get_wait_queue_size('invalid')


class TestIntegration(unittest.TestCase):
    """测试集成场景"""
    
    def setUp(self):
        """创建临时测试目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 创建必要的目录和初始状态
        os.makedirs("cycles", exist_ok=True)
        os.makedirs("cycles/task", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # 创建初始 scheduler_state.yaml
        initial_state = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'counters': {'task': 0, 'topic': 0, 'project': 0, 'system': 0},
            'thresholds': {'task': 1, 'topic': 4, 'project': 48, 'system': 336}
        }
        with open('cycles/scheduler_state.yaml', 'w') as f:
            yaml.dump(initial_state, f)
    
    def tearDown(self):
        """清理临时目录"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_process_wait_queue(self):
        """测试处理等待队列"""
        # 添加请求
        add_to_wait_queue('task', 'test_process')
        
        # 处理队列
        cycle_id = process_wait_queue('task')
        
        self.assertIsNotNone(cycle_id)
        self.assertTrue(cycle_id.startswith('task-'))
        
        # 验证队列已清空
        size = get_wait_queue_size('task')
        self.assertEqual(size, 0)
        
        # 验证 CycleUnit 文件存在
        file_path = f"cycles/task/{cycle_id}.yaml"
        self.assertTrue(os.path.exists(file_path))


if __name__ == "__main__":
    unittest.main(verbosity=2)