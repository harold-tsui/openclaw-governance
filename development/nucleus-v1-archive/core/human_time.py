#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Human Time - 双时间计量系统

实现机器时间（heartbeat 周期）和人类时间（工作时间）的转换。

依据：ARCH v1.4.3 §2.1.1 + §4.3

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import yaml
from typing import List, Optional
from datetime import datetime, time, timedelta, date
from zoneinfo import ZoneInfo


# ── 常量定义 ────────────────────────────────────────

DEFAULT_CONFIG_PATH = "config/business_hours.yaml"

# Heartbeat 间隔（分钟）
HEARTBEAT_INTERVAL_MINUTES = 30

# 每个工作日的 heartbeat 周期数
CYCLES_PER_WORK_HOUR = 2  # 30分钟一个周期


# ── 配置加载 ────────────────────────────────────────

def load_business_hours_config(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    """加载工作时间配置"""
    
    if not os.path.exists(config_path):
        # 返回默认配置
        return {
            'timezone': 'Asia/Shanghai',
            'work_hours': {'start': '09:00', 'end': '18:00'},
            'work_days': [0, 1, 2, 3, 4],
            'holidays': [],
            'heartbeat': {
                'interval_minutes': 30,
                'cycles_per_day': 48,
                'work_cycles_per_day': 18
            }
        }
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# ── 核心接口 ────────────────────────────────────────

def is_work_time(dt: datetime, config: Optional[dict] = None) -> bool:
    """
    判断是否为工作时间
    
    Args:
        dt: 待判断的时间点
        config: 配置字典（可选）
    
    Returns:
        bool: 是否为工作时间
    """
    
    if config is None:
        config = load_business_hours_config()
    
    # 获取时区
    tz = ZoneInfo(config.get('timezone', 'Asia/Shanghai'))
    
    # 转换为本地时间
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    local_dt = dt.astimezone(tz)
    
    # 检查是否为节假日
    date_str = local_dt.strftime('%Y-%m-%d')
    if date_str in config.get('holidays', []):
        return False
    
    # 检查是否为工作日
    weekday = local_dt.weekday()  # 0=周一, 6=周日
    if weekday not in config.get('work_days', [1, 2, 3, 4, 5]):
        return False
    
    # 检查是否在工作时段内
    work_hours = config.get('work_hours', {'start': '09:00', 'end': '18:00'})
    start_time = datetime.strptime(work_hours['start'], '%H:%M').time()
    end_time = datetime.strptime(work_hours['end'], '%H:%M').time()
    
    current_time = local_dt.time()
    return start_time <= current_time < end_time


def get_next_work_time(dt: datetime, config: Optional[dict] = None) -> datetime:
    """
    获取下一个工作时间
    
    Args:
        dt: 起始时间点
        config: 配置字典（可选）
    
    Returns:
        datetime: 下一个工作时间点
    """
    
    if config is None:
        config = load_business_hours_config()
    
    tz = ZoneInfo(config.get('timezone', 'Asia/Shanghai'))
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    
    local_dt = dt.astimezone(tz)
    work_hours = config.get('work_hours', {'start': '09:00', 'end': '18:00'})
    start_time = datetime.strptime(work_hours['start'], '%H:%M').time()
    end_time = datetime.strptime(work_hours['end'], '%H:%M').time()
    
    # 向前搜索，最多搜索 14 天
    for i in range(14):
        check_date = (local_dt + timedelta(days=i)).date()
        date_str = check_date.strftime('%Y-%m-%d')
        
        # 跳过节假日
        if date_str in config.get('holidays', []):
            continue
        
        # 跳过非工作日
        if check_date.weekday() not in config.get('work_days', [1, 2, 3, 4, 5]):
            continue
        
        # 构造工作开始时间
        candidate = datetime.combine(check_date, start_time, tzinfo=tz)
        
        # 如果是当天，检查是否已经过了工作开始时间
        if i == 0 and local_dt.time() >= start_time:
            # 今天已经过了开始时间，检查是否还在工作时段内
            if local_dt.time() < end_time:
                # 还在工作时段内，返回当前时间的下一个整点
                return local_dt
            else:
                # 已经过了工作时段，继续检查下一天
                continue
        
        return candidate
    
    # 找不到工作日，返回当前时间 + 14 天
    return local_dt + timedelta(days=14)


def calculate_work_hours(start: datetime, end: datetime, config: Optional[dict] = None) -> float:
    """
    计算两个时间点之间的工作小时数
    
    Args:
        start: 开始时间
        end: 结束时间
        config: 配置字典（可选）
    
    Returns:
        float: 工作小时数
    """
    
    if config is None:
        config = load_business_hours_config()
    
    if start >= end:
        return 0.0
    
    tz = ZoneInfo(config.get('timezone', 'Asia/Shanghai'))
    
    if start.tzinfo is None:
        start = start.replace(tzinfo=tz)
    if end.tzinfo is None:
        end = end.replace(tzinfo=tz)
    
    work_hours = config.get('work_hours', {'start': '09:00', 'end': '18:00'})
    start_time = datetime.strptime(work_hours['start'], '%H:%M').time()
    end_time = datetime.strptime(work_hours['end'], '%H:%M').time()
    
    total_hours = 0.0
    current = start
    
    while current < end:
        # 检查当天是否为工作日
        date_str = current.strftime('%Y-%m-%d')
        if date_str in config.get('holidays', []):
            current = datetime.combine(current.date() + timedelta(days=1), start_time, tzinfo=tz)
            continue
        
        if current.weekday() not in config.get('work_days', [1, 2, 3, 4, 5]):
            current = datetime.combine(current.date() + timedelta(days=1), start_time, tzinfo=tz)
            continue
        
        # 计算当天的工作时间
        day_start = datetime.combine(current.date(), start_time, tzinfo=tz)
        day_end = datetime.combine(current.date(), end_time, tzinfo=tz)
        
        # 计算实际时间段
        actual_start = max(current, day_start)
        actual_end = min(end, day_end)
        
        if actual_start < actual_end:
            hours = (actual_end - actual_start).total_seconds() / 3600
            total_hours += hours
        
        # 移动到下一天
        current = datetime.combine(current.date() + timedelta(days=1), start_time, tzinfo=tz)
    
    return total_hours


def add_work_hours(dt: datetime, hours: float, config: Optional[dict] = None) -> datetime:
    """
    在工作时间基础上添加指定小时数
    
    Args:
        dt: 起始时间
        hours: 工作小时数
        config: 配置字典（可选）
    
    Returns:
        datetime: 计算后的时间点
    """
    
    if config is None:
        config = load_business_hours_config()
    
    if hours <= 0:
        return dt
    
    tz = ZoneInfo(config.get('timezone', 'Asia/Shanghai'))
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    
    work_hours = config.get('work_hours', {'start': '09:00', 'end': '18:00'})
    start_time = datetime.strptime(work_hours['start'], '%H:%M').time()
    end_time = datetime.strptime(work_hours['end'], '%H:%M').time()
    
    remaining_hours = hours
    current = dt
    
    # 最多迭代 30 天
    for _ in range(30):
        # 如果不在工作时间，跳到下一个工作时间
        if not is_work_time(current, config):
            current = get_next_work_time(current, config)
        
        # 检查当天是否为工作日
        date_str = current.strftime('%Y-%m-%d')
        if date_str in config.get('holidays', []):
            current = datetime.combine(current.date() + timedelta(days=1), start_time, tzinfo=tz)
            continue
        
        if current.weekday() not in config.get('work_days', [1, 2, 3, 4, 5]):
            current = datetime.combine(current.date() + timedelta(days=1), start_time, tzinfo=tz)
            continue
        
        # 计算当天剩余工作时间
        day_end = datetime.combine(current.date(), end_time, tzinfo=tz)
        available_hours = (day_end - current).total_seconds() / 3600
        
        if remaining_hours <= available_hours:
            # 当天可以完成
            return current + timedelta(hours=remaining_hours)
        else:
            # 当天无法完成，移动到下一天
            remaining_hours -= available_hours
            current = datetime.combine(current.date() + timedelta(days=1), start_time, tzinfo=tz)
    
    # 超过 30 天，返回最后计算结果
    return current


def cycles_to_work_hours(cycles: int) -> float:
    """
    将 heartbeat 周期数转换为工作小时数
    
    Args:
        cycles: heartbeat 周期数
    
    Returns:
        float: 工作小时数
    """
    
    return cycles * HEARTBEAT_INTERVAL_MINUTES / 60


def work_hours_to_cycles(hours: float) -> int:
    """
    将工作小时数转换为 heartbeat 周期数
    
    Args:
        hours: 工作小时数
    
    Returns:
        int: heartbeat 周期数
    """
    
    return int(hours * 60 / HEARTBEAT_INTERVAL_MINUTES)


# ── 单元测试入口 ────────────────────────────────────

if __name__ == "__main__":
    print("Human Time 模块测试...")
    
    # 设置时区
    tz = ZoneInfo('Asia/Shanghai')
    
    print(f"\n1. 测试工作时间判断...")
    # 工作日 10:00
    dt1 = datetime(2026, 4, 6, 10, 0, tzinfo=tz)  # 周一
    print(f"   周一 10:00: is_work_time = {is_work_time(dt1)}")
    
    # 工作日 20:00
    dt2 = datetime(2026, 4, 6, 20, 0, tzinfo=tz)
    print(f"   周一 20:00: is_work_time = {is_work_time(dt2)}")
    
    # 周末
    dt3 = datetime(2026, 4, 5, 10, 0, tzinfo=tz)  # 周日
    print(f"   周日 10:00: is_work_time = {is_work_time(dt3)}")
    
    print(f"\n2. 测试周期转换...")
    hours = cycles_to_work_hours(4)
    print(f"   4 cycles = {hours} hours")
    
    cycles = work_hours_to_cycles(2)
    print(f"   2 hours = {cycles} cycles")
    
    print("\n✅ 基础测试完成")