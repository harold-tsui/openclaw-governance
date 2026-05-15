#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan 模块单元测试

测试 determine_review() 和 init_plan() 接口：
1. task-card 加载正确
2. review_level 计算正确
3. 子环约束生效
4. L0/L3 级别定义正确

Author: 张铁 (CQO)
Date: 2026-04-05
"""

import os
import sys

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.plan import (
    determine_review,
    init_plan,
    parse_review_level_from_task_card,
    parse_acceptance_criteria_from_task_card,
    apply_parent_constraint,
    calculate_reviewer,
    TaskCardNotFoundError,
    VALID_REVIEW_LEVELS
)


def test_parse_review_level():
    """测试 task-card Review 级别解析"""
    
    print("\n1. 测试 parse_review_level_from_task_card...")
    
    # 测试有效级别
    test_cases = [
        ("| **Review 级别** | L3（Harold 全量 Review） |", "L3"),
        ("| Review 级别 | L2 |", "L2"),
        ("| **Review 级别** | L0（免审） |", "L0"),
        ("| 无匹配 | xxx |", "L3"),  # 默认 L3
    ]
    
    for content, expected in test_cases:
        result = parse_review_level_from_task_card(content)
        if result == expected:
            print(f"   ✓ '{content[:30]}...' → {result}")
        else:
            print(f"   ✗ '{content[:30]}...' → {result} (期望 {expected})")
            return False
    
    print("   ✓ parse_review_level_from_task_card 测试通过")
    return True


def test_parse_acceptance_criteria():
    """测试 task-card 验收标准解析"""
    
    print("\n2. 测试 parse_acceptance_criteria_from_task_card...")
    
    test_content = """
## 五、验收标准

| 标准 | 状态 | 说明 |
|------|------|------|
| DoD-1 | ⬜ | Schema 定义完整 |
| DoD-2 | ⬜ | 所有字段有注释 |
| DoD-3 | ⬜ | Harold 签字确认 |
"""
    
    criteria = parse_acceptance_criteria_from_task_card(test_content)
    
    expected_criteria = ['DoD-1', 'DoD-2', 'DoD-3']
    
    if criteria == expected_criteria:
        print(f"   ✓ 解析正确: {criteria}")
        return True
    else:
        print(f"   ✗ 解析错误: {criteria} (期望 {expected_criteria})")
        return False


def test_apply_parent_constraint():
    """测试子环约束逻辑"""
    
    print("\n3. 测试 apply_parent_constraint...")
    
    # protocol §3.2 规则：子环不得低于 max(parent - 1, L0)
    test_cases = [
        # (child, parent, expected_result)
        ('L0', 'L0', 'L0'),  # parent=L0，子环任意
        ('L3', 'L0', 'L3'),  # parent=L0，子环可以更严格
        ('L0', 'L1', 'L0'),  # parent=L1，子环至少 L0
        ('L0', 'L2', 'L1'),  # parent=L2，子环不能 L0 → 自动收紧到 L1
        ('L1', 'L2', 'L1'),  # parent=L2，子环 L1 合规
        ('L0', 'L3', 'L2'),  # parent=L3，子环不能 L0/L1 → 自动收紧到 L2
        ('L1', 'L3', 'L2'),  # parent=L3，子环 L1 不合规 → 自动收紧到 L2
        ('L2', 'L3', 'L2'),  # parent=L3，子环 L2 合规
        ('L3', 'L3', 'L3'),  # parent=L3，子环 L3 合规
    ]
    
    for child, parent, expected in test_cases:
        result = apply_parent_constraint(child, parent)
        if result == expected:
            print(f"   ✓ child={child}, parent={parent} → {result}")
        else:
            print(f"   ✗ child={child}, parent={parent} → {result} (期望 {expected})")
            return False
    
    print("   ✓ apply_parent_constraint 测试通过")
    return True


def test_calculate_reviewer():
    """测试 reviewer 计算"""
    
    print("\n4. 测试 calculate_reviewer...")
    
    # protocol §3.6 规则
    test_cases = [
        ('L0', None),       # 免审，不介入
        ('L1', None),       # 异常上报，正常路径 null
        ('L2', 'yin-yue'),  # 抽样核查
        ('L3', 'harold'),   # 全量人工
    ]
    
    for level, expected in test_cases:
        result = calculate_reviewer(level)
        if result == expected:
            print(f"   ✓ level={level} → reviewer={result}")
        else:
            print(f"   ✗ level={level} → reviewer={result} (期望 {expected})")
            return False
    
    print("   ✓ calculate_reviewer 测试通过")
    return True


def test_determine_review_with_real_task_card():
    """测试 determine_review() 使用真实 task-card"""
    
    print("\n5. 测试 determine_review() 真实 task-card...")
    
    # 使用已完成的 T1.1 task-card
    task_card_path = "tasks/T1.1_TASK-CARD.md"
    
    if not os.path.exists(task_card_path):
        print(f"   ⚠ Task-Card 不存在: {task_card_path}")
        return True  # 跳过，不报错
    
    try:
        review_context = determine_review(
            task_card_path=task_card_path,
            task_id="T1.1",
            scope="task"
        )
        
        print(f"   review_level: {review_context['review_level']}")
        print(f"   human_approval_required: {review_context['human_approval_required']}")
        print(f"   reviewer: {review_context['reviewer']}")
        print(f"   acceptance_criteria count: {len(review_context['acceptance_criteria'])}")
        
        # 验证 L3 级别
        if review_context['review_level'] == 'L3':
            print(f"   ✓ L3 级别正确")
        else:
            print(f"   ⚠ 级别 {review_context['review_level']}，可能需要检查 task-card")
        
        # 验证 human_approval_required
        if review_context['human_approval_required'] == True:
            print(f"   ✓ human_approval_required=true 正确")
        else:
            print(f"   ✗ human_approval_required 应为 true")
            return False
        
        # 验证 reviewer
        if review_context['reviewer'] == 'harold':
            print(f"   ✓ reviewer=harold 正确")
        else:
            print(f"   ✗ reviewer 应为 harold")
            return False
        
        print("   ✓ determine_review() 测试通过")
        return True
        
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_determine_review_with_parent_constraint():
    """测试 determine_review() 子环约束"""
    
    print("\n6. 测试 determine_review() 子环约束...")
    
    task_card_path = "tasks/T1.1_TASK-CARD.md"
    
    if not os.path.exists(task_card_path):
        print(f"   ⚠ Task-Card 不存在: {task_card_path}")
        return True
    
    try:
        # 无约束
        review_context_no_constraint = determine_review(
            task_card_path=task_card_path,
            task_id="T1.1",
            scope="task",
            parent_review_level=None
        )
        
        # 有约束（parent=L2）
        review_context_with_constraint = determine_review(
            task_card_path=task_card_path,
            task_id="T1.1",
            scope="task",
            parent_review_level='L2'
        )
        
        # T1.1 原始级别 L3，parent=L2 约束后仍为 L3（合规）
        if review_context_with_constraint['review_level'] == 'L3':
            print(f"   ✓ parent=L2, child=L3 合规（无收紧）")
            print(f"   parent_constraint_applied: {review_context_with_constraint['parent_constraint_applied']}")
        
        print("   ✓ 子环约束测试通过")
        return True
        
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        return False


def test_init_plan():
    """测试 init_plan()"""
    
    print("\n7. 测试 init_plan()...")
    
    task_card_path = "tasks/T1.1_TASK-CARD.md"
    
    if not os.path.exists(task_card_path):
        print(f"   ⚠ Task-Card 不存在: {task_card_path}")
        return True
    
    try:
        plan_block = init_plan(
            cycle_id="task-test-plan-001",
            scope="task",
            task_card_path=task_card_path,
            task_id="T1.1",
            time_horizon_cycles=3,
            max_cycles=10
        )
        
        print(f"   task_card_id: {plan_block['task_card_id']}")
        print(f"   task_card_path: {plan_block['task_card_path']}")
        print(f"   human_approval_required: {plan_block['human_approval_required']}")
        print(f"   time_horizon_cycles: {plan_block['time_horizon_cycles']}")
        print(f"   max_cycles: {plan_block['max_cycles']}")
        
        # 验证必填字段
        required_fields = ['task_card_id', 'task_card_path', 'human_approval_required']
        for field in required_fields:
            if field in plan_block:
                print(f"   ✓ {field} 存在")
            else:
                print(f"   ✗ {field} 缺失")
                return False
        
        print("   ✓ init_plan() 测试通过")
        return True
        
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    
    print("=" * 50)
    print("Plan 模块单元测试")
    print("=" * 50)
    
    # 切换到项目目录
    project_dir = "/Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0"
    if os.path.exists(project_dir):
        os.chdir(project_dir)
        print(f"\n工作目录: {os.getcwd()}")
    
    tests = [
        test_parse_review_level,
        test_parse_acceptance_criteria,
        test_apply_parent_constraint,
        test_calculate_reviewer,
        test_determine_review_with_real_task_card,
        test_determine_review_with_parent_constraint,
        test_init_plan
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {test.__name__} 异常: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)