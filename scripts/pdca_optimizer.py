#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDCA Optimizer - 分析和优化PDCA流程的工具

该工具分析PDCA执行数据，识别瓶颈、低效环节和改进机会，
为NUCLEUS-4.0的流程优化提供指导。
"""

import os
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import statistics


def analyze_bottlenecks(pdca_dir: str) -> Dict[str, Any]:
    """
    分析PDCA流程中的瓶颈
    """
    if not os.path.exists(pdca_dir):
        return {"error": f"PDCA目录不存在: {pdca_dir}"}
    
    bottleneck_analysis = {
        "bottleneck_tasks": [],
        "common_failures": {},
        "cycle_efficiency": {
            "average_cycles_per_completion": 0,
            "tasks_requiring_multiple_cycles": 0,
            "total_tasks_analyzed": 0
        },
        "timing_analysis": {
            "average_plan_time": None,
            "average_do_time": None,
            "average_check_time": None,
            "average_act_time": None
        },
        "recommendations": []
    }
    
    cycle_counts = []
    plan_times = []
    do_times = []
    check_times = []
    act_times = []
    
    for filename in os.listdir(pdca_dir):
        if not filename.endswith('.yaml') or filename.startswith('_'):
            continue
            
        filepath = os.path.join(pdca_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not data or not data.get('cycles'):
                continue
                
            task_id = data['task_card_id']
            task_cycles = data['cycles']
            total_cycles = len(task_cycles)
            
            # 统计循环次数
            if total_cycles > 1:
                bottleneck_analysis["cycle_efficiency"]["tasks_requiring_multiple_cycles"] += 1
                bottleneck_analysis["bottleneck_tasks"].append({
                    "task_id": task_id,
                    "cycle_count": total_cycles,
                    "last_verdict": task_cycles[-1].get('c', {}).get('verdict', 'N/A')
                })
            
            cycle_counts.append(total_cycles)
            
            # 分析时间间隔
            for cycle in task_cycles:
                # 检查各个阶段的时间戳
                timestamps = {}
                if cycle.get('p') and cycle['p'].get('timestamp'):
                    timestamps['plan'] = cycle['p']['timestamp']
                if cycle.get('d') and cycle['d'].get('timestamp'):
                    timestamps['do'] = cycle['d']['timestamp']
                if cycle.get('c') and cycle['c'].get('timestamp'):
                    timestamps['check'] = cycle['c']['timestamp']
                if cycle.get('a') and cycle['a'].get('timestamp'):
                    timestamps['act'] = cycle['a']['timestamp']
                
                # 计算各阶段耗时
                if 'plan' in timestamps and 'do' in timestamps:
                    try:
                        plan_start = datetime.fromisoformat(timestamps['plan'].replace('Z', '+00:00'))
                        do_end = datetime.fromisoformat(timestamps['do'].replace('Z', '+00:00'))
                        plan_times.append((do_end - plan_start).total_seconds() / 3600)  # 转换为小时
                    except:
                        pass
                        
                if 'do' in timestamps and 'check' in timestamps:
                    try:
                        do_start = datetime.fromisoformat(timestamps['do'].replace('Z', '+00:00'))
                        check_end = datetime.fromisoformat(timestamps['check'].replace('Z', '+00:00'))
                        do_times.append((check_end - do_start).total_seconds() / 3600)
                    except:
                        pass
                        
                if 'check' in timestamps and 'act' in timestamps:
                    try:
                        check_start = datetime.fromisoformat(timestamps['check'].replace('Z', '+00:00'))
                        act_end = datetime.fromisoformat(timestamps['act'].replace('Z', '+00:00'))
                        check_times.append((act_end - check_start).total_seconds() / 3600)
                    except:
                        pass
                        
                if 'act' in timestamps and cycle.get('completed_at'):
                    try:
                        act_start = datetime.fromisoformat(timestamps['act'].replace('Z', '+00:00'))
                        completed = datetime.fromisoformat(cycle['completed_at'].replace('Z', '+00:00'))
                        act_times.append((completed - act_start).total_seconds() / 3600)
                    except:
                        pass
                
                # 分析失败原因
                if cycle.get('c'):
                    verdict = cycle['c'].get('verdict')
                    if verdict in ['fail', 'partial']:
                        evidence = cycle['c'].get('evidence', [])
                        for ev in evidence:
                            if ev in bottleneck_analysis["common_failures"]:
                                bottleneck_analysis["common_failures"][ev] += 1
                            else:
                                bottleneck_analysis["common_failures"][ev] = 1
    
        except Exception as e:
            continue  # 跳过有问题的文件
    
    bottleneck_analysis["cycle_efficiency"]["total_tasks_analyzed"] = len(cycle_counts)
    
    if cycle_counts:
        bottleneck_analysis["cycle_efficiency"]["average_cycles_per_completion"] = statistics.mean(cycle_counts)
    
    # 计算平均时间
    if plan_times:
        bottleneck_analysis["timing_analysis"]["average_plan_time"] = statistics.mean(plan_times)
    if do_times:
        bottleneck_analysis["timing_analysis"]["average_do_time"] = statistics.mean(do_times)
    if check_times:
        bottleneck_analysis["timing_analysis"]["average_check_time"] = statistics.mean(check_times)
    if act_times:
        bottleneck_analysis["timing_analysis"]["average_act_time"] = statistics.mean(act_times)
    
    # 生成改进建议
    if bottleneck_analysis["cycle_efficiency"]["average_cycles_per_completion"] > 2:
        bottleneck_analysis["recommendations"].append(
            "⚠️ 平均完成任务需要超过2个循环周期，考虑改进初始规划质量"
        )
    
    if bottleneck_analysis["cycle_efficiency"]["tasks_requiring_multiple_cycles"] / max(bottleneck_analysis["cycle_efficiency"]["total_tasks_analyzed"], 1) > 0.5:
        bottleneck_analysis["recommendations"].append(
            "⚠️ 超过一半的任务需要多次迭代，可能存在规划或执行问题"
        )
    
    # 排序瓶颈任务
    bottleneck_analysis["bottleneck_tasks"].sort(key=lambda x: x["cycle_count"], reverse=True)
    
    return bottleneck_analysis


def print_optimization_report(analysis: Dict[str, Any]):
    """
    打印优化报告
    """
    print("="*80)
    print("PDCA 流程优化分析报告")
    print("="*80)
    
    if "error" in analysis:
        print(f"错误: {analysis['error']}")
        return
    
    # 效率指标
    eff = analysis["cycle_efficiency"]
    print(f"📊 流程效率指标:")
    print(f"   • 分析任务数: {eff['total_tasks_analyzed']}")
    print(f"   • 需要多次迭代的任务: {eff['tasks_requiring_multiple_cycles']}")
    print(f"   • 平均完成周期数: {eff['average_cycles_per_completion']:.2f}")
    print()
    
    # 时间分析
    timing = analysis["timing_analysis"]
    print("⏱️  各阶段平均耗时:")
    if timing["average_plan_time"]:
        print(f"   • Plan 阶段: {timing['average_plan_time']:.2f} 小时")
    if timing["average_do_time"]:
        print(f"   • Do 阶段: {timing['average_do_time']:.2f} 小时")
    if timing["average_check_time"]:
        print(f"   • Check 阶段: {timing['average_check_time']:.2f} 小时")
    if timing["average_act_time"]:
        print(f"   • Act 阶段: {timing['average_act_time']:.2f} 小时")
    print()
    
    # 瓶颈任务
    print(f"🚨 严重瓶颈任务 (循环次数 > 3):")
    severe_bottlenecks = [t for t in analysis["bottleneck_tasks"] if t["cycle_count"] > 3]
    if severe_bottlenecks:
        for task in severe_bottlenecks[:10]:  # 只显示前10个
            print(f"   • {task['task_id']}: {task['cycle_count']} 次循环 (最后结论: {task['last_verdict']})")
    else:
        print("   • 未发现严重瓶颈任务")
    print()
    
    # 常见失败原因
    print("❌ 常见失败原因:")
    sorted_failures = sorted(analysis["common_failures"].items(), key=lambda x: x[1], reverse=True)
    if sorted_failures:
        for reason, count in sorted_failures[:10]:  # 只显示前10个
            print(f"   • {reason[:60]}{'...' if len(reason) > 60 else ''}: {count} 次")
    else:
        print("   • 未发现常见失败原因")
    print()
    
    # 改进建议
    print("💡 改进建议:")
    if analysis["recommendations"]:
        for rec in analysis["recommendations"]:
            print(f"   {rec}")
    else:
        print("   • 未发现明显需要改进的地方")
    
    # 具体优化建议
    print("\n🔧 具体优化措施:")
    print("   • 如果Plan阶段耗时过长: 考虑预先准备规划模板或检查清单")
    print("   • 如果Do阶段耗时过长: 检查任务分解是否足够细粒度")
    print("   • 如果Check阶段耗时过长: 优化验收标准的清晰度")
    print("   • 如果Act阶段耗时过长: 简化总结和下一步规划流程")
    print("   • 高频失败原因: 针对性地解决这些问题")
    
    print()
    print(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
    
    analysis = analyze_bottlenecks(pdca_dir)
    print_optimization_report(analysis)


if __name__ == "__main__":
    main()