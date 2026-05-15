#!/usr/bin/env python3
"""
NUCLEUS 数据迁移工具 - Legacy v1/v2 → v4.0

⚠️ P1-2 修复：提供迁移框架，实际迁移价值有限
原因：
  - v1 archive 仅 3 个测试文件，无完整 PDCA cycle
  - v2 仅文档，无数据文件
  - 仅提供框架，未来如有需要可扩展
"""

import argparse
import json
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


def migrate_v1_to_v4(
    v1_dir: Path,
    v4_dir: Path,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    将 v1 数据迁移到 v4 格式

    v1 格式 (简化版，仅 metadata):
        id: task-20260411T033745Z
        metadata:
          created_at: ...
          version: 1
        phase: plan
        plan:
          human_approval_required: false
          max_cycles: 10
        scope: task
        task_card_id: auto-task-cycle

    v4 格式:
        task_card_id: XXX
        task_card_path: null
        topic_id: null
        project_id: null
        cycles:
          - cycle_index: 1
            phase: ...
            p: {...}
            d: {...}
            c: {...}
            a: {...}

    迁移策略：
      v1 数据极简，大部分字段缺失
      只能迁移基本元数据，PDCA 阶段数据无法恢复
      建议：v1 数据作为 lesson learned 保留，不强制迁移
    """
    migrated = []
    errors = []
    skipped = []

    if not v1_dir.exists():
        return {
            'success': False,
            'error': f'v1 directory not found: {v1_dir}'
        }

    # 遍历 v1 cycles/task 目录
    v1_task_dir = v1_dir / 'task'
    if not v1_task_dir.exists():
        return {
            'success': False,
            'error': f'v1 task directory not found: {v1_task_dir}'
        }

    for v1_file in v1_task_dir.glob('*.yaml'):
        try:
            with open(v1_file, 'r', encoding='utf-8') as f:
                v1_data = yaml.safe_load(f)

            # v1 数据极简，缺少完整 PDCA cycle
            # 只能提取基本信息
            task_card_id = v1_data.get('task_card_id', v1_data.get('id'))
            phase = v1_data.get('phase', 'plan')
            created_at = v1_data.get('metadata', {}).get('created_at')

            # 判断是否值得迁移
            if phase == 'plan' and not v1_data.get('do'):
                skipped.append({
                    'file': str(v1_file),
                    'reason': 'v1 数据不完整，仅 plan 阶段，无 PDCA cycle',
                    'task_card_id': task_card_id
                })
                continue

            # 构造 v4 格式（最小可行版本）
            v4_data = {
                'task_card_id': task_card_id,
                'task_card_path': None,
                'topic_id': None,
                'project_id': None,
                'cycles': [{
                    'cycle_index': 1,
                    'phase': phase,
                    'started_at': created_at,
                    'completed_at': None,
                    'p': {
                        'summary': f'v1 迁移：{v1_file.stem}',
                        'acceptance_criteria': [],
                        'dl_refs': [],
                        'timestamp': created_at,
                    }
                }]
            }

            # 写入 v4 目录
            v4_file = v4_dir / f'{task_card_id}.yaml'

            if not dry_run:
                v4_dir.mkdir(parents=True, exist_ok=True)
                with open(v4_file, 'w', encoding='utf-8') as f:
                    yaml.dump(v4_data, f, allow_unicode=True, default_flow_style=False)

            migrated.append({
                'v1_file': str(v1_file),
                'v4_file': str(v4_file),
                'task_card_id': task_card_id,
                'phase': phase
            })

        except Exception as e:
            errors.append({
                'file': str(v1_file),
                'error': str(e)
            })

    return {
        'success': len(errors) == 0,
        'migrated_count': len(migrated),
        'skipped_count': len(skipped),
        'error_count': len(errors),
        'migrated': migrated,
        'skipped': skipped,
        'errors': errors,
        'dry_run': dry_run
    }


def main():
    parser = argparse.ArgumentParser(
        description='NUCLEUS v1/v2 → v4.0 数据迁移工具'
    )
    parser.add_argument(
        '--v1-dir',
        type=Path,
        required=True,
        help='v1 cycles 目录路径（如 nucleus-v1-archive/cycles）'
    )
    parser.add_argument(
        '--v4-dir',
        type=Path,
        required=True,
        help='v4 pdca 目录路径（如 skills/.../nucleus/pdca）'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Dry-run 模式（默认），不实际写入文件'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='实际执行迁移（覆盖 --dry-run）'
    )

    args = parser.parse_args()

    dry_run = not args.execute

    result = migrate_v1_to_v4(
        v1_dir=args.v1_dir,
        v4_dir=args.v4_dir,
        dry_run=dry_run
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result['success']:
        sys.exit(1)


if __name__ == '__main__':
    main()
