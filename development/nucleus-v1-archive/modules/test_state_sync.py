#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态同步模块单元测试

验证 on_act_complete()、sync_task_card()、sync_topic_brief()、sync_mission_board() 功能。

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import tempfile
import yaml
import pytest
from datetime import datetime, timezone

# 导入被测模块
import sys
sys.path.insert(0, os.path.dirname(__file__))
from state_sync import (
    on_act_complete,
    sync_task_card,
    sync_topic_brief,
    sync_mission_board,
    extract_topic_id,
    extract_project_id,
    StateSyncError,
    FileNotFoundError
)


# ── Fixtures ────────────────────────────────────────

@pytest.fixture
def temp_project_dir():
    """临时项目目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建基础结构
        os.makedirs(f"{tmpdir}/tasks")
        os.makedirs(f"{tmpdir}/topics/N4-P1-T01")
        yield tmpdir


@pytest.fixture
def temp_agent_dir():
    """临时 Agent 目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_cycle_unit():
    """示例 CycleUnit"""
    return {
        'id': 'task-20260406T145600Z',
        'task_id': 'T1.1',
        'check': {
            'verdict': 'pass',
            'evidence': ['test_passed']
        },
        'act': {
            'decision': 'maintain'
        }
    }


@pytest.fixture
def sample_task_card(temp_project_dir):
    """示例 Task-CARD"""
    task_card_path = f"{temp_project_dir}/tasks/T1.1_TASK-CARD.md"
    content = """# TASK-CARD · T1.1

> **Task ID**：T1.1
> **状态**：📋 待开始
> **完成日期**：待定

## 一、Task 概要
...
"""
    with open(task_card_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return task_card_path


@pytest.fixture
def sample_topic_brief(temp_project_dir):
    """示例 TOPIC-BRIEF"""
    topic_brief_path = f"{temp_project_dir}/topics/N4-P1-T01/TOPIC-BRIEF.md"
    content = """# TOPIC-BRIEF · N4-P1-T01

> **状态**：📋 待开始

## 三、Task 执行记录

| Task ID | Task 名称 | 执行日期 | 状态 | 交付物 |
|---------|-----------|----------|------|--------|
| **T1.1** | Schema 定义 | 待定 | 📋 待开始 | - |
"""
    with open(topic_brief_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return topic_brief_path


@pytest.fixture
def sample_mission_board(temp_agent_dir):
    """示例 MISSION_BOARD"""
    mission_board_path = f"{temp_agent_dir}/MISSION_BOARD.md"
    content = """# MISSION_BOARD

## 一、当前状态总览

| 指标 | 状态 |
|---|---|
| 本周完成任务数 | **0** |

## 三、Task 跟踪

| Task ID | 所属 Topic | 状态 | 优先级 | 完成时间 |
|---------|-----------|------|--------|---------|
| **T1.1** | N4-P1-T01 | ⚪ 待启动 | P0 | 待定 |
"""
    with open(mission_board_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return mission_board_path


# ── 测试用例 ────────────────────────────────────────

def test_extract_topic_id():
    """测试 Task ID → Topic ID 映射"""
    assert extract_topic_id('T1.1') == 'N4-P1-T01'
    assert extract_topic_id('T2.1') == 'N4-P1-T02'
    assert extract_topic_id('T5.8') == 'N4-P1-T05'
    assert extract_topic_id('Phase1-Improvement-001') == 'N4-P1-T05-Improvement'
    assert extract_topic_id('UnknownTask') is None


def test_extract_project_id():
    """测试项目目录 → Project ID 映射"""
    assert extract_project_id('/path/to/ZT-P015_NUCLEUS-4-0') == 'ZT-P015'
    assert extract_project_id('/path/to/ZT-P009') == 'ZT-P009'
    assert extract_project_id('/unknown/path') == 'UNKNOWN'


def test_sync_task_card_pass(sample_task_card):
    """测试 Task-CARD 更新（pass）"""
    sync_task_card(sample_task_card, 'pass')
    
    with open(sample_task_card, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 验证状态更新
    assert '✅ 已完成' in content
    assert '2026-04-06' in content  # 完成日期


def test_sync_task_card_fail(sample_task_card):
    """测试 Task-CARD 更新（fail）"""
    # 先设置为 pass，再 fail
    sync_task_card(sample_task_card, 'pass')
    
    # 重新创建文件测试 fail
    content = """# TASK-CARD · T1.1

> **Task ID**：T1.1
> **状态**：📋 待开始
"""
    with open(sample_task_card, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # fail 不更新状态（仅记录）
    sync_task_card(sample_task_card, 'fail')
    
    with open(sample_task_card, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # fail 不改变状态为完成
    assert '✅ 已完成' not in content


def test_sync_topic_brief_pass(sample_topic_brief):
    """测试 TOPIC-BRIEF 更新"""
    sync_topic_brief(sample_topic_brief, 'T1.1', 'pass')
    
    with open(sample_topic_brief, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 验证 Task 状态更新
    assert '✅ 完成' in content
    assert '2026-04-06' in content


def test_sync_mission_board_pass(sample_mission_board):
    """测试 MISSION_BOARD 更新"""
    sync_mission_board(sample_mission_board, 'ZT-P015', 'T1.1', 'pass')
    
    with open(sample_mission_board, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 验证 Task 状态更新
    assert '✅ 完成' in content
    
    # 验证计数增加
    assert '本周完成任务数 | **1**' in content


def test_on_act_complete_full(
    temp_project_dir,
    temp_agent_dir,
    sample_cycle_unit,
    sample_task_card,
    sample_topic_brief,
    sample_mission_board
):
    """测试完整同步流程"""
    result = on_act_complete(
        sample_cycle_unit,
        temp_project_dir,
        temp_agent_dir
    )
    
    # 验证同步成功
    assert len(result['updated_files']) == 3
    assert len(result['errors']) == 0
    
    # 验证文件内容
    with open(sample_task_card, 'r', encoding='utf-8') as f:
        assert '✅ 已完成' in f.read()
    
    with open(sample_topic_brief, 'r', encoding='utf-8') as f:
        assert '✅ 完成' in f.read()
    
    with open(sample_mission_board, 'r', encoding='utf-8') as f:
        assert '✅ 完成' in f.read()


def test_on_act_complete_missing_task_id(temp_project_dir, temp_agent_dir):
    """测试缺少 task_id 的错误处理"""
    cycle_unit = {'id': 'test', 'check': {'verdict': 'pass'}}
    
    result = on_act_complete(cycle_unit, temp_project_dir, temp_agent_dir)
    
    # 应返回错误
    assert len(result['errors']) > 0
    assert '缺少 task_id' in result['errors'][0]


def test_on_act_complete_file_not_found(temp_project_dir, temp_agent_dir):
    """测试文件未找到的错误处理"""
    cycle_unit = {
        'task_id': 'NonExistent',
        'check': {'verdict': 'pass'}
    }
    
    result = on_act_complete(cycle_unit, temp_project_dir, temp_agent_dir)
    
    # 应返回错误（但不抛出异常）
    assert len(result['errors']) > 0
    assert 'Task-CARD 未找到' in result['errors'][0]


def test_atomic_write(sample_task_card):
    """测试原子写入"""
    # 多次写入验证完整性
    for i in range(5):
        content = f"""# TASK-CARD · T1.1

Version {i}
"""
        sync_task_card(sample_task_card, 'pass')
        
        # 验证文件存在且可读
        assert os.path.exists(sample_task_card)
        with open(sample_task_card, 'r', encoding='utf-8') as f:
            assert len(f.read()) > 0


# ── Coverage Report ────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=state_sync", "--cov-report=term-missing"])