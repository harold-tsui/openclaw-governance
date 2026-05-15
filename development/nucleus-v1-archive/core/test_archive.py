#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
归档机制测试验证

验证 update_phase() 归档逻辑是否正确：
1. Phase 转换时创建归档文件
2. 归档文件命名符合规范
3. 归档文件内容完整
4. 版本号正确递增

Author: 张铁 (CQO)
Date: 2026-04-05
"""

import os
import sys
import yaml
from datetime import datetime, timezone

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cycle_unit import create_cycle, load_cycle, save_cycle, update_phase, _get_archive_path


def test_archive():
    """归档机制测试"""
    print("开始归档机制测试...")
    
    cycle_id = "archive-test-001"
    scope = "task"
    task_card_id = "T1.3"
    
    try:
        # Step 1: 创建 CycleUnit
        print("\n1. 创建 CycleUnit...")
        create_cycle(cycle_id, scope, task_card_id, {})
        unit = load_cycle(cycle_id, scope)
        print(f"   创建成功，初始 phase: {unit['phase']}, version: {unit['metadata']['version']}")
        
        # Step 2: Phase 转换 plan → do（触发归档）
        print("\n2. Phase 转换 plan → do...")
        update_phase(cycle_id, scope, 'do')
        
        # Step 3: 检查归档文件
        print("\n3. 检查归档文件...")
        archive_path = _get_archive_path(cycle_id, scope, 1)  # version=1（第一次归档）
        
        if os.path.exists(archive_path):
            print(f"   ✓ 归档文件存在: {archive_path}")
            
            # 检查归档内容
            with open(archive_path, 'r', encoding='utf-8') as f:
                archived_unit = yaml.safe_load(f)
            
            print(f"   归档 phase: {archived_unit['phase']} (应为 plan)")
            print(f"   归档 version: {archived_unit['metadata']['version']} (应为 1)")
            
            assert archived_unit['phase'] == 'plan', "归档 phase 应为 plan"
            assert archived_unit['metadata']['version'] == 1, "归档 version 应为 1"
            print("   ✓ 归档内容验证成功")
        else:
            print(f"   ✗ 归档文件不存在: {archive_path}")
            return False
        
        # Step 4: 检查主文件更新
        print("\n4. 检查主文件更新...")
        unit = load_cycle(cycle_id, scope)
        print(f"   主文件 phase: {unit['phase']} (应为 do)")
        print(f"   主文件 version: {unit['metadata']['version']} (应为 2)")
        
        assert unit['phase'] == 'do', "主文件 phase 应为 do"
        assert unit['metadata']['version'] == 2, "主文件 version 应为 2"
        print("   ✓ 主文件更新验证成功")
        
        # Step 5: 多次转换验证
        print("\n5. 多次转换验证（do → check）...")
        update_phase(cycle_id, scope, 'check')
        
        archive_path_v2 = _get_archive_path(cycle_id, scope, 2)
        if os.path.exists(archive_path_v2):
            print(f"   ✓ 归档 v2 文件存在: {archive_path_v2}")
            
            with open(archive_path_v2, 'r', encoding='utf-8') as f:
                archived_v2 = yaml.safe_load(f)
            
            assert archived_v2['phase'] == 'do', "归档 v2 phase 应为 do"
            assert archived_v2['metadata']['version'] == 2, "归档 v2 version 应为 2"
            print("   ✓ 归档 v2 验证成功")
        else:
            print(f"   ✗ 归档 v2 文件不存在")
            return False
        
        unit = load_cycle(cycle_id, scope)
        assert unit['phase'] == 'check', "主文件 phase 应为 check"
        assert unit['metadata']['version'] == 3, "主文件 version 应为 3"
        print("   ✓ 主文件 v3 验证成功")
        
        # Step 6: 目录结构确认
        print("\n6. 目录结构确认...")
        expected_structure = [
            f"cycles/{scope}/{cycle_id}.yaml",  # 主文件
            f"cycles/archive/{scope}/{cycle_id}_v1.yaml",  # 归档 v1
            f"cycles/archive/{scope}/{cycle_id}_v2.yaml",  # 归档 v2
        ]
        
        for path in expected_structure:
            if os.path.exists(path):
                print(f"   ✓ {path}")
            else:
                print(f"   ✗ {path} 不存在")
                return False
        
        print("\n✅ 归档机制测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试文件
        print("\n清理测试文件...")
        try:
            main_path = f"cycles/{scope}/{cycle_id}.yaml"
            if os.path.exists(main_path):
                os.remove(main_path)
                print(f"   ✓ 删除主文件: {main_path}")
            
            archive_path_v1 = _get_archive_path(cycle_id, scope, 1)
            if os.path.exists(archive_path_v1):
                os.remove(archive_path_v1)
                print(f"   ✓ 删除归档 v1: {archive_path_v1}")
            
            archive_path_v2 = _get_archive_path(cycle_id, scope, 2)
            if os.path.exists(archive_path_v2):
                os.remove(archive_path_v2)
                print(f"   ✓ 删除归档 v2: {archive_path_v2}")
        except Exception as e:
            print(f"   清理失败: {e}")


if __name__ == "__main__":
    success = test_archive()
    sys.exit(0 if success else 1)