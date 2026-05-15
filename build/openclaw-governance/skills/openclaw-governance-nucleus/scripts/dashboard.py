#!/usr/bin/env python3
"""
NUCLEUS v4.0 轻量级监控仪表板

⭐ P2-2: 数据聚合和可视化工具

功能：
  - 统计 PDCA 执行情况
  - 识别阻塞项和瓶颈
  - 生成文本/JSON 报告
  - 可集成到 heartbeat 流程

设计原则：
  - 纯数据聚合（无 Web UI，符合 NUCLEUS 极简原则）
  - 输出格式：text（人类可读）或 json（机器可读）
  - 数据源：pdca/*.yaml + pdca/_state.yaml
"""

import argparse
import json
import os
import sys
import yaml
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


# ── 路径常量 ─────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).parent
_SKILL_ROOT = _SCRIPT_DIR.parent
PDCA_DIR = _SKILL_ROOT / "pdca"
STATE_FILE = PDCA_DIR / "_state.yaml"


def _load_pdca_data() -> List[Dict[str, Any]]:
    """加载所有 pdca/*.yaml 文件"""
    if not PDCA_DIR.exists():
        return []

    records = []
    for fname in sorted(PDCA_DIR.iterdir()):
        if not fname.suffix == '.yaml' or fname.name.startswith('_'):
            continue
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            if data and data.get('cycles'):
                records.append(data)
        except Exception:
            continue
    return records


def _load_state() -> Dict[str, Any]:
    """加载聚合状态文件"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data if data else {}
    return {}


def collect_metrics() -> Dict[str, Any]:
    """
    收集核心指标

    返回：
      {
        'summary': {...},          # 总览统计
        'tasks': {...},            # 任务级统计
        'topics': {...},           # Topic 级统计
        'projects': {...},         # Project 级统计
        'blockers': [...],         # 阻塞项列表
        'audit_queue': {...},      # 审计队列状态
        'velocity': {...},         # 执行速度
      }
    """
    records = _load_pdca_data()
    state = _load_state()

    # ── 任务统计 ─────────────────────────────────────
    total_tasks = len(records)
    active_tasks = 0
    completed_tasks = 0
    blocked_tasks = 0
    pending_review = 0

    verdict_counts = defaultdict(int)
    phase_counts = defaultdict(int)
    review_level_counts = defaultdict(int)

    blockers = []
    audit_queue_count = 0

    for record in records:
        task_id = record['task_card_id']
        cycles = record.get('cycles', [])

        if not cycles:
            continue

        last_cycle = cycles[-1]
        phase = last_cycle.get('phase')
        phase_counts[phase] += 1

        if phase == 'completed':
            completed_tasks += 1
        else:
            active_tasks += 1

        # Check for blockers
        do_data = last_cycle.get('d') or {}
        if do_data.get('status') == 'blocked':
            blocked_tasks += 1
            blockers.append({
                'task_id': task_id,
                'blocker': do_data.get('blocker'),
                'phase': phase
            })

        # Verdict statistics
        check_data = last_cycle.get('c') or {}
        verdict = check_data.get('verdict')
        if verdict:
            verdict_counts[verdict] += 1
            if verdict == 'pending':
                pending_review += 1

        # Review level statistics
        review_level = check_data.get('review_level')
        if review_level:
            review_level_counts[review_level] += 1

        # Audit queue
        if check_data.get('audit_eligible') and check_data.get('audit_result') is None:
            audit_queue_count += 1

    # ── Topic/Project 统计 ─────────────────────────────
    topic_verdicts = state.get('topic_verdicts', {})
    project_verdicts = state.get('project_verdicts', {})

    # ── 执行速度（最近 24h 完成数） ───────────────────
    now = datetime.now(timezone.utc)
    recent_completions = 0

    for record in records:
        for cycle in record.get('cycles', []):
            if cycle.get('phase') == 'completed':
                completed_at = cycle.get('completed_at')
                if completed_at:
                    try:
                        completed_time = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                        hours_ago = (now - completed_time).total_seconds() / 3600
                        if hours_ago <= 24:
                            recent_completions += 1
                    except Exception:
                        pass

    # ── 返回汇总指标 ───────────────────────────────────
    return {
        'summary': {
            'total_tasks': total_tasks,
            'active_tasks': active_tasks,
            'completed_tasks': completed_tasks,
            'blocked_tasks': blocked_tasks,
            'pending_review': pending_review,
            'completion_rate': f"{completed_tasks / total_tasks * 100:.1f}%" if total_tasks > 0 else "0%",
        },
        'tasks': {
            'by_phase': dict(phase_counts),
            'by_verdict': dict(verdict_counts),
            'by_review_level': dict(review_level_counts),
        },
        'topics': {
            'total': len(topic_verdicts),
            'by_verdict': _count_verdicts(topic_verdicts),
        },
        'projects': {
            'total': len(project_verdicts),
            'by_verdict': _count_verdicts(project_verdicts),
        },
        'blockers': blockers,
        'audit_queue': {
            'count': audit_queue_count,
            'status': 'healthy' if audit_queue_count < 5 else 'needs_attention',
        },
        'velocity': {
            'completions_24h': recent_completions,
            'rate': f"{recent_completions / 24:.2f} tasks/hour" if recent_completions > 0 else "0 tasks/hour",
        },
        'timestamp': now.isoformat(),
    }


def _count_verdicts(verdicts_dict: Dict[str, Any]) -> Dict[str, int]:
    """统计 verdict 分布"""
    counts = defaultdict(int)
    for entry in verdicts_dict.values():
        v = entry.get('verdict')
        if v:
            counts[v] += 1
    return dict(counts)


def format_text_report(metrics: Dict[str, Any]) -> str:
    """格式化为人类可读的文本报告"""
    lines = []
    lines.append("═" * 60)
    lines.append("NUCLEUS v4.0 监控仪表板")
    lines.append(f"生成时间: {metrics['timestamp']}")
    lines.append("═" * 60)
    lines.append("")

    # 总览
    summary = metrics['summary']
    lines.append("📊 总览统计")
    lines.append(f"  • 总任务数: {summary['total_tasks']}")
    lines.append(f"  • 活跃任务: {summary['active_tasks']}")
    lines.append(f"  • 已完成:   {summary['completed_tasks']} ({summary['completion_rate']})")
    lines.append(f"  • 阻塞中:   {summary['blocked_tasks']}")
    lines.append(f"  • 待审批:   {summary['pending_review']}")
    lines.append("")

    # 执行速度
    velocity = metrics['velocity']
    lines.append(f"⚡ 执行速度 (24h)")
    lines.append(f"  • 完成数: {velocity['completions_24h']}")
    lines.append(f"  • 速率: {velocity['rate']}")
    lines.append("")

    # 阻塞项
    blockers = metrics['blockers']
    if blockers:
        lines.append("⚠️  阻塞项")
        for b in blockers:
            lines.append(f"  • {b['task_id']}: {b['blocker']} (phase={b['phase']})")
        lines.append("")

    # 审计队列
    audit = metrics['audit_queue']
    lines.append(f"🔍 审计队列")
    lines.append(f"  • 待审计: {audit['count']}")
    lines.append(f"  • 状态: {audit['status']}")
    lines.append("")

    # Topic/Project
    topics = metrics['topics']
    projects = metrics['projects']
    lines.append(f"📁 层级统计")
    lines.append(f"  • Topics: {topics['total']} (by verdict: {topics['by_verdict']})")
    lines.append(f"  • Projects: {projects['total']} (by verdict: {projects['by_verdict']})")
    lines.append("")

    # 任务分布
    tasks = metrics['tasks']
    lines.append("📋 任务分布")
    lines.append(f"  • Phase: {tasks['by_phase']}")
    lines.append(f"  • Verdict: {tasks['by_verdict']}")
    lines.append(f"  • Review Level: {tasks['by_review_level']}")
    lines.append("")

    lines.append("═" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='NUCLEUS v4.0 监控仪表板 (P2-2)'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='输出格式（text=人类可读，json=机器可读）'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='输出文件路径（不指定则输出到 stdout）'
    )

    args = parser.parse_args()

    # 收集指标
    metrics = collect_metrics()

    # 格式化输出
    if args.format == 'text':
        output = format_text_report(metrics)
    else:
        output = json.dumps(metrics, ensure_ascii=False, indent=2)

    # 输出到文件或 stdout
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"报告已生成: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
