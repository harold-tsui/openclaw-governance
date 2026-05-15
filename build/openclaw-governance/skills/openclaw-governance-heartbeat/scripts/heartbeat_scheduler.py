#!/usr/bin/env python3
"""
heartbeat_scheduler.py - Heartbeat 周期性任务时间匹配与触发引擎
Version: 1.0.0
Created: 2026-04-20 (NUCLEUS-4.0-TEST-002)

功能：
1. 解析 MISSION_BOARD.md §十一 的周期性任务定义
2. 匹配当前时间与任务触发条件
3. 识别应执行但未执行的任务
4. 调用对应的执行脚本
5. 记录执行状态

用法：
  python heartbeat_scheduler.py scan [--mission-board PATH]
  python heartbeat_scheduler.py check [--time HH:MM]
  python heartbeat_scheduler.py trigger [--task-id TASK_ID]
  python heartbeat_scheduler.py status
"""

import os
import sys
import re
import json
import yaml
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置
OPENCLAW_LOCAL_WORKSPACE = os.environ.get('OPENCLAW_LOCAL_WORKSPACE', 
                                            str(Path.home() / 'Workspaces' / 'openclaw' / 'main'))
HEARTBEAT_STATE_FILE = Path(OPENCLAW_LOCAL_WORKSPACE) / '.system' / 'governance' / 'heartbeat-state.json'
EXECUTION_LOG_FILE = Path(OPENCLAW_LOCAL_WORKSPACE) / '.system' / 'governance' / 'heartbeat-logs' / 'scheduled_tasks.json'

# 任务脚本路径映射
TASK_SCRIPTS = {
    'SYS-DATA-OPS-T01': {
        'script': Path(OPENCLAW_LOCAL_WORKSPACE) / 'skills' / 'openclaw-governance' / 
                   'skills' / 'openclaw-governance-data' / 'scripts' / 'backup.sh',
        'args': ['incremental'],
        'validator': 'backup_validator.py',
        'output_pattern': 'incremental/{date}/'
    },
    'SYS-DATA-OPS-T02': {
        'script': Path(OPENCLAW_LOCAL_WORKSPACE) / 'skills' / 'openclaw-governance' /
                   'skills' / 'openclaw-governance-data' / 'scripts' / 'backup.sh',
        'args': ['full'],
        'validator': 'backup_validator.py',
        'output_pattern': 'full/{year}-W{week}/'
    },
    'SYS-DATA-OPS-T05': {
        'script': None,  # 湖仓监控脚本（待创建）
        'args': [],
        'validator': None,
        'output_pattern': None
    },
}


class TaskDefinition:
    """周期性任务定义"""
    def __init__(self, task_id: str, trigger_time: str, trigger_day: Optional[str] = None,
                 script: Optional[str] = None, validator: Optional[str] = None):
        self.task_id = task_id
        self.trigger_time = trigger_time  # HH:MM 格式
        self.trigger_day = trigger_day    # None=每天, "Sunday"=每周日, etc.
        self.script = script
        self.validator = validator
        
    def should_execute(self, current_time: datetime) -> bool:
        """判断当前时间是否应该执行"""
        # 时间匹配（允许 30 分钟窗口）
        current_hhmm = current_time.strftime('%H:%M')
        trigger_hhmm = self.trigger_time
        
        # 计算时间窗口（触发时间前后 15 分钟）
        trigger_dt = datetime.strptime(trigger_hhmm, '%H:%M')
        current_dt = datetime.strptime(current_hhmm, '%H:%M')
        
        # 处理跨午夜情况
        diff = abs((current_dt - trigger_dt).total_seconds())
        if diff > 12 * 3600:  # 超过 12 小时，可能是跨午夜
            diff = 24 * 3600 - diff
        
        time_match = diff <= 900  # 15 分钟窗口
        
        # 星期匹配
        if self.trigger_day:
            day_match = current_time.strftime('%A') == self.trigger_day
        else:
            day_match = True
        
        return time_match and day_match
    
    def __repr__(self):
        return f"TaskDefinition({self.task_id}, time={self.trigger_time}, day={self.trigger_day})"


def parse_mission_board(mission_board_path: Path) -> List[TaskDefinition]:
    """解析 MISSION_BOARD.md §十一 的周期性任务定义"""
    tasks = []
    
    if not mission_board_path.exists():
        print(f"[WARN] MISSION_BOARD.md 不存在: {mission_board_path}")
        return tasks
    
    content = mission_board_path.read_text()
    
    # 匹配 §十一 或 §十一、📅 Heartbeat 自动化配置
    section_pattern = r'##\s*十一、📅 Heartbeat 自动化配置|##\s*十一.*Heartbeat.*配置'
    
    # 查找章节位置
    section_match = re.search(section_pattern, content)
    if not section_match:
        print(f"[WARN] 未找到 §十一 Heartbeat 自动化配置章节")
        return tasks
    
    section_content = content[section_match.end():]
    
    # 找到下一个 ## 标题作为结束
    next_section = re.search(r'\n##\s', section_content)
    if next_section:
        section_content = section_content[:next_section.start()]
    
    # 解析表格中的任务定义
    # 格式: | Task ID | 触发条件 | 执行时间 | Heartbeat 检查项 |
    table_pattern = r'\|[\s]*([A-Z0-9\-]+)[\s]*\|[\s]*(每天|每周日|触发式|每季度)[\s]*\|[\s]*(\d{2}:\d{2})[\s]*\|'
    
    for match in re.finditer(table_pattern, section_content):
        task_id = match.group(1).strip()
        trigger_condition = match.group(2).strip()
        trigger_time = match.group(3).strip()
        
        # 转换触发条件
        if trigger_condition == '每天':
            trigger_day = None
        elif trigger_condition == '每周日':
            trigger_day = 'Sunday'
        elif trigger_condition == '每季度':
            trigger_day = 'Quarterly'  # 特殊处理
        else:
            trigger_day = None
        
        # 获取脚本配置
        script_config = TASK_SCRIPTS.get(task_id, {})
        
        task = TaskDefinition(
            task_id=task_id,
            trigger_time=trigger_time,
            trigger_day=trigger_day,
            script=str(script_config.get('script', '')) if script_config.get('script') else None,
            validator=str(script_config.get('validator', '')) if script_config.get('validator') else None
        )
        tasks.append(task)
    
    return tasks


def get_execution_state() -> Dict:
    """获取执行状态"""
    if EXECUTION_LOG_FILE.exists():
        return json.loads(EXECUTION_LOG_FILE.read_text())
    return {'executions': {}, 'last_check': None}


def save_execution_state(state: Dict):
    """保存执行状态"""
    EXECUTION_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    EXECUTION_LOG_FILE.write_text(json.dumps(state, indent=2, default=str))


def check_already_executed(task_id: str, date_str: str, state: Dict) -> bool:
    """检查任务今日是否已执行"""
    executions = state.get('executions', {})
    task_executions = executions.get(task_id, [])
    
    for exec_record in task_executions:
        if exec_record.get('date') == date_str:
            return exec_record.get('status') == 'completed'
    
    return False


def execute_task(task: TaskDefinition) -> Tuple[bool, str]:
    """执行任务脚本"""
    if not task.script:
        return False, f"No script defined for {task.task_id}"
    
    script_path = Path(task.script)
    if not script_path.exists():
        return False, f"Script not found: {script_path}"
    
    # 获取脚本参数
    script_config = TASK_SCRIPTS.get(task.task_id, {})
    args = script_config.get('args', [])
    
    try:
        # 执行脚本
        cmd = ['bash', str(script_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, f"Script failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "Script execution timeout (300s)"
    except Exception as e:
        return False, f"Execution error: {str(e)}"


def scan_command(args):
    """扫描 MISSION_BOARD 并输出周期性任务"""
    mission_board_path = args.get('--mission-board', 
                                   Path(OPENCLAW_LOCAL_WORKSPACE) / '60_Agents' / 'cdo' / 'MISSION_BOARD.md')
    
    print(f"[INFO] 扫描 MISSION_BOARD: {mission_board_path}")
    tasks = parse_mission_board(Path(mission_board_path))
    
    print(f"\n发现 {len(tasks)} 个周期性任务:")
    for task in tasks:
        print(f"  - {task.task_id}: {task.trigger_time} ({task.trigger_day or '每天'})")
    
    return tasks


def check_command(args):
    """检查当前时间应执行的任务"""
    current_time = datetime.now()
    
    # 允许指定时间进行测试
    if '--time' in args:
        time_str = args['--time']
        current_time = datetime.strptime(f"{current_time.strftime('%Y-%m-%d')} {time_str}", 
                                          '%Y-%m-%d %H:%M')
    
    print(f"[INFO] 检查时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 扫描任务 - 读取全局 MISSION_BOARD.md（周期性任务定义在 §十一）
    mission_board_path = Path(OPENCLAW_LOCAL_WORKSPACE) / 'MISSION_BOARD.md'
    tasks = parse_mission_board(mission_board_path)
    
    # 获取执行状态
    state = get_execution_state()
    date_str = current_time.strftime('%Y-%m-%d')
    
    # 检查应执行的任务
    should_execute = []
    already_executed = []
    
    for task in tasks:
        if task.should_execute(current_time):
            if check_already_executed(task.task_id, date_str, state):
                already_executed.append(task)
            else:
                should_execute.append(task)
    
    print(f"\n应执行任务: {len(should_execute)}")
    for task in should_execute:
        print(f"  ⚠️ {task.task_id}: {task.trigger_time} - 未执行")
    
    print(f"\n已执行任务: {len(already_executed)}")
    for task in already_executed:
        print(f"  ✅ {task.task_id}: {task.trigger_time} - 已完成")
    
    return should_execute


def trigger_command(args):
    """触发指定任务执行"""
    task_id = args.get('--task-id')
    
    if not task_id:
        print("[ERROR] 需要指定 --task-id")
        return False
    
    # 获取任务定义 - 读取全局 MISSION_BOARD.md
    mission_board_path = Path(OPENCLAW_LOCAL_WORKSPACE) / 'MISSION_BOARD.md'
    tasks = parse_mission_board(mission_board_path)
    
    task = None
    for t in tasks:
        if t.task_id == task_id:
            task = t
            break
    
    if not task:
        print(f"[ERROR] 未找到任务: {task_id}")
        return False
    
    print(f"[INFO] 触发任务: {task_id}")
    print(f"[INFO] 脚本: {task.script}")
    
    # 执行任务
    success, output = execute_task(task)
    
    # 记录执行状态
    state = get_execution_state()
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    if task_id not in state['executions']:
        state['executions'][task_id] = []
    
    state['executions'][task_id].append({
        'date': date_str,
        'time': datetime.now().strftime('%H:%M:%S'),
        'status': 'completed' if success else 'failed',
        'output': output[:500] if output else None
    })
    
    state['last_check'] = datetime.now().isoformat()
    save_execution_state(state)
    
    if success:
        print(f"[SUCCESS] 任务执行成功")
        print(output)
    else:
        print(f"[FAILED] 任务执行失败: {output}")
    
    return success


def status_command(args):
    """显示执行状态"""
    state = get_execution_state()
    
    print(f"\n最后检查时间: {state.get('last_check', 'Never')}")
    print(f"\n执行记录:")
    
    for task_id, executions in state.get('executions', {}).items():
        print(f"\n{task_id}:")
        for exec_record in executions[-5:]:  # 最近 5 条
            status_icon = '✅' if exec_record['status'] == 'completed' else '❌'
            print(f"  {status_icon} {exec_record['date']} {exec_record['time']}")


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
    if command == 'scan':
        scan_command(args)
    elif command == 'check':
        check_command(args)
    elif command == 'trigger':
        trigger_command(args)
    elif command == 'status':
        status_command(args)
    else:
        print(f"[ERROR] 未知命令: {command}")
        print(__doc__)


if __name__ == '__main__':
    main()