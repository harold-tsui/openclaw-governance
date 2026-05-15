#!/usr/bin/env python3
"""
state_manager.py - 模块状态管理工具

管理 governance skills 的模块状态（success/degraded/failed/loading）。

Version: 7.0.0
Author: Governance Core Team
Created: 2026-04-04
Updated: 2026-04-22

Usage:
    python state_manager.py --get core
    python state_manager.py --set core success
    python state_manager.py --list
    python state_manager.py --help

References:
    - SKILL.md §三 Phase 屏障规则
    - SKILL.md §四 失败处理行为规范
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional


# 模块状态枚举（来自 governance-core SKILL.md）
STATE_ENUM = ["success", "degraded", "failed", "loading", "soft_failed"]

# 模块 Tier 分组（来自 SKILL.md §三.4）
MODULE_TIERS = {
    "Tier 1": ["core", "dispatch"],
    "Tier 2": ["config", "hierarchy", "data", "delegation"],
    "Tier 3": ["quality", "task", "heartbeat", "knowledge", "nucleus"]
}

# Tier 超时配置（来自 SKILL.md §三.4）
TIER_TIMEOUTS = {
    "Tier 1": 2,  # 2s
    "Tier 2": 5,  # 5s
    "Tier 3": 10  # 10s
}


class StateManager:
    """状态管理器"""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.states: Dict[str, str] = {}
        self.load_states()
    
    def load_states(self) -> None:
        """从文件加载状态"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.states = json.load(f)
        else:
            # 初始化默认状态
            self.states = {module: "loading" for module in self._all_modules()}
    
    def save_states(self) -> None:
        """保存状态到文件"""
        with open(self.state_file, 'w') as f:
            json.dump(self.states, f, indent=2)
    
    def get_state(self, module: str) -> str:
        """获取模块状态
        
        Args:
            module: 模块名称
            
        Returns:
            模块状态（success/degraded/failed/loading/soft_failed）
        """
        if module not in self.states:
            print(f"❌ Unknown module: {module}")
            return "unknown"
        
        return self.states[module]
    
    def set_state(self, module: str, state: str) -> bool:
        """设置模块状态
        
        Args:
            module: 模块名称
            state: 新状态
            
        Returns:
            True if successful, False otherwise
        """
        if module not in self.states:
            print(f"❌ Unknown module: {module}")
            return False
        
        if state not in STATE_ENUM:
            print(f"❌ Invalid state: {state}")
            print(f"   Valid states: {STATE_ENUM}")
            return False
        
        old_state = self.states[module]
        self.states[module] = state
        self.save_states()
        
        print(f"✅ {module}: {old_state} → {state}")
        
        # 检查传播规则
        self._check_propagation(module, state)
        
        return True
    
    def list_states(self) -> None:
        """列出所有模块状态"""
        print("Module States:")
        print("-" * 40)
        
        for module, state in sorted(self.states.items()):
            tier = self._get_tier(module)
            timeout = TIER_TIMEOUTS.get(tier, "N/A")
            
            status_icon = {
                "success": "✅",
                "degraded": "⚠️",
                "failed": "❌",
                "loading": "🔄",
                "soft_failed": "🔶"
            }.get(state, "❓")
            
            print(f"{status_icon} {module}: {state} ({tier}, timeout={timeout}s)")
    
    def check_blocking_conditions(self) -> bool:
        """检查阻塞条件
        
        Returns:
            True if blocked, False if not blocked
        """
        blocking_rules = [
            ("hierarchy", "failed", "严重降级"),
            ("delegation", "failed", "安全风险"),
            ("core", "failed", "致命错误"),
            ("dispatch", "failed", "无法路由")
        ]
        
        blocked = False
        for module, fail_state, reason in blocking_rules:
            if self.states.get(module) == fail_state:
                print(f"❌ BLOCKED: {module} is {fail_state} ({reason})")
                blocked = True
        
        return blocked
    
    def check_degradation_threshold(self) -> bool:
        """检查降级阈值
        
        Returns:
            True if threshold exceeded, False if not
        """
        degraded_count = sum(
            1 for s in self.states.values()
            if s in ["degraded", "failed", "soft_failed"]
        )
        
        total_count = len(self.states)
        threshold = 0.4  # 40%（来自 SKILL.md §四.2.1）
        
        ratio = degraded_count / total_count
        
        if ratio > threshold:
            print(f"❌ SNOWBALL ALERT: {degraded_count}/{total_count} ({ratio:.1%}) modules degraded")
            print("   Threshold exceeded (> 40%)")
            return True
        
        return False
    
    def _all_modules(self) -> list:
        """获取所有模块列表"""
        modules = []
        for tier_modules in MODULE_TIERS.values():
            modules.extend(tier_modules)
        return modules
    
    def _get_tier(self, module: str) -> str:
        """获取模块所属 Tier"""
        for tier, modules in MODULE_TIERS.items():
            if module in modules:
                return tier
        return "Unknown"
    
    def _check_propagation(self, module: str, new_state: str) -> None:
        """检查状态传播规则（来自 SKILL.md §四）"""
        propagation_rules = {
            "data": {
                "degraded": ["quality"],
                "failed": ["quality", "task"]
            },
            "hierarchy": {
                "failed": ["delegation", "task", "heartbeat"]
            },
            "delegation": {
                "failed": ["task"]
            }
        }
        
        if module in propagation_rules and new_state in propagation_rules[module]:
            downstream = propagation_rules[module][new_state]
            print(f"⚠️  Propagation alert: {module} → {new_state}")
            print(f"   Downstream modules affected: {downstream}")
            print(f"   Action: Check downstream module states")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="模块状态管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python state_manager.py --get core
    python state_manager.py --set core success
    python state_manager.py --list
    python state_manager.py --check-blocking
    python state_manager.py --check-threshold
        """
    )
    
    parser.add_argument(
        "--get",
        metavar="MODULE",
        help="获取单个模块状态"
    )
    
    parser.add_argument(
        "--set",
        nargs=2,
        metavar=("MODULE", "STATE"),
        help="设置模块状态"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有模块状态"
    )
    
    parser.add_argument(
        "--check-blocking",
        action="store_true",
        help="检查阻塞条件"
    )
    
    parser.add_argument(
        "--check-threshold",
        action="store_true",
        help="检查降级阈值"
    )
    
    parser.add_argument(
        "--state-file",
        default=".system/governance/current/gov-state.json",
        help="状态文件路径"
    )
    
    args = parser.parse_args()
    
    state_file = Path(args.state_file)
    manager = StateManager(state_file)
    
    if args.get:
        state = manager.get_state(args.get)
        print(state)
        sys.exit(0 if state != "failed" else 1)
    
    elif args.set:
        success = manager.set_state(args.set[0], args.set[1])
        sys.exit(0 if success else 1)
    
    elif args.list:
        manager.list_states()
        sys.exit(0)
    
    elif args.check_blocking:
        blocked = manager.check_blocking_conditions()
        sys.exit(1 if blocked else 0)
    
    elif args.check_threshold:
        exceeded = manager.check_degradation_threshold()
        sys.exit(1 if exceeded else 0)
    
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()