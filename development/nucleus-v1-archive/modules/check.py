#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Module - 验收阶段

实现 PDCA 循环的 Check 阶段，负责验收 verdict 和 human_review 流程。

依据：ARCH v1.4.3 §3.3 + pdca-check-protocol v1.3

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import json
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


# ── 常量定义 ────────────────────────────────────────

VALID_LEVELS = ['L0', 'L1', 'L2', 'L3']

# 级别对应的 reviewer
REVIEWER_MAPPING = {
    'L0': None,
    'L1': None,
    'L2': 'yin-yue',
    'L3': 'harold'
}


# ── 核心接口 ────────────────────────────────────────

def check_cycle(cycle_id: str) -> Dict[str, Any]:
    """
    执行 CycleUnit 的 Check 阶段
    
    Args:
        cycle_id: CycleUnit ID
    
    Returns:
        {
            'verdict': 'pass|partial|fail|skip|pending|pending_sampling',
            'evidence': List[Dict],
            'human_review_triggered': bool,
            'errors': List[str]
        }

    Note:
        L2 返回 pending_sampling，由 LLM（银月）在 SKILL.md 协议中决定最终 verdict
        L3 返回 pending，等待 Harold 飞书审批后回写 verdict
    """
    
    result = {
        'verdict': 'skip',
        'evidence': [],
        'human_review_triggered': False,
        'errors': []
    }
    
    try:
        # 1. 加载 CycleUnit
        cycle_path = _get_cycle_path(cycle_id)
        if not os.path.exists(cycle_path):
            result['verdict'] = 'fail'
            result['errors'].append(f"CycleUnit not found: {cycle_path}")
            return result
        
        with open(cycle_path, 'r', encoding='utf-8') as f:
            cycle_data = yaml.safe_load(f)
        
        # 2. 获取 review_level（从 task-card 文件，优先读 plan.task_card_path）
        task_card_path = (
            (cycle_data.get('plan') or {}).get('task_card_path')
            or cycle_data.get('task_card_path')
        )
        review_level = _get_review_level_from_task_card(task_card_path)
        
        if review_level not in VALID_LEVELS:
            result['errors'].append(f"Invalid review_level: {review_level}")
            return result
        
        # 3. 执行对应级别的验收
        check_result = execute_check_by_level(cycle_id, review_level)
        result.update(check_result)
        
        # 4. 如果需要人工审批，触发 human_review
        if review_level == 'L3':
            human_review_success = trigger_human_review(cycle_id, 'harold')
            result['human_review_triggered'] = human_review_success
        
        # 5. 更新 CycleUnit 的 check 字段
        _update_check_status(cycle_id, result)
        
        # 6. 写入执行日志
        write_execution_log(
            cycle_id=cycle_id,
            action='check_cycle',
            result=result['verdict'],
            metadata={
                'review_level': review_level,
                'human_review_triggered': result['human_review_triggered']
            }
        )
    
    except Exception as e:
        result['verdict'] = 'fail'
        result['errors'].append(str(e))
        write_execution_log(
            cycle_id=cycle_id,
            action='check_cycle',
            result='failed',
            metadata={'error': str(e)}
        )
    
    return result


def execute_check_by_level(cycle_id: str, review_level: str) -> Dict[str, Any]:
    """
    根据 review_level 执行对应级别的验收
    
    Args:
        cycle_id: CycleUnit ID
        review_level: 验收级别（L0/L1/L2/L3）
    
    Returns:
        验收结果字典
    """
    
    result = {
        'verdict': 'skip',
        'evidence': [],
        'errors': []
    }
    
    if review_level == 'L0':
        # L0：免审
        result['verdict'] = 'skip'
        result['evidence'].append({
            'type': 'auto_approval',
            'message': 'L0 level - auto approved (skip)',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    elif review_level == 'L1':
        # L1：机器自检（异常上报）
        evidence = collect_evidence(cycle_id)
        result['evidence'] = evidence
        
        # 检查是否有错误
        has_errors = any(e.get('level') == 'ERROR' for e in evidence)
        if has_errors:
            result['verdict'] = 'fail'
        else:
            result['verdict'] = 'pass'
    
    elif review_level == 'L2':
        # L2：银月抽样核查（20-30%），Python 只收集证据
        # verdict 由 LLM（银月）在 SKILL.md 协议中判定，此处设为 pending_sampling
        evidence = collect_evidence(cycle_id)
        result['evidence'] = evidence
        result['verdict'] = 'pending_sampling'
    
    elif review_level == 'L3':
        # L3：全量人工（等待人工响应）
        evidence = collect_evidence(cycle_id)
        result['evidence'] = evidence
        result['verdict'] = 'pending'  # 等待人工审批
    
    return result


def trigger_human_review(cycle_id: str, reviewer: str) -> bool:
    """
    触发人工审批流程
    
    Args:
        cycle_id: CycleUnit ID
        reviewer: 审批人
    
    Returns:
        bool: 是否成功触发
    """
    
    try:
        # 1. 发送飞书通知
        notification_sent = send_feishu_notification(cycle_id, reviewer)
        
        if not notification_sent:
            return False
        
        # 2. 更新 CycleUnit 的 human_review 状态
        _update_human_review_status(cycle_id, 'pending')
        
        return True
    
    except Exception as e:
        print(f"ERROR: Failed to trigger human review: {e}")
        return False


def write_review_request(cycle_id: str, reviewer: str, cycle_path: str) -> bool:
    """
    写入 review_request YAML，供 LLM 通过 feishu_post 发送通知。

    设计原则：飞书通知属于 LLM（银月）职责，Python 不直接调用飞书 API。
    Python 只写请求文件；LLM 读取后在 SKILL.md §4.2 Step 4 中用 feishu_post 发送。

    请求文件路径：cycles/pending_review/{cycle_id}_review_request.yaml

    Args:
        cycle_id: CycleUnit ID
        reviewer: 审批人（harold / yin-yue）
        cycle_path: CycleUnit 文件路径（用于读取任务摘要）

    Returns:
        bool: 是否成功写入
    """
    try:
        # 读取 CycleUnit 基本信息用于通知内容
        task_card_id = 'unknown'
        scope = 'task'
        if os.path.exists(cycle_path):
            with open(cycle_path, 'r', encoding='utf-8') as f:
                cycle_data = yaml.safe_load(f) or {}
            task_card_id = cycle_data.get('task_card_id', 'unknown')
            scope = cycle_data.get('scope', 'task')

        request = {
            'cycle_id': cycle_id,
            'scope': scope,
            'task_card_id': task_card_id,
            'reviewer': reviewer,
            'requested_at': datetime.now(timezone.utc).isoformat(),
            'status': 'pending',
            'feishu_message_id': None,  # LLM 发送成功后回填
            'message_template': (
                f"【NUCLEUS 4.0 审批请求】\n"
                f"任务：{task_card_id}（{scope} 级）\n"
                f"CycleUnit：{cycle_id}\n"
                f"需要审批人：{reviewer}\n"
                f"请查阅对应 Task-CARD 并回复验收结论（pass/partial/fail）。"
            )
        }

        request_dir = 'cycles/pending_review'
        os.makedirs(request_dir, exist_ok=True)
        request_path = f"{request_dir}/{cycle_id}_review_request.yaml"

        tmp_path = request_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            yaml.dump(request, f, allow_unicode=True, default_flow_style=False)
        os.replace(tmp_path, request_path)

        return True

    except Exception as e:
        print(f"ERROR: Failed to write review request: {e}")
        return False


def send_feishu_notification(cycle_id: str, reviewer: str) -> bool:
    """
    兼容旧接口：内部调用 write_review_request()。
    保留此函数名以避免破坏已有调用点。
    """
    cycle_path = _get_cycle_path(cycle_id)
    return write_review_request(cycle_id, reviewer, cycle_path)


def collect_evidence(cycle_id: str) -> List[Dict]:
    """
    收集验收证据
    
    Args:
        cycle_id: CycleUnit ID
    
    Returns:
        证据列表
    """
    
    evidence = []
    
    try:
        # 1. 从 executions/ 目录收集执行日志
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        exec_file = f"executions/{today}.jsonl"
        
        if os.path.exists(exec_file):
            with open(exec_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and cycle_id in line:
                        try:
                            entry = json.loads(line)
                            evidence.append({
                                'type': 'execution_log',
                                'data': entry,
                                'timestamp': entry.get('timestamp', datetime.now(timezone.utc).isoformat())
                            })
                        except json.JSONDecodeError:
                            continue
        
        # 2. 从 logs/ 目录收集观测日志
        log_file = f"logs/{today}.jsonl"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and cycle_id in line:
                        try:
                            entry = json.loads(line)
                            evidence.append({
                                'type': 'observation_log',
                                'data': entry,
                                'timestamp': entry.get('timestamp', datetime.now(timezone.utc).isoformat())
                            })
                        except json.JSONDecodeError:
                            continue
        
        # 3. 添加默认证据
        if not evidence:
            evidence.append({
                'type': 'default_evidence',
                'message': 'No specific evidence found',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
    
    except Exception as e:
        evidence.append({
            'type': 'error',
            'message': f'Failed to collect evidence: {str(e)}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    return evidence


# ── 辅助函数 ────────────────────────────────────────

def _get_cycle_path(cycle_id: str) -> str:
    """获取 CycleUnit 文件路径"""
    scope = cycle_id.split('-')[0] if '-' in cycle_id else 'task'
    return f"cycles/{scope}/{cycle_id}.yaml"


def _get_review_level_from_task_card(task_card_path: str) -> str:
    """从 task-card 文件路径读取并解析 review_level

    Args:
        task_card_path: Task-CARD 文件的完整路径（来自 CycleUnit.plan.task_card_path）

    Returns:
        'L0'|'L1'|'L2'|'L3'；路径为空或文件不存在时回退到 'L3'（最安全默认值）
    """
    import sys
    sys.path.append(os.path.dirname(__file__))
    from plan import parse_review_level_from_task_card

    if task_card_path and os.path.exists(task_card_path):
        try:
            with open(task_card_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return parse_review_level_from_task_card(content)
        except Exception:
            pass

    # task_card_path 为空或文件不存在，回退到最安全的 L3
    return 'L3'


def _update_check_status(cycle_id: str, check_result: Dict) -> None:
    """更新 Check 阶段状态，verdict 确定时推进 phase → act"""
    try:
        cycle_path = _get_cycle_path(cycle_id)
        if not os.path.exists(cycle_path):
            return

        with open(cycle_path, 'r', encoding='utf-8') as f:
            cycle_data = yaml.safe_load(f)

        if 'check' not in cycle_data:
            cycle_data['check'] = {}

        cycle_data['check']['verdict'] = check_result['verdict']
        cycle_data['check']['evidence'] = check_result['evidence']

        # verdict 确定（非 pending/pending_sampling）时推进 phase → act
        # pending* 状态表示等待外部审批，本轮不推进
        if check_result['verdict'] not in ('pending', 'pending_sampling'):
            cycle_data['phase'] = 'act'

        cycle_data['metadata']['updated_at'] = datetime.now(timezone.utc).isoformat()

        tmp_path = cycle_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
        os.replace(tmp_path, cycle_path)

    except Exception as e:
        print(f"WARNING: Failed to update check status: {e}")


def _update_human_review_status(cycle_id: str, status: str) -> None:
    """更新 human_review 状态"""
    try:
        cycle_path = _get_cycle_path(cycle_id)
        if not os.path.exists(cycle_path):
            return
        
        with open(cycle_path, 'r', encoding='utf-8') as f:
            cycle_data = yaml.safe_load(f)
        
        if 'check' not in cycle_data:
            cycle_data['check'] = {}
        
        if 'human_review' not in cycle_data['check']:
            cycle_data['check']['human_review'] = {}
        
        cycle_data['check']['human_review']['status'] = status
        cycle_data['check']['human_review']['requested_at'] = datetime.now(timezone.utc).isoformat()
        
        cycle_data['metadata']['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        with open(cycle_path, 'w', encoding='utf-8') as f:
            yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
    
    except Exception as e:
        print(f"WARNING: Failed to update human review status: {e}")


def _record_feishu_message_id(cycle_id: str, message_id: str) -> None:
    """记录飞书消息 ID"""
    try:
        cycle_path = _get_cycle_path(cycle_id)
        if not os.path.exists(cycle_path):
            return
        
        with open(cycle_path, 'r', encoding='utf-8') as f:
            cycle_data = yaml.safe_load(f)
        
        if 'check' not in cycle_data:
            cycle_data['check'] = {}
        
        if 'human_review' not in cycle_data['check']:
            cycle_data['check']['human_review'] = {}
        
        cycle_data['check']['human_review']['feishu_message_id'] = message_id
        
        with open(cycle_path, 'w', encoding='utf-8') as f:
            yaml.dump(cycle_data, f, allow_unicode=True, default_flow_style=False)
    
    except Exception as e:
        print(f"WARNING: Failed to record Feishu message ID: {e}")


def write_execution_log(
    cycle_id: str,
    action: str,
    result: str,
    metadata: Optional[Dict] = None
) -> None:
    """写入执行日志（复用 do.py 的实现）"""
    from modules.do import write_execution_log as do_write_log
    do_write_log(cycle_id, action, result, metadata)


# ── CLI 入口 ────────────────────────────────────────
# 用法：
#   python modules/check.py collect_evidence --cycle-id X
#   python modules/check.py check --cycle-id X

if __name__ == "__main__":
    import argparse
    import json
    import sys as _sys

    parser = argparse.ArgumentParser(description='Check Module CLI')
    subparsers = parser.add_subparsers(dest='command')

    # collect_evidence 子命令
    ev_parser = subparsers.add_parser('collect_evidence', help='收集验收证据并输出 JSON')
    ev_parser.add_argument('--cycle-id', required=True, help='CycleUnit ID')

    # check 子命令（完整 Check 阶段）
    check_parser = subparsers.add_parser('check', help='执行完整 Check 阶段并输出结果 JSON')
    check_parser.add_argument('--cycle-id', required=True, help='CycleUnit ID')

    args = parser.parse_args()

    if args.command == 'collect_evidence':
        evidence = collect_evidence(args.cycle_id)
        print(json.dumps(evidence, ensure_ascii=False, indent=2, default=str))

    elif args.command == 'check':
        result = check_cycle(args.cycle_id)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

    else:
        parser.print_help()
        _sys.exit(1)