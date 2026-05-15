#!/usr/bin/env python3
"""
decision_tree.py - 组合失败处理决策树

Usage:
    python decision_tree.py --failed "delegation,hierarchy"
    python decision_tree.py --test
    python decision_tree.py --help

来源：SKILL.md §四.2 组合失败传播矩阵
"""

import argparse
import sys
import json
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Decision:
    """决策结果"""
    action: str
    reason: str
    severity: str = "LOW"
    impact: List[str] = None
    
    def __post_init__(self):
        if self.impact is None:
            self.impact = []

def handle_combined_failure(failed_modules: List[str]) -> Decision:
    """组合失败处理决策树
    
    Args:
        failed_modules: 失败模块列表
        
    Returns:
        Decision: 决策结果
    """
    
    # Rule 1: 安全优先
    if "delegation" in failed_modules:
        return Decision(
            action="BLOCK_PHASE_3",
            reason="delegation 失败影响权限验证",
            severity="CRITICAL",
            impact=["无法验证 task 权限", "安全风险"]
        )
    
    # Rule 2: 架构优先
    if "hierarchy" in failed_modules:
        return Decision(
            action="BLOCK_PHASE_3",
            reason="hierarchy 失败影响 Project 树",
            severity="HIGH",
            impact=["Project 结构不可用", "task 无法归属"]
        )
    
    # Rule 3: 数据传播
    if "data" in failed_modules and "quality" in failed_modules:
        return Decision(
            action="DEGRADE_BOTH",
            reason="data 降级传播到 quality",
            severity="MEDIUM",
            impact=["只读模式", "闭环不可用"]
        )
    
    # Rule 4: 独立降级
    if "config" in failed_modules:
        return Decision(
            action="USE_DEFAULTS",
            reason="config 失败使用内置默认值",
            severity="LOW",
            impact=["降级运行", "配置不可修改"]
        )
    
    return Decision(
        action="CONTINUE",
        reason="无阻塞条件",
        severity="LOW"
    )

def detect_cascade_snowball(degraded_modules: List[str]) -> bool:
    """检测级联降级是否超过阈值
    
    Args:
        degraded_modules: 降级模块列表
        
    Returns:
        bool: True 表示触发雪崩保护
    """
    DEGRADATION_THRESHOLD = 0.4  # 40% 模块降级
    total_modules = 8  # Phase 2A+2B+3+L3 有效模块数
    
    if len(degraded_modules) / total_modules > DEGRADATION_THRESHOLD:
        return True  # 触发雪崩保护（>=3 个模块降级）
    return False

def main():
    parser = argparse.ArgumentParser(
        description="组合失败处理决策树",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python decision_tree.py --failed "delegation,hierarchy"
  python decision_tree.py --test
        """
    )
    
    parser.add_argument(
        "--failed",
        help="失败模块列表（逗号分隔）"
    )
    
    parser.add_argument(
        "--degraded",
        help="降级模块列表（逗号分隔）"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="运行测试场景"
    )
    
    args = parser.parse_args()
    
    if args.test:
        # 运行测试场景
        test_scenarios = [
            ["delegation"],
            ["hierarchy"],
            ["data", "quality"],
            ["config"],
            ["delegation", "hierarchy"],
            []
        ]
        
        print("=" * 60)
        print("组合失败决策树测试")
        print("=" * 60)
        
        for failed in test_scenarios:
            decision = handle_combined_failure(failed)
            print(f"\n失败模块: {failed if failed else '无'}")
            print(f"决策: {decision.action}")
            print(f"原因: {decision.reason}")
            print(f"严重度: {decision.severity}")
            if decision.impact:
                print(f"影响: {decision.impact}")
        
        # 雪崩检测测试
        print("\n" + "=" * 60)
        print("雪崩检测测试")
        print("=" * 60)
        
        for degraded_count in [2, 3, 4, 5]:
            degraded = [f"module_{i}" for i in range(degraded_count)]
            is_snowball = detect_cascade_snowball(degraded)
            print(f"\n降级模块数: {degraded_count}")
            print(f"触发雪崩: {is_snowball}")
        
        sys.exit(0)
    
    if args.failed:
        failed_modules = [m.strip() for m in args.failed.split(",")]
        decision = handle_combined_failure(failed_modules)
        
        result = {
            "failed_modules": failed_modules,
            "decision": {
                "action": decision.action,
                "reason": decision.reason,
                "severity": decision.severity,
                "impact": decision.impact
            }
        }
        
        print(json.dumps(result, indent=2))
        sys.exit(0 if decision.action == "CONTINUE" else 1)
    
    if args.degraded:
        degraded_modules = [m.strip() for m in args.degraded.split(",")]
        is_snowball = detect_cascade_snowball(degraded_modules)
        
        result = {
            "degraded_modules": degraded_modules,
            "count": len(degraded_modules),
            "threshold": 3,
            "trigger_snowball": is_snowball
        }
        
        print(json.dumps(result, indent=2))
        sys.exit(1 if is_snowball else 0)
    
    parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()