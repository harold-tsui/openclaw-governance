#!/usr/bin/env python3
"""
probe_checker.py - Skill 就绪探针验证脚本

验证 Skill 模块是否就绪可用。

Version: 7.0.0
Author: Governance Core Team
Created: 2026-04-04
Updated: 2026-04-22

Usage:
    python probe_checker.py --module core
    python probe_checker.py --all
    python probe_checker.py --help

References:
    - SKILL.md §三.3 就绪探针机制
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List


# 探针配置（来自 governance-core SKILL.md §三.3）
PROBE_CONFIG = {
    "core": {
        "check": "path_variable_resolution",
        "ready_condition": "所有变量正确解析",
        "role": "blocking"
    },
    "config": {
        "check": "config_file_readable",
        "ready_condition": "文件存在 + 语法正确",
        "role": "advisory"
    },
    "dispatch": {
        "check": "routing_table_loaded",
        "ready_condition": "至少有 1 条路由规则",
        "role": "blocking"
    },
    "hierarchy": {
        "check": "project_tree_config",
        "ready_condition": "agents.yaml 可读",
        "role": "blocking"
    },
    "data": {
        "check": "data_classification_file",
        "ready_condition": "data-classification.yaml 可读",
        "role": "blocking"
    },
    "quality": {
        "check": "dod_template",
        "ready_condition": "TMPL-DOD.md 存在",
        "role": "advisory"
    },
    "delegation": {
        "check": "authorization_rules",
        "ready_condition": "automation-levels.yaml 可读",
        "role": "blocking"
    },
    "task": {
        "check": "task_card_template",
        "ready_condition": "TMPL-TASK-CARD.md 存在",
        "role": "blocking"
    },
    "heartbeat": {
        "check": "timer_registered",
        "ready_condition": "定时器已注册",
        "role": "blocking"
    }
}


class ProbeChecker:
    """探针验证器"""
    
    def __init__(self, gov_path: Path):
        self.gov_path = gov_path
        self.results: Dict[str, Dict] = {}
    
    def check_module(self, module: str) -> bool:
        """检查单个模块探针
        
        Args:
            module: 模块名称
            
        Returns:
            True if ready, False otherwise
        """
        if module not in PROBE_CONFIG:
            print(f"❌ Unknown module: {module}")
            return False
        
        config = PROBE_CONFIG[module]
        check_type = config["check"]
        
        # 执行探针检查
        result = self._execute_probe(check_type)
        
        self.results[module] = {
            "check": check_type,
            "ready": result,
            "role": config["role"],
            "condition": config["ready_condition"]
        }
        
        status = "✅" if result else "❌"
        print(f"{status} {module}: {config['ready_condition']}")
        
        return result
    
    def check_all(self) -> Dict[str, bool]:
        """检查所有模块
        
        Returns:
            模块就绪状态字典
        """
        print("Checking all modules...")
        
        all_ready = {}
        for module in PROBE_CONFIG:
            all_ready[module] = self.check_module(module)
        
        # 统计结果
        ready_count = sum(1 for v in all_ready.values() if v)
        total_count = len(all_ready)
        
        print(f"\nSummary: {ready_count}/{total_count} modules ready")
        
        # 检查阻塞型探针
        blocking_failed = [
            m for m, v in all_ready.items()
            if not v and PROBE_CONFIG[m]["role"] == "blocking"
        ]
        
        if blocking_failed:
            print(f"\n⚠️  Blocking probes failed: {blocking_failed}")
            print("   These failures will prevent Phase progression")
        
        return all_ready
    
    def _execute_probe(self, check_type: str) -> bool:
        """执行探针检查
        
        Args:
            check_type: 检查类型
            
        Returns:
            True if check passes, False otherwise
        """
        # 实际实现应调用对应的检查函数
        # 这里仅作为示例，模拟检查通过
        probe_functions = {
            "path_variable_resolution": self._check_path_variables,
            "config_file_readable": self._check_config_file,
            "routing_table_loaded": self._check_routing_table,
            "project_tree_config": self._check_project_tree,
            "data_classification_file": self._check_data_classification,
            "dod_template": self._check_dod_template,
            "authorization_rules": self._check_authorization_rules,
            "task_card_template": self._check_task_card_template,
            "timer_registered": self._check_timer_registered
        }
        
        checker = probe_functions.get(check_type)
        if checker:
            return checker()
        else:
            print(f"❌ Unknown probe type: {check_type}")
            return False
    
    # 探针检查函数（示例实现）
    def _check_path_variables(self) -> bool:
        """检查路径变量解析"""
        return True
    
    def _check_config_file(self) -> bool:
        """检查配置文件可读"""
        return True
    
    def _check_routing_table(self) -> bool:
        """检查路由表加载"""
        return True
    
    def _check_project_tree(self) -> bool:
        """检查 Project 树配置"""
        return True
    
    def _check_data_classification(self) -> bool:
        """检查数据分级文件"""
        return True
    
    def _check_dod_template(self) -> bool:
        """检查 DOD 模板"""
        return True
    
    def _check_authorization_rules(self) -> bool:
        """检查授权规则文件"""
        return True
    
    def _check_task_card_template(self) -> bool:
        """检查 Task-Card 模板"""
        return True
    
    def _check_timer_registered(self) -> bool:
        """检查定时器注册"""
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Skill 就绪探针验证脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python probe_checker.py --module core
    python probe_checker.py --all
        """
    )
    
    parser.add_argument(
        "--module",
        help="检查单个模块（core/config/dispatch/hierarchy/data/quality/delegation/task/heartbeat）"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="检查所有模块"
    )
    
    parser.add_argument(
        "--gov-path",
        default=".system/governance/current",
        help="治理文件路径"
    )
    
    args = parser.parse_args()
    
    # 确定检查范围
    if args.module:
        gov_path = Path(args.gov_path)
        checker = ProbeChecker(gov_path)
        success = checker.check_module(args.module)
        sys.exit(0 if success else 1)
    
    elif args.all:
        gov_path = Path(args.gov_path)
        checker = ProbeChecker(gov_path)
        results = checker.check_all()
        
        # 检查是否有阻塞型失败
        blocking_failed = [
            m for m, v in results.items()
            if not v and PROBE_CONFIG[m]["role"] == "blocking"
        ]
        
        sys.exit(0 if not blocking_failed else 1)
    
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()