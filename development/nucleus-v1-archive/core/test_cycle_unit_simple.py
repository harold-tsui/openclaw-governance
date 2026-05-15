#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleUnit 简单测试（不依赖 pytest）

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import shutil
import tempfile
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cycle_unit import (
    load_cycle, save_cycle, update_phase, create_cycle, get_cycle_version,
    CycleUnitNotFoundError, CycleUnitWriteError
)


def test_create_and_load_cycle():
    """测试创建和加载 CycleUnit"""
    print("Testing create_and_load_cycle...")
    
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        # 创建目录结构
        os.makedirs('cycles/task', exist_ok=True)
        
        cycle_id = "task-20260405-abc123"
        scope = "task"
        initial_data = {
            'plan': {
                'intent': 'Test intent',
                'success_criteria': ['criteria1', 'criteria2']
            }
        }
        
        # 创建 CycleUnit
        create_cycle(cycle_id, scope, 'T1.1', initial_data)
        
        # 加载并验证
        unit = load_cycle(cycle_id, scope)
        
        assert unit['id'] == cycle_id
        assert unit['scope'] == scope
        assert unit['phase'] == 'plan'
        assert unit['plan']['intent'] == 'Test intent'
        assert unit['metadata']['version'] == 1
        
        print("✅ create_and_load_cycle passed")
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


def test_update_phase():
    """测试 Phase 转换"""
    print("Testing update_phase...")
    
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        os.makedirs('cycles/task', exist_ok=True)
        os.makedirs('cycles/archive/task', exist_ok=True)
        
        cycle_id = "task-20260405-phase"
        scope = "task"
        initial_data = {'plan': {'intent': 'Phase test'}}
        
        create_cycle(cycle_id, scope, 'T1.2', initial_data)
        
        # Phase 转换 plan → do
        update_phase(cycle_id, scope, 'do')
        
        unit = load_cycle(cycle_id, scope)
        assert unit['phase'] == 'do'
        assert unit['metadata']['version'] == 2
        
        print("✅ update_phase passed")
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


def test_get_cycle_version():
    """测试获取版本号"""
    print("Testing get_cycle_version...")
    
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        os.makedirs('cycles/task', exist_ok=True)
        
        cycle_id = "task-20260405-version"
        scope = "task"
        initial_data = {'plan': {'intent': 'Version test'}}
        
        create_cycle(cycle_id, scope, 'T1.3', initial_data)
        
        version = get_cycle_version(cycle_id, scope)
        assert version == 1
        
        update_phase(cycle_id, scope, 'do')
        version = get_cycle_version(cycle_id, scope)
        assert version == 2
        
        print("✅ get_cycle_version passed")
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


def test_cycle_not_found():
    """测试加载不存在的 CycleUnit"""
    print("Testing cycle_not_found...")
    
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        os.makedirs('cycles/task', exist_ok=True)
        
        try:
            load_cycle("nonexistent-cycle", "task")
            assert False, "Should raise CycleUnitNotFoundError"
        except CycleUnitNotFoundError:
            print("✅ cycle_not_found passed (正确抛出异常)")
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


def main():
    """运行所有测试"""
    print("Running CycleUnit tests...\n")
    
    try:
        test_create_and_load_cycle()
        test_update_phase()
        test_get_cycle_version()
        test_cycle_not_found()
        
        print("\n🎉 All CycleUnit tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)