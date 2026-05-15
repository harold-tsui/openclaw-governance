#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Module 单元测试

测试验收阶段的核心功能

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

from modules.check import (
    check_cycle,
    execute_check_by_level,
    collect_evidence,
    _get_review_level_from_task_card
)


class TestCheckModule(unittest.TestCase):
    """测试 Check 模块核心功能"""
    
    def setUp(self):
        """创建临时测试目录和数据"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 创建必要的目录
        os.makedirs("executions", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("cycles/task", exist_ok=True)
        
        # 创建测试日志
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        with open(f"executions/{today}.jsonl", 'w') as f:
            json.dump({
                'cycle_id': 'test-001',
                'action': 'create_cycle',
                'result': 'success'
            }, f)
            f.write('\n')
        
        with open(f"logs/{today}.jsonl", 'w') as f:
            json.dump({
                'cycle_id': 'test-001',
                'level': 'INFO',
                'message': 'test log'
            }, f)
            f.write('\n')
        
        # 创建测试 CycleUnit
        cycle_data = {
            'id': 'task-test-001',
            'scope': 'task',
            'phase': 'check',
            'task_card_id': 'T5.6_TASK-CARD',
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'version': 1
            }
        }
        with open('cycles/task/task-test-001.yaml', 'w') as f:
            yaml.dump(cycle_data, f)
    
    def tearDown(self):
        """清理临时目录"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_review_level_from_task_card(self):
        """测试从 task-card 获取 review_level"""
        level = _get_review_level_from_task_card('test-task-card')
        self.assertEqual(level, 'L2')  # 简化实现返回 L2
    
    def test_collect_evidence(self):
        """测试证据收集"""
        evidence = collect_evidence('test-001')
        
        self.assertIsInstance(evidence, list)
        self.assertGreater(len(evidence), 0)
        
        # 验证证据格式
        for item in evidence:
            self.assertIn('type', item)
            self.assertIn('timestamp', item)
    
    def test_execute_check_by_level_L0(self):
        """测试 L0 级别验收"""
        result = execute_check_by_level('test-cycle', 'L0')
        
        self.assertEqual(result['verdict'], 'skip')
        self.assertGreater(len(result['evidence']), 0)
        self.assertEqual(result['evidence'][0]['type'], 'auto_approval')
    
    def test_execute_check_by_level_L1(self):
        """测试 L1 级别验收"""
        result = execute_check_by_level('test-cycle', 'L1')
        
        self.assertIn(result['verdict'], ['pass', 'fail'])
        self.assertGreater(len(result['evidence']), 0)
    
    def test_execute_check_by_level_L2(self):
        """测试 L2 级别验收"""
        result = execute_check_by_level('test-cycle', 'L2')
        
        self.assertIn(result['verdict'], ['pass', 'partial'])
        self.assertGreater(len(result['evidence']), 0)
    
    def test_execute_check_by_level_L3(self):
        """测试 L3 级别验收"""
        result = execute_check_by_level('test-cycle', 'L3')
        
        self.assertEqual(result['verdict'], 'pending')
        self.assertGreater(len(result['evidence']), 0)
    
    def test_execute_check_by_level_invalid(self):
        """测试无效级别验收"""
        result = execute_check_by_level('test-cycle', 'invalid')
        
        self.assertEqual(result['verdict'], 'skip')  # 默认行为
    
    def test_check_cycle_nonexistent(self):
        """测试检查不存在的 CycleUnit"""
        result = check_cycle('nonexistent-cycle')
        
        self.assertEqual(result['verdict'], 'fail')
        self.assertGreater(len(result['errors']), 0)
    
    def test_check_cycle_existing(self):
        """测试检查存在的 CycleUnit"""
        result = check_cycle('task-test-001')
        
        # 应该成功完成（简化实现返回 L2）
        self.assertIn(result['verdict'], ['pass', 'partial'])
        self.assertGreater(len(result['evidence']), 0)
        self.assertEqual(len(result['errors']), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)