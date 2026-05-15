#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NUCLEUS 4.0 核心功能快速验证

Author: 张铁 (CQO)
Date: 2026-04-16
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("NUCLEUS 4.0 核心功能验证")
print("=" * 60)

# 1. 测试 scheduler 导入
print("\n[1] 测试 scheduler 导入...")
try:
    from core.scheduler import on_heartbeat
    print("✅ scheduler import OK")
except Exception as e:
    print(f"❌ scheduler import FAILED: {e}")
    sys.exit(1)

# 2. 测试 cycle_aggregator 导入
print("\n[2] 测试 cycle_aggregator 导入...")
try:
    from modules.cycle_aggregator import CycleAggregator
    print("✅ cycle_aggregator import OK")
except Exception as e:
    print(f"❌ cycle_aggregator import FAILED: {e}")
    sys.exit(1)

# 3. 测试 on_heartbeat 调用
print("\n[3] 测试 on_heartbeat 调用...")
try:
    result = on_heartbeat()
    print(f"✅ on_heartbeat executed: {result}")
except Exception as e:
    print(f"❌ on_heartbeat FAILED: {e}")
    sys.exit(1)

# 4. 测试 CycleAggregator 初始化
print("\n[4] 测试 CycleAggregator 初始化...")
try:
    cycles_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cycles")
    aggregator = CycleAggregator(cycles_dir)
    print("✅ CycleAggregator initialized")
except Exception as e:
    print(f"❌ CycleAggregator FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有核心功能验证通过")
print("=" * 60)