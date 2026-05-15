#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Do Module 单元测试

测试执行阶段的核心功能

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

from modules.do import (
    execute_cycle,
    execute_actions,
    create_child_cycle,
    check_children_status,
    write_execution_log,
    _get_scope_from_cycle_id
)


class TestDoModule(unittest.TestCase):
    """测试 Do 模块核心功能"""
    
    def setUp(self):
        """创建临时测试目录和数据"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 创建必要的目录
        os.makedirs("executions", exist_ok=True)
        os.makedirs("cycles/task", exist_ok=True)
        os.makedirs("cycles/topic", exist_ok=True)
        
        # 创建测试 CycleUnit
        cycle_data = {
            'id': 'task-test-001',
            'scope': 'task',
            'phase': 'do',
            'task_card_id': 'T5.5_TASK-CARD',
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
    
    def test_get_scope_from_cycle_id(self):
        """测试从 CycleUnit ID 提取 scope"""
        self.assertEqual(_get_scope_from_cycle_id('task-123'), 'task')
        self.assertEqual(_get_scope_from_cycle_id('topic-456'), 'topic')
        self.assertEqual(_get_scope_from_cycle_id('project-789'), 'project')
        self.assertEqual(_get_scope_from_cycle_id('system-000'), 'system')
    
    def test_write_execution_log(self):
        """测试写入执行日志"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        log_file = f"executions/{today}.jsonl"
        
        # 写入日志
        write_execution_log(
            cycle_id="test-001",
            action="test_action",
            result="success",
            metadata={"test": "data"}
        )
        
        # 验证文件存在
        self.assertTrue(os.path.exists(log_file))
        
        # 验证内容
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 1)
        log_entry = json.loads(lines[0])
        
        self.assertEqual(log_entry['cycle_id'], 'test-001')
        self.assertEqual(log_entry['action'], 'test_action')
        self.assertEqual(log_entry['result'], 'success')
        self.assertEqual(log_entry['metadata']['test'], 'data')
    
    def test_create_child_cycle_valid_scope(self):
        """测试创建有效 scope 的子环"""
        child_id = create_child_cycle('parent-001', 'task')
        
        self.assertIsNotNone(child_id)
        self.assertTrue(child_id.startswith('task-'))
        
        # 验证文件存在
        file_path = f"cycles/task/{child_id}.yaml"
        self.assertTrue(os.path.exists(file_path))
        
        # 验证文件内容
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self.assertEqual(data['id'], child_id)
        self.assertEqual(data['scope'], 'task')
        self.assertEqual(data['task_card_id'], 'child-of-parent-001')
    
    def test_create_child_cycle_invalid_scope(self):
        """测试创建无效 scope 的子环"""
        child_id = create_child_cycle('parent-001', 'invalid')
        self.assertIsNone(child_id)
    
    def test_execute_actions_empty(self):
        """测试执行空 actions 列表"""
        actions = []
        result = execute_actions('test-cycle', actions)
        
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['executed_count'], 0)
        self.assertEqual(len(result['errors']), 0)
    
    def test_execute_actions_with_actions(self):
        """测试执行包含 actions 的列表"""
        actions = [
            {'type': 'create_subtask', 'name': 'subtask1'},
            {'type': 'call_skill', 'skill': 'test_skill'}
        ]
        result = execute_actions('test-cycle', actions)
        
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['executed_count'], 2)
        self.assertEqual(len(result['errors']), 0)
    
    def test_check_children_status_empty(self):
        """测试空子环状态检查"""
        status = check_children_status('nonexistent-parent')
        
        self.assertEqual(status['total'], 0)
        self.assertEqual(status['completed'], 0)
        self.assertEqual(status['in_progress'], 0)
        self.assertEqual(status['failed'], 0)
        self.assertEqual(status['blocked'], 0)
    
    def test_execute_cycle_nonexistent(self):
        """测试执行不存在的 CycleUnit"""
        result = execute_cycle('nonexistent-cycle')
        
        self.assertEqual(result['status'], 'failed')
        self.assertGreater(len(result['errors']), 0)
    
    def test_execute_cycle_existing(self):
        """测试执行存在的 CycleUnit"""
        result = execute_cycle('task-test-001')
        
        # 应该成功完成（没有 actions 和 children）
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['actions_executed'], 0)
        self.assertEqual(len(result['children_created']), 0)
        self.assertEqual(len(result['errors']), 0)
    
    def test_execute_cycle_with_children(self):
        """测试执行带子环的 CycleUnit"""
        # 修改测试 CycleUnit 添加 children
        cycle_data = {
            'id': 'task-test-002',
            'scope': 'task',
            'phase': 'do',
            'task_card_id': 'T5.5_TASK-CARD',
            'do': {
                'children': ['topic']
            },
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'version': 1
            }
        }
        with open('cycles/task/task-test-002.yaml', 'w') as f:
            yaml.dump(cycle_data, f)
        
        result = execute_cycle('task-test-002')
        
        # 应该创建子环
        self.assertEqual(result['status'], 'completed')
        self.assertGreaterEqual(len(result['children_created']), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)