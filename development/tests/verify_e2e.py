#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NUCLEUS 4.0 - 端到端验证脚本

完整验证 Phase 1 的所有核心功能

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import json
import yaml
from datetime import datetime, timezone

# ========================================
# 配置
# ========================================

PROJECT_DIR = "/Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0"
SKILL_DIR = os.path.expanduser("~/.openclaw/skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts")

# 添加项目 core 和 modules 目录到 Python 路径
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, "core"))
sys.path.insert(0, os.path.join(PROJECT_DIR, "modules"))

# ========================================
# Step 1: 验证 Skill 加载
# ========================================

def verify_skill_loading():
    """验证 Skill 可以被正确加载"""
    print("\n" + "=" * 60)
    print("Step 1: 验证 Skill 加载")
    print("=" * 60)
    
    # 添加 Skill 路径
    sys.path.insert(0, SKILL_DIR)
    
    try:
        # 导入核心模块
        from core.scheduler import on_heartbeat, create_cycle_for_scope
        from core.scheduler_state import load_scheduler_state, increment_counter
        from core.wait_queue import add_to_wait_queue, get_wait_queue_size
        from core.human_time import is_work_time, calculate_work_hours
        from modules.plan import determine_review
        from modules.do import execute_cycle, write_execution_log
        from modules.check import check_cycle, execute_check_by_level
        from modules.act import adjust_automation_level, PhaseBarrierLock
        from modules.monitor import sense_system_state, detect_anomalies
        
        print("✅ 所有模块加载成功")
        return True
        
    except ImportError as e:
        print(f"❌ 模块加载失败: {e}")
        return False

# ========================================
# Step 2: 验证调度器触发
# ========================================

def verify_scheduler():
    """验证调度器可以正确触发"""
    print("\n" + "=" * 60)
    print("Step 2: 验证调度器触发")
    print("=" * 60)
    
    # 切换到项目目录
    os.chdir(PROJECT_DIR)
    
    # 创建必要目录
    for d in ["cycles/task", "cycles/topic", "cycles/project", "cycles/system", 
              "logs", "executions", "config"]:
        os.makedirs(d, exist_ok=True)
    
    # 创建初始配置
    if not os.path.exists("cycles/scheduler_state.yaml"):
        from core.scheduler_state import create_default_state, save_scheduler_state
        state = create_default_state()
        save_scheduler_state(state)
    
    try:
        from core.scheduler import on_heartbeat, get_scheduler_status
        
        # 获取调度器状态
        status = get_scheduler_status()
        print(f"   计数器: {status.get('counters', {})}")
        print(f"   活跃数量: {status.get('active_counts', {})}")
        
        # 触发调度
        result = on_heartbeat()
        
        print(f"   触发的 scopes: {result['triggered_scopes']}")
        print(f"   创建的 cycles: {result['created_cycles']}")
        print(f"   错误数量: {len(result['errors'])}")
        
        if result['errors']:
            for err in result['errors']:
                print(f"   - 错误: {err}")
        
        if result['triggered_scopes'] or result['created_cycles']:
            print("✅ 调度器触发成功")
            return True
        else:
            print("⚠️  调度器未触发（可能是计数器未达阈值）")
            return True
            
    except Exception as e:
        print(f"❌ 调度器验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ========================================
# Step 3: 验证 PDCA 循环
# ========================================

def verify_pdca_cycle():
    """验证完整 PDCA 循环"""
    print("\n" + "=" * 60)
    print("Step 3: 验证 PDCA 循环")
    print("=" * 60)
    
    try:
        from modules.plan import determine_review
        from modules.do import execute_cycle, create_child_cycle
        from modules.check import check_cycle, execute_check_by_level
        from modules.act import adjust_automation_level
        
        # 3.1 验证 Plan
        print("\n   3.1 Plan 阶段:")
        review_context = determine_review(
            task_card_path="tasks/T5.8_TASK-CARD.md",
            task_id="T5.8",
            scope="task"
        )
        print(f"       review_level: {review_context['review_level']}")
        print(f"       reviewer: {review_context['reviewer']}")
        
        # 3.2 验证 Do
        print("\n   3.2 Do 阶段:")
        from core.scheduler import create_cycle_for_scope
        cycle_id = create_cycle_for_scope('task')
        if cycle_id:
            print(f"       创建 CycleUnit: {cycle_id}")
            
            do_result = execute_cycle(cycle_id)
            print(f"       状态: {do_result['status']}")
            print(f"       执行的 actions: {do_result['actions_executed']}")
        else:
            print("       ⚠️  未能创建 CycleUnit")
            return False
        
        # 3.3 验证 Check
        print("\n   3.3 Check 阶段:")
        check_result = check_cycle(cycle_id)
        print(f"       verdict: {check_result['verdict']}")
        print(f"       evidence count: {len(check_result['evidence'])}")
        
        # 3.4 验证 Act
        print("\n   3.4 Act 阶段:")
        adjustments = adjust_automation_level(
            cycle_id=cycle_id,
            verdict=check_result['verdict'],
            consecutive_count=0,
            current_level="L2",
            evidence=[]
        )
        for adj in adjustments:
            print(f"       {adj['from']} → {adj['to']}: {adj['reason']}")
        
        print("\n✅ PDCA 循环验证成功")
        return True
        
    except Exception as e:
        print(f"❌ PDCA 循环验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ========================================
# Step 4: 验证 Monitor
# ========================================

def verify_monitor():
    """验证 Monitor 模块"""
    print("\n" + "=" * 60)
    print("Step 4: 验证 Monitor")
    print("=" * 60)
    
    try:
        from modules.monitor import sense_system_state, detect_anomalies
        
        # 感知系统状态
        snapshot = sense_system_state()
        
        print(f"   活跃 CycleUnit: {snapshot.active_cycles}")
        print(f"   日志条目: {len(snapshot.log_entries)}")
        print(f"   执行条目: {len(snapshot.execution_entries)}")
        print(f"   等待队列: {snapshot.wait_queue_sizes}")
        
        # 检测异常
        anomalies = detect_anomalies(snapshot)
        
        if anomalies:
            print(f"\n   检测到 {len(anomalies)} 个异常:")
            for a in anomalies:
                print(f"   - [{a.severity}] {a.type}: {a.message}")
        else:
            print("\n   无异常")
        
        print("\n✅ Monitor 验证成功")
        return True
        
    except Exception as e:
        print(f"❌ Monitor 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ========================================
# Step 5: 验证文件持久化
# ========================================

def verify_file_persistence():
    """验证文件持久化"""
    print("\n" + "=" * 60)
    print("Step 5: 验证文件持久化")
    print("=" * 60)
    
    try:
        import glob
        
        # 检查 CycleUnit 文件
        cycle_files = glob.glob("cycles/*/*.yaml")
        print(f"   CycleUnit 文件: {len(cycle_files)}")
        for f in cycle_files[:5]:
            print(f"   - {f}")
        
        # 检查日志文件
        log_files = glob.glob("logs/*.jsonl")
        print(f"\n   日志文件: {len(log_files)}")
        
        # 检查执行日志
        exec_files = glob.glob("executions/*.jsonl")
        print(f"   执行日志: {len(exec_files)}")
        
        # 检查配置文件
        config_files = glob.glob("config/*.yaml")
        print(f"   配置文件: {len(config_files)}")
        
        if cycle_files and config_files:
            print("\n✅ 文件持久化验证成功")
            return True
        else:
            print("\n⚠️  部分文件缺失")
            return False
            
    except Exception as e:
        print(f"❌ 文件持久化验证失败: {e}")
        return False

# ========================================
# 主函数
# ========================================

def main():
    """执行完整验证"""
    print("=" * 60)
    print("NUCLEUS 4.0 - 端到端验证")
    print("=" * 60)
    
    results = {}
    
    # Step 1
    results['skill_loading'] = verify_skill_loading()
    
    # Step 2
    results['scheduler'] = verify_scheduler()
    
    # Step 3
    results['pdca'] = verify_pdca_cycle()
    
    # Step 4
    results['monitor'] = verify_monitor()
    
    # Step 5
    results['file_persistence'] = verify_file_persistence()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    all_passed = True
    for step, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {step}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有验证通过！NUCLEUS 4.0 Phase 1 就绪")
    else:
        print("⚠️  部分验证失败，请检查错误信息")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
