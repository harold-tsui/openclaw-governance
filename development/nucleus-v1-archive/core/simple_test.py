#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleUnit 简单功能测试
"""

import os
import sys
import tempfile
import shutil

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cycle_unit import create_cycle, load_cycle, save_cycle


def test_simple():
    """简单测试（v1.3 Schema）"""
    print("开始简单测试（v1.3 Schema）...")
    
    # 创建临时工作目录
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        # 创建 cycles 目录
        os.makedirs('cycles/task', exist_ok=True)
        
        cycle_id = "task-simple-test"
        scope = "task"
        task_card_id = "T1.2"  # v1.2: 必填，绑定 task-card
        
        # 创建 CycleUnit（v1.3-fixed Schema）
        print("1. 创建 CycleUnit（v1.3-fixed Schema）...")
        create_cycle(cycle_id, scope, task_card_id, {})
        print("   ✓ 创建成功（v1.2 字段已继承）")
        
        # 加载并验证
        print("2. 加载 CycleUnit...")
        unit = load_cycle(cycle_id, scope)
        print(f"   ID: {unit['id']}")
        print(f"   Scope: {unit['scope']}")
        print(f"   task_card_id: {unit['task_card_id']} (v1.2) ✅")
        print(f"   Phase: {unit['phase']}")
        print(f"   Version: {unit['metadata']['version']}")
        print("   ✓ 加载成功")
        
        # 验证 v1.3-fixed 结构（移除 check_reference + 继承 v1.2 字段）
        print("3. 验证 v1.3-fixed 结构...")
        assert 'task_card_id' in unit
        assert unit['task_card_id'] == task_card_id
        # v1.3-fixed: 继承 v1.2 字段
        assert 'task_card_path' in unit  # 继承 v1.2
        assert 'blocked_reason' in unit['do']  # 继承 v1.2
        assert 'lesson_learn_ref' in unit['act']  # 继承 v1.2
        assert 'plan' in unit
        assert 'check_reference' not in unit['plan']  # v1.3: 已移除
        assert 'time_horizon_cycles' in unit['plan']  # 时间约束保留
        assert 'human_approval_required' in unit['plan']  # 设计时声明保留
        assert 'do' in unit
        assert 'status' in unit['do']  # v1.2: status
        assert 'children' in unit['do']  # v1.2: ID 引用
        assert 'criteria_results' in unit['check']  # v1.2: 逐项核对
        assert 'next_cycle_id' in unit['act']  # v1.2: ID 引用
        print("   ✓ v1.3-fixed 结构验证成功（check_reference 已移除 + v1.2 字段已继承）")
        
        # 修改并保存
        print("4. 修改并保存...")
        unit['do']['status'] = 'in_progress'
        unit['check']['criteria_results'] = [{'criterion': 'test', 'result': 'pass'}]
        save_cycle(unit)
        
        # 验证修改
        updated = load_cycle(cycle_id, scope)
        print(f"   Updated Version: {updated['metadata']['version']}")
        print(f"   Updated do.status: {updated['do']['status']}")
        print(f"   Updated check.criteria_results: {updated['check']['criteria_results']}")
        print("   ✓ 保存成功")
        
        print("\n✅ v1.3-fixed Schema 测试通过（Claude 评审修复完成）！")
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
    success = test_simple()
    sys.exit(0 if success else 1)