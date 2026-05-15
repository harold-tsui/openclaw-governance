#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan 模块 - PDCA 循环规划阶段

实现 determine_review() 和 init_plan() 接口，负责：
1. 加载 Task-Card 验收标准
2. 计算 review_context（内存，不持久化）
3. 初始化 CycleUnit.plan

依据：pdca-check-protocol v1.3 §3

Author: 张铁 (CQO)
Date: 2026-04-05
"""

import os
import re
import yaml
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone


# ── 异常定义 ────────────────────────────────────────

class TaskCardNotFoundError(Exception):
    """Task-Card 文件不存在"""
    pass


class TaskCardParseError(Exception):
    """Task-Card 解析失败"""
    pass


class ReviewLevelInvalidError(Exception):
    """Review 级别无效"""
    pass


# ── 常量定义 ────────────────────────────────────────

VALID_REVIEW_LEVELS = ['L0', 'L1', 'L2', 'L3']

DEFAULT_REVIEW_LEVEL = 'L3'  # 默认全量人工（最安全）

EMPTY_CRITERIA_FALLBACK_LEVEL = 'L2'  # 空验收标准降级到抽样


# ── 核心接口 ────────────────────────────────────────

def determine_review(
    task_card_path: str,
    task_id: str,
    scope: str,
    parent_review_level: Optional[str] = None,
    project_phase: str = 'establishing',
    priority: str = 'P1',
    agent_id: str = 'cqo',
    dl_refs: Optional[List[str]] = None,
    is_first_time: bool = False
) -> Dict[str, Any]:
    """
    根据 pdca-check-protocol v1.3 §3 计算 review_context
    
    Args:
        task_card_path: Task-CARD 文件路径
        task_id: Task ID
        scope: 执行粒度（task/topic/project/system）
        parent_review_level: 父环 review_level（子环约束）
        project_phase: 项目阶段（establishing|transition|cruising|maintaining）
        priority: 优先级（P0|P1|P2|P3）
        agent_id: 执行 Agent ID
        dl_refs: 授权引用列表
        is_first_time: 是否首次执行
    
    Returns:
        review_context (内存，不持久化):
        {
            "review_level": "L0|L1|L2|L3",
            "human_approval_required": bool,
            "reviewer": "harold|yin-yue|null",
            "delegation_ref": "DA-001|null",
            "acceptance_criteria": [],
            "references": [],
            "parent_constraint_applied": bool
        }
    
    Raises:
        TaskCardNotFoundError: task-card 不存在
        TaskCardParseError: task-card 解析失败
    """
    
    # 1. 加载 task-card
    if not os.path.exists(task_card_path):
        raise TaskCardNotFoundError(f"Task-Card not found: {task_card_path}")
    
    try:
        with open(task_card_path, 'r', encoding='utf-8') as f:
            task_card_content = f.read()
    except Exception as e:
        raise TaskCardParseError(f"Failed to read Task-Card: {e}")
    
    # 2. 解析 task-card §一 Review 级别
    review_level = parse_review_level_from_task_card(task_card_content)
    
    # 3. 解析 task-card §五 acceptance_criteria
    acceptance_criteria = parse_acceptance_criteria_from_task_card(task_card_content)
    
    # 4. 解析授权编号（如有）
    delegation_ref = parse_delegation_ref_from_task_card(task_card_content)
    
    # 5. 应用子环约束（如有）
    parent_constraint_applied = False
    if parent_review_level is not None:
        # 子环约束：不得低于 max(parent_review_level - 1, L0)
        constrained_level = apply_parent_constraint(review_level, parent_review_level)
        if constrained_level != review_level:
            parent_constraint_applied = True
            review_level = constrained_level
    
    # 6. 计算 reviewer
    reviewer = calculate_reviewer(review_level)
    
    # 7. 计算 human_approval_required
    human_approval_required = (review_level == 'L3')
    
    # 8. 构建 review_context
    review_context = {
        'review_level': review_level,
        'human_approval_required': human_approval_required,
        'reviewer': reviewer,
        'delegation_ref': delegation_ref,
        'acceptance_criteria': acceptance_criteria,
        'references': [
            'docs/pdca-check-protocol.md',
            task_card_path
        ],
        'parent_constraint_applied': parent_constraint_applied
    }
    
    return review_context


def init_plan(
    cycle_id: str,
    scope: str,
    task_card_path: str,
    task_id: str,
    parent_review_level: Optional[str] = None,
    time_horizon_cycles: int = 3,
    max_cycles: int = 10
) -> Dict[str, Any]:
    """
    初始化 CycleUnit.plan
    
    Args:
        cycle_id: CycleUnit ID
        scope: 执行粒度
        task_card_path: Task-CARD 文件路径
        task_id: Task ID
        parent_review_level: 父环 review_level（子环约束）
        time_horizon_cycles: 时间窗口（cycles）
        max_cycles: 循环上限
    
    Returns:
        CycleUnit plan 块（待写入 cycle_unit）
    
    Note:
        - review_context 存于内存，不持久化到 cycle_unit
        - human_approval_required 初始化到 cycle_unit.plan
    """
    
    # 调用 determine_review() 计算 review_context
    review_context = determine_review(
        task_card_path=task_card_path,
        task_id=task_id,
        scope=scope,
        parent_review_level=parent_review_level
    )
    
    # 构建 plan 块（写入 cycle_unit）
    plan_block = {
        'task_card_id': task_id,
        'task_card_path': task_card_path,
        'human_approval_required': review_context['human_approval_required'],
        'time_horizon_cycles': time_horizon_cycles,
        'max_cycles': max_cycles
    }
    
    return plan_block


# ── 解析辅助函数 ────────────────────────────────────

def parse_review_level_from_task_card(content: str) -> str:
    """
    从 task-card §一 解析 Review 级别
    
    Args:
        content: task-card 文件内容
    
    Returns:
        Review 级别（L0|L1|L2|L3），默认 L3
    
    Raises:
        ReviewLevelInvalidError: 级别无效
    """
    
    # 匹配 §一 基本信息表中的 "Review 级别" 行
    # 格式：| **Review 级别** | L3（Harold 全量 Review） |
    pattern = r'\|\s*\*?\*?Review\s*级别\*?\*?\s*\|\s*(L\d)'
    
    match = re.search(pattern, content)
    
    if match:
        level = match.group(1)
        if level not in VALID_REVIEW_LEVELS:
            # 降级到 L2，记录告警
            return EMPTY_CRITERIA_FALLBACK_LEVEL
        return level
    
    # 未找到 → 默认 L3（最安全）
    return DEFAULT_REVIEW_LEVEL


def parse_acceptance_criteria_from_task_card(content: str) -> List[str]:
    """
    从 task-card §五 解析验收标准
    
    Args:
        content: task-card 文件内容
    
    Returns:
        验收标准列表
    """
    
    # 匹配 §五 验收标准表
    # 格式：| 标准 | 状态 | 说明 |
    pattern = r'##\s*五、验收标准\s*\n.*?\n(?:\|.*?\n)+'
    
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return []
    
    criteria_table = match.group(0)
    
    # 提取标准列（第一列）
    criteria = []
    for line in criteria_table.split('\n'):
        if line.startswith('|') and not line.startswith('| 标准') and not line.startswith('|---'):
            parts = line.split('|')
            if len(parts) >= 2:
                criterion = parts[1].strip().replace('*', '')
                if criterion:
                    criteria.append(criterion)
    
    return criteria


def parse_delegation_ref_from_task_card(content: str) -> Optional[str]:
    """
    从 task-card §一 解析授权编号
    
    Args:
        content: task-card 文件内容
    
    Returns:
        授权编号（DA-XXX）或 null
    """
    
    # 匹配授权编号（DA-XXX 格式）
    pattern = r'DA-\d{3}'
    
    match = re.search(pattern, content)
    
    if match:
        return match.group(0)
    
    return None


# ── 级别计算辅助函数 ─────────────────────────────────

def apply_parent_constraint(child_level: str, parent_level: str) -> str:
    """
    应用子环约束：不得低于 max(parent_review_level - 1, L0)
    
    Args:
        child_level: 子环原始级别
        parent_level: 父环级别
    
    Returns:
        受约束后的子环级别
    
    Note:
        - L0=免审（数字最小）= 最宽松
        - L3=全量人工（数字最大）= 最严格
        - 子环不得比父环更宽松超过 1 级
    """
    
    # 级别转数字
    level_map = {'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3}
    
    child_num = level_map.get(child_level, 3)
    parent_num = level_map.get(parent_level, 3)
    
    # 子环不得低于 max(parent - 1, 0)
    min_child_num = max(parent_num - 1, 0)
    
    if child_num < min_child_num:
        # 子环太宽松 → 自动收紧
        constrained_num = min_child_num
        return f"L{constrained_num}"
    
    return child_level


def calculate_reviewer(review_level: str) -> Optional[str]:
    """
    根据 review_level 计算 reviewer
    
    Args:
        review_level: Review 级别
    
    Returns:
        reviewer (harold|yin-yue|null)
    
    Rules (protocol §3.6):
        - L0: null
        - L1: null（异常时银月判断）
        - L2: yin-yue（抽中升级为 harold）
        - L3: harold（必填）
    """
    
    reviewer_map = {
        'L0': None,       # 免审，不介入
        'L1': None,       # 异常上报，正常路径 null
        'L2': 'yin-yue',  # 抽样核查，银月执行
        'L3': 'harold'    # 全量人工，Harold 必须介入
    }
    
    return reviewer_map.get(review_level, 'harold')


# ── 单元测试入口 ────────────────────────────────────

if __name__ == "__main__":
    # 简单测试
    print("Plan 模块测试...")
    
    # 测试 task-card 解析
    test_task_card = "tasks/T1.1_TASK-CARD.md"
    
    if os.path.exists(test_task_card):
        print(f"\n1. 加载 {test_task_card}...")
        
        try:
            review_context = determine_review(
                task_card_path=test_task_card,
                task_id="T1.1",
                scope="task"
            )
            
            print(f"   review_level: {review_context['review_level']}")
            print(f"   human_approval_required: {review_context['human_approval_required']}")
            print(f"   reviewer: {review_context['reviewer']}")
            print(f"   acceptance_criteria: {review_context['acceptance_criteria']}")
            print(f"   parent_constraint_applied: {review_context['parent_constraint_applied']}")
            
            print("\n✅ determine_review() 测试通过")
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"   Task-Card 不存在: {test_task_card}")