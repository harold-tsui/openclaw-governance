#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NUCLEUS 4.0 - Phase 1 实施演示

展示完整的 PDCA 循环运行。

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import json
import yaml
from datetime import datetime, timezone

# 添加项目路径
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# 导入 NUCLEUS 4.0 模块
from core.scheduler import on_heartbeat, create_cycle_for_scope, get_scheduler_status
from core.scheduler_state import load_scheduler_state, increment_counter
from modules.plan import determine_review, init_plan
from modules.do import execute_cycle, write_execution_log
from modules.check import check_cycle, execute_check_by_level, collect_evidence
from modules.act import adjust_automation_level
from modules.monitor import sense_system_state, detect_anomalies


def setup_environment():
    """初始化环境"""
    print("=" * 60)
    print("NUCLEUS 4.0 - Phase 1 实施演示")
    print("=" * 60)
    
    # 创建必要的目录
    dirs = [
        "cycles/task", "cycles/topic", "cycles/project", "cycles/system",
        "cycles/archive/task", "cycles/archive/topic",
        "logs", "executions", "config"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    # 创建初始配置（如果不存在）
    if not os.path.exists("cycles/scheduler_state.yaml"):
        from core.scheduler_state import create_default_state, save_scheduler_state
        state = create_default_state()
        save_scheduler_state(state)
    
    print("✅ 环境初始化完成")


def demo_plan_phase():
    """演示 Plan 阶段"""
    print("\n" + "=" * 60)
    print("Phase: Plan（规划阶段）")
    print("=" * 60)
    
    # 1. 创建 Task-CARD（模拟）
    task_card_path = "tasks/DEMO-TASK-CARD.md"
    os.makedirs("tasks", exist_ok=True)
    
    task_card_content = """# TASK-CARD · DEMO-001

## 一、Task 概要
| 字段 | 内容 |
|------|------|
| **Task ID** | DEMO-001 |
| **Task 名称** | Phase 1 演示任务 |
| **Review 级别** | L2 |

## 五、验收标准
| 标准 | 说明 |
|------|------|
| **DoD-1** | 演示成功运行 |
| **DoD-2** | PDCA 循环完整 |
"""
    with open(task_card_path, 'w') as f:
        f.write(task_card_content)
    
    # 2. 调用 determine_review
    print("\n1. 调用 determine_review()...")
    try:
        review_context = determine_review(
            task_card_path=task_card_path,
            task_id="DEMO-001",
            scope="task"
        )
        print(f"   review_level: {review_context['review_level']}")
        print(f"   human_approval_required: {review_context['human_approval_required']}")
        print(f"   reviewer: {review_context['reviewer']}")
    except Exception as e:
        print(f"   ℹ️  使用默认配置（task-card 解析跳过）: {e}")
        review_context = {
            'review_level': 'L2',
            'human_approval_required': False,
            'reviewer': 'yin-yue'
        }
    
    # 3. 初始化 CycleUnit
    print("\n2. 创建 CycleUnit...")
    cycle_id = create_cycle_for_scope('task')
    if cycle_id:
        print(f"   ✅ CycleUnit 创建成功: {cycle_id}")
    else:
        print("   ❌ CycleUnit 创建失败")
    
    return cycle_id, review_context


def demo_do_phase(cycle_id):
    """演示 Do 阶段"""
    print("\n" + "=" * 60)
    print("Phase: Do（执行阶段）")
    print("=" * 60)
    
    if not cycle_id:
        print("   ⚠️  跳过（无 CycleUnit）")
        return
    
    print(f"\n1. 执行 CycleUnit: {cycle_id}")
    result = execute_cycle(cycle_id)
    
    print(f"   状态: {result['status']}")
    print(f"   执行的 actions: {result['actions_executed']}")
    print(f"   创建的子环: {len(result['children_created'])}")
    
    if result['errors']:
        print(f"   错误: {result['errors']}")


def demo_check_phase(cycle_id):
    """演示 Check 阶段"""
    print("\n" + "=" * 60)
    print("Phase: Check（验收阶段）")
    print("=" * 60)
    
    if not cycle_id:
        print("   ⚠️  跳过（无 CycleUnit）")
        return 'skip', []
    
    print(f"\n1. 检查 CycleUnit: {cycle_id}")
    result = check_cycle(cycle_id)
    
    print(f"   verdict: {result['verdict']}")
    print(f"   evidence count: {len(result['evidence'])}")
    print(f"   human_review_triggered: {result['human_review_triggered']}")
    
    if result['errors']:
        print(f"   错误: {result['errors']}")
    
    # 显示部分证据
    if result['evidence']:
        print("\n   证据示例:")
        for i, e in enumerate(result['evidence'][:3]):
            print(f"   [{i+1}] {e.get('type', 'unknown')}")
    
    return result['verdict'], result['evidence']


def demo_act_phase(cycle_id, verdict, evidence):
    """演示 Act 阶段"""
    print("\n" + "=" * 60)
    print("Phase: Act（调整阶段）")
    print("=" * 60)
    
    if not cycle_id:
        print("   ⚠️  跳过（无 CycleUnit）")
        return
    
    print(f"\n1. 调整自动化级别")
    print(f"   当前 verdict: {verdict}")
    
    # 调用 adjust_automation_level
    adjustments = adjust_automation_level(
        cycle_id=cycle_id,
        verdict=verdict,
        consecutive_count=0,
        current_level="L2",
        evidence=[e.get('type', 'unknown') for e in evidence]
    )
    
    print(f"   调整结果:")
    for adj in adjustments:
        print(f"   - type: {adj['type']}")
        print(f"     from: {adj['from']} → to: {adj['to']}")
        print(f"     reason: {adj['reason']}")


def demo_monitor_phase():
    """演示 Monitor 阶段"""
    print("\n" + "=" * 60)
    print("Phase: Monitor（监控阶段）")
    print("=" * 60)
    
    print("\n1. 感知系统状态...")
    snapshot = sense_system_state()
    
    print(f"   活跃 CycleUnit: {snapshot.active_cycles}")
    print(f"   日志条目: {len(snapshot.log_entries)}")
    print(f"   执行条目: {len(snapshot.execution_entries)}")
    print(f"   等待队列: {snapshot.wait_queue_sizes}")
    
    print("\n2. 检测异常...")
    anomalies = detect_anomalies(snapshot)
    
    if anomalies:
        print(f"   检测到 {len(anomalies)} 个异常:")
        for a in anomalies:
            print(f"   - [{a.severity}] {a.type}: {a.message}")
    else:
        print("   ✅ 无异常")


def demo_scheduler():
    """演示调度器"""
    print("\n" + "=" * 60)
    print("Scheduler: 多粒度调度")
    print("=" * 60)
    
    print("\n1. 获取调度器状态...")
    status = get_scheduler_status()
    
    print(f"   计数器: {status.get('counters', {})}")
    print(f"   活跃数量: {status.get('active_counts', {})}")
    print(f"   等待队列: {status.get('wait_queue_sizes', {})}")
    
    print("\n2. 触发 Heartbeat...")
    result = on_heartbeat()
    
    print(f"   触发的 scopes: {result['triggered_scopes']}")
    print(f"   创建的 cycles: {result['created_cycles']}")
    print(f"   拒绝的请求: {len(result['rejected'])}")
    print(f"   错误: {len(result['errors'])}")


def show_summary():
    """显示总结"""
    print("\n" + "=" * 60)
    print("📊 Phase 1 实施总结")
    print("=" * 60)
    
    # 统计文件
    cycle_files = []
    for scope in ['task', 'topic', 'project', 'system']:
        pattern = f"cycles/{scope}/*.yaml"
        import glob
        cycle_files.extend(glob.glob(pattern))
    
    print(f"\n创建的 CycleUnit: {len(cycle_files)}")
    for f in cycle_files:
        print(f"   - {os.path.basename(f)}")
    
    # 统计日志
    log_dir = "logs"
    exec_dir = "executions"
    
    log_count = 0
    exec_count = 0
    
    if os.path.exists(log_dir):
        for f in os.listdir(log_dir):
            if f.endswith('.jsonl'):
                with open(os.path.join(log_dir, f)) as file:
                    log_count += len(file.readlines())
    
    if os.path.exists(exec_dir):
        for f in os.listdir(exec_dir):
            if f.endswith('.jsonl'):
                with open(os.path.join(exec_dir, f)) as file:
                    exec_count += len(file.readlines())
    
    print(f"\n日志条目: {log_count}")
    print(f"执行条目: {exec_count}")
    
    print("\n" + "=" * 60)
    print("✅ Phase 1 实施演示完成！")
    print("=" * 60)


def main():
    """主函数"""
    # 初始化环境
    setup_environment()
    
    # 运行完整的 PDCA 循环
    cycle_id, review_context = demo_plan_phase()
    demo_do_phase(cycle_id)
    verdict, evidence = demo_check_phase(cycle_id)
    demo_act_phase(cycle_id, verdict, evidence)
    
    # 运行 Monitor
    demo_monitor_phase()
    
    # 运行 Scheduler
    demo_scheduler()
    
    # 显示总结
    show_summary()


if __name__ == "__main__":
    main()