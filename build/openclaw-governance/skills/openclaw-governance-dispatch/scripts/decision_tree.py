#!/usr/bin/env python3
"""
decision_tree.py - Dispatch Routing Decision Tree

意图识别与路由决策树，用于 governance-dispatch 消息分拣。

Version: 3.0.0
Author: Governance Core Team
Created: 2026-04-22
Updated: 2026-04-22

Usage:
    python decision_tree.py --intent "创建项目"
    python decision_tree.py --classify "帮我写个文件"
    python decision_tree.py --help

References:
    - governance-dispatch SKILL.md §二 意图分类与路由表
    - governance-dispatch SKILL.md §三 路由执行流程
"""

import argparse
import json
import sys
from typing import Dict, Optional


# 意图映射表（来自 governance-dispatch SKILL.md §二.1）
INTENT_ROUTING = {
    "create_project": {
        "keywords": ["创建项目", "新建项目"],
        "skill": "governance-hierarchy",
        "agent": "main"
    },
    "create_task": {
        "keywords": ["创建任务", "新建任务", "分派任务"],
        "skill": "governance-task",
        "agent": "main"
    },
    "create_topic": {
        "keywords": ["创建 Topic", "新建主题"],
        "skill": "governance-hierarchy",
        "agent": "main"
    },
    "quality_review": {
        "keywords": ["审核", "验收交付物", "质量检查"],
        "skill": "governance-quality",
        "agent": "main"
    },
    "data_classify": {
        "keywords": ["数据分级", "路径校验"],
        "skill": "governance-data",
        "agent": "main"
    },
    "delegation_check": {
        "keywords": ["授权检查", "Review 级别判定", "降级申请"],
        "skill": "governance-delegation",
        "agent": "main"
    },
    "heartbeat_check": {
        "keywords": ["heartbeat", "日报", "巡检"],
        "skill": "governance-heartbeat",
        "agent": "main"
    },
    "risk_assess": {
        "keywords": ["风险评估", "风险识别", "风险登记"],
        "skill": "governance-risk",
        "agent": "main"
    },
    "pipeline_run": {
        "keywords": ["执行流水线", "启动 pipeline", "阀点管理"],
        "skill": "governance-pipeline",
        "agent": "main"
    },
    "evolution_eval": {
        "keywords": ["系统评估", "Skill 进化", "治理改进"],
        "skill": "governance-evolution",
        "agent": "main"
    },
    "chat": {
        "keywords": ["你好", "谢谢", "再见"],
        "skill": None,
        "agent": "main"
    }
}


class DecisionTree:
    """路由决策树"""
    
    def __init__(self):
        self.intent_routing = INTENT_ROUTING
        self.last_intent: Optional[str] = None
        self.last_result: Optional[Dict] = None
    
    def classify_intent(self, user_message: str) -> Dict:
        """分类用户意图
        
        Args:
            user_message: 用户消息
            
        Returns:
            分类结果字典
        """
        result = {
            "intent": None,
            "type": None,
            "is_production": False,
            "has_task_card": False,
            "skill": None,
            "agent": None,
            "blocked": False,
            "block_reason": None
        }
        
        # 1. 匹配意图关键词
        for intent_type, config in self.intent_routing.items():
            for keyword in config["keywords"]:
                if keyword in user_message:
                    result["intent"] = intent_type
                    result["skill"] = config["skill"]
                    result["agent"] = config["agent"]
                    break
            
            if result["intent"]:
                break
        
        # 2. 判断意图类型
        if result["intent"] in ["create_project", "create_task", "create_topic"]:
            result["type"] = "task"
            result["is_production"] = True
        elif result["intent"] == "chat":
            result["type"] = "chat"
        else:
            result["type"] = "task"
        
        # 3. 检查生产工作阻断
        if result["is_production"] and not result["has_task_card"]:
            result["blocked"] = True
            result["block_reason"] = "生产工作必须有 task-card，请先创建"
        
        # 4. 保存结果
        self.last_intent = result["intent"]
        self.last_result = result
        
        return result
    
    def check_route_permission(self, skill: str, agent: str) -> bool:
        """检查路由权限（调用 governance-delegation）
        
        Args:
            skill: 目标 Skill
            agent: 目标 Agent
            
        Returns:
            True if permitted, False otherwise
        """
        # 实际实现应调用 governance-delegation.check_route_permission()
        # 这里仅作为示例，默认返回 True
        return True
    
    def suggest_guidance(self, intent: str) -> str:
        """提供引导模板（来自 SKILL.md §三.4）
        
        Args:
            intent: 意图类型
            
        Returns:
            引导文本
        """
        guidance_templates = {
            "create_project": """
我理解您想创建新项目。请确认：

A. 在已有项目基础上创建新 Task/Topic（推荐，避免重复）
B. 确实需要创建新 Project（需要 Harold 审批）
C. 只是查询/讨论，不需要创建

回复 A/B/C 或描述具体需求。
""",
            "create_task": """
请确认 Task 归属：

A. 选择已有 Project + Topic（推荐）
B. 放入临时工作台（ZT-P-AGT-{agent}）
C. 放入 NUCLEUS 治理基础（ZT-P000）

回复 A/B/C 或描述具体归属。
""",
            "unknown": """
我理解您想{概括用户意图}，但需要确认具体操作：

A. {最可能的操作}
B. {次可能的操作}
C. 其他（请描述）

回复 A/B/C 或描述具体需求。
"""
        }
        
        return guidance_templates.get(intent, guidance_templates["unknown"])
    
    def format_result(self, result: Dict) -> str:
        """格式化结果输出
        
        Args:
            result: 分类结果
            
        Returns:
            格式化文本
        """
        if result["blocked"]:
            return f"❌ BLOCKED: {result['block_reason']}"
        
        status = "✅" if result["intent"] else "❓"
        
        output = [
            f"{status} Intent: {result['intent'] or 'unknown'}",
            f"   Type: {result['type'] or 'unknown'}",
            f"   Production: {result['is_production']}",
            f"   Skill: {result['skill'] or 'N/A'}",
            f"   Agent: {result['agent'] or 'N/A'}"
        ]
        
        return "\n".join(output)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Dispatch 路由决策树",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python decision_tree.py --intent "创建项目"
    python decision_tree.py --classify "帮我写个文件"
    python decision_tree.py --guide create_project
        """
    )
    
    parser.add_argument(
        "--intent",
        metavar="MESSAGE",
        help="识别用户意图"
    )
    
    parser.add_argument(
        "--classify",
        metavar="MESSAGE",
        help="分类用户消息"
    )
    
    parser.add_argument(
        "--guide",
        metavar="INTENT",
        help="提供引导模板"
    )
    
    args = parser.parse_args()
    
    tree = DecisionTree()
    
    if args.intent or args.classify:
        message = args.intent or args.classify
        result = tree.classify_intent(message)
        print(tree.format_result(result))
        
        # 如果意图不明确，提供引导
        if not result["intent"]:
            print("\n" + tree.suggest_guidance("unknown").format(
                概括用户意图=message[:50],
                最可能的操作="创建 Task",
                次可能的操作="查询状态"
            ))
        
        sys.exit(0 if not result["blocked"] else 1)
    
    elif args.guide:
        print(tree.suggest_guidance(args.guide))
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()