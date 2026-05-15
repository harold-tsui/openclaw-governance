#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态文件自动同步模块

在 Act 阶段完成时，自动触发状态文件同步更新。
覆盖 Task/Topic/Project/Agent 四层状态文件。

Author: 张铁 (CQO)
Version: 1.0
Date: 2026-04-06
"""

import os
import re
import yaml
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path


class StateSyncError(Exception):
    """状态同步异常基类"""
    pass


class FileNotFoundError(StateSyncError):
    """状态文件未找到"""
    pass


class ParseError(StateSyncError):
    """状态文件解析错误"""
    pass


def on_act_complete(cycle_unit: Dict[str, Any], 
                    project_dir: str,
                    agent_dir: str) -> Dict[str, Any]:
    """
    Act 完成时触发状态同步
    
    Args:
        cycle_unit: 当前 CycleUnit 数据
        project_dir: 项目目录路径
        agent_dir: Agent 工作目录路径
        
    Returns:
        sync_result: 同步结果
            - updated_files: 更新的文件列表
            - errors: 错误列表
    """
    updated_files = []
    errors = []

    # 获取 Task ID（schema 字段名为 task_card_id，兼容旧 task_id）
    task_id = cycle_unit.get('task_card_id') or cycle_unit.get('task_id')
    if not task_id:
        errors.append("CycleUnit 缺少 task_card_id")
        return {"updated_files": updated_files, "errors": errors}

    # 获取 Act 结果
    verdict = cycle_unit.get('check', {}).get('verdict')

    # 1. 更新 Task-CARD
    # 优先从 CycleUnit.plan.task_card_path 或顶层 task_card_path 读取精确路径
    try:
        task_card_path = (
            (cycle_unit.get('plan') or {}).get('task_card_path')
            or cycle_unit.get('task_card_path')
            or f"{project_dir}/tasks/{task_id}_TASK-CARD.md"  # 降级：按规则推断
        )
        if os.path.exists(task_card_path):
            sync_task_card(task_card_path, verdict)
            updated_files.append(task_card_path)
        else:
            errors.append(f"Task-CARD 未找到: {task_card_path}")
    except Exception as e:
        errors.append(f"Task-CARD 更新失败: {e}")
    
    # 2. 更新 TOPIC-BRIEF
    try:
        # 优先从 CycleUnit metadata 读取 topic_id
        topic_id = cycle_unit.get('metadata', {}).get('topic_id') or extract_topic_id(task_id)
        if topic_id:
            topic_brief_path = f"{project_dir}/topics/{topic_id}/TOPIC-BRIEF.md"
            if os.path.exists(topic_brief_path):
                sync_topic_brief(topic_brief_path, task_id, verdict)
                updated_files.append(topic_brief_path)
    except Exception as e:
        errors.append(f"TOPIC-BRIEF 更新失败: {e}")
    
    # 3. 更新 MISSION_BOARD
    try:
        mission_board_path = f"{agent_dir}/MISSION_BOARD.md"
        if os.path.exists(mission_board_path):
            # 从 project_dir 提取 project_id
            project_id = extract_project_id(project_dir)
            sync_mission_board(mission_board_path, project_id, task_id, verdict)
            updated_files.append(mission_board_path)
    except Exception as e:
        errors.append(f"MISSION_BOARD 更新失败: {e}")
    
    return {"updated_files": updated_files, "errors": errors}


def sync_task_card(task_card_path: str, verdict: str) -> bool:
    """
    更新 Task-CARD 状态
    
    Args:
        task_card_path: Task-CARD 文件路径
        verdict: Act 结果（pass/fail）
        
    Returns:
        True if success
    """
    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新状态
    if verdict == 'pass':
        new_status = "✅ 已完成"
        completion_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # 更新状态行
        content = re.sub(
            r'> \*\*状态\*\*：[^\n]+',
            f'> **状态**：{new_status}',
            content
        )
        
        # 更新完成日期
        content = re.sub(
            r'> \*\*完成日期\*\*：[^\n]+',
            f'> **完成日期**：{completion_date}',
            content
        )
    
    # 原子写入
    write_atomic(task_card_path, content)
    return True


def sync_topic_brief(topic_brief_path: str, task_id: str, verdict: str) -> bool:
    """
    更新 TOPIC-BRIEF Task 进度
    
    Args:
        topic_brief_path: TOPIC-BRIEF 文件路径
        task_id: 完成的 Task ID
        verdict: Act 结果
        
    Returns:
        True if success
    """
    with open(topic_brief_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新 Task 状态
    if verdict == 'pass':
        completion_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # 在 Task 执行记录表格中更新状态
        # 格式：| **{task_id}** | 名称 | 日期 | 📋 状态 | 交付物 |
        content = re.sub(
            rf'(\| \*\*{task_id}\*\* \|[^|]+\|[^|]+\|) 📋 [^|]+ (\|)',
            f'\\1 ✅ 完成 {completion_date} \\2',
            content
        )
    
    write_atomic(topic_brief_path, content)
    return True


def sync_mission_board(mission_board_path: str, 
                       project_id: str,
                       task_id: str,
                       verdict: str) -> bool:
    """
    更新 MISSION_BOARD §一~§三
    
    Args:
        mission_board_path: MISSION_BOARD 文件路径
        project_id: 项目 ID
        task_id: Task ID
        verdict: Act 结果
        
    Returns:
        True if success
    """
    with open(mission_board_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if verdict == 'pass':
        completion_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # 更新 §三 Task 跟踪
        # 格式：| **{task_id}** | 所属 Topic | ⚪ 状态 | 优先级 | 完成时间 |
        content = re.sub(
            rf'(\| \*\*{task_id}\*\* \|[^|]+\|) ⚪ [^|]+ (\|[^|]+\|)',
            f'\\1 ✅ 完成 {completion_date} \\2',
            content
        )
        
        # 更新 §一 状态总览 - 本周完成任务数
        # 增加计数（需要解析当前值）
        match = re.search(r'本周完成任务数 \| \*\*(\d+)\*\*', content)
        if match:
            current_count = int(match.group(1))
            new_count = current_count + 1
            content = re.sub(
                r'本周完成任务数 \| \*\*\d+\*\*',
                f'本周完成任务数 | **{new_count}**',
                content
            )
    
    write_atomic(mission_board_path, content)
    return True


def write_atomic(file_path: str, content: str) -> None:
    """
    原子写入文件
    
    Args:
        file_path: 文件路径
        content: 文件内容
    """
    # 写入临时文件
    tmp_path = f"{file_path}.tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 原子替换
    os.replace(tmp_path, file_path)


def extract_topic_id(task_id: str) -> Optional[str]:
    """
    从 Task ID 推断 Topic ID（通用规则）

    优先级：
    1. CycleUnit.metadata.topic_id（由 on_act_complete 调用方注入）
    2. Task ID 前缀规则（通用：T{n}.x → topic 序号）

    Args:
        task_id: Task ID（如 T1.1、ZT-P015-T02-001、T2.1）

    Returns:
        Topic ID 或 None（无法推断时）
    """
    if not task_id:
        return None

    # 通用规则：T{topic}.{sub} 格式，提取 topic 部分
    # 例：T1.1 → topic=1，T3.2 → topic=3
    import re
    m = re.match(r'^T(\d+)\.\d+$', task_id)
    if m:
        return f"T{m.group(1).zfill(2)}"

    # ZT-PXXX-T{n}-{seq} 格式
    m = re.match(r'^(ZT-P\d+)-T(\d+)-', task_id)
    if m:
        return f"{m.group(1)}-T{m.group(2).zfill(2)}"

    return None


def extract_project_id(project_dir: str) -> str:
    """
    从项目目录提取 Project ID
    
    Args:
        project_dir: 项目目录路径
        
    Returns:
        Project ID（如 ZT-P015）
    """
    # 从路径中提取
    match = re.search(r'ZT-P\d+', project_dir)
    if match:
        return match.group(0)
    return "UNKNOWN"


# CLI 接口
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='状态文件自动同步')
    parser.add_argument('--cycle-unit', required=True, help='CycleUnit YAML 文件路径')
    parser.add_argument('--project-dir', required=True, help='项目目录路径')
    parser.add_argument('--agent-dir', required=True, help='Agent 工作目录路径')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    
    args = parser.parse_args()
    
    # 加载 CycleUnit
    with open(args.cycle_unit, 'r', encoding='utf-8') as f:
        cycle_unit = yaml.safe_load(f)
    
    # 执行同步
    result = on_act_complete(cycle_unit, args.project_dir, args.agent_dir)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"✅ 更新文件: {len(result['updated_files'])}")
        for f in result['updated_files']:
            print(f"   - {f}")
        if result['errors']:
            print(f"❌ 错误: {len(result['errors'])}")
            for e in result['errors']:
                print(f"   - {e}")