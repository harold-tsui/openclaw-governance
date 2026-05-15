#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Human Time 单元测试

测试双时间计量系统的核心功能

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import unittest
import tempfile
import yaml
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.human_time import (
    load_business_hours_config,
    is_work_time,
    get_next_work_time,
    calculate_work_hours,
    add_work_hours,
    cycles_to_work_hours,
    work_hours_to_cycles
)


class TestHumanTime(unittest.TestCase):
    """测试人类时间计算核心功能"""
    
    def setUp(self):
        """创建临时测试目录和配置"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 创建配置目录
        os.makedirs("config", exist_ok=True)
        
        # 创建测试配置
        self.test_config = {
            'timezone': 'Asia/Shanghai',
            'work_hours': {'start': '09:00', 'end': '18:00'},
            'work_days': [0, 1, 2, 3, 4],  # 周一至周五
            'holidays': ['2026-04-06'],  # 清明节假期
            'heartbeat': {
                'interval_minutes': 30,
                'cycles_per_day': 48,
                'work_cycles_per_day': 18
            }
        }
        
        with open('config/business_hours.yaml', 'w') as f:
            yaml.dump(self.test_config, f)
    
    def tearDown(self):
        """清理临时目录"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_config(self):
        """测试配置加载"""
        config = load_business_hours_config()
        
        self.assertEqual(config['timezone'], 'Asia/Shanghai')
        self.assertEqual(config['work_hours']['start'], '09:00')
        self.assertEqual(config['work_hours']['end'], '18:00')
    
    def test_is_work_time_workday(self):
        """测试工作日工作时间判断"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周一 10:00（工作日，工作时间）
        dt = datetime(2026, 4, 7, 10, 0, tzinfo=tz)  # 周二
        self.assertTrue(is_work_time(dt, self.test_config))
        
        # 周一 12:00（中午，工作时间）
        dt = datetime(2026, 4, 7, 12, 0, tzinfo=tz)
        self.assertTrue(is_work_time(dt, self.test_config))
        
        # 周一 17:30（工作时间）
        dt = datetime(2026, 4, 7, 17, 30, tzinfo=tz)
        self.assertTrue(is_work_time(dt, self.test_config))
    
    def test_is_work_time_outside_hours(self):
        """测试工作日非工作时间"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周一 08:00（工作日，非工作时间）
        dt = datetime(2026, 4, 7, 8, 0, tzinfo=tz)
        self.assertFalse(is_work_time(dt, self.test_config))
        
        # 周一 18:00（工作日，非工作时间）
        dt = datetime(2026, 4, 7, 18, 0, tzinfo=tz)
        self.assertFalse(is_work_time(dt, self.test_config))
        
        # 周一 20:00（工作日，非工作时间）
        dt = datetime(2026, 4, 7, 20, 0, tzinfo=tz)
        self.assertFalse(is_work_time(dt, self.test_config))
    
    def test_is_work_time_weekend(self):
        """测试周末判断"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周六 10:00
        dt = datetime(2026, 4, 11, 10, 0, tzinfo=tz)
        self.assertFalse(is_work_time(dt, self.test_config))
        
        # 周日 14:00
        dt = datetime(2026, 4, 12, 14, 0, tzinfo=tz)
        self.assertFalse(is_work_time(dt, self.test_config))
    
    def test_is_work_time_holiday(self):
        """测试节假日判断"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 清明节假期（2026-04-06，周一，但配置为节假日）
        dt = datetime(2026, 4, 6, 10, 0, tzinfo=tz)
        self.assertFalse(is_work_time(dt, self.test_config))
    
    def test_get_next_work_time_from_weekend(self):
        """测试从周末获取下一个工作时间"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周六 10:00 → 下一个工作日周一 09:00
        dt = datetime(2026, 4, 11, 10, 0, tzinfo=tz)
        next_work = get_next_work_time(dt, self.test_config)
        
        self.assertEqual(next_work.weekday(), 0)  # 周一
        self.assertEqual(next_work.hour, 9)
    
    def test_get_next_work_time_from_evening(self):
        """测试从晚上获取下一个工作时间"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周一 20:00 → 下一个工作日周二 09:00
        dt = datetime(2026, 4, 7, 20, 0, tzinfo=tz)
        next_work = get_next_work_time(dt, self.test_config)
        
        self.assertEqual(next_work.day, 8)  # 周二
        self.assertEqual(next_work.hour, 9)
    
    def test_calculate_work_hours_same_day(self):
        """测试同一天的工作小时计算"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周一 09:00 到 周一 12:00
        start = datetime(2026, 4, 7, 9, 0, tzinfo=tz)
        end = datetime(2026, 4, 7, 12, 0, tzinfo=tz)
        
        hours = calculate_work_hours(start, end, self.test_config)
        self.assertEqual(hours, 3.0)
    
    def test_calculate_work_hours_cross_days(self):
        """测试跨天的工作小时计算"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周一 09:00 到 周二 12:00
        start = datetime(2026, 4, 7, 9, 0, tzinfo=tz)
        end = datetime(2026, 4, 8, 12, 0, tzinfo=tz)
        
        hours = calculate_work_hours(start, end, self.test_config)
        # 周一 9h + 周二 3h = 12h
        self.assertEqual(hours, 12.0)
    
    def test_calculate_work_hours_skip_weekend(self):
        """测试跨周末的工作小时计算"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周五 09:00 到 下周一 12:00
        start = datetime(2026, 4, 10, 9, 0, tzinfo=tz)  # 周五
        end = datetime(2026, 4, 13, 12, 0, tzinfo=tz)  # 下周一
        
        hours = calculate_work_hours(start, end, self.test_config)
        # 周五 9h + 周一 3h = 12h
        self.assertEqual(hours, 12.0)
    
    def test_add_work_hours_same_day(self):
        """测试同一天添加工作小时"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周一 10:00 + 3 小时
        start = datetime(2026, 4, 7, 10, 0, tzinfo=tz)
        result = add_work_hours(start, 3, self.test_config)
        
        self.assertEqual(result.day, 7)
        self.assertEqual(result.hour, 13)
    
    def test_add_work_hours_cross_day(self):
        """测试跨天添加工作小时"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周一 16:00 + 4 小时 → 周二 11:00
        start = datetime(2026, 4, 7, 16, 0, tzinfo=tz)
        result = add_work_hours(start, 4, self.test_config)
        
        self.assertEqual(result.day, 8)  # 周二
        self.assertEqual(result.hour, 11)
    
    def test_add_work_hours_skip_weekend(self):
        """测试跨周末添加工作小时"""
        tz = ZoneInfo('Asia/Shanghai')
        
        # 周五 16:00 + 4 小时 → 下周一 11:00
        start = datetime(2026, 4, 10, 16, 0, tzinfo=tz)  # 周五
        result = add_work_hours(start, 4, self.test_config)
        
        self.assertEqual(result.weekday(), 0)  # 周一
        self.assertEqual(result.hour, 11)
    
    def test_cycles_to_work_hours(self):
        """测试周期到工作小时转换"""
        # 4 个周期 = 2 小时
        hours = cycles_to_work_hours(4)
        self.assertEqual(hours, 2.0)
        
        # 1 个周期 = 0.5 小时
        hours = cycles_to_work_hours(1)
        self.assertEqual(hours, 0.5)
    
    def test_work_hours_to_cycles(self):
        """测试工作小时到周期转换"""
        # 2 小时 = 4 个周期
        cycles = work_hours_to_cycles(2)
        self.assertEqual(cycles, 4)
        
        # 1 小时 = 2 个周期
        cycles = work_hours_to_cycles(1)
        self.assertEqual(cycles, 2)
    
    def test_round_trip_conversion(self):
        """测试往返转换"""
        original_hours = 3.5
        cycles = work_hours_to_cycles(original_hours)
        converted_hours = cycles_to_work_hours(cycles)
        
        self.assertEqual(original_hours, converted_hours)


if __name__ == "__main__":
    unittest.main(verbosity=2)