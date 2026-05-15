#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
governance-task 核心实现
任务管理全流程，支持Task-Card v3.1规范
基于ARCH v1.4.3 §4.1 Skills增强计划
Author: 张铁 (CQO)
Date: 2026-04-11
"""
import os
import sys
import yaml
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
# 导入依赖
sys.path.append(os.path.join(os.path.dirname(__file__), "../../openclaw-governance-config"))
from core.config import load_config, update_config, load_system, load_user
sys.path.append(os.path.join(os.path.dirname(__file__), "../../openclaw-governance-delegation"))
from core.delegation import check_authorization
sys.path.append(os.path.join(os.path.dirname(__file__), "../../openclaw-governance-nucleus"))
from core.cycle_unit import create_cycle
class TaskError(Exception):
    """任务操作异常基类"""
    pass
class ProjectNotFoundError(TaskError):
    """项目不存在"""
    pass
class ProjectDirNotFoundError(TaskError):
    """项目目录不存在"""
    pass
class AssigneeMissingError(TaskError):
    """未指定指派人"""
    pass
class PICMissingError(TaskError):
    """未指定Task PIC"""
    pass
class PathInvalidError(TaskError):
    """路径格式错误"""
    pass
class NotAuthorizedError(TaskError):
    """无权限"""
    pass
class StateInvalidError(TaskError):
    """状态无效"""
    pass
class ReviewDeniedError(TaskError):
    """无权限验收"""
    pass
class ReviewLevelMismatchError(TaskError):
    """验收人级别不匹配"""
    pass
class CloseDeniedError(TaskError):
    """无权限关闭"""
    pass
class ReviewIncompleteError(TaskError):
    """验收未完成"""
    pass
class IssueNotResolvedError(TaskError):
    """关联Issue未解决"""
    pass
class KnowledgeCaptureIncompleteError(TaskError):
    """知识沉淀未完成"""
    pass
# 工具函数
def get_project_config(project_id: str) -> Dict[str, Any]:
    """
    查询项目配置
    Args:
        project_id: 项目ID
    Returns:
        项目配置字典
    Raises:
        ProjectNotFoundError: 项目不存在
    """
    system_projects = load_system("projects")
    user_projects = load_user("projects")
    # 合并配置，user优先
    all_projects = {**system_projects, **user_projects}
    if project_id not in all_projects:
        raise ProjectNotFoundError(f"Project not found: {project_id}")
    project = all_projects[project_id]
    # 检查目录存在
    if not os.path.exists(project["dir_path"]):
        raise ProjectDirNotFoundError(f"Project directory not found: {project['dir_path']}")
    return project
def _read_task_card(task_card_path: str) -> Dict[str, Any]:
    """读取Task-Card内容（简化实现，实际需要解析Markdown结构）"""
    if not os.path.exists(task_card_path):
        raise TaskError(f"Task card not found: {task_card_path}")
    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 简化解析，实际需要按TMPL-TASK-CARD v3.1结构解析各部分
    task_data = {
        "content": content,
        "state": "[ ]",
        "assignee": "",
        "task_pic": "",
        "deliverables": [],
        "related_issues": []
    }
    # 解析当前状态
    state_match = re.search(r"§七\.1 当前状态.*?(\[[^\]]+\])", content, re.DOTALL)
    if state_match:
        task_data["state"] = state_match.group(1)
    # 解析指派人
    assignee_match = re.search(r"§一\.3 指派人.*?(\w+)", content, re.DOTALL)
    if assignee_match:
        task_data["assignee"] = assignee_match.group(1)
    # 解析Task PIC
    pic_match = re.search(r"§一\.2 Task PIC.*?(\w+)", content, re.DOTALL)
    if pic_match:
        task_data["task_pic"] = pic_match.group(1)
    return task_data
def _write_task_card(task_card_path: str, content: str) -> None:
    """原子性写入Task-Card"""
    tmp_path = task_card_path + ".tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    os.rename(tmp_path, task_card_path)
def _update_task_state(task_card_path: str, new_state: str) -> None:
    """更新Task状态"""
    task_data = _read_task_card(task_card_path)
    new_content = re.sub(
        r"(§七\.1 当前状态.*?)\[[^\]]+\]",
        f"\\g<1>{new_state}",
        task_data["content"],
        flags=re.DOTALL
    )
    _write_task_card(task_card_path, new_content)
# 核心函数实现
def create_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建任务
    Args:
        params: 创建参数
            - task_title: 任务标题（必填）
            - task_type: 任务类型（必填）
            - project_id: 项目ID（必填）
            - topic_id: Topic ID（必填）
            - assignee: 指派人（必填）
            - task_pic: Task PIC（必填）
            - reviewer: 验收人
            - priority: 优先级（P0-P3）
            - review_level: Review级别（L0-L3）
            - task_goal: 任务目标
            - deliverables: 交付物列表
    Returns:
        创建结果
    """
    required_fields = ["task_title", "task_type", "project_id", "topic_id", "assignee", "task_pic"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    project_id = params["project_id"]
    topic_id = params["topic_id"]
    # 查询项目配置
    project = get_project_config(project_id)
    dir_path = project["dir_path"]
    # 校验路径合法性
    if "60_Agents/" in dir_path or not ("10_Projects/" in dir_path or ".system/" in dir_path):
        raise PathInvalidError(f"Invalid project path: {dir_path}")
    # 生成Task ID
    topic_dir = os.path.join(dir_path, topic_id)
    tasks_dir = os.path.join(topic_dir, "tasks")
    os.makedirs(tasks_dir, exist_ok=True)
    # 查找最大Task编号
    existing_tasks = [f for f in os.listdir(tasks_dir) if f.startswith("TASK-CARD-") and f.endswith(".md")]
    max_task_no = 0
    for task_file in existing_tasks:
        match = re.search(r"-T(\d+)\.md", task_file)
        if match:
            no = int(match.group(1))
            if no > max_task_no:
                max_task_no = no
    task_no = max_task_no + 1
    task_id = f"{project_id}-{topic_id}-T{task_no:02d}"
    # 生成交付物目录
    deliverable_dir = os.path.join(topic_dir, "deliverables")
    os.makedirs(deliverable_dir, exist_ok=True)
    # 生成Task-Card内容（简化版，实际需要完整TMPL-TASK-CARD v3.1）
    task_card_content = f"""# TASK-CARD {task_id} - {params['task_title']}
## §一 基本信息
### §一.1 Task ID: {task_id}
### §一.2 Task PIC: {params['task_pic']}
### §一.3 指派人: {params['assignee']}
### §一.4 任务类型: {params['task_type']}
### §一.5 优先级: {params.get('priority', 'P2')}
### §一.6 Review级别: {params.get('review_level', 'L2')}
### §一.7 任务目标: {params.get('task_goal', '')}
## §二 归属信息
### §二.1 归属Project: {project_id}
### §二.2 归属Topic: {topic_id}
## §三 进度计划
## §四 交付物定义
| 交付物名称 | 文件名 | 格式 | Review级别 | 验收标准 | 状态 |
|---|---|---|---|---|---|
"""
    # 添加交付物行
    deliverables = params.get("deliverables", [])
    for d in deliverables:
        name = d['name']
        filename = d['filename']
        format = d.get('format', '.md')
        review_level = d.get('review_level', params.get('review_level', 'L2'))
        criteria = d.get('acceptance_criteria', '')
        task_card_content += f"| {name} | {filename} | {format} | {review_level} | {criteria} | ☐ |\n"
    task_card_content += f"""
## §五 依赖与约束
## §六 前置条件
## §七 运行时状态
### §七.1 当前状态: [ ]
### §七.2 状态变更记录
- {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}: 任务创建
## §八 评审记录
## §九 知识沉淀
"""
    # 写入Task-Card
    task_card_filename = f"TASK-CARD-{task_id}.md"
    task_card_path = os.path.join(tasks_dir, task_card_filename)
    with open(task_card_path, 'w', encoding='utf-8') as f:
        f.write(task_card_content)
    # 创建CycleUnit
    create_cycle(
        id=task_id,
        scope="task",
        task_card_id=task_id,
        initial_data={
            "task_card_path": task_card_path,
            "plan": {
                "human_approval_required": params.get('review_level', 'L2') == 'L3',
                "review_level": params.get('review_level', 'L2')
            }
        }
    )
    # 更新MISSION_BOARD（简化，实际需要调用对应Agent的MISSION_BOARD更新逻辑）
    # ...
    # 通知Task PIC
    # ...
    return {
        "status": "OK",
        "task_id": task_id,
        "task_card_path": task_card_path,
        "state": "[ ]",
        "next_action": "等待 Task PIC 接收"
    }
def accept_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    接收任务
    Args:
        params: 参数
            - task_id: 任务ID（必填）
            - task_pic: Task PIC（必填）
    Returns:
        接收结果
    """
    required_fields = ["task_id", "task_pic"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    task_id = params["task_id"]
    task_pic = params["task_pic"]
    # 查找Task-Card路径（简化，实际需要通过project/topic查找）
    # 此处简化，假设知道路径
    # 实际需要先解析task_id获取project_id/topic_id，然后查询项目配置
    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    # 读取Task-Card
    task_data = _read_task_card(task_card_path)
    # 校验权限
    if task_data["task_pic"] != task_pic:
        raise NotAuthorizedError(f"Only task PIC {task_data['task_pic']} can accept this task")
    # 校验状态
    if task_data["state"] != "[ ]":
        raise StateInvalidError(f"Task state is {task_data['state']}, must be [ ] to accept")
    # 更新状态为[P]
    _update_task_state(task_card_path, "[P]")
    # 更新MISSION_BOARD
    # ...
    # 通知指派人
    # ...
    return {
        "status": "OK",
        "state": "[P]",
        "next_action": "开始执行，更新 Task-Card Zone B §七"
    }
def reject_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    拒绝任务
    Args:
        params: 参数
            - task_id: 任务ID（必填）
            - task_pic: Task PIC（必填）
            - reason: 拒绝原因
    Returns:
        拒绝结果
    """
    required_fields = ["task_id", "task_pic", "reason"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    task_id = params["task_id"]
    task_pic = params["task_pic"]
    reason = params["reason"]
    # 查找Task-Card路径
    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    # 读取Task-Card
    task_data = _read_task_card(task_card_path)
    # 校验权限
    if task_data["task_pic"] != task_pic:
        raise NotAuthorizedError(f"Only task PIC {task_data['task_pic']} can reject this task")
    # 校验状态
    if task_data["state"] != "[ ]":
        raise StateInvalidError(f"Task state is {task_data['state']}, must be [ ] to reject")
    # 记录拒绝原因到Task-Card
    new_content = task_data["content"] + f"\n### §七.2 拒绝记录\n- {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}: 拒绝原因: {reason}\n"
    _write_task_card(task_card_path, new_content)
    # 通知指派人重新分派
    # ...
    return {
        "status": "OK",
        "state": "[ ]",
        "next_action": "已通知指派人重新分派"
    }
def create_issue_ticket(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建问题单
    Args:
        params: 参数
            - issue_title: 问题标题（必填）
            - issue_description: 问题描述（必填）
            - issue_severity: 严重级别（P0-P3）
            - issue_reporter: 提出人（必填）
            - task_pic: Task PIC（必填）
            - project_id: 项目ID（必填）
            - source_task_id: 源任务ID
    Returns:
        创建结果
    """
    required_fields = ["issue_title", "issue_description", "issue_reporter", "task_pic", "project_id"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    # 创建Issue Task
    issue_params = {
        "task_title": params["issue_title"],
        "task_type": "Issue",
        "project_id": params["project_id"],
        "topic_id": params.get("topic_id", "T00"),  # 默认放入T00临时Topic
        "assignee": params["issue_reporter"],
        "task_pic": params["task_pic"],
        "reviewer": params["issue_reporter"],
        "priority": params.get("issue_severity", "P2"),
        "review_level": "L3",  # Issue默认L3
        "task_goal": params["issue_description"],
        "deliverables": [{
            "name": "问题修复报告",
            "filename": f"ISSUE-REPORT-{params.get('source_task_id', 'unknown')}.md",
            "format": ".md",
            "review_level": "L3",
            "acceptance_criteria": "问题修复验证通过"
        }]
    }
    result = create_task(issue_params)
    issue_task_id = result["task_id"]
    # 阻塞源任务
    if "source_task_id" in params:
        source_task_id = params["source_task_id"]
        # 解析源任务路径
        parts = source_task_id.split("-")
        source_project_id = "-".join(parts[:2])
        source_topic_id = parts[2]
        try:
            source_project = get_project_config(source_project_id)
            source_task_card_path = os.path.join(source_project["dir_path"], source_topic_id, "tasks", f"TASK-CARD-{source_task_id}.md")
            if os.path.exists(source_task_card_path):
                # 更新源任务状态为[?]阻塞
                _update_task_state(source_task_card_path, "[?]")
                # 添加阻塞原因
                source_data = _read_task_card(source_task_card_path)
                new_content = source_data["content"] + f"\n### §七.2 阻塞记录\n- {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}: 阻塞原因: 关联Issue {issue_task_id}\n"
                _write_task_card(source_task_card_path, new_content)
        except:
            # 源任务不存在时忽略错误
            pass
    return {
        "status": "OK",
        "task_id": issue_task_id,
        "state": "[ ]",
        "source_task_state": "[?]" if "source_task_id" in params else None,
        "next_action": "等待 Task PIC 接收，通知提出人已创建"
    }
def review_deliverable(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    验收交付物
    Args:
        params: 参数
            - task_id: 任务ID（必填）
            - deliverable_name: 交付物名称（必填）
            - reviewer: 验收人（必填）
            - review_result: pass/fail/reject（必填）
            - feedback: 反馈内容
    Returns:
        验收结果
    """
    required_fields = ["task_id", "deliverable_name", "reviewer", "review_result"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    review_result = params["review_result"]
    if review_result not in ["pass", "fail", "reject"]:
        raise ValueError(f"Invalid review_result: {review_result}, must be pass/fail/reject")
    task_id = params["task_id"]
    # 查找Task-Card路径
    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    # 读取Task-Card
    task_data = _read_task_card(task_card_path)
    # 校验状态必须为[V]
    if task_data["state"] != "[V]":
        raise StateInvalidError(f"Task state is {task_data['state']}, must be [V] to review")
    # 校验验收权限
    auth_params = {
        "actor": params["reviewer"],
        "operation": "review_deliverable",
        "target": task_id
    }
    auth_result = check_authorization(auth_params)
    if not auth_result["authorized"]:
        raise ReviewDeniedError(f"Reviewer {params['reviewer']} is not authorized to review this task")
    # 更新交付物状态
    new_content = task_data["content"]
    if review_result == "pass":
        # 更新为✅
        new_content = re.sub(
            rf"(| {params['deliverable_name']}.*?\| )☐",
            f"\\1✅",
            new_content
        )
    else:
        # 更新为❌
        new_content = re.sub(
            rf"(| {params['deliverable_name']}.*?\| )☐",
            f"\\1❌",
            new_content
        )
    # 添加评审记录到§八
    new_content += f"\n### §八.1 评审记录\n- {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}: 评审人: {params['reviewer']}, 结果: {review_result}\n  反馈: {params.get('feedback', '')}\n"
    _write_task_card(task_card_path, new_content)
    # 状态更新
    new_state = "[V]"
    if review_result in ["fail", "reject"]:
        # 打回重新执行，状态改为[P]
        new_state = "[P]"
        _update_task_state(task_card_path, "[P]")
    # 通知Task PIC
    # ...
    return {
        "status": "OK",
        "state": new_state,
        "review_result": review_result,
        "next_action": "验收通过，等待关闭" if review_result == "pass" else "交付物打回，重新修订"
    }
def verify_task_closed(task_id: str) -> Dict[str, Any]:
    """
    验证任务是否满足关闭条件
    Args:
        task_id: 任务ID
    Returns:
        验证结果
    """
    # 查找Task-Card路径
    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    # 读取Task-Card
    task_data = _read_task_card(task_card_path)
    # 检查状态必须为[V]
    if task_data["state"] != "[V]":
        raise StateInvalidError(f"E_STATE_INVALID: 当前状态为 {task_data['state']}，需为 [V]")
    # 检查所有交付物状态为✅
    # 使用更精确的正则表达式匹配交付物状态列
    deliverable_match = re.findall(r"\|.*?\|.*?\|.*?\|.*?\|.*?\|\s*([☐✅❌])\s*\|", task_data["content"])
    deliverable_count = 0
    passed_count = 0
    for match in deliverable_match:
        if match.strip() in ["☐", "✅", "❌"]:
            deliverable_count += 1
            if match.strip() == "✅":
                passed_count += 1
    if deliverable_count > 0 and passed_count < deliverable_count:
        raise ReviewIncompleteError(f"E_REVIEW_INCOMPLETE: {deliverable_count - passed_count} 个交付物未验收通过")
    # 检查关联Issue全部为[x]（简化实现）
    issue_match = re.findall(r"关联Issue.*?(\[[xX]\])", task_data["content"], re.DOTALL)
    for issue_state in issue_match:
        if issue_state.lower() != "[x]":
            raise IssueNotResolvedError(f"E_ISSUE_NOT_RESOLVED: 存在未关闭的关联 Issue")
    return {
        "verified": True,
        "task_id": task_id,
        "deliverables_checked": deliverable_count,
        "issues_checked": len(issue_match)
    }
def close_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    关闭任务
    Args:
        params: 参数
            - task_id: 任务ID（必填）
            - closed_by: 关闭人（必填）
    Returns:
        关闭结果
    """
    required_fields = ["task_id", "closed_by"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    task_id = params["task_id"]
    closed_by = params["closed_by"]
    # 查找Task-Card路径
    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    # 读取Task-Card
    task_data = _read_task_card(task_card_path)
    # 校验权限：关闭人必须等于指派人
    if task_data["assignee"] != closed_by:
        raise CloseDeniedError(f"E_CLOSE_DENIED: 只有指派人 {task_data['assignee']} 可以关闭此任务")
    # 验证关闭条件
    verify_result = verify_task_closed(task_id)
    # 更新状态为[x]并添加知识沉淀内容
    # 先更新状态
    task_data = _read_task_card(task_card_path)  # 重新读取最新内容
    new_content = re.sub(
        r"(§七\.1 当前状态.*?)\[[^\]]+\]",
        f"\\g<1>[x]",
        task_data["content"],
        flags=re.DOTALL
    )
    # 然后添加知识沉淀
    new_content += f"\n### §九 知识沉淀\n沉淀状态: ⏳ pending\n知识沉淀截止时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
    _write_task_card(task_card_path, new_content)
    # 更新MISSION_BOARD到已完成区
    # ...
    # 计算知识沉淀截止时间（3个工作日）
    from datetime import timedelta
    deadline = datetime.now(timezone.utc) + timedelta(days=3)
    deadline_str = deadline.strftime('%Y-%m-%d')
    return {
        "status": "OK",
        "state": "[x]",
        "closed_at": datetime.now(timezone.utc).isoformat(),
        "zone_c_triggered": True,
        "knowledge_capture_deadline": deadline_str,
        "next_action": "知识沉淀宽限期 3 个工作日，银月 Weekly Review 核查"
    }
def archive_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    归档任务
    Args:
        params: 参数
            - task_id: 任务ID（必填）
            - archived_by: 归档人（必填）
    Returns:
        归档结果
    """
    required_fields = ["task_id", "archived_by"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    task_id = params["task_id"]
    archived_by = params["archived_by"]
    # 查找Task-Card路径
    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    # 读取Task-Card
    task_data = _read_task_card(task_card_path)
    # 校验状态必须为[x]
    if task_data["state"] != "[x]":
        raise StateInvalidError(f"Task state is {task_data['state']}, must be [x] to archive")
    # 检查知识沉淀是否完成
    if "沉淀状态: ⏳ pending" in task_data["content"]:
        raise KnowledgeCaptureIncompleteError(f"知识沉淀未完成，不可归档")
    # 创建归档目录
    archive_dir = os.path.join(project["dir_path"], topic_id, "tasks", "archive")
    os.makedirs(archive_dir, exist_ok=True)
    # 生成归档文件名
    version = 1
    while True:
        archive_filename = f"TASK-CARD-{task_id}_v{version}.md"
        archive_path = os.path.join(archive_dir, archive_filename)
        if not os.path.exists(archive_path):
            break
        version += 1
    # 复制文件到归档目录
    with open(task_card_path, 'r', encoding='utf-8') as src:
        content = src.read()
    with open(archive_path, 'w', encoding='utf-8') as dst:
        dst.write(content + f"\n\n## 归档记录\n- 归档人: {archived_by}\n- 归档时间: {datetime.now(timezone.utc).isoformat()}\n- 版本: v{version}\n")
    # 更新Task-Card状态为[archived]
    _update_task_state(task_card_path, "[archived]")
    # 从MISSION_BOARD移除
    # ...
    # 更新TOPIC-BRIEF
    # ...
    return {
        "status": "OK",
        "state": "[archived]",
        "archive_path": archive_path,
        "archived_at": datetime.now(timezone.utc).isoformat()
    }
# 导出公共接口
__all__ = [
    "get_project_config",
    "create_task",
    "accept_task",
    "reject_task",
    "create_issue_ticket",
    "review_deliverable",
    "verify_task_closed",
    "close_task",
    "archive_task",
    "TaskError",
    "ProjectNotFoundError",
    "ProjectDirNotFoundError",
    "AssigneeMissingError",
    "PICMissingError",
    "PathInvalidError",
    "NotAuthorizedError",
    "StateInvalidError",
    "ReviewDeniedError",
    "ReviewLevelMismatchError",
    "CloseDeniedError",
    "ReviewIncompleteError",
    "IssueNotResolvedError",
    "KnowledgeCaptureIncompleteError"
]
