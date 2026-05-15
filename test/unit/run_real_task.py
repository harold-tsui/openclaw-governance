#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NUCLEUS 4.0 - 真实 Task 执行

用 N4-P2-T01-T01（CycleAggregator 实现）作为试点

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import json
import yaml
from datetime import datetime, timezone

# ========================================
# 环境设置
# ========================================

PROJECT_DIR = "/Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0"
SKILL_DIR = os.path.expanduser("~/.openclaw/skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts")

sys.path.insert(0, SKILL_DIR)
os.chdir(PROJECT_DIR)

# 创建必要目录
for d in ["cycles/task", "cycles/topic", "cycles/project", "cycles/system", 
          "logs", "executions", "config", "tasks"]:
    os.makedirs(d, exist_ok=True)

# ========================================
# 导入 NUCLEUS 4.0 模块
# ========================================

from scheduler import create_cycle_for_scope, get_scheduler_status
from scheduler_state import load_scheduler_state, save_scheduler_state, create_default_state
from plan import determine_review
from do import execute_cycle, write_execution_log
from check import check_cycle
from act import adjust_automation_level
from monitor import sense_system_state, detect_anomalies

# ========================================
# Task 定义
# ========================================

TASK_CARD_PATH = "tasks/N4-P2-T01-T01_TASK-CARD.md"
TASK_ID = "N4-P2-T01-T01"
SCOPE = "task"

# ========================================
# Phase: Plan
# ========================================

def run_plan_phase():
    """Plan 阶段"""
    print("=" * 60)
    print("Phase: Plan（规划阶段）")
    print("=" * 60)
    
    # 1. 计算 review_level
    print("\n1. 计算 review_level...")
    review_context = determine_review(
        task_card_path=TASK_CARD_PATH,
        task_id=TASK_ID,
        scope=SCOPE
    )
    
    print(f"   Task ID: {TASK_ID}")
    print(f"   review_level: {review_context['review_level']}")
    print(f"   human_approval_required: {review_context['human_approval_required']}")
    print(f"   reviewer: {review_context['reviewer']}")
    
    # 2. 创建 CycleUnit
    print("\n2. 创建 CycleUnit...")
    cycle_id = create_cycle_for_scope(SCOPE)
    
    if cycle_id:
        print(f"   ✅ CycleUnit 创建成功: {cycle_id}")
        
        # 3. 更新 CycleUnit 的 task_card_id
        cycle_path = f"cycles/{SCOPE}/{cycle_id}.yaml"
        with open(cycle_path, 'r') as f:
            cycle_data = yaml.safe_load(f)
        
        cycle_data['task_card_id'] = TASK_ID
        cycle_data['metadata']['review_level'] = review_context['review_level']
        
        with open(cycle_path, 'w') as f:
            yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
        
        print(f"   ✅ 已关联 Task-CARD: {TASK_ID}")
        
    else:
        print("   ❌ CycleUnit 创建失败")
        return None
    
    return cycle_id, review_context

# ========================================
# Phase: Do
# ========================================

def run_do_phase(cycle_id):
    """Do 阶段"""
    print("\n" + "=" * 60)
    print("Phase: Do（执行阶段）")
    print("=" * 60)
    
    print(f"\n执行 CycleUnit: {cycle_id}")
    
    # 执行
    result = execute_cycle(cycle_id)
    
    print(f"   状态: {result['status']}")
    print(f"   执行的 actions: {result['actions_executed']}")
    print(f"   创建的子环: {len(result['children_created'])}")
    
    if result['errors']:
        print(f"   错误: {result['errors']}")
    
    return result['status']

# ========================================
# Phase: Check
# ========================================

def run_check_phase(cycle_id):
    """Check 阶段"""
    print("\n" + "=" * 60)
    print("Phase: Check（验收阶段）")
    print("=" * 60)
    
    print(f"\n检查 CycleUnit: {cycle_id}")
    
    result = check_cycle(cycle_id)
    
    print(f"   verdict: {result['verdict']}")
    print(f"   evidence count: {len(result['evidence'])}")
    print(f"   human_review_triggered: {result['human_review_triggered']}")
    
    if result['errors']:
        print(f"   错误: {result['errors']}")
    
    # 显示证据
    if result['evidence']:
        print("\n   证据列表:")
        for i, e in enumerate(result['evidence'][:3]):
            print(f"   [{i+1}] {e.get('type', 'unknown')}")
    
    return result['verdict'], result['evidence']

# ========================================
# Phase: Act
# ========================================

def run_act_phase(cycle_id, verdict, evidence):
    """Act 阶段"""
    print("\n" + "=" * 60)
    print("Phase: Act（调整阶段）")
    print("=" * 60)
    
    print(f"\n调整自动化级别")
    print(f"   当前 verdict: {verdict}")
    
    # 调用 adjust_automation_level
    adjustments = adjust_automation_level(
        cycle_id=cycle_id,
        verdict=verdict,
        consecutive_count=0,
        current_level="L2",
        evidence=[e.get('type', 'unknown') for e in evidence]
    )
    
    print(f"\n   调整结果:")
    for adj in adjustments:
        print(f"   - type: {adj['type']}")
        print(f"     from: {adj['from']} → to: {adj['to']}")
        print(f"     reason: {adj['reason']}")
    
    return adjustments

# ========================================
# Phase: Monitor
# ========================================

def run_monitor_phase():
    """Monitor 阶段"""
    print("\n" + "=" * 60)
    print("Phase: Monitor（监控阶段）")
    print("=" * 60)
    
    print("\n感知系统状态...")
    snapshot = sense_system_state()
    
    print(f"   活跃 CycleUnit: {snapshot.active_cycles}")
    print(f"   日志条目: {len(snapshot.log_entries)}")
    print(f"   执行条目: {len(snapshot.execution_entries)}")
    
    print("\n检测异常...")
    anomalies = detect_anomalies(snapshot)
    
    if anomalies:
        print(f"   检测到 {len(anomalies)} 个异常:")
        for a in anomalies:
            print(f"   - [{a.severity}] {a.type}: {a.message}")
    else:
        print("   ✅ 无异常")

# ========================================
# 生成执行报告
# ========================================

def generate_report(cycle_id, review_context, verdict, adjustments):
    """生成执行报告"""
    print("\n" + "=" * 60)
    print("📋 执行报告")
    print("=" * 60)
    
    report = {
        "task_id": TASK_ID,
        "cycle_id": cycle_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phases": {
            "plan": {
                "review_level": review_context['review_level'],
                "reviewer": review_context['reviewer']
            },
            "do": {
                "status": "completed"
            },
            "check": {
                "verdict": verdict
            },
            "act": {
                "adjustments": len(adjustments)
            }
        }
    }
    
    # 写入执行日志
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    report_path = f"executions/{today}_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n   Task ID: {TASK_ID}")
    print(f"   Cycle ID: {cycle_id}")
    print(f"   review_level: {review_context['review_level']}")
    print(f"   verdict: {verdict}")
    print(f"   adjustments: {len(adjustments)}")
    print(f"\n   报告已保存: {report_path}")
    
    return report

# ========================================
# 主函数
# ========================================

def main():
    """执行完整 PDCA 循环"""
    print("=" * 60)
    print("NUCLEUS 4.0 - 真实 Task 执行")
    print(f"Task: {TASK_ID} - CycleAggregator 核心实现")
    print("=" * 60)
    
    # Plan
    cycle_id, review_context = run_plan_phase()
    
    if not cycle_id:
        print("\n❌ 执行失败：CycleUnit 创建失败")
        return
    
    # Do
    do_status = run_do_phase(cycle_id)
    
    # Check
    verdict, evidence = run_check_phase(cycle_id)
    
    # Act
    adjustments = run_act_phase(cycle_id, verdict, evidence)
    
    # Monitor
    run_monitor_phase()
    
    # 生成报告
    report = generate_report(cycle_id, review_context, verdict, adjustments)
    
    print("\n" + "=" * 60)
    print("✅ PDCA 循环执行完成")
    print("=" * 60)

if __name__ == "__main__":
    main()