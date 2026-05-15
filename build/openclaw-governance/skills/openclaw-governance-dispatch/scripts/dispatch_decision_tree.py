#!/usr/bin/env python3
"""
dispatch_decision_tree.py - Dispatch 引导决策树

Usage:
    python dispatch_decision_tree.py --intent "create_project"
    python dispatch_decision_tree.py --test
    python dispatch_decision_tree.py --help

来源：SKILL.md §二 意图分类与路由表
"""

import argparse
import sys
import json
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class DispatchDecision:
    """路由决策结果"""
    intent: str
    type: str  # task, chat, query
    skill: Optional[str]
    agent: str = "main"
    is_production: bool = False
    needs_guidance: bool = False
    guidance_type: Optional[str] = None

# 意图路由表
INTENT_ROUTING = {
    "create_project": DispatchDecision(
        intent="create_project",
        type="task",
        skill="governance-hierarchy",
        is_production=True,
        needs_guidance=True,
        guidance_type="create_project"
    ),
    "create_task": DispatchDecision(
        intent="create_task",
        type="task",
        skill="governance-task",
        is_production=True,
        needs_guidance=True,
        guidance_type="create_task"
    ),
    "create_topic": DispatchDecision(
        intent="create_topic",
        type="task",
        skill="governance-hierarchy",
        is_production=True,
        needs_guidance=True,
        guidance_type="create_topic"
    ),
    "quality_review": DispatchDecision(
        intent="quality_review",
        type="task",
        skill="governance-quality"
    ),
    "data_classify": DispatchDecision(
        intent="data_classify",
        type="task",
        skill="governance-data"
    ),
    "delegation_check": DispatchDecision(
        intent="delegation_check",
        type="task",
        skill="governance-delegation"
    ),
    "execute_task": DispatchDecision(
        intent="execute_task",
        type="task",
        skill="governance-heartbeat",
        is_production=True
    ),
    "task_complete": DispatchDecision(
        intent="task_complete",
        type="task",
        skill="governance-heartbeat",
        is_production=True
    ),
    "task_blocked": DispatchDecision(
        intent="task_blocked",
        type="task",
        skill="governance-heartbeat",
        is_production=True
    ),
    "heartbeat_check": DispatchDecision(
        intent="heartbeat_check",
        type="task",
        skill="governance-heartbeat"
    ),
    "risk_assess": DispatchDecision(
        intent="risk_assess",
        type="task",
        skill="governance-risk"
    ),
    "pipeline_run": DispatchDecision(
        intent="pipeline_run",
        type="task",
        skill="governance-pipeline"
    ),
    "evolution_eval": DispatchDecision(
        intent="evolution_eval",
        type="task",
        skill="governance-evolution"
    ),
    "chat": DispatchDecision(
        intent="chat",
        type="chat",
        skill=None,
        agent="main"
    )
}

# 引导触发关键词
GUIDANCE_KEYWORDS = {
    # P0 关键引导
    "create_project": ["创建项目", "新建项目", "立项"],
    "create_task": ["创建任务", "新建任务", "分派任务"],
    "create_topic": ["创建专题", "新建 Topic"],
    "execute_task": ["推进", "执行任务", "继续任务", "推进任务", "做这个任务"],
    
    # P1 重要引导
    "task_complete": ["做完了", "任务完成", "完成了"],
    "task_blocked": ["卡住了", "阻塞了", "无法继续"],
    "check_status": ["检查状态", "看看进度", "查一下"],
    "general_intent": ["帮我处理", "处理一下", "帮我"],
    
    # P2 次要引导
    "archive_task": ["归档这个任务", "归档"],
}

def match_intent(user_message: str) -> str:
    """匹配用户消息到意图类型
    
    Args:
        user_message: 用户消息
        
    Returns:
        str: 意图类型
    """
    # 简化版匹配逻辑（实际应使用更复杂的 NLP）
    for intent, keywords in GUIDANCE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in user_message:
                return intent
    return "chat"  # 默认闲聊

def determine_guidance(intent: str) -> Optional[str]:
    """判断是否需要引导
    
    Args:
        intent: 意图类型
        
    Returns:
        Optional[str]: 引导类型（None 表示不需要）
    """
    if intent in INTENT_ROUTING:
        return INTENT_ROUTING[intent].guidance_type
    return None

def main():
    parser = argparse.ArgumentParser(
        description="Dispatch 引导决策树",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python dispatch_decision_tree.py --intent "create_project"
  python dispatch_decision_tree.py --message "创建一个新项目"
  python dispatch_decision_tree.py --test
        """
    )
    
    parser.add_argument(
        "--intent",
        help="意图类型"
    )
    
    parser.add_argument(
        "--message",
        help="用户消息"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="运行测试场景"
    )
    
    args = parser.parse_args()
    
    if args.test:
        # 运行测试场景
        test_messages = [
            "创建一个新项目",
            "帮我完成任务",
            "今天天气怎么样",
            "处理一下文档",
            "任务完成了"
        ]
        
        print("=" * 60)
        print("Dispatch 引导决策树测试")
        print("=" * 60)
        
        for msg in test_messages:
            intent = match_intent(msg)
            decision = INTENT_ROUTING.get(intent, INTENT_ROUTING["chat"])
            
            print(f"\n用户消息: {msg}")
            print(f"意图: {intent}")
            print(f"类型: {decision.type}")
            print(f"路由 Skill: {decision.skill}")
            print(f"是否需要引导: {decision.needs_guidance}")
            if decision.guidance_type:
                print(f"引导类型: {decision.guidance_type}")
        
        sys.exit(0)
    
    if args.intent:
        decision = INTENT_ROUTING.get(args.intent, INTENT_ROUTING["chat"])
        print(json.dumps({
            "intent": decision.intent,
            "type": decision.type,
            "skill": decision.skill,
            "agent": decision.agent,
            "is_production": decision.is_production,
            "needs_guidance": decision.needs_guidance,
            "guidance_type": decision.guidance_type
        }, indent=2))
        sys.exit(0)
    
    if args.message:
        intent = match_intent(args.message)
        decision = INTENT_ROUTING.get(intent, INTENT_ROUTING["chat"])
        print(json.dumps({
            "message": args.message,
            "intent": intent,
            "decision": {
                "type": decision.type,
                "skill": decision.skill,
                "agent": decision.agent,
                "needs_guidance": decision.needs_guidance,
                "guidance_type": decision.guidance_type
            }
        }, indent=2))
        sys.exit(0)
    
    parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()