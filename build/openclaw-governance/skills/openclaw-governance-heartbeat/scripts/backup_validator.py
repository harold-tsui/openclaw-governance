#!/usr/bin/env python3
"""
backup_validator.py - 备份执行验证器
Version: 1.0.0
Created: 2026-04-20 (NUCLEUS-4.0-TEST-002)

功能：
1. 检查备份目录是否存在
2. 验证备份文件数量和大小
3. 检查备份完整性
4. 生成验证报告

用法：
  python backup_validator.py check [--date YYYY-MM-DD] [--type incremental|full]
  python backup_validator.py verify [--backup-dir PATH]
  python backup_validator.py report
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置
OPENCLAW_LOCAL_WORKSPACE = os.environ.get('OPENCLAW_LOCAL_WORKSPACE',
                                            str(Path.home() / 'Workspaces' / 'openclaw' / 'main'))
BACKUP_ROOT = os.environ.get('OPENCLAW_BACKUP_WORKSPACE',
                              str(Path.home() / 'Workspaces' / 'openclaw.bak'))

# 默认值
DEFAULT_BACKUP_ROOT = str(Path.home() / 'Workspaces' / 'openclaw.bak')
DEFAULT_LOCAL_WORKSPACE = str(Path.home() / 'Workspaces' / 'openclaw' / 'main')

# 验证标准
MIN_FILE_COUNT_INCREMENTAL = 100  # 增量备份最少文件数
MIN_FILE_COUNT_FULL = 500         # 全量备份最少文件数
MIN_SIZE_INCREMENTAL_MB = 10      # 增量备份最小大小
MIN_SIZE_FULL_MB = 50             # 全量备份最小大小


def get_backup_root() -> Path:
    """获取备份根目录"""
    backup_root = BACKUP_ROOT
    if backup_root.startswith('$HOME') or backup_root == '' or backup_root.startswith('~'):
        backup_root = DEFAULT_BACKUP_ROOT
    # 展开 ~ 为实际路径
    backup_root = backup_root.replace('~', str(Path.home()))
    return Path(backup_root)


def get_local_workspace() -> Path:
    """获取本地工作区"""
    local_ws = OPENCLAW_LOCAL_WORKSPACE
    if local_ws.startswith('$HOME') or local_ws == '':
        local_ws = DEFAULT_LOCAL_WORKSPACE
    return Path(local_ws)


def find_backup_dir(date_str: str, backup_type: str) -> Optional[Path]:
    """查找备份目录"""
    backup_root = get_backup_root()
    
    if backup_type == 'incremental':
        backup_dir = backup_root / 'incremental' / date_str
    elif backup_type == 'full':
        # 全量备份使用周格式 YYYY-WWW
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        week_str = date_obj.strftime('%Y-W%W')
        backup_dir = backup_root / 'full' / week_str
    else:
        return None
    
    if backup_dir.exists():
        return backup_dir
    
    return None


def count_files_and_dirs(path: Path) -> Tuple[int, int, int]:
    """统计文件数、目录数和总大小"""
    file_count = 0
    dir_count = 0
    total_size = 0
    
    for item in path.rglob('*'):
        if item.is_file():
            file_count += 1
            total_size += item.stat().st_size
        elif item.is_dir():
            dir_count += 1
    
    return file_count, dir_count, total_size


def verify_backup_integrity(backup_dir: Path) -> Dict:
    """验证备份完整性"""
    result = {
        'path': str(backup_dir),
        'exists': backup_dir.exists(),
        'is_directory': backup_dir.is_dir() if backup_dir.exists() else False,
    }
    
    if not backup_dir.exists():
        result['status'] = 'not_found'
        result['message'] = f"备份目录不存在: {backup_dir}"
        return result
    
    # 统计文件
    file_count, dir_count, total_size = count_files_and_dirs(backup_dir)
    
    result['file_count'] = file_count
    result['dir_count'] = dir_count
    result['total_size_bytes'] = total_size
    result['total_size_mb'] = round(total_size / (1024 * 1024), 2)
    
    # 判断备份类型
    backup_type = 'unknown'
    if 'incremental' in str(backup_dir):
        backup_type = 'incremental'
    elif 'full' in str(backup_dir):
        backup_type = 'full'
    
    result['backup_type'] = backup_type
    
    # 验证标准
    if backup_type == 'incremental':
        min_files = MIN_FILE_COUNT_INCREMENTAL
        min_size_mb = MIN_SIZE_INCREMENTAL_MB
    elif backup_type == 'full':
        min_files = MIN_FILE_COUNT_FULL
        min_size_mb = MIN_SIZE_FULL_MB
    else:
        min_files = 100
        min_size_mb = 10
    
    # 检查完整性
    checks = []
    
    if file_count >= min_files:
        checks.append(('file_count', True, f"{file_count} >= {min_files}"))
    else:
        checks.append(('file_count', False, f"{file_count} < {min_files}"))
    
    if result['total_size_mb'] >= min_size_mb:
        checks.append(('size', True, f"{result['total_size_mb']}MB >= {min_size_mb}MB"))
    else:
        checks.append(('size', False, f"{result['total_size_mb']}MB < {min_size_mb}MB"))
    
    # 检查关键文件
    local_ws = get_local_workspace()
    critical_files = [
        '.system/governance/current',
        'MISSION_BOARD.md',
        'SOUL.md',
        'IDENTITY.md',
    ]
    
    for critical_file in critical_files:
        backup_path = backup_dir / critical_file
        if backup_path.exists():
            checks.append((f'critical_file:{critical_file}', True, 'exists'))
        else:
            checks.append((f'critical_file:{critical_file}', False, 'missing'))
    
    result['checks'] = checks
    result['passed'] = all(c[1] for c in checks)
    
    if result['passed']:
        result['status'] = 'valid'
        result['message'] = f"备份验证通过: {file_count} 文件, {result['total_size_mb']}MB"
    else:
        result['status'] = 'invalid'
        result['message'] = f"备份验证失败: {file_count} 文件, {result['total_size_mb']}MB"
    
    return result


def check_command(args):
    """检查指定日期的备份"""
    date_str = args.get('--date', datetime.now().strftime('%Y-%m-%d'))
    backup_type = args.get('--type', 'incremental')
    
    print(f"[INFO] 检查备份: {date_str} ({backup_type})")
    
    backup_dir = find_backup_dir(date_str, backup_type)
    
    if backup_dir:
        print(f"[INFO] 备份目录: {backup_dir}")
        result = verify_backup_integrity(backup_dir)
        
        status_icon = '✅' if result['passed'] else '❌'
        print(f"\n{status_icon} {result['message']}")
        
        print(f"\n详细统计:")
        print(f"  文件数: {result['file_count']}")
        print(f"  目录数: {result['dir_count']}")
        print(f"  总大小: {result['total_size_mb']}MB")
        
        print(f"\n验证项:")
        for check in result['checks']:
            icon = '✅' if check[1] else '❌'
            print(f"  {icon} {check[0]}: {check[2]}")
        
        return result['passed']
    else:
        print(f"[WARN] 备份目录不存在")
        
        # 检查备份根目录是否存在
        backup_root = get_backup_root()
        if not backup_root.exists():
            print(f"[ERROR] 备份根目录不存在: {backup_root}")
            print(f"[HINT] 请先创建备份目录: mkdir -p {backup_root}")
        
        return False


def verify_command(args):
    """验证指定备份目录"""
    backup_dir_str = args.get('--backup-dir')
    
    if not backup_dir_str:
        print("[ERROR] 需要指定 --backup-dir")
        return False
    
    backup_dir = Path(backup_dir_str)
    
    print(f"[INFO] 验证备份目录: {backup_dir}")
    result = verify_backup_integrity(backup_dir)
    
    status_icon = '✅' if result['passed'] else '❌'
    print(f"\n{status_icon} {result['message']}")
    
    return result['passed']


def report_command(args):
    """生成备份报告"""
    backup_root = get_backup_root()
    
    print(f"[INFO] 备份报告生成")
    print(f"[INFO] 备份根目录: {backup_root}")
    
    if not backup_root.exists():
        print(f"[ERROR] 备份根目录不存在")
        return
    
    # 检查增量备份
    incremental_dir = backup_root / 'incremental'
    if incremental_dir.exists():
        print(f"\n增量备份:")
        for backup_date in sorted(incremental_dir.iterdir(), reverse=True)[:10]:
            if backup_date.is_dir():
                result = verify_backup_integrity(backup_date)
                status_icon = '✅' if result['passed'] else '❌'
                print(f"  {status_icon} {backup_date.name}: {result['file_count']} 文件, {result['total_size_mb']}MB")
    
    # 检查全量备份
    full_dir = backup_root / 'full'
    if full_dir.exists():
        print(f"\n全量备份:")
        for backup_week in sorted(full_dir.iterdir(), reverse=True)[:10]:
            if backup_week.is_dir():
                result = verify_backup_integrity(backup_week)
                status_icon = '✅' if result['passed'] else '❌'
                print(f"  {status_icon} {backup_week.name}: {result['file_count']} 文件, {result['total_size_mb']}MB")
    
    # 检查最近备份状态
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\n备份状态检查:")
    print(f"  今日 ({today}):")
    today_backup = find_backup_dir(today, 'incremental')
    if today_backup:
        print(f"    ✅ 已备份")
    else:
        print(f"    ❌ 未备份")
    
    print(f"  昨日 ({yesterday}):")
    yesterday_backup = find_backup_dir(yesterday, 'incremental')
    if yesterday_backup:
        print(f"    ✅ 已备份")
    else:
        print(f"    ❌ 未备份")


def get_last_backup_date() -> Optional[str]:
    """获取最后一次备份日期"""
    backup_root = get_backup_root()
    
    if not backup_root.exists():
        return None
    
    incremental_dir = backup_root / 'incremental'
    if not incremental_dir.exists():
        return None
    
    # 找到最新的备份目录
    backups = sorted([d for d in incremental_dir.iterdir() if d.is_dir()], reverse=True)
    
    if backups:
        return backups[0].name
    
    return None


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    args = {}
    
    # 解析参数
    i = 2
    while i < len(sys.argv):
        if sys.argv[i].startswith('--'):
            key = sys.argv[i]
            value = sys.argv[i + 1] if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--') else True
            args[key] = value
            i += 2 if value != True else 1
        else:
            i += 1
    
    # 执行命令
    if command == 'check':
        check_command(args)
    elif command == 'verify':
        verify_command(args)
    elif command == 'report':
        report_command(args)
    else:
        print(f"[ERROR] 未知命令: {command}")
        print(__doc__)


if __name__ == '__main__':
    main()