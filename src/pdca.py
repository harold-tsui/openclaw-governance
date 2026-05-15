#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdca.py - PDCA 状态记录器 + 层间传播 + 并发控制

Python 职责（唯一）：记录 LLM 执行 PDCA 各阶段后的状态，原子写入 pdca/ 目录。
LLM 职责：所有推断、执行、判断、决策。

新增功能（Phase 2）：
  - aggregate(): 轻量级层间传播，扫描 pdca/*.yaml 聚合 verdict 到 _state.yaml
  - check_concurrency(): 并发上限校验（task≤10, topic≤5, project≤3）

新增功能（v8.1）：
  - cqo_review(): CQO 合规闸门，Do→Check 之间的过程性检查（pass/revise/reject）

用法：
  python scripts/pdca.py p   --task-card-id T1.1 --summary "..." [--criteria "a|b"] [--task-card-path PATH] [--topic-id T06] [--project-id ZT-P015]
  python scripts/pdca.py d   --task-card-id T1.1 --summary "..." --status completed|blocked|partial [--blocker "..."]
  python scripts/pdca.py cqo-review --task-card-id T1.1 --result pass|revise|reject [--report-path PATH] [--issues "CQO-01|CQO-03"]
  python scripts/pdca.py c   --task-card-id T1.1 --verdict pass|partial|fail|skip|pending --level L0|L1|L2|L3 [--evidence "a|b"]
  python scripts/pdca.py a   --task-card-id T1.1 --summary "..." [--next-task T1.2] [--lessons "a|b"]
  python scripts/pdca.py status  --task-card-id T1.1
  python scripts/pdca.py pending

ADAS 级别与 Check 行为：
  L0/L1  自验收，不允许 verdict=pending（无需人工介入）
  L2     抽样审批，允许 pass 或 pending（由 LLM 决定是否抽中）
  L3     Harold 全量审批，首次 Check 必须 verdict=pending；Harold 回复后第二次调用记录最终结论

Task-CARD 状态更新由 LLM 负责（写穿透规则，见 nucleus SKILL.md §4.2 Harness 规则 A2）：
  pdca.py a() 完成后，LLM 必须立即：
    1. 更新 Task-CARD 状态标记（Task-CARD 是唯一真相源）
    2. 更新 MISSION_BOARD 对应条目状态
  pdca.py 不再存储 task_state 字段（减少状态来源）。

所有命令输出 JSON。

Author: 张铁 (CQO)
Date: 2026-04-16
"""

import os
import re
import sys
import json
import hashlib
import argparse
import yaml
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ── 常量 ─────────────────────────────────────────────

# ⭐ P0-2 修复：使用绝对路径，移除 CWD 依赖
# 计算 skill 根目录的绝对路径
# ⭐ P0-3 修复：使用 realpath 解析软链接，确保通过软链接运行时路径正确
_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_SKILL_ROOT = os.path.dirname(_SCRIPT_DIR)  # scripts/ 的上级

PDCA_DIR = os.path.join(_SKILL_ROOT, "pdca")
STATE_FILE = os.path.join(PDCA_DIR, "_state.yaml")  # 聚合状态文件（单文件方案）
LOG_DIR = os.path.join(_SKILL_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "pdca.log")  # 执行日志（JSON lines，一行一次调用）
CONFIG_FILE = os.path.join(_SKILL_ROOT, "config", "pdca_config.yaml")

VALID_STATUSES = {'completed', 'blocked', 'partial'}
VALID_VERDICTS = {'pass', 'partial', 'fail', 'skip', 'pending'}
VALID_LEVELS   = {'L0', 'L1', 'L2', 'L3'}
FINAL_VERDICTS = {'pass', 'partial', 'fail', 'skip'}  # 触发 phase → act
CQO_REVIEW_RESULTS = {'pass', 'revise', 'reject'}
CQO_REVISE_LIMIT = 3  # 同一 cycle 内 revise 上限


# ── 配置加载 ─────────────────────────────────────────

def _load_config() -> Dict[str, Any]:
    """
    从 config/pdca_config.yaml 加载可配置参数。

    向后兼容：缺失的文件或字段使用默认值，不会导致启动失败。
    """
    defaults: Dict[str, Any] = {
        'adas': {
            'levels_self_approve': ['L0', 'L1'],
            'level_full_human': 'L3',
        },
        'concurrency': {
            'task': 10,
            'topic': 5,
            'project': 3,
        },
        'audit': {
            'score_threshold': 80,
        },
        'pending_timeout': {
            'warning_days': 7,
            'critical_days': 14,
        },
        'weighted_aggregate': {
            'pass_threshold': 0.80,
            'fail_threshold': 0.20,
        },
        'limits': {
            'max_yaml_size_kb': 1024,
            'archive_older_than_days': 30,
            'max_pdca_files': 500,
            'max_cycles_per_task': 20,
        },
    }
    if not os.path.exists(CONFIG_FILE):
        return defaults
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        if not cfg or not isinstance(cfg, dict):
            return defaults
        # 深度合并：cfg 覆盖 defaults
        for section, values in cfg.items():
            if isinstance(values, dict) and section in defaults:
                defaults[section].update(values)
            else:
                defaults[section] = values
        return defaults
    except Exception:
        return defaults


# 模块级配置单例（首次 import 时加载）
_CFG = _load_config()

# ── 从配置派生的常量（保持向后兼容） ───────────────────

# ADAS 分级规则
LEVELS_SELF_APPROVE = set(_CFG['adas']['levels_self_approve'])
LEVEL_FULL_HUMAN = _CFG['adas']['level_full_human']

# 并发上限
CONCURRENCY_LIMIT_TASK = _CFG['concurrency']['task']
CONCURRENCY_LIMIT_TOPIC = _CFG['concurrency']['topic']
CONCURRENCY_LIMIT_PROJECT = _CFG['concurrency']['project']

# 审计评分阈值
AUDIT_SCORE_THRESHOLD = _CFG['audit']['score_threshold']

# Pending 超时升级阈值（天数）
PENDING_WARNING_DAYS = _CFG['pending_timeout']['warning_days']
PENDING_CRITICAL_DAYS = _CFG['pending_timeout']['critical_days']

# 加权聚合模式阈值
WEIGHTED_PASS_THRESHOLD = _CFG['weighted_aggregate']['pass_threshold']
WEIGHTED_FAIL_THRESHOLD = _CFG['weighted_aggregate']['fail_threshold']

# 安全限制
MAX_YAML_SIZE_KB = _CFG['limits']['max_yaml_size_kb']
MAX_PDCA_FILES = _CFG['limits']['max_pdca_files']
MAX_CYCLES_PER_TASK = _CFG['limits']['max_cycles_per_task']
ARCHIVE_OLDER_THAN_DAYS = _CFG['limits']['archive_older_than_days']

# ⭐ 安全修复：ID 格式校验，防止 path traversal 攻击
# 允许的 ID 格式：字母/数字开头，后续可含字母/数字/点/连字符/下划线
# 示例合法 ID: T1.1, T06, ZT-P015, N4-P2-TEST-01, ZTP015-IMP-001
_VALID_ID_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$')
_BLOCKED_ID_SUBSTRINGS = {'..', '/', '\\'}
# 控制字符（\x00-\x1f）也不允许出现在 ID 中
_CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x1f]')


def _validate_id(id_str: str, field_name: str = 'id') -> Optional[str]:
    """
    校验 ID 格式，防止 path traversal 和其他注入攻击。

    Returns:
        None if valid, error message string if invalid.
    """
    if not id_str or not isinstance(id_str, str):
        return f'{field_name} 不能为空'
    if len(id_str) > 128:
        return f'{field_name} 长度超过 128 字符'
    for blocked in _BLOCKED_ID_SUBSTRINGS:
        if blocked in id_str:
            return f'{field_name} 包含非法字符: {blocked!r}'
    if _CONTROL_CHAR_PATTERN.search(id_str):
        return f'{field_name} 包含控制字符'
    if not _VALID_ID_PATTERN.match(id_str):
        return f'{field_name} 格式无效（仅允许字母/数字/点/连字符/下划线，且以字母或数字开头）: {id_str!r}'
    return None


# ── 路径工具 ─────────────────────────────────────────

_original_cwd = None  # main() 中 _setup() 时记录调用者原始 CWD


def _setup() -> None:
    """
    ⭐ P0-2 修复：移除 os.chdir()，改为使用绝对路径

    记录调用者原始 CWD（用于日志记录），但不改变当前工作目录。
    所有路径操作都使用上面定义的绝对路径常量（PDCA_DIR, LOG_DIR 等）。
    """
    global _original_cwd
    _original_cwd = os.getcwd()  # 记录调用时的原始 CWD（仅用于日志）
    # ❌ 不再执行 os.chdir() - 多线程安全
    # 所有文件操作都使用绝对路径 PDCA_DIR, LOG_DIR


def _log_call(command: str, args: Dict[str, Any], result: Any) -> None:
    """
    追加一条 JSON line 到 logs/pdca.log。
    用于事后调试、排查 CWD 漂移、复现 bug 场景。

    注意：result 可能是 Dict（PDCA 操作）或 List（查询操作如 audit-queue, history, pending）
    """
    # 如果 result 是 list（查询类命令），只记录命令和返回条目数
    if isinstance(result, list):
        entry = {
            'ts': _now(),
            'cwd': _original_cwd,
            'cmd': command,
            'task_card_id': args.get('task_card_id'),
            'ok': True,  # 查询成功
            'result_count': len(result),
        }
    else:
        # Dict 类型的 result（PDCA 操作返回）
        entry = {
            'ts': _now(),
            'cwd': _original_cwd,
            'cmd': command,
            'task_card_id': args.get('task_card_id'),
            'phase': command if command in ('p', 'd', 'c', 'a') else None,
            'ok': result.get('ok'),
            'error': result.get('error'),
            'verdict': result.get('verdict'),
            'new_phase': result.get('phase'),
            'status': result.get('status'),
        }
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f'[pdca] 警告: 日志写入失败: {e}', file=sys.stderr)


def _record_path(task_card_id: str) -> str:
    """
    构建 PDCA 记录文件路径，包含安全校验。

    ⭐ 安全修复：验证 task_card_id 格式 + 确保解析后的路径在 PDCA_DIR 内，
    防止 path traversal 攻击（如 ../../etc/passwd）。
    """
    err = _validate_id(task_card_id, 'task-card-id')
    if err:
        raise ValueError(err)
    # 只取文件名部分，丢弃任何路径组件（防御性）
    safe_name = os.path.basename(f"{task_card_id}.yaml")
    path = os.path.join(PDCA_DIR, safe_name)
    # 双重校验：解析后的绝对路径必须在 PDCA_DIR 内
    abs_path = os.path.abspath(path)
    abs_pdca_dir = os.path.abspath(PDCA_DIR) + os.sep
    if not abs_path.startswith(abs_pdca_dir):
        raise ValueError(f'task-card-id 导致路径逃逸，拒绝访问: {task_card_id!r}')
    return path


# ── 记录读写 ─────────────────────────────────────────

def _load(task_card_id: str) -> Dict[str, Any]:
    os.makedirs(PDCA_DIR, exist_ok=True)
    try:
        path = _record_path(task_card_id)
    except ValueError as e:
        return {'ok': False, 'error': str(e)}
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError:
            # ⭐ 数据校验：YAML 解析失败，返回空记录（避免崩溃）
            import sys
            print(f'[pdca] 警告: {path} YAML 解析失败，已重置为空记录', file=sys.stderr)
            return _empty_record(task_card_id)
        if not data or not isinstance(data, dict):
            return _empty_record(task_card_id)
        # ⭐ 数据校验：修复常见损坏字段
        if data.get('task_card_id') != task_card_id:
            data['task_card_id'] = task_card_id  # 修正 ID 不匹配
        if not isinstance(data.get('cycles'), list):
            data['cycles'] = []  # 修复 cycles 非列表
        # 校验每个 cycle 的核心字段
        for i, c in enumerate(data['cycles']):
            if not isinstance(c, dict):
                continue
            if c.get('phase') not in ('plan', 'do', 'cqo_review', 'check', 'act', 'completed'):
                c['phase'] = 'plan'  # 修复非法 phase
            if not isinstance(c.get('cycle_index'), int) or c['cycle_index'] < 1:
                c['cycle_index'] = i + 1  # 修复非法 cycle_index
        return data
    return _empty_record(task_card_id)


def _save(record: Dict[str, Any]) -> None:
    try:
        path = _record_path(record['task_card_id'])
    except ValueError as e:
        raise ValueError(f"保存失败: {e}")

    # ⭐ 安全限制：pdca/ 目录文件数上限
    os.makedirs(PDCA_DIR, exist_ok=True)
    existing_files = [f for f in os.listdir(PDCA_DIR)
                      if f.endswith('.yaml') and not f.startswith('_')]
    if len(existing_files) > MAX_PDCA_FILES and not os.path.exists(path):
        raise ValueError(f"pdca/ 目录文件数已达上限 {MAX_PDCA_FILES}，拒绝创建新文件")

    # ⭐ 审计完整性：写入前计算 checksum
    record['_checksum'] = _compute_checksum(record)

    tmp = path + '.tmp'
    # 防御性：确保 pdca/ 目录存在，使用绝对路径避免 CWD 漂移
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(os.path.abspath(tmp), 'w', encoding='utf-8') as f:
        yaml.dump(record, f, allow_unicode=True, default_flow_style=False)

    # ⭐ 安全限制：写入后检查文件大小
    file_size_kb = os.path.getsize(os.path.abspath(tmp)) // 1024
    if file_size_kb > MAX_YAML_SIZE_KB:
        os.remove(os.path.abspath(tmp))
        raise ValueError(
            f"文件大小 {file_size_kb}KB 超过上限 {MAX_YAML_SIZE_KB}KB，"
            f"task_card_id={record['task_card_id']!r}。请减少 cycle 数或拆分任务。"
        )

    os.replace(os.path.abspath(tmp), os.path.abspath(path))


def _safe_save(record: Dict[str, Any]) -> Dict[str, Any]:
    """安全保存：捕获 _save() 的 ValueError 并返回错误 dict，供 p/d/c/a/mark_audit 使用。"""
    try:
        _save(record)
        return {}
    except ValueError as e:
        return {'ok': False, 'error': str(e)}


def _compute_checksum(record: Dict[str, Any]) -> str:
    """
    ⭐ 审计完整性：计算 record 内容的 SHA-256 校验和。
    排除 _checksum 字段本身，确保幂等。
    """
    content = {k: v for k, v in record.items() if k != '_checksum'}
    raw = json.dumps(content, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]


def _empty_record(task_card_id: str) -> Dict[str, Any]:
    return {
        'task_card_id': task_card_id,
        'task_card_path': None,              # 所属 Topic ID（用于 aggregate 聚合）
        'topic_id': None,            # 所属 Project ID（用于 aggregate 聚合）
        'project_id': None,
        'cycles': [],
        '_checksum': None,  # ⭐ 审计完整性：写入时计算
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── 4 个核心记录函数 ──────────────────────────────────

def _new_cycle(cycles: list) -> Dict[str, Any]:
    """创建新 cycle 并追加到 cycles 列表"""
    nc = {
        'cycle_index': len(cycles) + 1,
        'started_at': _now(),
        'completed_at': None,
        'phase': 'plan',
        'p': None,
        'd': None,
        'cqo_review': None,
        'c': None,
        'a': None,
    }
    cycles.append(nc)
    return nc


def p(task_card_id: str,
      summary: str,
      acceptance_criteria: Optional[List[str]] = None,
      task_card_path: Optional[str] = None,
      dl_refs: Optional[List[str]] = None,
      topic_id: Optional[str] = None,
      project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    记录 Plan 阶段。

    创建新 cycle 的条件（三选一）：
      1. 首次调用（无历史 cycle）
      2. 上一个 cycle 已 completed
      3. 上一个 cycle 卡在 check/pending（LLM 放弃等待，重新规划）

    复用现有 cycle 的条件：
      上一个 cycle 处于 plan/do/act 阶段（正常迭代中途恢复）
    """
    # ⭐ 安全修复：校验所有 ID 参数
    err = _validate_id(task_card_id, 'task-card-id')
    if err:
        return {'ok': False, 'error': err}
    if topic_id:
        err = _validate_id(topic_id, 'topic-id')
        if err:
            return {'ok': False, 'error': err}
    if project_id:
        err = _validate_id(project_id, 'project-id')
        if err:
            return {'ok': False, 'error': err}
    # ⭐ P0-1 修复：强制并发控制检查
    # 在创建 Plan 之前，必须通过并发上限检查
    # 如果当前活跃 task 数量已达上限（10），则拒绝创建新 Plan
    concurrency_check = check_concurrency('task')
    if not concurrency_check['ok']:
        return concurrency_check  # 直接返回错误，阻止执行

    # ⭐ v6.2.0 修复：补充 topic/project 并发上限校验
    if topic_id:
        topic_check = check_concurrency('topic', scope_id=topic_id)
        if not topic_check['ok']:
            return topic_check
    if project_id:
        proj_check = check_concurrency('project', scope_id=project_id)
        if not proj_check['ok']:
            return proj_check

    record = _load(task_card_id)
    if task_card_path:
        record['task_card_path'] = task_card_path
    if topic_id:
        record['topic_id'] = topic_id
    if project_id:
        record['project_id'] = project_id

    cycles = record['cycles']
    if not cycles:
        cycle = _new_cycle(cycles)
    else:
        last = cycles[-1]
        last_phase = last.get('phase')
        last_verdict = (last.get('c') or {}).get('verdict')
        # 放弃等待 pending 或上轮已完成 → 新 cycle
        if last_phase == 'completed' or (last_phase == 'check' and last_verdict == 'pending'):
            # ⭐ 安全限制：每个 task 的 PDCA 循环数上限
            if len(cycles) >= MAX_CYCLES_PER_TASK:
                return {
                    'ok': False,
                    'error': f'PDCA 循环数已达上限 {MAX_CYCLES_PER_TASK}，'
                             f'task_card_id={task_card_id!r}。请检查任务是否存在结构性问题。'
                }
            cycle = _new_cycle(cycles)
        else:
            # plan/do/act 中途恢复：复用当前 cycle
            cycle = last

    cycle['phase'] = 'plan'
    cycle['p'] = {
        'timestamp': _now(),
        'summary': summary,
        'acceptance_criteria': acceptance_criteria or [],
        'dl_refs': dl_refs or [],   # LLM 在 Plan 阶段引用的 DL 条目（审计溯源用）
    }
    err = _safe_save(record)
    if err:
        return err
    return {'ok': True, 'cycle_index': cycle['cycle_index'], 'phase': 'plan'}


def d(task_card_id: str,
      summary: str,
      status: str,
      blocker: Optional[str] = None) -> Dict[str, Any]:
    """
    记录 Do 阶段。
    LLM 完成实际执行工作后调用。
    status: completed / blocked / partial

    前置校验（Phase 锁定）：
      当前 cycle phase 必须是 plan 或 do（P 之后才能 D）。
      若无 cycle 或 phase 不在 {plan, do} → 报错。
    """
    if status not in VALID_STATUSES:
        return {
            'ok': False,
            'error': f'invalid status: {status!r}，必须是 {sorted(VALID_STATUSES)} 之一'
        }
    # ⭐ 安全修复：校验 task_card_id
    err = _validate_id(task_card_id, 'task-card-id')
    if err:
        return {'ok': False, 'error': err}
    record = _load(task_card_id)
    cycles = record['cycles']

    # Phase 锁定：Do 必须在 Plan 之后
    if not cycles:
        return {'ok': False, 'error': 'Do 阶段不能在没有 Plan 的情况下调用。请先执行 pdca.py p'}
    last = cycles[-1]
    last_phase = last.get('phase')
    if last_phase == 'completed':
        return {'ok': False, 'error': '上一轮 PDCA 已完成。如需新的 PDCA 循环，请先执行 pdca.py p'}
    if last_phase not in ('plan', 'do'):
        return {'ok': False, 'error': f'Do 不能在 phase={last_phase!r} 时调用。当前应在 plan 或 do 阶段'}

    cycle = last
    cycle['d'] = {
        'timestamp': _now(),
        'summary': summary,
        'status': status,
        'blocker': blocker,
    }
    # Do 完成后进入 cqo_review 阶段（v8.1: CQO 合规闸门）
    if status == 'completed':
        cycle['phase'] = 'cqo_review'
    else:
        cycle['phase'] = 'do'
    err = _safe_save(record)
    if err:
        return err
    return {
        'ok': True,
        'cycle_index': cycle['cycle_index'],
        'phase': cycle['phase'],
        'status': status,
    }


def cqo_review(task_card_id: str,
               result: str,
               report_path: Optional[str] = None,
               issues: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    记录 CQO 合规闸门审核结果（v8.1 新增）。

    CQO Review 是 Do→Check 之间的过程性检查，不是 PDCA 的第 5 阶段。
    - pass → phase 推进到 check
    - revise → phase 退回 do（同一 cycle，revise_count+1）
    - reject → phase 退回 do（同一 cycle，revise_count+1，通知银月）

    result: pass / revise / reject
    report_path: CQO 合规报告路径
    issues: CQO 审核不通过项列表（如 ['CQO-01', 'CQO-03']）
    """
    if result not in CQO_REVIEW_RESULTS:
        return {
            'ok': False,
            'error': f'invalid cqo result: {result!r}，必须是 {sorted(CQO_REVIEW_RESULTS)} 之一'
        }
    err = _validate_id(task_card_id, 'task-card-id')
    if err:
        return {'ok': False, 'error': err}

    record = _load(task_card_id)
    cycles = record['cycles']

    if not cycles:
        return {'ok': False, 'error': 'CQO Review 不能在没有 Do 的情况下调用。请先执行 pdca.py d'}
    last = cycles[-1]
    last_phase = last.get('phase')
    if last_phase == 'completed':
        return {'ok': False, 'error': '上一轮 PDCA 已完成。如需新的 PDCA 循环，请先执行 pdca.py p'}
    if last_phase not in ('cqo_review', 'do'):
        return {'ok': False, 'error': f'CQO Review 不能在 phase={last_phase!r} 时调用。必须先完成 Do 阶段'}

    cycle = last
    existing_cqo = cycle.get('cqo_review') or {}
    revise_count = existing_cqo.get('revise_count', 0)

    if result in ('revise', 'reject'):
        revise_count += 1
        # CQO revise 上限检查
        if revise_count > CQO_REVISE_LIMIT:
            # 自动升级为 reject
            result = 'reject'

    cycle['cqo_review'] = {
        'timestamp': _now(),
        'result': result,
        'report_path': report_path,
        'issues': issues or [],
        'revise_count': revise_count,
    }

    if result == 'pass':
        cycle['phase'] = 'check'
    else:
        # revise 或 reject：退回 do
        cycle['phase'] = 'do'

    err = _safe_save(record)
    if err:
        return err
    return {
        'ok': True,
        'cycle_index': cycle['cycle_index'],
        'phase': cycle['phase'],
        'cqo_result': result,
        'revise_count': revise_count,
    }


def c(task_card_id: str,
      verdict: str,
      review_level: str,
      evidence: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    记录 Check 阶段。
    LLM 完成自查或获得人工审批结果后调用。

    verdict:
      pass/partial/fail/skip → phase 自动推进到 act
      pending                 → 等待人工审批，phase 保持 check

    review_level: 必填。不可省略，不可默认。
      - 首次 Check：从 Task-CARD 读取 review_level，必须传入
      - 后续 Check（Harold 回复后）：沿用同一 review_level

    ADAS 级别约束（自动校验）：
      L0/L1：不允许 verdict=pending（自验收，无需人工介入）
      L3：首次 Check 必须 verdict=pending；Harold 回复后第二次调用记录最终结论
    """
    if verdict not in VALID_VERDICTS:
        return {
            'ok': False,
            'error': f'invalid verdict: {verdict!r}，必须是 {sorted(VALID_VERDICTS)} 之一'
        }
    if review_level not in VALID_LEVELS:
        return {
            'ok': False,
            'error': f'invalid level: {review_level!r}，必须是 {sorted(VALID_LEVELS)} 之一'
        }
    # ⭐ 安全修复：校验 task_card_id
    err = _validate_id(task_card_id, 'task-card-id')
    if err:
        return {'ok': False, 'error': err}

    # ADAS 规则校验
    if review_level in LEVELS_SELF_APPROVE and verdict == 'pending':
        return {
            'ok': False,
            'error': f'{review_level} 为自验收级别，不允许 verdict=pending（ADAS 规则：L0/L1 必须自行给出 pass/fail）'
        }

    record = _load(task_card_id)
    cycles = record['cycles']

    # Phase 锁定：Check 必须在 Do 或 CQO Review 之后
    if not cycles:
        return {'ok': False, 'error': 'Check 阶段不能在没有 Plan/Do 的情况下调用。请先执行 pdca.py p 和 d'}
    last = cycles[-1]
    last_phase = last.get('phase')
    if last_phase == 'completed':
        return {'ok': False, 'error': '上一轮 PDCA 已完成。如需新的 PDCA 循环，请先执行 pdca.py p'}
    # 允许的 phase：cqo_review（CQO pass 后）、do（跳过 CQO 的兼容路径）、check（L3 第二次 Check：pending→final）
    if last_phase not in ('cqo_review', 'do', 'check'):
        return {'ok': False, 'error': f'Check 不能在 phase={last_phase!r} 时调用。必须先完成 CQO Review（pdca.py cqo-review）或 Do 阶段'}

    cycle = last
    existing_c = cycle.get('c')

    # Idempotency 防护：同一 cycle 内不可静默覆盖已有终态 verdict
    if existing_c and existing_c.get('verdict') not in (None, 'pending'):
        return {
            'ok': False,
            'warning': f'Check 阶段已有 verdict={existing_c["verdict"]!r}（cycle_index={cycle["cycle_index"]}），不可静默覆盖。如需更改请执行新的 PDCA 循环（pdca.py p）',
            'existing_verdict': existing_c.get('verdict'),
            'existing_review_level': existing_c.get('review_level'),
        }

    if review_level == LEVEL_FULL_HUMAN and existing_c is None:
        # L3 首次 Check：必须 pending，等待 Harold 审批
        if verdict != 'pending':
            return {
                'ok': False,
                'error': 'L3 首次 Check 必须 verdict=pending（ADAS 规则：Harold 全量审批，需等待回复）'
            }
    # L0/L1 自动通过 → 标记为可外部审计（audit heartbeat 入口）
    audit_eligible = (verdict == 'pass' and review_level in LEVELS_SELF_APPROVE)

    cycle['c'] = {
        'timestamp': _now(),
        'verdict': verdict,
        'review_level': review_level,
        'evidence': evidence or [],
        'audit_eligible': audit_eligible,
        'audit_result': None,       # 外部审计 heartbeat 通过 mark_audit() 填写
    }

    if verdict in FINAL_VERDICTS:
        cycle['phase'] = 'act'
    else:
        cycle['phase'] = 'check'  # pending：等待外部审批

    err = _safe_save(record)
    if err:
        return err
    return {
        'ok': True,
        'cycle_index': cycle['cycle_index'],
        'phase': cycle['phase'],
        'verdict': verdict,
        'needs_act': verdict in FINAL_VERDICTS,
    }


def a(task_card_id: str,
      summary: str,
      next_task: Optional[str] = None,
      lessons: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    记录 Act 阶段，完成本轮 PDCA。
    LLM 决定下一步行动后调用。

    前置校验（Phase 锁定）：
      Act 必须在 Check 之后调用（phase 必须是 act 或 check）。
      若无 cycle 或 phase 不在 {act, check} → 报错。
      特殊情况：phase=check + verdict=pending 时允许 Act（Harold 回复后补执行）。

    ⚠️ 写穿透强制要求（Harness 规则 A2）：
      a() 返回 ok=true 后，LLM 必须立即：
        1. 更新 Task-CARD 状态标记
        2. 更新 MISSION_BOARD 对应条目
      pdca.py 不再存储 task_state，由 Task-CARD 作为唯一真相源。
    """
    # ⭐ 安全修复：校验 task_card_id
    err = _validate_id(task_card_id, 'task-card-id')
    if err:
        return {'ok': False, 'error': err}
    record = _load(task_card_id)
    cycles = record['cycles']

    # Phase 锁定：Act 必须在 Check 之后
    if not cycles:
        return {'ok': False, 'error': 'Act 阶段不能在没有 PDCA 历史的情况下调用。请先执行完整的 P→D→C 流程'}
    last = cycles[-1]
    last_phase = last.get('phase')
    last_verdict = (last.get('c') or {}).get('verdict')
    if last_phase == 'completed':
        return {'ok': False, 'error': '上一轮 PDCA 已完成。如需新的 PDCA 循环，请先执行 pdca.py p'}
    if last_phase not in ('act', 'check'):
        return {'ok': False, 'error': f'Act 不能在 phase={last_phase!r} 时调用。必须先完成 Check 阶段（pdca.py c）'}
    if last_phase == 'check' and last_verdict != 'pending':
        return {'ok': False, 'error': 'Check 阶段 verdict 不是 pending，但 phase 未推进到 act。可能数据不一致，请检查'}

    cycle = last
    cycle['a'] = {
        'timestamp': _now(),
        'summary': summary,
        'next_task': next_task,
        'lessons': lessons or [],
    }
    cycle['phase'] = 'completed'
    cycle['completed_at'] = _now()

    err = _safe_save(record)
    if err:
        return err

    # T06.2：Act 完成后自动触发层间传播
    agg_result = aggregate(triggered_by=f'act:{task_card_id}')

    return {
        'ok': True,
        'cycle_index': cycle['cycle_index'],
        'phase': 'completed',
        'next_task': next_task,
        'aggregate': agg_result,
    }


# ── 查询函数 ─────────────────────────────────────────

def get_status(task_card_id: str) -> Dict[str, Any]:
    """返回该 task 的当前 PDCA 状态（最近一个 cycle 的摘要）"""
    # ⭐ 安全修复：校验 task_card_id
    err = _validate_id(task_card_id, 'task-card-id')
    if err:
        return {'ok': False, 'error': err}
    record = _load(task_card_id)
    cycles = record['cycles']
    if not cycles:
        return {
            'task_card_id': task_card_id,
            'cycles_total': 0,
            'current_phase': None,
        }
    last = cycles[-1]

    # 修复 #19：计算连续失败次数（连续 fail/partial 计数，pass 时重置）
    consecutive_fails = 0
    for c in reversed(cycles):
        verdict = (c.get('c') or {}).get('verdict')
        if verdict in ('fail', 'partial'):
            consecutive_fails += 1
        elif verdict == 'pass':
            break
        elif verdict == 'skip':
            continue  # ⭐ v6.2.0 修复：skip = "不适用"，既不计数也不重置
        else:
            break  # pending 终止计数（等待人工审核，状态未定）

    return {
        'task_card_id': task_card_id,
        'task_card_path': record.get('task_card_path'),
        'cycles_total': len(cycles),
        'current_cycle_index': last['cycle_index'],
        'current_phase': last['phase'],
        'current_verdict': (last.get('c') or {}).get('verdict'),
        'cqo_review_status': (last.get('cqo_review') or {}).get('result'),
        'last_p_summary': (last.get('p') or {}).get('summary'),
        'last_d_status': (last.get('d') or {}).get('status'),
        'started_at': last.get('started_at'),
        'completed_at': last.get('completed_at'),
        'consecutive_fails': consecutive_fails,
        'needs_escalation': consecutive_fails >= 3,
    }


def get_history(task_card_id: str) -> Dict[str, Any]:
    """
    返回该 task 的完整 PDCA 历史（所有 cycle 摘要）。
    供 Harold 审批、审计、复盘时查看迭代历史。
    """
    # ⭐ 安全修复：校验 task_card_id
    err = _validate_id(task_card_id, 'task-card-id')
    if err:
        return {'ok': False, 'error': err}
    record = _load(task_card_id)
    cycles = record['cycles']
    if not cycles:
        return {
            'task_card_id': task_card_id,
            'task_card_path': record.get('task_card_path'),
            'cycles_total': 0,
            'cycles': [],
        }
    return {
        'task_card_id': task_card_id,
        'task_card_path': record.get('task_card_path'),
        'cycles_total': len(cycles),
        'cycles': [
            {
                'cycle_index': c['cycle_index'],
                'phase': c['phase'],
                'p_summary': (c.get('p') or {}).get('summary'),
                'd_status': (c.get('d') or {}).get('status'),
                'd_summary': (c.get('d') or {}).get('summary'),
                'cqo_result': (c.get('cqo_review') or {}).get('result'),
                'verdict': (c.get('c') or {}).get('verdict'),
                'review_level': (c.get('c') or {}).get('review_level'),
                'evidence': (c.get('c') or {}).get('evidence', []),
                'a_summary': (c.get('a') or {}).get('summary'),
                'next_task': (c.get('a') or {}).get('next_task'),
                'started_at': c.get('started_at'),
                'completed_at': c.get('completed_at'),
            }
            for c in cycles
        ],
    }


def get_pending(review_level: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    扫描所有 pdca/*.yaml，返回 verdict=pending（等待人工审批）的 task 列表。
    heartbeat Step 0 调用：确认是否有上一轮未完成的审批。

    review_level 过滤（修复 #6：L2/L3 混同问题）：
      - None：返回所有 pending
      - 'L2'：仅返回 L2 pending（等待银月抽检审核）
      - 'L3'：仅返回 L3 pending（等待 Harold 全量审批）

    返回中增加 reviewer 字段，供 heartbeat 区分处理：
      - L2 pending → reviewer=银月（检查银月审核状态）
      - L3 pending → reviewer=harold（检查 Harold DM 回复）
    """
    if not os.path.exists(PDCA_DIR):
        return []
    pending_list = []
    for fname in sorted(os.listdir(PDCA_DIR)):
        if not fname.endswith('.yaml') or fname.startswith('_'):
            continue
        path = os.path.join(PDCA_DIR, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                record = yaml.safe_load(f)
            if not record or not record.get('cycles'):
                continue
            last = record['cycles'][-1]
            if last.get('phase') == 'check':
                check = last.get('c') or {}
                if check.get('verdict') == 'pending':
                    rl = check.get('review_level')
                    if review_level and rl != review_level:
                        continue
                    check_ts = check.get('timestamp')
                    days = _days_waiting(check_ts)
                    reviewer = '银月' if rl == 'L2' else 'harold' if rl == 'L3' else 'unknown'
                    # ⭐ 超时升级分级：normal → warning → critical
                    if days > PENDING_CRITICAL_DAYS:
                        escalation = 'critical'
                    elif days > PENDING_WARNING_DAYS:
                        escalation = 'warning'
                    else:
                        escalation = 'normal'
                    pending_list.append({
                        'task_card_id': record['task_card_id'],
                        'task_card_path': record.get('task_card_path'),
                        'cycle_index': last['cycle_index'],
                        'review_level': rl,
                        'reviewer': reviewer,
                        'check_timestamp': check_ts,
                        'days_waiting': days,
                        'is_overdue': days > PENDING_WARNING_DAYS,
                        'escalation': escalation,
                        'needs_escalation': escalation != 'normal',
                        'p_summary': (last.get('p') or {}).get('summary'),
                    })
        except Exception:
            continue
    return pending_list


def get_audit_queue() -> List[Dict[str, Any]]:
    """
    扫描所有 pdca/*.yaml，返回 audit_eligible=True 且 audit_result=None 的 cycle 列表。

    供外部审计 heartbeat（本身是一个 task-card）调用：
      - 读取此队列，对每个交付物进行评分（LLM 判断）
      - 评分 < 80 → 调用方执行 governance-knowledge.create_lesson_learned()，
        质疑对应 p.dl_refs 中的 DL 条目，降低其置信度
      - 调用 mark_audit() 记录审计结果
      - 存在问题项 → popup 给用户重新 review
    """
    if not os.path.exists(PDCA_DIR):
        return []
    queue = []
    for fname in sorted(os.listdir(PDCA_DIR)):
        if not fname.endswith('.yaml') or fname.startswith('_'):
            continue
        path = os.path.join(PDCA_DIR, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                record = yaml.safe_load(f)
            if not record or not record.get('cycles'):
                continue
            for cycle in record['cycles']:
                check = cycle.get('c') or {}
                if check.get('audit_eligible') and check.get('audit_result') is None:
                    queue.append({
                        'task_card_id': record['task_card_id'],
                        'task_card_path': record.get('task_card_path'),
                        'cycle_index': cycle['cycle_index'],
                        'review_level': check.get('review_level'),
                        'check_timestamp': check.get('timestamp'),
                        'dl_refs': (cycle.get('p') or {}).get('dl_refs', []),
                        'evidence': check.get('evidence', []),
                        'p_summary': (cycle.get('p') or {}).get('summary'),
                        'd_summary': (cycle.get('d') or {}).get('summary'),
                    })
        except Exception:
            continue
    return queue


def mark_audit(task_card_id: str,
               cycle_index: int,
               score: int,
               issues: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    外部审计 heartbeat 记录审计结果。
    Python 只做写入；评分判断、LL 创建、DL 质疑均由 LLM 执行。

    score  : 0-100，审计评分（<80 表示存在问题）
    issues : 发现的具体问题列表
    """
    # ⭐ v6.2.0 修复：score 范围校验
    if not 0 <= score <= 100:
        return {'ok': False, 'error': f'score 必须在 0-100 范围内，当前值: {score}'}
    # ⭐ 安全修复：校验 task_card_id
    err = _validate_id(task_card_id, 'task-card-id')
    if err:
        return {'ok': False, 'error': err}
    # ⭐ 输入校验：cycle_index 必须 ≥ 1
    if not isinstance(cycle_index, int) or cycle_index < 1:
        return {'ok': False, 'error': f'cycle_index 必须是 ≥ 1 的整数，当前值: {cycle_index}'}

    record = _load(task_card_id)
    cycles = record['cycles']
    target = next((c for c in cycles if c['cycle_index'] == cycle_index), None)
    if target is None:
        return {'ok': False, 'error': f'cycle_index={cycle_index} 不存在'}
    check = target.get('c')
    if not check:
        return {'ok': False, 'error': 'Check 阶段尚未记录，无法审计'}
    if not check.get('audit_eligible'):
        return {'ok': False, 'error': '该 cycle 不是 audit_eligible 状态'}

    # ⭐ v6.2.0 修复：防止重复审计覆盖
    if check.get('audit_result'):
        return {'ok': False, 'error': '该 cycle 已存在审计结果，不可重复审计'}

    check['audit_result'] = {
        'timestamp': _now(),
        'score': score,
        'issues': issues or [],
        'has_problem': score < AUDIT_SCORE_THRESHOLD,
    }
    err = _safe_save(record)
    if err:
        return err
    return {
        'ok': True,
        'task_card_id': task_card_id,
        'cycle_index': cycle_index,
        'score': score,
        'has_problem': score < AUDIT_SCORE_THRESHOLD,
        'dl_refs': (target.get('p') or {}).get('dl_refs', []),
        'next_action': (
            '评分 < 80：调用 governance-knowledge.create_lesson_learned() 质疑对应 DL，popup 给用户重新 review'
            if score < AUDIT_SCORE_THRESHOLD else
            '审计通过，无需额外操作'
        ),
    }


# ── 层间传播 ─────────────────────────────────────────

def _load_state() -> Dict[str, Any]:
    """加载聚合状态文件（不存在则返回空结构）

    向后兼容：旧版 _state.yaml 无 version 字段时自动补 '1.0'。
    """
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not data:
            return _empty_state()
        # 向后兼容：旧版文件可能无 version 字段
        if 'version' not in data:
            data['version'] = '1.0'
        return data
    return _empty_state()


def _empty_state() -> Dict[str, Any]:
    return {
        'scope': 'aggregate',
        'version': '1.0',
        'last_updated': None,
        'topic_verdicts': {},
        'project_verdicts': {},
        '_file_cache': {},  # ⭐ 增量聚合：{filename: {mtime, task_map_entry}}
    }


def _aggregate_verdict(verdicts: List[str], mode: str = 'strict') -> str:
    """
    聚合多个子项 verdict → 父级 verdict

    ⭐ P2-1 增强：支持两种模式

    mode='strict'（默认，向后兼容）：
      - 全部 pass → pass
      - 任一 fail → fail
      - 全部 skip → skip
      - 混合 → partial

    mode='weighted'（权重模式）：
      - 考虑比例：≥80% pass → pass (WEIGHTED_PASS_THRESHOLD), ≥20% fail → fail (WEIGHTED_FAIL_THRESHOLD)
      - 严重程度权重：fail=3, partial=2, skip=1, pass=0
      - 加权平均后判断：<0.5→pass, 0.5-1.5→partial, >1.5→fail
    """
    if not verdicts:
        return 'skip'

    if mode == 'strict':
        # 原有严格规则（向后兼容）
        if all(v == 'pass' for v in verdicts):
            return 'pass'
        if any(v == 'fail' for v in verdicts):
            return 'fail'
        if all(v == 'skip' for v in verdicts):
            return 'skip'
        return 'partial'

    elif mode == 'weighted':
        # 权重模式：考虑比例和严重程度
        total = len(verdicts)
        counts = {
            'pass': verdicts.count('pass'),
            'partial': verdicts.count('partial'),
            'fail': verdicts.count('fail'),
            'skip': verdicts.count('skip'),
        }

        # 比例阈值判断
        pass_ratio = counts['pass'] / total
        fail_ratio = counts['fail'] / total

        if pass_ratio >= WEIGHTED_PASS_THRESHOLD:
            return 'pass'
        if fail_ratio >= WEIGHTED_FAIL_THRESHOLD:
            return 'fail'

        # 严重程度加权
        severity_weights = {'pass': 0, 'skip': 1, 'partial': 2, 'fail': 3}
        weighted_sum = sum(severity_weights.get(v, 0) for v in verdicts)
        avg_severity = weighted_sum / total

        if avg_severity < 0.5:
            return 'pass'
        elif avg_severity < 1.5:
            return 'partial'
        else:
            return 'fail'

    else:
        # 未知模式，回退到 strict
        return _aggregate_verdict(verdicts, mode='strict')


def _verdicts_equal(new: Dict[str, Any], old: Dict[str, Any]) -> bool:
    """比较两个 verdict dict 是否语义等价（忽略 updated_at 时间戳差异）

    ⭐ v6.2.0 修复：
    - 统一处理 children/topics key 名不一致问题
    - 比较 active_count/task_count 变化（之前只比较 verdict 和 children）
    """
    if set(new.keys()) != set(old.keys()):
        return False
    for k in new:
        if new[k].get('verdict') != old.get(k, {}).get('verdict'):
            return False
        # ⭐ 统一处理 children/topics 两种 key 名
        new_children = new[k].get('children') or new[k].get('topics')
        old_children = old.get(k, {}).get('children') or old.get(k, {}).get('topics')
        if new_children != old_children:
            return False
        # ⭐ 比较 active_count/task_count 变化（之前忽略这些字段）
        if new[k].get('active_count') != old.get(k, {}).get('active_count'):
            return False
        if new[k].get('task_count') != old.get(k, {}).get('task_count'):
            return False
    return True


def aggregate(triggered_by: Optional[str] = None, mode: str = 'strict') -> Dict[str, Any]:
    """
    轻量级层间传播：扫描所有 pdca/*.yaml，聚合 task verdict 到 topic/project 级。
    结果写入 pdca/_state.yaml（单文件方案）。

    ⭐ 增量优化：使用 mtime 缓存，仅重新处理变更的文件。

    mode='strict'（默认）：
      - 全部 pass → pass
      - 任一 fail → fail
      - 全部 skip → skip
      - 混合 → partial

    mode='weighted'（权重模式）：
      - 考虑比例和严重程度
      - ≥80% pass → pass
      - ≥20% fail → fail
      - 加权评分决定 partial

    触发：a() 完成后自动调用，或 heartbeat 定期调用。
    """
    if not os.path.exists(PDCA_DIR):
        return {'ok': True, 'changes': False, 'reason': 'pdca/ 目录不存在'}

    state = _load_state()
    file_cache: Dict[str, Any] = state.get('_file_cache', {})

    task_map: Dict[str, Dict[str, Any]] = {}
    topic_tasks: Dict[str, List[str]] = {}
    project_tasks: Dict[str, List[str]] = {}
    new_cache: Dict[str, Any] = {}
    files_changed = 0

    for fname in sorted(os.listdir(PDCA_DIR)):
        if not fname.endswith('.yaml') or fname.startswith('_'):
            continue
        path = os.path.join(PDCA_DIR, fname)
        try:
            # ⭐ 增量优化：用 mtime 判断文件是否变更
            current_mtime = str(os.path.getmtime(path))
            cached = file_cache.get(fname)

            if cached and cached.get('mtime') == current_mtime:
                # 文件未变，直接使用缓存
                new_cache[fname] = cached  # ⭐ 始终写入 new_cache 保持一致性
                entry = cached.get('entry')
                if entry:
                    task_id = entry.get('task_card_id')
                    if task_id:
                        task_map[task_id] = entry
                        tid = entry.get('topic_id')
                        pid = entry.get('project_id')
                        if tid:
                            topic_tasks.setdefault(tid, []).append(task_id)
                        if pid:
                            project_tasks.setdefault(pid, []).append(task_id)
                continue

            # 文件变更或新文件，需要重新解析
            files_changed += 1
            with open(path, 'r', encoding='utf-8') as f:
                record = yaml.safe_load(f)
            if not record or not record.get('cycles'):
                new_cache[fname] = {'mtime': current_mtime, 'entry': None}
                continue

            task_id = record['task_card_id']

            # 层间传播过滤：只聚合已完成的 cycle
            completed_cycles = [c for c in record['cycles'] if c.get('phase') == 'completed']
            if not completed_cycles:
                new_cache[fname] = {'mtime': current_mtime, 'entry': None}
                continue

            # 取最近一个已完成 cycle 的 verdict
            last_completed = completed_cycles[-1]
            verdict = (last_completed.get('c') or {}).get('verdict')
            if verdict is None:
                new_cache[fname] = {'mtime': current_mtime, 'entry': None}
                continue

            last_cycle = record['cycles'][-1]
            is_active = last_cycle.get('phase') != 'completed'

            entry = {
                'task_card_id': task_id,
                'verdict': verdict,
                'topic_id': record.get('topic_id'),
                'project_id': record.get('project_id'),
                'cycle_index': last_completed['cycle_index'],
                'is_active': is_active,
            }
            task_map[task_id] = entry
            tid = record.get('topic_id')
            pid = record.get('project_id')
            if tid:
                topic_tasks.setdefault(tid, []).append(task_id)
            if pid:
                project_tasks.setdefault(pid, []).append(task_id)

            new_cache[fname] = {'mtime': current_mtime, 'entry': entry}
        except Exception:
            continue

    changes = False

    # 聚合 topic 级 verdict
    new_topic_verdicts: Dict[str, Any] = {}
    for topic_id, tasks in topic_tasks.items():
        child_verdicts = []
        child_details: Dict[str, str] = {}
        for tid in tasks:
            info = task_map.get(tid, {})
            v = info.get('verdict')
            if v:
                child_verdicts.append(v)
                child_details[tid] = v
        verdict = _aggregate_verdict(child_verdicts, mode=mode)
        new_topic_verdicts[topic_id] = {
            'verdict': verdict,
            'children': child_details,
            'task_count': len(tasks),
            'active_count': sum(1 for tid in tasks if task_map.get(tid, {}).get('is_active')),
            'updated_at': _now(),
        }

    if not _verdicts_equal(new_topic_verdicts, state.get('topic_verdicts', {})):
        state['topic_verdicts'] = new_topic_verdicts
        changes = True

    # 聚合 project 级 verdict（基于 topic verdicts）
    new_project_verdicts: Dict[str, Any] = {}
    for project_id, tasks in project_tasks.items():
        topic_ids = set()
        for tid in tasks:
            tid_val = task_map.get(tid, {}).get('topic_id')
            if tid_val:
                topic_ids.add(tid_val)
        topic_verdicts_list = []
        topic_details: Dict[str, str] = {}
        for t_id in topic_ids:
            t_info = new_topic_verdicts.get(t_id, {})
            v = t_info.get('verdict')
            if v:
                topic_verdicts_list.append(v)
                topic_details[t_id] = v
        verdict = _aggregate_verdict(topic_verdicts_list, mode=mode)
        new_project_verdicts[project_id] = {
            'verdict': verdict,
            'topics': topic_details,
            'topic_count': len(topic_ids),
            'updated_at': _now(),
        }

    if not _verdicts_equal(new_project_verdicts, state.get('project_verdicts', {})):
        state['project_verdicts'] = new_project_verdicts
        changes = True

    if changes:
        state['last_updated'] = _now()
        state['triggered_by'] = triggered_by

    # ⭐ 向后兼容：确保 version 字段持久化到磁盘（旧文件回填）
    needs_version_backfill = False
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            raw = yaml.safe_load(f)
        if raw and 'version' not in raw:
            needs_version_backfill = True
    if needs_version_backfill:
        changes = True

    # ⭐ 增量优化：始终更新 file_cache（mtime 变化即写入）
    cache_changed = new_cache != file_cache
    if cache_changed:
        state['_file_cache'] = new_cache
        changes = True

    if changes:
        _save_state(state)

    return {
        'ok': True,
        'changes': changes,
        'topics': len(new_topic_verdicts),
        'projects': len(new_project_verdicts),
        'tasks_scanned': len(task_map),
        'files_changed': files_changed,
    }


def _save_state(state: Dict[str, Any]) -> None:
    """原子写入 _state.yaml

    ⭐ v6.2.0 修复：使用 os.path.abspath() 确保 CWD 漂移时仍能正确写入
    """
    tmp = STATE_FILE + '.tmp'
    os.makedirs(os.path.dirname(os.path.abspath(STATE_FILE)), exist_ok=True)
    with open(os.path.abspath(tmp), 'w', encoding='utf-8') as f:
        yaml.dump(state, f, allow_unicode=True, default_flow_style=False)
    os.replace(os.path.abspath(tmp), os.path.abspath(STATE_FILE))


# ── 并发控制 ─────────────────────────────────────────

CONCURRENCY_LIMITS = {
    'task': CONCURRENCY_LIMIT_TASK,
    'topic': CONCURRENCY_LIMIT_TOPIC,
    'project': CONCURRENCY_LIMIT_PROJECT,
}


def verify_cycle_write(task_card_id: str, cycle_index: int) -> Dict[str, Any]:
    """
    ⭐ P1-1: 幂等性验证 - 验证 cycle 写入后状态正确记录

    Args:
        task_card_id: 任务 ID
        cycle_index: cycle 索引（从 1 开始）

    Returns:
        {
            'ok': bool,
            'task_card_id': str,
            'cycle_index': int,
            'phase': str,  # 当前 phase
            'verdict': str | None,  # Check 阶段的 verdict（如果存在）
            'timestamps': Dict[str, str],  # 各阶段时间戳
            'completed_at': str | None,
            'error': str | None
        }

    用途：LLM 在调用 a() 后，调用此函数验证写入是否成功
    示例：
        # LLM 执行完 Act
        result = a(task_card_id='ZTP015-IMP-001', summary='...')
        # 立即验证写入
        verify = verify_cycle_write('ZTP015-IMP-001', cycle_index=1)
        if not verify['ok']:
            raise RuntimeError(f"写入验证失败: {verify['error']}")
    """
    # ⭐ 安全修复：校验 task_card_id
    err = _validate_id(task_card_id, 'task-card-id')
    if err:
        return {'ok': False, 'error': err}
    # ⭐ 输入校验：cycle_index 必须 ≥ 1
    if not isinstance(cycle_index, int) or cycle_index < 1:
        return {'ok': False, 'error': f'cycle_index 必须是 ≥ 1 的整数，当前值: {cycle_index}'}
    try:
        record = _load(task_card_id)
        if not record or not record.get('cycles'):
            return {
                'ok': False,
                'error': f'Task {task_card_id} has no cycles'
            }

        cycles = record['cycles']
        if cycle_index < 1 or cycle_index > len(cycles):
            return {
                'ok': False,
                'error': f'Invalid cycle_index {cycle_index}, valid range: 1-{len(cycles)}'
            }

        cycle = cycles[cycle_index - 1]
        phase = cycle.get('phase')
        c_data = cycle.get('c', {})
        verdict = c_data.get('verdict')

        timestamps = {}
        for stage in ['p', 'd', 'c', 'a']:
            if stage in cycle:
                timestamps[stage] = cycle[stage].get('timestamp', 'missing')

        return {
            'ok': True,
            'task_card_id': task_card_id,
            'cycle_index': cycle_index,
            'phase': phase,
            'verdict': verdict,
            'timestamps': timestamps,
            'completed_at': cycle.get('completed_at'),
        }

    except Exception as e:
        return {
            'ok': False,
            'error': f'Failed to verify cycle: {str(e)}'
        }


def check_concurrency(scope: str = 'task', scope_id: Optional[str] = None) -> Dict[str, Any]:
    """
    并发上限校验。p() 前置调用，防止超出并发上限。

    scope: 'task' | 'topic' | 'project'
    scope_id: topic 或 project 级时指定 ID

    默认上限：task≤10, topic≤5, project≤3
    """
    if scope not in CONCURRENCY_LIMITS:
        return {'ok': False, 'error': f'未知 scope: {scope}，必须是 task/topic/project'}

    limit = CONCURRENCY_LIMITS[scope]

    if not os.path.exists(PDCA_DIR):
        return {'ok': True, 'scope': scope, 'active': 0, 'limit': limit}

    active_tasks: List[Dict[str, Any]] = []

    for fname in sorted(os.listdir(PDCA_DIR)):
        if not fname.endswith('.yaml') or fname.startswith('_'):
            continue
        path = os.path.join(PDCA_DIR, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                record = yaml.safe_load(f)
            if not record or not record.get('cycles'):
                continue

            active_cycles = [c for c in record['cycles']
                             if c.get('phase') != 'completed'
                             and not (c.get('phase') == 'check'
                                      and (c.get('c') or {}).get('verdict') == 'pending')]
            if not active_cycles:
                continue

            if scope == 'topic' and scope_id:
                if record.get('topic_id') != scope_id:
                    continue
            elif scope == 'project' and scope_id:
                if record.get('project_id') != scope_id:
                    continue

            last = record['cycles'][-1]
            active_tasks.append({
                'task_card_id': record['task_card_id'],
                'topic_id': record.get('topic_id'),
                'project_id': record.get('project_id'),
                'phase': last.get('phase'),
                'verdict': (last.get('c') or {}).get('verdict'),
            })
        except Exception:
            continue

    count = len(active_tasks)
    if count >= limit:
        return {
            'ok': False,
            'scope': scope,
            'scope_id': scope_id,
            'active': count,
            'limit': limit,
            'error': f'{scope} 并发上限 {limit}，当前活跃 {count}，请等待完成',
            'active_tasks': active_tasks,
        }

    return {
        'ok': True,
        'scope': scope,
        'active': count,
        'limit': limit,
        'remaining': limit - count,
    }


def _days_waiting(timestamp_str: Optional[str]) -> int:
    """计算从 timestamp_str 到现在经过了多少天"""
    if not timestamp_str:
        return 0
    try:
        ts = datetime.fromisoformat(timestamp_str)
        delta = datetime.now(timezone.utc) - ts
        return delta.days
    except Exception:
        return 0


def verify_integrity(task_card_id: Optional[str] = None) -> Dict[str, Any]:
    """
    ⭐ 审计完整性：验证 pdca 文件的 checksum 是否一致。

    - 指定 task_card_id 时验证单个文件
    - 不指定时验证所有 pdca/*.yaml 文件
    - 返回通过/失败/无 checksum（旧文件）的统计
    """
    if task_card_id:
        err = _validate_id(task_card_id, 'task-card-id')
        if err:
            return {'ok': False, 'error': err}
        try:
            path = _record_path(task_card_id)
        except ValueError as e:
            return {'ok': False, 'error': str(e)}
        if not os.path.exists(path):
            return {'ok': False, 'error': f'文件不存在: {task_card_id}'}
        files_to_check = [(task_card_id, path)]
    else:
        if not os.path.exists(PDCA_DIR):
            return {'ok': True, 'total': 0, 'valid': 0, 'invalid': 0, 'no_checksum': 0}
        files_to_check = []
        for fname in sorted(os.listdir(PDCA_DIR)):
            if not fname.endswith('.yaml') or fname.startswith('_'):
                continue
            tid = fname[:-5]  # strip .yaml
            files_to_check.append((tid, os.path.join(PDCA_DIR, fname)))

    results = {'valid': [], 'invalid': [], 'no_checksum': []}
    for tid, path in files_to_check:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            if not data or not isinstance(data, dict):
                results['invalid'].append({'task_card_id': tid, 'reason': 'YAML 解析失败'})
                continue
            stored = data.get('_checksum')
            if not stored:
                results['no_checksum'].append(tid)
                continue
            computed = _compute_checksum(data)
            if computed == stored:
                results['valid'].append(tid)
            else:
                results['invalid'].append({
                    'task_card_id': tid,
                    'reason': 'checksum 不匹配',
                    'stored': stored,
                    'computed': computed,
                })
        except Exception as e:
            results['invalid'].append({'task_card_id': tid, 'reason': str(e)})

    total = len(results['valid']) + len(results['invalid']) + len(results['no_checksum'])
    return {
        'ok': True,
        'total': total,
        'valid': len(results['valid']),
        'invalid': len(results['invalid']),
        'no_checksum': len(results['no_checksum']),
        'details': results if results['invalid'] else None,
    }


def archive(older_than_days: int = 30, dry_run: bool = False) -> Dict[str, Any]:
    """
    ⭐ 归档过期数据：将 completed 超过 N 天的 pdca YAML 文件移入 pdca/_archive/。

    归档规则：
      - 所有 cycle 均 completed（最后一个 cycle.phase=completed）
      - 最后 completed_at 距今超过 older_than_days 天
      - 移入 pdca/_archive/{task_card_id}.yaml（保留原文件名）

    dry_run=True 时仅报告待归档文件数，不实际移动。

    归档文件仍可被 verify-integrity 和 aggregate(--mode=strict) 按需读取，
    但不再参与并发计数、pending 检查和默认聚合扫描。
    """
    if not os.path.exists(PDCA_DIR):
        return {'ok': True, 'archived': 0, 'reason': 'pdca/ 目录不存在'}

    archive_dir = os.path.join(PDCA_DIR, '_archive')
    now = datetime.now(timezone.utc)
    candidates = []

    for fname in sorted(os.listdir(PDCA_DIR)):
        if not fname.endswith('.yaml') or fname.startswith('_'):
            continue
        path = os.path.join(PDCA_DIR, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                record = yaml.safe_load(f)
            if not record or not record.get('cycles'):
                continue

            # 检查是否所有 cycle 均已完成
            last = record['cycles'][-1]
            if last.get('phase') != 'completed':
                continue

            # 检查最后完成时间
            completed_at_str = last.get('completed_at')
            if not completed_at_str:
                continue
            try:
                completed_at = datetime.fromisoformat(completed_at_str)
                if completed_at.tzinfo is None:
                    completed_at = completed_at.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                continue

            days_since = (now - completed_at).days
            if days_since >= older_than_days:
                candidates.append({
                    'task_card_id': record['task_card_id'],
                    'file': fname,
                    'days_since_completed': days_since,
                    'completed_at': completed_at_str,
                })
        except Exception:
            continue

    archived = 0
    if not dry_run and candidates:
        os.makedirs(archive_dir, exist_ok=True)
        for c in candidates:
            src = os.path.join(PDCA_DIR, c['file'])
            dst = os.path.join(archive_dir, c['file'])
            try:
                os.replace(src, dst)
                archived += 1
            except OSError:
                continue

    return {
        'ok': True,
        'candidates': len(candidates),
        'archived': archived if not dry_run else 0,
        'dry_run': dry_run,
        'older_than_days': older_than_days,
        'details': candidates if dry_run or archived > 0 else None,
    }


def health_check() -> Dict[str, Any]:
    """
    ⭐ 系统健康检查：汇总 pdca/ 目录状态，供 heartbeat 和 Phase 3 自监控使用。

    检查项：
      - 文件总数 vs 上限
      - 总占用磁盘空间
      - pending 超时任务数（warning/critical）
      - 审计队列积压数
      - checksum 覆盖率
      - 并发使用率
    """
    checks: Dict[str, Any] = {
        'status': 'healthy',
        'timestamp': _now(),
    }

    # 文件统计
    if not os.path.exists(PDCA_DIR):
        checks['pdca_dir'] = 'missing'
        checks['status'] = 'degraded'
        return checks

    files = [f for f in os.listdir(PDCA_DIR)
             if f.endswith('.yaml') and not f.startswith('_')]
    file_count = len(files)
    total_size_kb = sum(
        os.path.getsize(os.path.join(PDCA_DIR, f)) // 1024 for f in files
        if os.path.isfile(os.path.join(PDCA_DIR, f))
    )
    checks['files'] = {
        'count': file_count,
        'limit': MAX_PDCA_FILES,
        'usage_pct': round(file_count / MAX_PDCA_FILES * 100, 1) if MAX_PDCA_FILES else 0,
        'total_size_kb': total_size_kb,
    }
    if file_count > MAX_PDCA_FILES * 0.9:
        checks['status'] = 'warning'

    # Pending 超时
    pending = get_pending()
    warning_count = sum(1 for p in pending if p.get('escalation') == 'warning')
    critical_count = sum(1 for p in pending if p.get('escalation') == 'critical')
    checks['pending'] = {
        'total': len(pending),
        'warning': warning_count,
        'critical': critical_count,
    }
    if critical_count > 0:
        checks['status'] = 'critical'
    elif warning_count > 0 and checks['status'] == 'healthy':
        checks['status'] = 'warning'

    # 审计队列
    audit_q = get_audit_queue()
    checks['audit_queue'] = len(audit_q)

    # Checksum 覆盖率
    integrity = verify_integrity()
    total = integrity.get('total', 0)
    checks['checksum'] = {
        'total_files': total,
        'with_checksum': total - integrity.get('no_checksum', 0),
        'coverage_pct': round((total - integrity.get('no_checksum', 0)) / total * 100, 1) if total else 100,
        'invalid': integrity.get('invalid', 0),
    }
    if integrity.get('invalid', 0) > 0:
        checks['status'] = 'critical'

    # 并发使用率
    cc = check_concurrency('task')
    checks['concurrency'] = {
        'active': cc.get('active', 0),
        'limit': cc.get('limit', 0),
        'usage_pct': round(cc.get('active', 0) / cc.get('limit', 1) * 100, 1),
    }

    return checks


# ── CLI ──────────────────────────────────────────────

def _parse_list(value: Optional[str]) -> List[str]:
    """将 '|' 分隔的字符串解析为列表"""
    if not value:
        return []
    return [v.strip() for v in value.split('|') if v.strip()]


def main() -> None:
    """CLI 入口函数"""
    _setup()

    parser = argparse.ArgumentParser(
        description='PDCA 状态记录器 — Python 只做 I/O，LLM 负责推断与执行'
    )
    subparsers = parser.add_subparsers(dest='command')

    # p
    p_p = subparsers.add_parser('p', help='记录 Plan 阶段')
    p_p.add_argument('--task-card-id', required=True, help='Task-CARD ID（如 T1.1）')
    p_p.add_argument('--summary', required=True, help='本轮计划摘要')
    p_p.add_argument('--criteria', default=None,
                     help="验收标准列表，用 '|' 分隔（如 '测试通过|文档更新'）")
    p_p.add_argument('--task-card-path', default=None, help='Task-CARD 文件绝对路径（可选）')
    p_p.add_argument('--dl-refs', default=None,
                     help="本轮 Plan 引用的 DL 条目，用 '|' 分隔（如 'DL-2026-001|DL-2026-002'）")
    p_p.add_argument('--topic-id', default=None, help='所属 Topic ID（如 T06，用于层间传播聚合）')
    p_p.add_argument('--project-id', default=None, help='所属 Project ID（如 ZT-P015，用于层间传播聚合）')

    # d
    d_p = subparsers.add_parser('d', help='记录 Do 阶段')
    d_p.add_argument('--task-card-id', required=True)
    d_p.add_argument('--summary', required=True, help='执行结果摘要')
    d_p.add_argument('--status', required=True, choices=sorted(VALID_STATUSES),
                     help='执行状态：completed / blocked / partial')
    d_p.add_argument('--blocker', default=None, help='阻塞原因（status=blocked 时填写）')

    # cqo-review (v8.1 新增)
    cqo_p = subparsers.add_parser('cqo-review', help='记录 CQO 合规闸门审核结果（Do→Check 之间）')
    cqo_p.add_argument('--task-card-id', required=True)
    cqo_p.add_argument('--result', required=True, choices=sorted(CQO_REVIEW_RESULTS),
                       help='CQO 审核结果：pass/revise/reject')
    cqo_p.add_argument('--report-path', default=None,
                       help='CQO 合规报告路径')
    cqo_p.add_argument('--issues', default=None,
                       help="CQO 审核不通过项列表，用 '|' 分隔（如 'CQO-01|CQO-03'）")

    # c
    c_p = subparsers.add_parser('c', help='记录 Check 阶段')
    c_p.add_argument('--task-card-id', required=True)
    c_p.add_argument('--verdict', required=True, choices=sorted(VALID_VERDICTS),
                     help='验收结论：pass/partial/fail/skip/pending')
    c_p.add_argument('--level', required=True, choices=sorted(VALID_LEVELS),
                     help='Review 级别：L0/L1/L2/L3（必填，不可省略）')
    c_p.add_argument('--evidence', default=None,
                     help="验收证据列表，用 '|' 分隔")

    # a
    a_p = subparsers.add_parser('a', help='记录 Act 阶段（完成本轮 PDCA）')
    a_p.add_argument('--task-card-id', required=True)
    a_p.add_argument('--summary', required=True, help='行动决策摘要')
    a_p.add_argument('--next-task', default=None, help='下一个 task ID（如 T1.2）')
    a_p.add_argument('--lessons', default=None,
                     help="经验总结列表，用 '|' 分隔")

    # status
    s_p = subparsers.add_parser('status', help='查看 task 的当前 PDCA 状态（最近 cycle 摘要）')
    s_p.add_argument('--task-card-id', required=True)

    # history
    h_p = subparsers.add_parser('history', help='查看 task 的完整 PDCA 历史（所有 cycle）')
    h_p.add_argument('--task-card-id', required=True)

    # pending
    # pending
    pend_p = subparsers.add_parser('pending',
                          help='列出所有 verdict=pending 的 task（heartbeat Step 0 调用）')
    pend_p.add_argument('--review-level', default=None, choices=['L2', 'L3'],
                        help='按 review_level 过滤（L2=银月抽检，L3=Harold 审批）')

    # audit-queue
    subparsers.add_parser('audit-queue',
                          help='列出所有 audit_eligible=True 且未审计的 cycle（审计 heartbeat 调用）')

    # mark-audit
    ma_p = subparsers.add_parser('mark-audit', help='记录外部审计结果')
    ma_p.add_argument('--task-card-id', required=True)
    ma_p.add_argument('--cycle-index', required=True, type=int, help='要审计的 cycle_index')
    ma_p.add_argument('--score', required=True, type=int, help='审计评分 0-100（<80 表示存在问题）')
    ma_p.add_argument('--issues', default=None, help="发现的问题列表，用 '|' 分隔")

    # aggregate
    agg_p = subparsers.add_parser('aggregate', help='聚合 task verdict 到 topic/project 级（写入 _state.yaml）')
    agg_p.add_argument('--triggered-by', default=None, help='触发来源（如 act:T1.1、heartbeat）')
    agg_p.add_argument('--mode', default='strict', choices=['strict', 'weighted'],
                       help='⭐ P2-1: 聚合模式（strict=严格规则，weighted=权重模式，默认 strict）')

    # verify-cycle-write (P1-1: 幂等性验证)
    vcw_p = subparsers.add_parser('verify-cycle-write', help='⭐ P1-1: 验证 cycle 写入是否成功')
    vcw_p.add_argument('--task-card-id', required=True, help='Task ID')
    vcw_p.add_argument('--cycle-index', type=int, required=True, help='Cycle 索引（从 1 开始）')

    # check-concurrency
    cc_p = subparsers.add_parser('check-concurrency', help='检查当前并发上限')
    cc_p.add_argument('--scope', default='task', choices=['task', 'topic', 'project'],
                      help='检查维度（默认 task）')
    cc_p.add_argument('--scope-id', default=None, help='topic 或 project 级时指定 ID')

    # verify-integrity
    vi_p = subparsers.add_parser('verify-integrity', help='验证 PDCA 文件完整性（checksum）')
    vi_p.add_argument('--task-card-id', default=None, help='指定单个 task 验证（不指定则验证全部）')

    # health-check
    subparsers.add_parser('health-check', help='系统健康检查（文件数/超时/审计/并发）')

    # archive
    arc_p = subparsers.add_parser('archive', help='归档已完成超过 N 天的 PDCA 文件到 _archive/')
    arc_p.add_argument('--older-than-days', type=int, default=None,
                       help=f'归档多少天前完成的数据（默认从配置读取，当前 {ARCHIVE_OLDER_THAN_DAYS}）')
    arc_p.add_argument('--dry-run', action='store_true',
                       help='仅列出待归档文件，不实际移动')

    args = parser.parse_args()

    if args.command == 'p':
        result = p(
            task_card_id=args.task_card_id,
            summary=args.summary,
            acceptance_criteria=_parse_list(args.criteria),
            task_card_path=args.task_card_path,
            dl_refs=_parse_list(args.dl_refs),
            topic_id=args.topic_id,
            project_id=args.project_id,
        )
    elif args.command == 'd':
        result = d(
            task_card_id=args.task_card_id,
            summary=args.summary,
            status=args.status,
            blocker=args.blocker,
        )
    elif args.command == 'cqo-review':
        result = cqo_review(
            task_card_id=args.task_card_id,
            result=args.result,
            report_path=args.report_path,
            issues=_parse_list(args.issues),
        )
    elif args.command == 'c':
        result = c(
            task_card_id=args.task_card_id,
            verdict=args.verdict,
            review_level=args.level,
            evidence=_parse_list(args.evidence),
        )
    elif args.command == 'a':
        result = a(
            task_card_id=args.task_card_id,
            summary=args.summary,
            next_task=args.next_task,
            lessons=_parse_list(args.lessons),
        )
    elif args.command == 'status':
        result = get_status(args.task_card_id)
    elif args.command == 'history':
        result = get_history(args.task_card_id)
    elif args.command == 'pending':
        result = get_pending(review_level=getattr(args, 'review_level', None))
    elif args.command == 'audit-queue':
        result = get_audit_queue()
    elif args.command == 'mark-audit':
        result = mark_audit(
            task_card_id=args.task_card_id,
            cycle_index=args.cycle_index,
            score=args.score,
            issues=_parse_list(args.issues),
        )
    elif args.command == 'aggregate':
        result = aggregate(triggered_by=args.triggered_by, mode=args.mode)
    elif args.command == 'verify-cycle-write':
        result = verify_cycle_write(
            task_card_id=args.task_card_id,
            cycle_index=args.cycle_index
        )
    elif args.command == 'check-concurrency':
        result = check_concurrency(scope=args.scope, scope_id=args.scope_id)
    elif args.command == 'verify-integrity':
        result = verify_integrity(task_card_id=getattr(args, 'task_card_id', None))
    elif args.command == 'health-check':
        result = health_check()
    elif args.command == 'archive':
        days = args.older_than_days if args.older_than_days is not None else ARCHIVE_OLDER_THAN_DAYS
        result = archive(older_than_days=days, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)

    # 执行日志（所有命令）
    _log_call(args.command, vars(args), result)

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
