#!/usr/bin/env python3
"""
task_functions.py - Task 管理核心函数

Usage:
    python task_functions.py --action create_task --task-id "ZT-P008-T06-T01"
    python task_functions.py --test
    python task_functions.py --help

来源：SKILL.md §三 函数接口
"""

import argparse
import sys
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class TaskState(Enum):
    """Task 状态枚举"""
    PENDING = "[ ]"
    IN_PROGRESS = "[P]"
    WAITING_REVIEW = "[V]"
    COMPLETED = "[x]"
    ARCHIVED = "[archived]"
    BLOCKED = "[?]"

@dataclass
class Deliverable:
    """交付物定义"""
    name: str
    filename: str
    format: str
    review_level: str
    acceptance_criteria: str
    status: str = "pending"

@dataclass
class TaskCard:
    """Task-Card 数据结构"""
    task_id: str
    task_title: str
    task_type: str
    project_id: str
    topic_id: str
    assignee: str
    task_pic: str
    reviewer: str
    priority: str
    review_level: str
    deliverables: List[Deliverable]
    state: TaskState = TaskState.PENDING

def create_task(
    task_title: str,
    task_type: str,
    project_id: str,
    topic_id: str,
    assignee: str,
    task_pic: str,
    reviewer: str,
    priority: str,
    review_level: str,
    deliverables: List[Dict]
) -> Dict:
    """创建任务
    
    Args:
        task_title: 任务标题
        task_type: 任务类型
        project_id: 项目 ID
        topic_id: Topic ID
        assignee: 指派人
        task_pic: Task PIC
        reviewer: Reviewer
        priority: 优先级
        review_level: Review 级别
        deliverables: 交付物列表
        
    Returns:
        Dict: 创建结果
    """
    # Step 1: 校验项目存在
    # TODO: 实际实现需要读取 projects.yaml
    
    # Step 2: 校验必填字段
    if not assignee:
        return {"error": "E_ASSIGNEE_MISSING"}
    if not task_pic:
        return {"error": "E_PIC_MISSING"}
    
    # Step 3: 生成 Task ID
    task_id = f"{project_id}-{topic_id}-T01"
    
    # Step 4: 创建 Deliverable 对象
    deliverable_objs = [
        Deliverable(
            name=d["name"],
            filename=d["filename"],
            format=d["format"],
            review_level=d.get("review_level", review_level),
            acceptance_criteria=d["acceptance_criteria"]
        )
        for d in deliverables
    ]
    
    # Step 5: 创建 Task-Card
    task_card = TaskCard(
        task_id=task_id,
        task_title=task_title,
        task_type=task_type,
        project_id=project_id,
        topic_id=topic_id,
        assignee=assignee,
        task_pic=task_pic,
        reviewer=reviewer,
        priority=priority,
        review_level=review_level,
        deliverables=deliverable_objs
    )
    
    return {
        "status": "OK",
        "task_id": task_id,
        "state": TaskState.PENDING.value,
        "next_action": "等待 Task PIC 接收"
    }

def accept_task(task_id: str, task_pic: str) -> Dict:
    """接收任务
    
    Args:
        task_id: Task ID
        task_pic: Task PIC
        
    Returns:
        Dict: 接收结果
    """
    # 状态流转：[ ] → [P]
    return {
        "status": "OK",
        "task_id": task_id,
        "state": TaskState.IN_PROGRESS.value,
        "next_action": "开始执行"
    }

def review_deliverable(
    task_id: str,
    deliverable_name: str,
    reviewer: str,
    review_result: str,
    feedback: str
) -> Dict:
    """验收交付物
    
    Args:
        task_id: Task ID
        deliverable_name: 交付物名称
        reviewer: Reviewer
        review_result: pass|fail|reject
        feedback: 反馈内容
        
    Returns:
        Dict: 验收结果
    """
    # 状态影响
    if review_result == "pass":
        return {
            "status": "OK",
            "task_id": task_id,
            "deliverable": deliverable_name,
            "result": "pass",
            "state": TaskState.WAITING_REVIEW.value
        }
    elif review_result == "fail":
        return {
            "status": "OK",
            "task_id": task_id,
            "deliverable": deliverable_name,
            "result": "fail",
            "state": TaskState.IN_PROGRESS.value,
            "action": "局部修订后重新提交"
        }
    else:  # reject
        return {
            "status": "OK",
            "task_id": task_id,
            "deliverable": deliverable_name,
            "result": "reject",
            "state": TaskState.IN_PROGRESS.value,
            "action": "全量返工后重新提交"
        }

def close_task(task_id: str, closed_by: str) -> Dict:
    """关闭任务
    
    Args:
        task_id: Task ID
        closed_by: 关闭人
        
    Returns:
        Dict: 关闭结果
    """
    # 状态流转：[V] → [x]
    return {
        "status": "OK",
        "task_id": task_id,
        "state": TaskState.COMPLETED.value,
        "closed_at": "2026-04-22T23:45:00+08:00",
        "zone_c_triggered": True,
        "next_action": "知识沉淀宽限期 3 个工作日"
    }

def archive_task(task_id: str, archived_by: str) -> Dict:
    """归档任务
    
    Args:
        task_id: Task ID
        archived_by: 归档人
        
    Returns:
        Dict: 归档结果
    """
    # 状态流转：[x] → [archived]
    return {
        "status": "OK",
        "task_id": task_id,
        "state": TaskState.ARCHIVED.value,
        "archived_at": "2026-04-25T10:00:00+08:00"
    }

def main():
    parser = argparse.ArgumentParser(
        description="Task 管理核心函数",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python task_functions.py --action create_task --task-id "ZT-P008-T06-T01"
  python task_functions.py --test
        """
    )
    
    parser.add_argument(
        "--action",
        choices=["create_task", "accept_task", "review_deliverable", "close_task", "archive_task"],
        help="操作类型"
    )
    
    parser.add_argument(
        "--task-id",
        help="Task ID"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="运行测试场景"
    )
    
    args = parser.parse_args()
    
    if args.test:
        # 运行测试场景
        print("=" * 60)
        print("Task 管理函数测试")
        print("=" * 60)
        
        # 创建任务
        result = create_task(
            task_title="测试任务",
            task_type="常规任务",
            project_id="ZT-P008",
            topic_id="T06",
            assignee="main",
            task_pic="cqo",
            reviewer="main",
            priority="P1",
            review_level="L2",
            deliverables=[
                {
                    "name": "测试文档",
                    "filename": "test.md",
                    "format": ".md",
                    "acceptance_criteria": "格式正确"
                }
            ]
        )
        print(f"\n创建任务: {result}")
        
        # 接收任务
        result = accept_task("ZT-P008-T06-T01", "cqo")
        print(f"\n接收任务: {result}")
        
        # 验收交付物
        result = review_deliverable(
            "ZT-P008-T06-T01",
            "测试文档",
            "main",
            "pass",
            "符合标准"
        )
        print(f"\n验收交付物: {result}")
        
        # 关闭任务
        result = close_task("ZT-P008-T06-T01", "main")
        print(f"\n关闭任务: {result}")
        
        # 归档任务
        result = archive_task("ZT-P008-T06-T01", "yinyue")
        print(f"\n归档任务: {result}")
        
        sys.exit(0)
    
    if args.action and args.task_id:
        # 执行具体操作
        if args.action == "accept_task":
            result = accept_task(args.task_id, "test_pic")
        elif args.action == "close_task":
            result = close_task(args.task_id, "test_assignee")
        elif args.action == "archive_task":
            result = archive_task(args.task_id, "yinyue")
        else:
            result = {"error": "Action not implemented"}
        
        print(json.dumps(result, indent=2))
        sys.exit(0)
    
    parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()