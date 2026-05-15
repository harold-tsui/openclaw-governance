#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler State 单元测试

测试持久化调度计数器的核心功能

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import unittest
import tempfile
import yaml
import threading
import time
from datetime import datetime, timezone

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.scheduler_state import (
    load_scheduler_state,
    save_scheduler_state,
    increment_counter,
    check_threshold,
    reset_counter,
    reset_all_counters,
    create_default_state,
    validate_state,
    atomic_write_yaml,
    get_all_triggers,
    get_next_trigger_count,
    SchedulerStateCorruptedError,
    SchedulerStateError
)


class TestSchedulerState(unittest.TestCase):
    """测试调度状态核心功能"""
    
    def setUp(self):
        """创建临时测试目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_path = os.path.join(self.temp_dir, "scheduler_state.yaml")
    
    def tearDown(self):
        """清理临时目录"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_default_state(self):
        """测试默认状态创建"""
        state = create_default_state()
        
        self.assertIn('last_updated', state)
        self.assertIn('counters', state)
        self.assertIn('thresholds', state)
        
        # 验证默认计数器
        self.assertEqual(state['counters']['task'], 0)
        self.assertEqual(state['counters']['topic'], 0)
        self.assertEqual(state['counters']['project'], 0)
        self.assertEqual(state['counters']['system'], 0)
    
    def test_save_and_load(self):
        """测试保存和加载"""
        state = create_default_state()
        save_scheduler_state(state, self.test_path)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(self.test_path))
        
        # 加载并验证
        loaded = load_scheduler_state(self.test_path)
        self.assertEqual(loaded['counters'], state['counters'])
        self.assertEqual(loaded['thresholds'], state['thresholds'])
    
    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        state = load_scheduler_state("/nonexistent/path.yaml")
        
        # 应该返回默认状态
        self.assertIn('counters', state)
        self.assertEqual(state['counters']['task'], 0)
    
    def test_increment_counter_task(self):
        """测试 task 计数器递增"""
        # task 阈值为 1，每次都触发
        result = increment_counter('task', self.test_path)
        
        self.assertEqual(result['counter'], 1)
        self.assertTrue(result['triggered'])
        self.assertEqual(result['state']['counters']['task'], 0)  # 触发后重置
    
    def test_increment_counter_topic(self):
        """测试 topic 计数器递增"""
        # topic 阈值为 4
        for i in range(3):
            result = increment_counter('topic', self.test_path)
            self.assertFalse(result['triggered'])
        
        # 第 4 次触发
        result = increment_counter('topic', self.test_path)
        self.assertTrue(result['triggered'])
        self.assertEqual(result['state']['counters']['topic'], 0)
    
    def test_increment_counter_project(self):
        """测试 project 计数器递增"""
        # project 阈值为 48
        for i in range(47):
            result = increment_counter('project', self.test_path)
            self.assertFalse(result['triggered'])
        
        # 第 48 次触发
        result = increment_counter('project', self.test_path)
        self.assertTrue(result['triggered'])
    
    def test_increment_counter_system(self):
        """测试 system 计数器递增"""
        # system 阈值为 336
        for i in range(335):
            increment_counter('system', self.test_path)
        
        # 第 336 次触发
        result = increment_counter('system', self.test_path)
        self.assertTrue(result['triggered'])
    
    def test_increment_invalid_scope(self):
        """测试无效 scope"""
        with self.assertRaises(ValueError):
            increment_counter('invalid', self.test_path)
    
    def test_check_threshold(self):
        """测试阈值检查"""
        state = create_default_state()
        
        # 未达到阈值
        self.assertFalse(check_threshold('task', 0, state))
        self.assertFalse(check_threshold('topic', 3, state))
        
        # 达到阈值
        self.assertTrue(check_threshold('task', 1, state))
        self.assertTrue(check_threshold('topic', 4, state))
    
    def test_reset_counter(self):
        """测试计数器重置"""
        # 递增几次
        for _ in range(5):
            increment_counter('topic', self.test_path)
        
        # 重置
        reset_counter('topic', self.test_path)
        
        # 验证
        state = load_scheduler_state(self.test_path)
        self.assertEqual(state['counters']['topic'], 0)
    
    def test_reset_all_counters(self):
        """测试重置所有计数器"""
        # 递增所有
        for scope in ['task', 'topic', 'project', 'system']:
            increment_counter(scope, self.test_path)
        
        # 重置所有
        reset_all_counters(self.test_path)
        
        # 验证
        state = load_scheduler_state(self.test_path)
        for scope in ['task', 'topic', 'project', 'system']:
            self.assertEqual(state['counters'][scope], 0)
    
    def test_validate_state_valid(self):
        """测试有效状态验证"""
        state = create_default_state()
        self.assertTrue(validate_state(state))
    
    def test_validate_state_missing_counters(self):
        """测试缺少计数器的状态"""
        state = {'thresholds': {}}
        self.assertFalse(validate_state(state))
    
    def test_validate_state_invalid_counter_type(self):
        """测试计数器类型无效"""
        state = {
            'counters': {'task': 'not_an_int'},
            'thresholds': {}
        }
        self.assertFalse(validate_state(state))
    
    def test_atomic_write(self):
        """测试原子写入"""
        data = {'test': 'data', 'value': 123}
        atomic_write_yaml(self.test_path, data)
        
        # 验证文件存在且内容正确
        self.assertTrue(os.path.exists(self.test_path))
        
        with open(self.test_path, 'r') as f:
            loaded = yaml.safe_load(f)
        
        self.assertEqual(loaded['test'], 'data')
        self.assertEqual(loaded['value'], 123)
        
        # 验证临时文件已清理
        self.assertFalse(os.path.exists(f"{self.test_path}.tmp"))
    
    def test_persistence_across_reloads(self):
        """测试重新加载后的持久性"""
        # 递增计数器
        for _ in range(10):
            increment_counter('project', self.test_path)
        
        # 重新加载
        state = load_scheduler_state(self.test_path)
        self.assertEqual(state['counters']['project'], 10)
    
    def test_get_all_triggers(self):
        """测试获取所有触发状态"""
        # 创建默认状态（所有 counter=0）
        state = create_default_state()
        save_scheduler_state(state, self.test_path)
        
        # 检查默认状态：task counter=0，但阈值是 1，未达到
        triggers = get_all_triggers(self.test_path)
        
        self.assertFalse(triggers['task'])   # 0 < 1
        self.assertFalse(triggers['topic'])  # 0 < 4
        self.assertFalse(triggers['project'])
        self.assertFalse(triggers['system'])
    
    def test_get_next_trigger_count(self):
        """测试获取剩余次数"""
        # 递增 topic 2 次
        increment_counter('topic', self.test_path)
        increment_counter('topic', self.test_path)
        
        remaining = get_next_trigger_count('topic', self.test_path)
        self.assertEqual(remaining, 2)  # 4 - 2 = 2
    
    def test_corrupted_file(self):
        """测试损坏文件处理"""
        # 写入无效 YAML
        with open(self.test_path, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        with self.assertRaises(SchedulerStateCorruptedError):
            load_scheduler_state(self.test_path)


class TestConcurrency(unittest.TestCase):
    """测试并发安全"""
    
    def setUp(self):
        """创建临时测试目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_path = os.path.join(self.temp_dir, "scheduler_state.yaml")
    
    def tearDown(self):
        """清理临时目录"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_concurrent_writes(self):
        """测试并发写入"""
        num_threads = 10
        writes_per_thread = 10
        
        def writer_thread(thread_id):
            for i in range(writes_per_thread):
                increment_counter('task', self.test_path)
        
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=writer_thread, args=(i,))
            threads.append(t)
        
        # 启动所有线程
        for t in threads:
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 验证文件未损坏
        state = load_scheduler_state(self.test_path)
        self.assertIn('counters', state)
        
        print(f"\n   并发测试完成：{num_threads} 线程 × {writes_per_thread} 次写入")


if __name__ == "__main__":
    unittest.main(verbosity=2)