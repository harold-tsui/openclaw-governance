#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态同步模块简单测试

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(__file__))

from state_sync import (
    on_act_complete,
    sync_task_card,
    sync_topic_brief,
    sync_mission_board,
    extract_topic_id,
    extract_project_id
)


def test_extract_topic_id():
    """测试 Task ID → Topic ID 映射"""
    print("Testing extract_topic_id...")
    assert extract_topic_id('T1.1') == 'N4-P1-T01'
    assert extract_topic_id('T2.1') == 'N4-P1-T02'
    assert extract_topic_id('T5.8') == 'N4-P1-T05'
    assert extract_topic_id('Phase1-Improvement-001') == 'N4-P1-T05-Improvement'
    assert extract_topic_id('UnknownTask') is None
    print("✅ extract_topic_id passed")


def test_extract_project_id():
    """测试项目目录 → Project ID 映射"""
    print("Testing extract_project_id...")
    assert extract_project_id('/path/to/ZT-P015_NUCLEUS-4-0') == 'ZT-P015'
    assert extract_project_id('/path/to/ZT-P009') == 'ZT-P009'
    assert extract_project_id('/unknown/path') == 'UNKNOWN'
    print("✅ extract_project_id passed")


def test_basic_functionality():
    """基本功能测试"""
    print("Testing basic functionality...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试文件
        task_card = f"{tmpdir}/T1.1_TASK-CARD.md"
        with open(task_card, 'w') as f:
            f.write("> **状态**：📋 待开始\n> **完成日期**：待定")
        
        # 测试同步
        sync_task_card(task_card, 'pass')
        
        # 验证结果
        with open(task_card, 'r') as f:
            content = f.read()
            assert '✅ 已完成' in content
        
        print("✅ basic functionality passed")


def main():
    """运行所有测试"""
    print("Running state_sync tests...\n")
    
    try:
        test_extract_topic_id()
        test_extract_project_id()
        test_basic_functionality()
        
        print("\n🎉 All tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)