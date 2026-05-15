#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test NUCLEUS Scheduler Integration

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys

# 添加项目路径
project_dir = "/Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0"
sys.path.insert(0, project_dir)

# 创建必要的目录
os.makedirs("logs", exist_ok=True)
os.makedirs("cycles/task", exist_ok=True)

from core.nucleus_scheduler_integration import integrate_nucleus_scheduler

if __name__ == "__main__":
    print("Testing NUCLEUS Scheduler Integration...")
    result = integrate_nucleus_scheduler()
    print(f"Integration result: {result}")
    
    if result:
        print("✅ Integration successful!")
        print(f"   Triggered scopes: {result.get('triggered_scopes', [])}")
        print(f"   Created cycles: {result.get('created_cycles', [])}")
    else:
        print("ℹ️  Integration returned None (expected if no triggers)")