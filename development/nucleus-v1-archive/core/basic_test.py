#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleUnit 基本功能测试（不依赖 pytest）
"""

import os
import sys
import shutil
import tempfile
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cycle_unit import (
    load_cycle, save_cycle, update_phase, create_cycle, get_cycle_version,
    CycleUnitNotFoundError, CycleUnitWriteError
)


def test_basic_functionality():
    """基本功能测试"""
    print("开始基本功能测试...")
    
    # 创建临时工作目录
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        # 创建 cycles 目录结构
        os.makedirs('cycles/task', exist_ok=True)
        os.makedirs('cycles/archive/task', exist_ok=True)
        
        cycle_id = "task-test-basic-001"
        scope = "task"
        
        # 测试创建 CycleUnit
        print("1. 测试创建 CycleUnit...")
        initial_data = {
            'plan': {
                'intent': 'Basic test intent',
                'success_criteria': ['criteria1', 'criteria2']
            }
        }
        create_cycle(cycle_id, scope, initial_data)
        print("   ✓ 创建成功")
        
        # 测试加载 CycleUnit
        print("2. 测试加载 CycleUnit...")
        unit = load_cycle(cycle_id, scope)
        assert unit['id'] == cycle_id
        assert unit['scope'] == scope
        assert unit['phase'] == 'plan'
        assert unit['plan']['intent'] == 'Basic test intent'
        assert unit['metadata']['version'] == 1
        print("   ✓ 加载成功")
        
        # 测试保存 CycleUnit
        print("3. 测试保存 CycleUnit...")
        unit['plan']['intent'] = 'Modified intent'
        save_cycle(unit)
        updated_unit = load_cycle(cycle_id, scope)
        assert updated_unit['metadata']['version'] == 2
        assert updated_unit['plan']['intent'] == 'Modified intent'
        print("   ✓ 保存成功")
        
        # 测试更新 phase
        print("4. 测试更新 phase...")
        update_phase(cycle_id, scope, 'do')
        phase_updated = load_cycle(cycle_id, scope)
        assert phase_updated['phase'] == 'do'
        assert phase_updated['metadata']['version'] == 3
        print("   ✓ Phase 更新成功")
        
        # 测试归档
        print("5. 测试归档功能...")
        archive_path = f'cycles/archive/{scope}/{cycle_id}_v1.yaml'
        assert os.path.exists(archive_path)
        print("   ✓ 归档成功")
        
        # 测试版本获取
        print("6. 测试版本获取...")
        version = get_cycle_version(cycle_id, scope)
        assert version == 3
        print("   ✓ 版本获取成功")
        
        # 测试错误处理
        print("7. 测试错误处理...")
        try:
            load_cycle("nonexistent", "task")
            assert False, "应该抛出异常"
        except CycleUnitNotFoundError:
            print("   ✓ 文件未找到异常正确")
        
        try:
            update_phase(cycle_id, scope, "invalid_phase")
            assert False, "应该抛出异常"
        except ValueError:
            print("   ✓ 无效 phase 异常正确")
        
        print("\n✅ 所有基本功能测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    success = test_basic_functionality()
    sys.exit(0 if success else 1)