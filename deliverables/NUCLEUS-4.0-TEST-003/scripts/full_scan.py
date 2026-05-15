#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
full_scan.py - 全盘扫描函数 v1.0
用途：扫描 10_Projects 目录所有 TASK-CARD，提取状态，生成全局视图
执行频率：每次 Heartbeat 巡检

核心功能：
1. 扫描 10_Projects 目录下所有 TASK-CARD*.md 文件
2. 提取状态标记（[ ]/[P]/[V]/[x]/[?]/[!]）
3. 提取关键信息（Task ID, Task PIC, Project, Topic, 优先级等）
4. 生成全局状态报告（JSON + Markdown）
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 配置
WORKSPACE = "/Users/haroldtsui/Workspaces/openclaw/main"
PROJECTS_DIR = os.path.join(WORKSPACE, "10_Projects")
OUTPUT_DIR = os.path.join(WORKSPACE, "10_Projects/ZT-P015_NUCLEUS-4-0/deliverables/NUCLEUS-4.0-TEST-003")

# 状态标记定义
STATE_MARKERS = {
    "[ ]": "待接收",
    "[P]": "执行中",
    "[V]": "待验收",
    "[x]": "已完成",
    "[?]": "阻塞",
    "[!]": "Harold 待决"
}

# 优先级映射
PRIORITY_MAP = {
    "P0": 0,
    "P1": 1,
    "P2": 2,
    "P3": 3
}


def find_all_task_cards(base_dir: str) -> List[str]:
    """
    递归查找目录下所有 TASK-CARD*.md 文件
    返回：文件路径列表
    """
    task_cards = []
    for root, dirs, files in os.walk(base_dir):
        # 跳过 archives 和 .git 目录
        if '.git' in root or 'Archives' in root or '40_Archives' in root:
            continue
        for file in files:
            if file.startswith('TASK-CARD') and file.endswith('.md'):
                task_cards.append(os.path.join(root, file))
    return sorted(task_cards)


def extract_state_marker(content: str) -> str:
    """
    从 TASK-CARD 内容中提取状态标记
    优先级：[x] > [!] > [?] > [V] > [P] > [ ]
    """
    # 查找 Zone B 中的状态标记（运行时状态区域）
    # 通常在 "## 七、状态与执行记录" 或 "### 7.1 当前状态" 附近
    
    # 方法 1：查找表格中的状态标记
    state_pattern = r'\|\s*\*\*状态标记\*\*\s*\|\s*(\[[ xPV?!]\])\s*\|'
    match = re.search(state_pattern, content)
    if match:
        return match.group(1)
    
    # 方法 2：查找任意状态标记（按优先级）
    for marker in ["[x]", "[!]", "[?]", "[V]", "[P]", "[ ]"]:
        if marker in content:
            # 确保是在状态上下文中（不是示例或说明）
            # 简单启发式：标记前后 100 字符内包含"状态"关键词
            idx = content.find(marker)
            if idx != -1:
                context = content[max(0, idx-100):min(len(content), idx+100)]
                if '状态' in context or 'Status' in context:
                    return marker
    
    return "[ ]"  # 默认待接收


def extract_task_info(filepath: str) -> Dict[str, Any]:
    """
    从 TASK-CARD 文件中提取关键信息
    返回：字典包含 Task ID, Task PIC, Project, Topic, 状态，优先级等
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e), "filepath": filepath}
    
    # 提取 Task ID（从文件名或内容）
    filename = os.path.basename(filepath)
    task_id_match = re.search(r'TASK-CARD[-_]?(.+?)\.md', filename)
    task_id = task_id_match.group(1) if task_id_match else "UNKNOWN"
    
    # 从内容中提取 Task ID（更准确）
    task_id_content = re.search(r'\|\s*\*\*Task ID\*\*\s*\|\s*(.+?)\s*\|', content)
    if task_id_content:
        task_id = task_id_content.group(1).strip()
    
    # 提取 Task 标题
    task_title_match = re.search(r'\|\s*\*\*Task 标题\*\*\s*\|\s*(.+?)\s*\|', content)
    task_title = task_title_match.group(1).strip() if task_title_match else "无标题"
    
    # 提取 Task PIC
    task_pic_match = re.search(r'\|\s*\*\*Task PIC\*\*\s*\|\s*(.+?)\s*\|', content)
    task_pic = task_pic_match.group(1).strip() if task_pic_match else "未指定"
    
    # 提取归属 Project
    project_match = re.search(r'\|\s*\*\*归属 Project\*\*\s*\|\s*(.+?)\s*\|', content)
    project = project_match.group(1).strip() if project_match else "未知"
    
    # 提取归属 Topic
    topic_match = re.search(r'\|\s*\*\*归属 Topic\*\*\s*\|\s*(.+?)\s*\|', content)
    topic = topic_match.group(1).strip() if topic_match else "未知"
    
    # 提取优先级
    priority_match = re.search(r'\|\s*\*\*优先级\*\*\s*\|\s*(P[0-3])\s*([←].*)?\|', content)
    priority = priority_match.group(1) if priority_match else "P2"
    
    # 提取状态标记
    state = extract_state_marker(content)
    
    # 提取 Review 级别
    review_match = re.search(r'\|\s*\*\*Review 级别\*\*\s*\|\s*(L[0-3])\s*([←].*)?\|', content)
    review_level = review_match.group(1) if review_match else "L1"
    
    # 提取截止日期
    deadline_match = re.search(r'\|\s*\*\*截止日期\*\*\s*\|\s*(.+?)\s*\|', content)
    deadline = deadline_match.group(1).strip() if deadline_match else "未指定"
    
    # 计算相对路径（用于链接）
    rel_path = filepath.replace(WORKSPACE + "/", "")
    
    return {
        "task_id": task_id,
        "task_title": task_title,
        "task_pic": task_pic,
        "project": project,
        "topic": topic,
        "priority": priority,
        "priority_num": PRIORITY_MAP.get(priority, 2),
        "state": state,
        "state_desc": STATE_MARKERS.get(state, "未知"),
        "review_level": review_level,
        "deadline": deadline,
        "filepath": filepath,
        "rel_path": rel_path,
        "scan_time": datetime.now().isoformat()
    }


def scan_all_tasks() -> List[Dict[str, Any]]:
    """
    扫描所有 TASK-CARD，返回任务列表
    """
    task_cards = find_all_task_cards(PROJECTS_DIR)
    tasks = []
    
    for filepath in task_cards:
        task_info = extract_task_info(filepath)
        tasks.append(task_info)
    
    # 按优先级和状态排序
    # 优先级：P0 > P1 > P2 > P3
    # 状态：[!] > [?] > [P] > [V] > [ ] > [x]
    state_order = {"[!]": 0, "[?]": 1, "[P]": 2, "[V]": 3, "[ ]": 4, "[x]": 5}
    
    tasks.sort(key=lambda x: (x.get("priority_num", 2), state_order.get(x.get("state"), 4)))
    
    return tasks


def generate_summary_report(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    生成汇总统计报告
    """
    total = len(tasks)
    
    # 按状态统计
    by_state = {}
    for task in tasks:
        state = task.get("state", "[ ]")
        by_state[state] = by_state.get(state, 0) + 1
    
    # 按优先级统计
    by_priority = {}
    for task in tasks:
        priority = task.get("priority", "P2")
        by_priority[priority] = by_priority.get(priority, 0) + 1
    
    # 按 Project 统计
    by_project = {}
    for task in tasks:
        project = task.get("project", "未知")
        if project not in by_project:
            by_project[project] = []
        by_project[project].append(task)
    
    # 按 Task PIC 统计
    by_pic = {}
    for task in tasks:
        pic = task.get("task_pic", "未指定")
        by_pic[pic] = by_pic.get(pic, 0) + 1
    
    # 活跃任务（未完成且非待接收）
    active_tasks = [t for t in tasks if t.get("state") not in ["[x]", "[ ]"]]
    
    # 阻塞任务
    blocked_tasks = [t for t in tasks if t.get("state") in ["[?]", "[!]"]]
    
    # 高优先级任务（P0/P1）
    high_priority_tasks = [t for t in tasks if t.get("priority") in ["P0", "P1"]]
    
    return {
        "total": total,
        "by_state": by_state,
        "by_priority": by_priority,
        "by_project": {k: len(v) for k, v in by_project.items()},
        "by_pic": by_pic,
        "active_count": len(active_tasks),
        "blocked_count": len(blocked_tasks),
        "high_priority_count": len(high_priority_tasks),
        "scan_time": datetime.now().isoformat()
    }


def generate_markdown_report(tasks: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    """
    生成 Markdown 格式的全局状态报告
    """
    md = []
    md.append("# 全局任务状态报告 · Full Scan Report")
    md.append("")
    md.append(f"**扫描时间**: {summary['scan_time']}")
    md.append(f"**扫描范围**: {PROJECTS_DIR}")
    md.append(f"**总任务数**: {summary['total']}")
    md.append("")
    
    # 汇总统计
    md.append("## 一、汇总统计")
    md.append("")
    md.append("### 1.1 按状态分布")
    md.append("")
    md.append("| 状态 | 数量 | 说明 |")
    md.append("|------|------|------|")
    for state, count in sorted(summary['by_state'].items()):
        desc = STATE_MARKERS.get(state, "未知")
        md.append(f"| {state} | {count} | {desc} |")
    md.append("")
    
    md.append("### 1.2 按优先级分布")
    md.append("")
    md.append("| 优先级 | 数量 |")
    md.append("|--------|------|")
    for priority in ["P0", "P1", "P2", "P3"]:
        count = summary['by_priority'].get(priority, 0)
        md.append(f"| {priority} | {count} |")
    md.append("")
    
    md.append("### 1.3 关键指标")
    md.append("")
    md.append(f"- **活跃任务**: {summary['active_count']}")
    md.append(f"- **阻塞任务**: {summary['blocked_count']}")
    md.append(f"- **高优先级任务 (P0/P1)**: {summary['high_priority_count']}")
    md.append("")
    
    # 高优先级任务详情
    high_priority = [t for t in tasks if t.get("priority") in ["P0", "P1"] and t.get("state") != "[x]"]
    if high_priority:
        md.append("## 二、高优先级任务 (P0/P1)")
        md.append("")
        md.append("| Task ID | 标题 | Project | PIC | 状态 | 优先级 |")
        md.append("|---------|------|---------|-----|------|--------|")
        for task in high_priority[:20]:  # 最多显示 20 个
            md.append(f"| {task['task_id']} | {task['task_title'][:30]} | {task['project']} | {task['task_pic']} | {task['state']} | {task['priority']} |")
        md.append("")
    
    # 阻塞任务详情
    blocked = [t for t in tasks if t.get("state") in ["[?]", "[!]"]]
    if blocked:
        md.append("## 三、阻塞任务")
        md.append("")
        md.append("| Task ID | 标题 | Project | PIC | 状态 |")
        md.append("|---------|------|---------|-----|------|")
        for task in blocked:
            md.append(f"| {task['task_id']} | {task['task_title'][:30]} | {task['project']} | {task['task_pic']} | {task['state']} |")
        md.append("")
    
    # 按 Project 分组详情
    md.append("## 四、按 Project 分组")
    md.append("")
    by_project = {}
    for task in tasks:
        project = task.get("project", "未知")
        if project not in by_project:
            by_project[project] = []
        by_project[project].append(task)
    
    for project, project_tasks in sorted(by_project.items()):
        md.append(f"### {project}")
        md.append("")
        md.append("| Task ID | 标题 | PIC | 状态 | 优先级 |")
        md.append("|---------|------|-----|------|--------|")
        for task in sorted(project_tasks, key=lambda x: x.get("priority_num", 2))[:15]:  # 每个 Project 最多 15 个
            md.append(f"| {task['task_id']} | {task['task_title'][:25]} | {task['task_pic']} | {task['state']} | {task['priority']} |")
        if len(project_tasks) > 15:
            md.append(f"| ... | 还有 {len(project_tasks) - 15} 个任务 | ... | ... | ... |")
        md.append("")
    
    # 附录：扫描说明
    md.append("## 附录：扫描说明")
    md.append("")
    md.append("### 扫描范围")
    md.append(f"- 根目录：{PROJECTS_DIR}")
    md.append("- 文件模式：TASK-CARD*.md")
    md.append("- 排除目录：.git, Archives, 40_Archives")
    md.append("")
    md.append("### 状态标记定义")
    for marker, desc in STATE_MARKERS.items():
        md.append(f"- `{marker}`: {desc}")
    md.append("")
    md.append("### 数据来源")
    md.append("- 状态标记：从 TASK-CARD Zone B（运行时状态）提取")
    md.append("- 优先级：从 TASK-CARD Zone A（任务定义）提取")
    md.append("- Task PIC：从 TASK-CARD Zone A 提取")
    md.append("")
    md.append("---")
    md.append(f"*报告生成时间：{datetime.now().isoformat()}*")
    
    return "\n".join(md)


def main():
    """
    主函数：执行全盘扫描，生成报告
    """
    print(f"=== Full Scan Started ===")
    print(f"Workspace: {WORKSPACE}")
    print(f"Projects Dir: {PROJECTS_DIR}")
    print()
    
    # 扫描所有任务
    print("Scanning all TASK-CARD files...")
    tasks = scan_all_tasks()
    print(f"Found {len(tasks)} tasks")
    
    # 生成汇总统计
    print("Generating summary report...")
    summary = generate_summary_report(tasks)
    
    # 生成 Markdown 报告
    print("Generating Markdown report...")
    md_report = generate_markdown_report(tasks, summary)
    
    # 保存 JSON 报告
    json_output = os.path.join(OUTPUT_DIR, "full_scan_result.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump({
            "tasks": tasks,
            "summary": summary
        }, f, ensure_ascii=False, indent=2)
    print(f"JSON report saved: {json_output}")
    
    # 保存 Markdown 报告
    md_output = os.path.join(OUTPUT_DIR, "global_status_report.md")
    with open(md_output, 'w', encoding='utf-8') as f:
        f.write(md_report)
    print(f"Markdown report saved: {md_output}")
    
    # 输出摘要
    print()
    print("=== Scan Summary ===")
    print(f"Total tasks: {summary['total']}")
    print(f"Active tasks: {summary['active_count']}")
    print(f"Blocked tasks: {summary['blocked_count']}")
    print(f"High priority (P0/P1): {summary['high_priority_count']}")
    print()
    print("By state:")
    for state, count in sorted(summary['by_state'].items()):
        desc = STATE_MARKERS.get(state, "未知")
        print(f"  {state} ({desc}): {count}")
    print()
    print("=== Scan Completed ===")
    
    return {
        "tasks": tasks,
        "summary": summary,
        "json_output": json_output,
        "md_output": md_output
    }


if __name__ == "__main__":
    main()
