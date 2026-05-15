#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDCA Dashboard - 可视化PDCA执行状态的仪表板

该工具创建一个简单的文本仪表板，展示当前所有任务的PDCA状态，
便于快速了解项目整体进展。
"""

import os
import yaml
from datetime import datetime
from typing import Dict, List, Any


def get_dashboard_data(pdca_dir: str) -> Dict[str, Any]:
    """
    获取用于仪表板的数据
    """
    if not os.path.exists(pdca_dir):
        return {"error": f"PDCA目录不存在: {pdca_dir}", "tasks": []}
    
    dashboard_data = {
        "summary": {
            "total": 0,
            "completed": 0,
            "active": 0,
            "blocked": 0,
            "pending_approval": 0
        },
        "by_phase": {
            "plan": 0,
            "do": 0,
            "check": 0,
            "act": 0,
            "completed": 0
        },
        "by_verdict": {
            "pass": 0,
            "partial": 0,
            "fail": 0,
            "skip": 0,
            "pending": 0
        },
        "tasks": []
    }
    
    for filename in os.listdir(pdca_dir):
        if not filename.endswith('.yaml') or filename.startswith('_'):
            continue
            
        filepath = os.path.join(pdca_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not data or not data.get('cycles'):
                continue
                
            # 获取最新cycle
            latest_cycle = data['cycles'][-1]
            task_id = data['task_card_id']
            
            # 统计数据
            phase = latest_cycle['phase']
            dashboard_data["by_phase"][phase] = dashboard_data["by_phase"].get(phase, 0) + 1
            
            # 统计verdict
            if latest_cycle.get('c') and latest_cycle['c'].get('verdict'):
                verdict = latest_cycle['c']['verdict']
                dashboard_data["by_verdict"][verdict] = dashboard_data["by_verdict"].get(verdict, 0) + 1
            
            # 分类任务状态
            if phase == 'completed':
                dashboard_data["summary"]["completed"] += 1
            elif phase == 'check' and latest_cycle.get('c', {}).get('verdict') == 'pending':
                dashboard_data["summary"]["pending_approval"] += 1
            elif phase == 'do' and latest_cycle.get('d', {}).get('status') == 'blocked':
                dashboard_data["summary"]["blocked"] += 1
            else:
                dashboard_data["summary"]["active"] += 1
                
            dashboard_data["summary"]["total"] += 1
            
            # 添加任务信息
            task_info = {
                "id": task_id,
                "phase": phase,
                "verdict": latest_cycle.get('c', {}).get('verdict'),
                "status": latest_cycle.get('d', {}).get('status'),
                "summary": latest_cycle.get('p', {}).get('summary', '')[:60] + "..." if latest_cycle.get('p', {}).get('summary', '') and len(latest_cycle.get('p', {}).get('summary', '')) > 60 else latest_cycle.get('p', {}).get('summary', '')
            }
            
            dashboard_data["tasks"].append(task_info)
            
        except Exception as e:
            continue  # 跳过有问题的文件
    
    return dashboard_data


def print_dashboard(dashboard_data: Dict[str, Any]):
    """
    打印仪表板
    """
    if "error" in dashboard_data:
        print(f"错误: {dashboard_data['error']}")
        return
        
    print("="*80)
    print("NUCLEUS-4.0 PDCA 仪表板")
    print("="*80)
    print()
    
    # 确保所有数值都是整数
    summary = dashboard_data["summary"]
    total_tasks = int(summary['total']) if isinstance(summary['total'], str) else summary['total']
    completed_tasks = int(summary['completed']) if isinstance(summary['completed'], str) else summary['completed']
    active_tasks = int(summary['active']) if isinstance(summary['active'], str) else summary['active']
    pending_tasks = int(summary['pending_approval']) if isinstance(summary['pending_approval'], str) else summary['pending_approval']
    blocked_tasks = int(summary['blocked']) if isinstance(summary['blocked'], str) else summary['blocked']
    
    # 摘要统计
    print(f"📊 总体概况:")
    print(f"   • 总任务数: {total_tasks}")
    
    completion_bar = '█' * int(completed_tasks/max(total_tasks, 1)*20)
    completion_percentage = completed_tasks/max(total_tasks, 1)*100
    print(f"   • 已完成: {completed_tasks} ({completion_bar:20} {completion_percentage:5.1f}%)")
    print(f"   • 活跃中: {active_tasks}")
    print(f"   • 待审批: {pending_tasks}")
    print(f"   • 已阻塞: {blocked_tasks}")
    print()
    
    # 按阶段分布
    phases = dashboard_data["by_phase"]
    print("🔄 按阶段分布:")
    for phase, count in phases.items():
        if count > 0:
            print(f"   • {phase.upper()}: {count}")
    print()
    
    # 按结论分布
    verdicts = dashboard_data["by_verdict"]
    print("✅ 按结论分布:")
    for verdict, count in verdicts.items():
        if count > 0:
            print(f"   • {verdict.upper()}: {count}")
    print()
    
    # 当前任务列表
    print("📋 当前任务状态:")
    print("-" * 80)
    print(f"{'任务ID':<15} {'阶段':<8} {'结论':<8} {'状态':<8} {'摘要'}")
    print("-" * 80)
    
    for task in dashboard_data["tasks"]:
        task_id = task["id"][:14] if len(task["id"]) > 14 else task["id"]
        phase = task["phase"][:7] if len(task["phase"]) > 7 else task["phase"]
        verdict = str(task["verdict"]) if task["verdict"] else "-"
        status = str(task["status"]) if task["status"] else "-"
        summary = str(task["summary"])
        
        print(f"{task_id:<15} {phase:<8} {verdict:<8} {status:<8} {summary}")
    
    print("-" * 80)
    print()
    
    # 关键指标
    print("📈 关键指标:")
    completion_rate = completed_tasks / max(total_tasks, 1) * 100
    print(f"   • 完成率: {completion_rate:.1f}%")
    if total_tasks > 0:
        avg_verdicts = {k: v/total_tasks*100 for k, v in dashboard_data["by_verdict"].items() if v > 0}
        for k, v in avg_verdicts.items():
            print(f"   • {k.upper()} 率: {v:.1f}%")
    
    print()
    print(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


def main():
    # 使用标准的PDCA目录路径
    pdca_dir = "./pdca"
    
    # 如果相对路径不存在，尝试绝对路径
    if not os.path.exists(pdca_dir):
        pdca_dir = "/Users/haroldtsui/Workspaces/openclaw/main/skills/openclaw-governance/skills/openclaw-governance-nucleus/pdca"
    
    if not os.path.exists(pdca_dir):
        print(f"错误: 找不到PDCA目录，尝试路径: {pdca_dir}")
        return
    
    dashboard_data = get_dashboard_data(pdca_dir)
    print_dashboard(dashboard_data)


if __name__ == "__main__":
    main()