#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端验证：状态同步机制

模拟 Task 完成，验证状态文件自动更新。

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import tempfile
import yaml
from datetime import datetime, timezone


def main():
    """端到端验证"""
    print("🧪 端到端验证：状态同步机制")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建项目结构
        project_dir = f"{tmpdir}/ZT-P015_NUCLEUS-4-0"
        agent_dir = f"{tmpdir}/cqo"
        
        os.makedirs(f"{project_dir}/tasks")
        os.makedirs(f"{project_dir}/topics/N4-P1-T01")
        os.makedirs(agent_dir)
        
        # 创建测试文件
        task_card_path = f"{project_dir}/tasks/T1.1_TASK-CARD.md"
        with open(task_card_path, 'w') as f:
            f.write("""# TASK-CARD · T1.1

> **Task ID**：T1.1
> **状态**：📋 待开始
> **完成日期**：待定

## 一、Task 概要
...
""")
        
        topic_brief_path = f"{project_dir}/topics/N4-P1-T01/TOPIC-BRIEF.md"
        with open(topic_brief_path, 'w') as f:
            f.write("""# TOPIC-BRIEF · N4-P1-T01

> **状态**：📋 待开始

## 三、Task 执行记录

| Task ID | Task 名称 | 执行日期 | 状态 | 交付物 |
|---------|-----------|----------|------|--------|
| **T1.1** | Schema 定义 | 待定 | 📋 待开始 | - |
""")
        
        mission_board_path = f"{agent_dir}/MISSION_BOARD.md"
        with open(mission_board_path, 'w') as f:
            f.write("""# MISSION_BOARD

## 一、当前状态总览

| 指标 | 状态 |
|---|---|
| 本周完成任务数 | **0** |

## 三、Task 跟踪

| Task ID | 所属 Topic | 状态 | 优先级 | 完成时间 |
|---------|-----------|------|--------|---------|
| **T1.1** | N4-P1-T01 | ⚪ 待启动 | P0 | 待定 |
""")
        
        # 创建 CycleUnit
        cycle_unit = {
            'id': 'task-20260406T150000Z',
            'task_id': 'T1.1',
            'check': {
                'verdict': 'pass',
                'evidence': ['test_passed']
            },
            'act': {
                'decision': 'maintain'
            }
        }
        
        cycle_path = f"{project_dir}/cycles/task/task-20260406T150000Z.yaml"
        os.makedirs(os.path.dirname(cycle_path), exist_ok=True)
        with open(cycle_path, 'w') as f:
            yaml.dump(cycle_unit, f)
        
        # 导入状态同步模块
        import sys
        sys.path.insert(0, '/Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0/modules')
        from state_sync import on_act_complete
        
        # 执行同步
        print("🔄 执行状态同步...")
        result = on_act_complete(cycle_unit, project_dir, agent_dir)
        
        # 验证结果
        print(f"✅ 更新文件: {len(result['updated_files'])}")
        for f in result['updated_files']:
            print(f"   - {os.path.basename(f)}")
        
        if result['errors']:
            print(f"❌ 错误: {len(result['errors'])}")
            for e in result['errors']:
                print(f"   - {e}")
            return False
        
        # 验证内容
        with open(task_card_path, 'r') as f:
            if '✅ 已完成' not in f.read():
                print("❌ Task-CARD 未正确更新")
                return False
        
        with open(topic_brief_path, 'r') as f:
            if '✅ 完成' not in f.read():
                print("❌ TOPIC-BRIEF 未正确更新")
                return False
        
        with open(mission_board_path, 'r') as f:
            content = f.read()
            if '✅ 完成' not in content or '本周完成任务数 | **1**' not in content:
                print("❌ MISSION_BOARD 未正确更新")
                return False
        
        print("🎉 端到端验证成功！")
        return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)