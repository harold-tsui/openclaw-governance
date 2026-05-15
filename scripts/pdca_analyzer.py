#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDCA Analyzer - 分析PDCA执行情况的工具

该工具扫描pdca/目录下的所有YAML文件，分析执行趋势、成功率、瓶颈等，
为NUCLEUS-4-0的持续改进提供数据支持。
"""

import os
import yaml
import json
from datetime import datetime
from typing import Dict, List, Any
import argparse


def analyze_pdca_data(pdca_dir: str) -> Dict[str, Any]:
    """
    分析pdca目录中的所有YAML文件
    """
    if not os.path.exists(pdca_dir):
        return {"error": f"PDCA目录不存在: {pdca_dir}"}
    
    analysis_results = {
        "summary": {
            "total_tasks": 0,
            "completed_tasks": 0,
            "active_tasks": 0,
            "failed_tasks": 0,
            "pending_tasks": 0
        },
        "verdict_stats": {
            "pass": 0,
            "partial": 0,
            "fail": 0,
            "skip": 0,
            "pending": 0
        },
        "cycle_stats": {
            "avg_cycles_per_task": 0,
            "max_cycles_in_task": 0,
            "tasks_with_multiple_cycles": 0
        },
        "tasks": []
    }
    
    total_cycles = 0
    
    for filename in os.listdir(pdca_dir):
        if not filename.endswith('.yaml') or filename.startswith('_'):
            continue
            
        filepath = os.path.join(pdca_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not data or not data.get('cycles'):
                continue
                
            task_analysis = {
                "task_id": data['task_card_id'],
                "total_cycles": len(data['cycles']),
                "latest_cycle": None,
                "status": "active"  # 默认为活跃
            }
            
            total_cycles += len(data['cycles'])
            
            # 分析最新的cycle
            if data['cycles']:
                latest_cycle = data['cycles'][-1]
                task_analysis["latest_cycle"] = {
                    "index": latest_cycle['cycle_index'],
                    "phase": latest_cycle['phase'],
                    "verdict": None
                }
                
                # 获取最新的verdict
                if latest_cycle.get('c'):
                    verdict = latest_cycle['c'].get('verdict')
                    if verdict:
                        task_analysis["latest_cycle"]["verdict"] = verdict
                        analysis_results["verdict_stats"][verdict] = analysis_results["verdict_stats"].get(verdict, 0) + 1
                        
                        # 根据最新verdict统计任务状态
                        if verdict == 'pass':
                            analysis_results["summary"]["completed_tasks"] += 1
                            task_analysis["status"] = "completed"
                        elif verdict == 'fail':
                            analysis_results["summary"]["failed_tasks"] += 1
                        elif verdict == 'pending':
                            analysis_results["summary"]["pending_tasks"] += 1
                            
                # 检查任务是否完成
                if latest_cycle['phase'] == 'completed':
                    analysis_results["summary"]["completed_tasks"] += 1
                    task_analysis["status"] = "completed"
                else:
                    analysis_results["summary"]["active_tasks"] += 1
                    
            # 检查是否有多个cycles
            if len(data['cycles']) > 1:
                analysis_results["cycle_stats"]["tasks_with_multiple_cycles"] += 1
                
            # 更新最大cycles数
            if len(data['cycles']) > analysis_results["cycle_stats"]["max_cycles_in_task"]:
                analysis_results["cycle_stats"]["max_cycles_in_task"] = len(data['cycles'])
                
            analysis_results["tasks"].append(task_analysis)
            analysis_results["summary"]["total_tasks"] += 1
            
        except Exception as e:
            print(f"警告：无法分析文件 {filepath}: {str(e)}")
            continue
    
    # 计算平均cycles数
    if analysis_results["summary"]["total_tasks"] > 0:
        analysis_results["cycle_stats"]["avg_cycles_per_task"] = (
            total_cycles / analysis_results["summary"]["total_tasks"]
        )
    
    return analysis_results


def print_analysis_report(results: Dict[str, Any]):
    """
    打印分析报告
    """
    print("="*60)
    print("PDCA 执行情况分析报告")
    print("="*60)
    
    if "error" in results:
        print(f"错误: {results['error']}")
        return
        
    # 摘要信息
    summary = results["summary"]
    print(f"任务总数: {summary['total_tasks']}")
    print(f"已完成任务: {summary['completed_tasks']}")
    print(f"活跃任务: {summary['active_tasks']}")
    print(f"失败任务: {summary['failed_tasks']}")
    print(f"待审批任务: {summary['pending_tasks']}")
    print()
    
    # Verdict统计
    verdicts = results["verdict_stats"]
    print("Verdict 统计:")
    for verdict, count in verdicts.items():
        print(f"  {verdict.upper()}: {count}")
    print()
    
    # Cycle统计
    cycles = results["cycle_stats"]
    print("Cycle 统计:")
    print(f"  平均每任务Cycle数: {cycles['avg_cycles_per_task']:.2f}")
    print(f"  单任务最大Cycle数: {cycles['max_cycles_in_task']}")
    print(f"  有多次迭代的任务数: {cycles['tasks_with_multiple_cycles']}")
    print()
    
    # 任务详情（只显示部分）
    print("任务详情 (最多显示10个):")
    for i, task in enumerate(results["tasks"][:10]):
        latest = task["latest_cycle"]
        if latest:
            verdict = latest.get("verdict", "N/A")
            print(f"  {task['task_id']}: {task['status']} ({task['total_cycles']} cycles), 最新verdict: {verdict}")
        else:
            print(f"  {task['task_id']}: {task['status']} ({task['total_cycles']} cycles)")
    
    if len(results["tasks"]) > 10:
        print(f"  ... 还有 {len(results['tasks']) - 10} 个任务")


def main():
    parser = argparse.ArgumentParser(description='PDCA 执行情况分析工具')
    parser.add_argument('--pdca-dir', default='./pdca', 
                       help='PDCA数据目录路径 (默认: ./pdca)')
    parser.add_argument('--output-format', choices=['console', 'json'], 
                       default='console', help='输出格式 (默认: console)')
    
    args = parser.parse_args()
    
    results = analyze_pdca_data(args.pdca_dir)
    
    if args.output_format == 'console':
        print_analysis_report(results)
    elif args.output_format == 'json':
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()