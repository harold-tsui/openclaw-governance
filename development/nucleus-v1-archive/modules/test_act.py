#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Act 模块单元测试

测试 adjust_automation_level()、PhaseBarrierLock 和 propagate_adjustments() 功能

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import unittest
import tempfile
import yaml
from datetime import datetime, timezone

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.act import (
    adjust_automation_level,
    PhaseBarrierLock,
    apply_adjustments,
    propagate_adjustments,
    CycleUnitNotFoundError,
    AdjustmentError
)


class TestAdjustAutomationLevel(unittest.TestCase):
    """测试 adjust_automation_level() 函数"""
    
    def test_pass_upgrade_l0_to_l1(self):
        """测试 L0 → L1 升级"""
        adjustments = adjust_automation_level(
            cycle_id="test-001",
            verdict="pass",
            consecutive_count=2,  # 第3次成功
            current_level="L0",
            evidence=["test_evidence"]
        )
        
        self.assertEqual(len(adjustments), 1)
        adj = adjustments[0]
        self.assertEqual(adj['type'], 'level_change')
        self.assertEqual(adj['from'], 'L0')
        self.assertEqual(adj['to'], 'L1')
        self.assertFalse(adj['requires_harold_confirmation'])
    
    def test_pass_upgrade_l1_to_l2(self):
        """测试 L1 → L2 升级"""
        adjustments = adjust_automation_level(
            cycle_id="test-002",
            verdict="pass",
            consecutive_count=3,  # 超过阈值
            current_level="L1",
            evidence=["test_evidence"]
        )
        
        self.assertEqual(len(adjustments), 1)
        adj = adjustments[0]
        self.assertEqual(adj['type'], 'level_change')
        self.assertEqual(adj['from'], 'L1')
        self.assertEqual(adj['to'], 'L2')
        self.assertFalse(adj['requires_harold_confirmation'])
    
    def test_pass_l2_to_l3_requires_confirmation(self):
        """测试 L2 → L3 需要 Harold 确认"""
        adjustments = adjust_automation_level(
            cycle_id="test-003",
            verdict="pass",
            consecutive_count=3,
            current_level="L2",
            evidence=["test_evidence"]
        )
        
        self.assertEqual(len(adjustments), 1)
        adj = adjustments[0]
        self.assertEqual(adj['type'], 'level_change_pending_confirmation')
        self.assertEqual(adj['from'], 'L2')
        self.assertEqual(adj['to'], 'L3')
        self.assertTrue(adj['requires_harold_confirmation'])
    
    def test_pass_l3_max_level(self):
        """测试 L3 已达最高级别，维持不变"""
        adjustments = adjust_automation_level(
            cycle_id="test-004",
            verdict="pass",
            consecutive_count=5,
            current_level="L3",
            evidence=["test_evidence"]
        )
        
        self.assertEqual(len(adjustments), 1)
        adj = adjustments[0]
        self.assertEqual(adj['type'], 'maintain')
        self.assertEqual(adj['from'], 'L3')
        self.assertEqual(adj['to'], 'L3')
    
    def test_fail_downgrade_l3_to_l2(self):
        """测试 L3 → L2 降级"""
        adjustments = adjust_automation_level(
            cycle_id="test-005",
            verdict="fail",
            consecutive_count=1,  # 第2次失败
            current_level="L3",
            evidence=["test_evidence"]
        )
        
        self.assertEqual(len(adjustments), 1)
        adj = adjustments[0]
        self.assertEqual(adj['type'], 'level_change')
        self.assertEqual(adj['from'], 'L3')
        self.assertEqual(adj['to'], 'L2')
        self.assertFalse(adj['requires_harold_confirmation'])
    
    def test_fail_l0_min_level(self):
        """测试 L0 已达最低级别，维持不变"""
        adjustments = adjust_automation_level(
            cycle_id="test-006",
            verdict="fail",
            consecutive_count=3,
            current_level="L0",
            evidence=["test_evidence"]
        )
        
        self.assertEqual(len(adjustments), 1)
        adj = adjustments[0]
        self.assertEqual(adj['type'], 'maintain')
        self.assertEqual(adj['from'], 'L0')
        self.assertEqual(adj['to'], 'L0')
    
    def test_partial_maintain(self):
        """测试 partial 维持当前级别"""
        adjustments = adjust_automation_level(
            cycle_id="test-007",
            verdict="partial",
            consecutive_count=5,
            current_level="L2",
            evidence=["test_evidence"]
        )
        
        self.assertEqual(len(adjustments), 1)
        adj = adjustments[0]
        self.assertEqual(adj['type'], 'maintain')
        self.assertEqual(adj['from'], 'L2')
        self.assertEqual(adj['to'], 'L2')
        self.assertEqual(adj['consecutive_count_snapshot'], 0)  # 重置计数
    
    def test_skip_maintain_consecutive_unchanged(self):
        """测试 skip 维持且连续计数不变"""
        original_count = 7
        adjustments = adjust_automation_level(
            cycle_id="test-008",
            verdict="skip",
            consecutive_count=original_count,
            current_level="L1",
            evidence=[]
        )
        
        self.assertEqual(len(adjustments), 1)
        adj = adjustments[0]
        self.assertEqual(adj['type'], 'maintain')
        self.assertEqual(adj['from'], 'L1')
        self.assertEqual(adj['to'], 'L1')
        self.assertEqual(adj['consecutive_count_snapshot'], original_count)  # 计数不变
    
    def test_invalid_verdict(self):
        """测试无效 verdict"""
        with self.assertRaises(ValueError):
            adjust_automation_level(
                cycle_id="test-009",
                verdict="invalid",
                consecutive_count=0,
                current_level="L1",
                evidence=[]
            )
    
    def test_invalid_level(self):
        """测试无效级别"""
        with self.assertRaises(ValueError):
            adjust_automation_level(
                cycle_id="test-010",
                verdict="pass",
                consecutive_count=0,
                current_level="L5",
                evidence=[]
            )


class TestPhaseBarrierLock(unittest.TestCase):
    """测试 PhaseBarrierLock 类"""
    
    def setUp(self):
        """创建临时测试文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_cycle_path = os.path.join(self.temp_dir, "test_cycle.yaml")
        
        # 创建测试 CycleUnit
        test_data = {
            'id': 'test-001',
            'scope': 'task',
            'phase': 'act',
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'version': 1
            }
        }
        
        with open(self.test_cycle_path, 'w') as f:
            yaml.dump(test_data, f)
    
    def tearDown(self):
        """清理临时文件"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_backup_and_rollback(self):
        """测试备份和回滚功能"""
        lock = PhaseBarrierLock(self.test_cycle_path)
        
        # 备份
        lock.backup()
        backup_path = f"{self.test_cycle_path}.backup"
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(lock.backed_up)
        
        # 修改原文件
        modified_data = {
            'id': 'test-001-modified',
            'scope': 'task',
            'phase': 'act',
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'version': 2
            }
        }
        with open(self.test_cycle_path, 'w') as f:
            yaml.dump(modified_data, f)
        
        # 回滚
        lock.rollback()
        self.assertFalse(os.path.exists(backup_path))
        self.assertFalse(lock.backed_up)
        
        # 验证原文件恢复
        with open(self.test_cycle_path, 'r') as f:
            restored_data = yaml.safe_load(f)
        
        self.assertEqual(restored_data['id'], 'test-001')
        self.assertEqual(restored_data['metadata']['version'], 1)
    
    def test_context_manager_with_exception(self):
        """测试上下文管理器在异常时自动回滚"""
        original_content = None
        with open(self.test_cycle_path, 'r') as f:
            original_content = f.read()
        
        try:
            with PhaseBarrierLock(self.test_cycle_path) as lock:
                lock.backup()
                
                # 修改文件
                modified_data = {'modified': True}
                with open(self.test_cycle_path, 'w') as f:
                    yaml.dump(modified_data, f)
                
                # 抛出异常触发回滚
                raise Exception("Test exception")
        
        except Exception:
            pass  # 预期的异常
        
        # 验证文件已回滚
        with open(self.test_cycle_path, 'r') as f:
            restored_content = f.read()
        
        self.assertEqual(restored_content, original_content)
    
    def test_verify_success(self):
        """测试验证成功"""
        lock = PhaseBarrierLock(self.test_cycle_path)
        
        # 应用调整
        adjustments = [{'type': 'maintain', 'from': 'L1', 'to': 'L1'}]
        apply_adjustments(self.test_cycle_path, adjustments)
        
        # 验证
        self.assertTrue(lock.verify())
    
    def test_verify_failure(self):
        """测试验证失败"""
        lock = PhaseBarrierLock(self.test_cycle_path)
        
        # 不应用任何调整，直接验证
        self.assertFalse(lock.verify())


class TestApplyAdjustments(unittest.TestCase):
    """测试 apply_adjustments() 函数"""
    
    def setUp(self):
        """创建临时测试文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_cycle_path = os.path.join(self.temp_dir, "test_cycle.yaml")
        
        test_data = {
            'id': 'test-001',
            'scope': 'task',
            'phase': 'act',
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'version': 1
            }
        }
        
        with open(self.test_cycle_path, 'w') as f:
            yaml.dump(test_data, f)
    
    def tearDown(self):
        """清理临时文件"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_apply_adjustments_success(self):
        """测试成功应用调整"""
        adjustments = [
            {
                'type': 'level_change',
                'from': 'L1',
                'to': 'L2',
                'reason': 'test',
                'consecutive_count_snapshot': 3,
                'evidence': ['test_evidence']
            }
        ]
        
        success = apply_adjustments(self.test_cycle_path, adjustments)
        self.assertTrue(success)
        
        # 验证文件内容
        with open(self.test_cycle_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self.assertIn('act', data)
        self.assertIn('adjustments', data['act'])
        self.assertEqual(len(data['act']['adjustments']), 1)
        self.assertEqual(data['act']['adjustments'][0]['type'], 'level_change')
        self.assertEqual(data['metadata']['version'], 2)
    
    def test_apply_adjustments_file_not_found(self):
        """测试文件不存在"""
        non_existent_path = os.path.join(self.temp_dir, "non_existent.yaml")
        
        with self.assertRaises(CycleUnitNotFoundError):
            apply_adjustments(non_existent_path, [])


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)