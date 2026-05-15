#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
governance-hierarchy 核心实现

实现 Project/Topic 创建，自动生成对应 CycleUnit 实例。
基于 ARCH v1.4.3 §4.1 Skills 增强计划。

Author: 张铁 (CQO)
Date: 2026-04-11
"""

import os
import sys
import yaml
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# 导入 NUCLEUS CycleUnit
sys.path.append(os.path.join(os.path.dirname(__file__), "../../openclaw-governance-nucleus"))
from core.cycle_unit import create_cycle, load_cycle

# 导入 governance-config
sys.path.append(os.path.join(os.path.dirname(__file__), "../../openclaw-governance-config"))
from core.config import load_config, update_config, load_system, load_user


class HierarchyError(Exception):
    """层级操作异常基类"""
    pass


class ProjectNotFoundError(HierarchyError):
    """项目不存在"""
    pass


class NameDuplicateError(HierarchyError):
    """名称重复"""
    pass


class OwnerInvalidError(HierarchyError):
    """负责人无效"""
    pass


def _generate_id(scope: str) -> str:
    """
    生成唯一ID
    
    Args:
        scope: 粒度（project/topic/task）
    
    Returns:
        唯一ID
    """
    timestamp = int(datetime.now(timezone.utc).timestamp())
    random_suffix = uuid.uuid4().hex[:6]
    return f"{scope}-{timestamp}-{random_suffix}"


def create_project(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建新项目
    
    Args:
        params: 创建参数
            - name: 项目名称 (必填)
            - alias: 别名列表
            - description: 项目描述
            - owner: 项目所有者 Agent (必填)
            - members: 成员列表
            - tags: 标签列表
            - privacy_level: 隐私级别 (P1/P2, 默认P2)
            - source: 创建来源 (manual/task-card/system, 默认manual)
    
    Returns:
        创建结果，包含CycleUnit实例
    """
    # 校验必填字段
    required_fields = ['name', 'owner']
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    
    name = params['name']
    owner = params['owner']
    
    # 加载现有项目配置
    system_projects = load_system("projects")
    user_projects = load_user("projects")
    all_projects = {**system_projects, **user_projects}
    
    # 检查项目名是否重复
    for project_id, project in all_projects.items():
        if project['name'].lower().replace(" ", "") == name.lower().replace(" ", ""):
            raise NameDuplicateError(f"Project name already exists: {name}")
    
    # 校验owner是否是有效Agent
    agents = load_system("agents")
    if owner not in agents:
        raise OwnerInvalidError(f"Invalid owner agent: {owner}")
    
    # 生成项目ID
    max_id = 0
    for project_id in all_projects.keys():
        if project_id.startswith("ZT-P"):
            try:
                id_num = int(project_id.split("-")[1])
                if id_num > max_id:
                    max_id = id_num
            except:
                pass
    new_project_id = f"ZT-P{max_id + 1}"
    
    # 生成项目目录名
    dir_name = f"{new_project_id}_{name.replace(' ', '_')}"
    dir_path = f"10_Projects/{dir_name}/"
    
    # 创建目录
    os.makedirs(dir_path, exist_ok=True)
    
    # 创建 PROJECT-CHARTER.md
    charter_path = os.path.join(dir_path, "PROJECT-CHARTER.md")
    with open(charter_path, 'w', encoding='utf-8') as f:
        f.write(f"""# PROJECT-CHARTER · {name}

## 基本信息
- **项目ID**: {new_project_id}
- **项目名称**: {name}
- **项目描述**: {params.get('description', '')}
- **负责人**: {owner}
- **成员**: {', '.join(params.get('members', []))}
- **标签**: {', '.join(params.get('tags', []))}
- **隐私级别**: {params.get('privacy_level', 'P2')}
- **创建来源**: {params.get('source', 'manual')}
- **创建时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

## 目标
[填写项目目标]

## 范围
[填写项目范围]

## 验收标准
[填写验收标准]
""")
    
    # 保存项目配置
    new_project = {
        "id": new_project_id,
        "name": name,
        "alias": params.get('alias', []),
        "description": params.get('description', ''),
        "owner": owner,
        "members": params.get('members', []),
        "tags": params.get('tags', []),
        "privacy_level": params.get('privacy_level', 'P2'),
        "source": params.get('source', 'manual'),
        "dir_path": dir_path,
        "charter_path": charter_path,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "topics_count": 0,
        "completed_topics": 0
    }
    
    # 写入用户项目配置
    user_projects[new_project_id] = new_project
    update_config("user/user-projects.yaml", user_projects)
    
    # 生成 CycleUnit ID
    cycle_id = _generate_id("project")
    
    # 创建 Project 级 CycleUnit
    create_cycle(
        id=cycle_id,
        scope="project",
        task_card_id=new_project_id,
        initial_data={
            "plan": {
                "human_approval_required": True,  # Project 默认L3审核
                "review_window": "7d"
            },
            "task_card_path": charter_path
        }
    )
    
    # 加载生成的CycleUnit
    cycle_unit = load_cycle(cycle_id, "project")
    
    # 返回结果
    return {
        "status": "OK",
        "project_id": new_project_id,
        "dir_path": dir_path,
        "charter_path": charter_path,
        "review_level": "L3",
        "cycle_unit_id": cycle_id,
        "cycle_unit": cycle_unit,
        "next_action": "等待 Harold 审批"
    }


def create_topic(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建主题
    
    Args:
        params: 创建参数
            - project_id: 项目ID (必填)
            - name: 主题名称 (必填)
            - description: 主题描述
            - topic_pm: 主题负责人 (必填)
            - source: 创建来源 (manual/task-card/system, 默认manual)
    
    Returns:
        创建结果，包含CycleUnit实例
    """
    # 校验必填字段
    required_fields = ['project_id', 'name', 'topic_pm']
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    
    project_id = params['project_id']
    name = params['name']
    topic_pm = params['topic_pm']
    
    # 校验项目是否存在
    system_projects = load_system("projects")
    user_projects = load_user("projects")
    all_projects = {**system_projects, **user_projects}
    
    if project_id not in all_projects:
        raise ProjectNotFoundError(f"Project not found: {project_id}")
    
    project = all_projects[project_id]
    
    # 校验PM是否是有效Agent
    agents = load_system("agents")
    if topic_pm not in agents:
        raise OwnerInvalidError(f"Invalid topic PM: {topic_pm}")
    
    # 生成Topic ID
    # 获取当前项目下最大topic序号
    topic_dirs = [d for d in os.listdir(project['dir_path']) if os.path.isdir(os.path.join(project['dir_path'], d)) and d.startswith("T")]
    
    max_topic_num = 0
    for dir_name in topic_dirs:
        if dir_name.startswith("T"):
            try:
                num_part = dir_name.split("-")[0][1:]
                topic_num = int(num_part)
                if topic_num > max_topic_num:
                    max_topic_num = topic_num
            except:
                pass
    
    new_topic_num = max_topic_num + 1
    topic_id = f"T{new_topic_num:02d}-{name.replace(' ', '_')}"
    
    # 生成主题目录
    dir_path = os.path.join(project['dir_path'], f"{topic_id}/")
    os.makedirs(dir_path, exist_ok=True)
    
    # 创建 TOPIC-BRIEF.md
    brief_path = os.path.join(dir_path, "TOPIC-BRIEF.md")
    with open(brief_path, 'w', encoding='utf-8') as f:
        f.write(f"""# TOPIC-BRIEF · {name}

## 基本信息
- **主题ID**: {topic_id}
- **所属项目**: {project_id} - {project['name']}
- **主题描述**: {params.get('description', '')}
- **负责人**: {topic_pm}
- **创建来源**: {params.get('source', 'manual')}
- **创建时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

## 目标
[填写主题目标]

## 范围
[填写主题范围]

## 任务列表
| 任务ID | 任务名称 | 状态 | 优先级 | 负责人 | 完成时间 |
|--------|----------|------|--------|--------|----------|
|        |          |      |        |        |          |

## 验收标准
[填写验收标准]
""")
    
    # 更新项目topics_count
    project['topics_count'] += 1
    if project_id in user_projects:
        user_projects[project_id] = project
        update_config("user/user-projects.yaml", user_projects)
    else:
        system_projects[project_id] = project
        update_config("system/system-projects.yaml", system_projects)
    
    # 生成 CycleUnit ID
    cycle_id = _generate_id("topic")
    
    # 创建 Topic 级 CycleUnit
    create_cycle(
        id=cycle_id,
        scope="topic",
        task_card_id=topic_id,
        initial_data={
            "plan": {
                "human_approval_required": False,  # Topic 默认L2审核
                "review_window": "48h"
            },
            "task_card_path": brief_path
        }
    )
    
    # 加载生成的CycleUnit
    cycle_unit = load_cycle(cycle_id, "topic")
    
    # 返回结果
    return {
        "status": "OK",
        "topic_id": topic_id,
        "dir_path": dir_path,
        "brief_path": brief_path,
        "review_level": "L2",
        "cycle_unit_id": cycle_id,
        "cycle_unit": cycle_unit,
        "next_action": "创建 Task"
    }


# 导出公共接口
__all__ = [
    'create_project',
    'create_topic',
    'HierarchyError',
    'ProjectNotFoundError',
    'NameDuplicateError',
    'OwnerInvalidError'
]
